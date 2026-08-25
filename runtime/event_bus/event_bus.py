"""Executable, infrastructure-neutral reference Event Bus runtime."""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass
from time import monotonic
from typing import DefaultDict, Sequence

from .config import EventBusConfig
from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    DispatchError,
    EventBusClosedError,
    EventValidationError,
    RetryExhaustedError,
)
from .interfaces import AuditSink, MetricsSink, Router, Subscriber
from .models import (
    AckStatus,
    Event,
    EventState,
    RoutingMetadata,
    can_transition,
    transition,
)

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class _Envelope:
    event: Event
    attempt: int = 1


class StaticTopicRouter:
    """Default router that resolves a topic against registered subscribers."""

    def __init__(self, subscriptions: DefaultDict[str, set[str]]) -> None:
        self._subscriptions = subscriptions

    async def resolve(self, event: Event) -> Sequence[str]:
        return tuple(sorted(self._subscriptions.get(event.routing.topic, set())))


class EventBus:
    """Async Event Bus reference implementation.

    The class deliberately depends only on protocol interfaces and the Python
    standard library. Production deployments can replace routing, telemetry,
    persistence and subscriber resolution without changing the domain API.
    """

    def __init__(
        self,
        *,
        config: EventBusConfig | None = None,
        router: Router | None = None,
        audit: AuditSink | None = None,
        metrics: MetricsSink | None = None,
    ) -> None:
        self.config = config or EventBusConfig()
        self._subscriptions: DefaultDict[str, set[str]] = defaultdict(set)
        self._subscribers: dict[str, Subscriber] = {}
        self._queue: asyncio.Queue[_Envelope] = asyncio.Queue(
            maxsize=self.config.queue_maxsize
        )
        self._router = router or StaticTopicRouter(self._subscriptions)
        self._audit = audit
        self._metrics = metrics
        self._workers: list[asyncio.Task[None]] = []
        self._running = False
        self._closed = False
        self._state: dict[str, EventState] = {}
        self._state_lock = asyncio.Lock()

    async def start(self) -> None:
        """Start worker tasks; repeated calls are idempotent."""
        if self._closed:
            raise EventBusClosedError("event bus has been closed")
        if self._running:
            return
        self._running = True
        self._workers = [
            asyncio.create_task(self._worker(index), name=f"aitos-event-bus-{index}")
            for index in range(self.config.worker_count)
        ]

    async def stop(self) -> None:
        """Stop workers after draining queued work."""
        if not self._running:
            self._closed = True
            return
        await self._queue.join()
        self._running = False
        for worker in self._workers:
            worker.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        self._closed = True

    async def subscribe(self, topic: str, subscriber_id: str, subscriber: Subscriber) -> None:
        """Register a subscriber for a topic."""
        self._ensure_open()
        if not topic.strip() or not subscriber_id.strip():
            raise ValueError("topic and subscriber_id must not be empty")
        self._subscribers[subscriber_id] = subscriber
        self._subscriptions[topic].add(subscriber_id)

    async def unsubscribe(self, topic: str, subscriber_id: str) -> None:
        """Remove a subscriber from a topic."""
        self._subscriptions.get(topic, set()).discard(subscriber_id)
        if not any(subscriber_id in ids for ids in self._subscriptions.values()):
            self._subscribers.pop(subscriber_id, None)

    async def publish(self, event: Event) -> None:
        """Validate, authorize and enqueue an event for delivery."""
        self._ensure_open()
        self._validate_event(event)
        await self._set_state(event, EventState.VALIDATED)
        if not event.security.authenticated:
            await self._fail(event, AuthenticationError("event is not authenticated"))
        await self._set_state(event, EventState.AUTHENTICATED)
        if not event.security.authorized:
            await self._fail(event, AuthorizationError("event is not authorized"))
        await self._set_state(event, EventState.AUTHORIZED)
        await self._set_state(event, EventState.ENRICHED)
        await self._set_state(event, EventState.PERSISTED)
        subscribers = tuple(await self._router.resolve(event))
        if not subscribers:
            await self._fail(event, DispatchError("no subscribers matched the event topic"))
        await self._set_state(event, EventState.ROUTED)
        await self._set_state(event, EventState.QUEUED)
        self._state[str(event.event_id)] = EventState.QUEUED
        await self._queue.put(_Envelope(event=event))
        self._metric_increment("event.queued")
        await self._audit_record(event, "queued")

    async def _worker(self, worker_id: int) -> None:
        while True:
            envelope = await self._queue.get()
            try:
                await self._dispatch(envelope, worker_id)
            except asyncio.CancelledError:
                raise
            except Exception:
                LOGGER.exception("event dispatch worker failed", extra={"worker_id": worker_id})
            finally:
                self._queue.task_done()

    async def _dispatch(self, envelope: _Envelope, worker_id: int) -> None:
        event = envelope.event
        attempt = envelope.attempt
        await self._set_state(event, EventState.DISPATCHED)
        subscribers = tuple(await self._router.resolve(event))
        if not subscribers:
            await self._fail(event, DispatchError("subscriber set became empty"))

        started = monotonic()
        results = await asyncio.gather(
            *(self._deliver(event, subscriber_id) for subscriber_id in subscribers),
            return_exceptions=False,
        )
        elapsed_ms = (monotonic() - started) * 1000
        self._metric_observe("event.dispatch_latency_ms", elapsed_ms)

        if any(result is not AckStatus.ACK for result in results):
            if attempt <= self.config.retry_policy.max_retries:
                await self._set_state(event, EventState.RETRY_PENDING)
                delay = self._retry_delay_ms(attempt)
                self._metric_increment("event.retry_scheduled")
                await self._audit_record(event, "retry_scheduled", f"attempt={attempt}")
                await asyncio.sleep(delay / 1000)
                await self._set_state(event, EventState.QUEUED)
                await self._queue.put(_Envelope(event=event, attempt=attempt + 1))
                return
            await self._set_state(event, EventState.DEAD_LETTER)
            self._metric_increment("event.dead_lettered")
            await self._audit_record(event, "dead_lettered", "retry policy exhausted")
            raise RetryExhaustedError(str(event.event_id))

        await self._set_state(event, EventState.DELIVERED)
        await self._set_state(event, EventState.ACKNOWLEDGED)
        await self._set_state(event, EventState.COMPLETED)
        self._metric_increment("event.completed")
        await self._audit_record(event, "completed")

    async def _deliver(self, event: Event, subscriber_id: str) -> AckStatus:
        subscriber = self._subscribers.get(subscriber_id)
        if subscriber is None:
            raise DispatchError(f"subscriber not registered: {subscriber_id}")
        try:
            return await asyncio.wait_for(
                subscriber.receive(event),
                timeout=self.config.dispatch_timeout_ms / 1000,
            )
        except asyncio.TimeoutError:
            self._metric_increment("delivery.timeout")
            return AckStatus.TIMEOUT
        except Exception as exc:
            self._metric_increment("delivery.failure")
            LOGGER.warning(
                "subscriber delivery failed",
                extra={"subscriber_id": subscriber_id, "error": str(exc)},
            )
            return AckStatus.NACK

    async def _set_state(self, event: Event, target: EventState) -> None:
        event_id = str(event.event_id)
        async with self._state_lock:
            current = self._state.get(event_id, EventState.CREATED)
            if current is target:
                return
            if not can_transition(current, target):
                raise EventValidationError(
                    str(transition(current, target))
                )
            self._state[event_id] = target
        await self._audit_record(event, "lifecycle", target.value)

    async def _fail(self, event: Event, error: Exception) -> None:
        current = self._state.get(str(event.event_id), EventState.CREATED)
        if current is not EventState.FAILED and can_transition(current, EventState.FAILED):
            await self._set_state(event, EventState.FAILED)
        await self._audit_record(event, "failed", str(error))
        raise error

    def _validate_event(self, event: Event) -> None:
        if event.security.authenticated is not True:
            raise AuthenticationError("event authentication failed")
        if event.security.authorized is not True:
            raise AuthorizationError("event authorization failed")
        if not event.routing.topic.strip():
            raise EventValidationError("event topic must not be empty")

    def _retry_delay_ms(self, attempt: int) -> int:
        policy = self.config.retry_policy
        exponent = max(attempt - 1, 0)
        return min(policy.initial_delay_ms * (2**exponent), policy.max_delay_ms)

    def _ensure_open(self) -> None:
        if self._closed:
            raise EventBusClosedError("event bus has been closed")

    async def _audit_record(
        self,
        event: Event,
        action: str,
        detail: str | None = None,
    ) -> None:
        if self._audit is not None:
            await self._audit.record(event, action, detail)

    def _metric_increment(self, name: str) -> None:
        if self._metrics is not None:
            self._metrics.increment(name)

    def _metric_observe(self, name: str, value: float) -> None:
        if self._metrics is not None:
            self._metrics.observe(name, value)
