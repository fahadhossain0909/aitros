"""Dependency-inversion interfaces for the Event Bus runtime."""

from __future__ import annotations

from typing import Protocol, Sequence

from .models import AckStatus, Event, EventState


class Subscriber(Protocol):
    """A runtime component capable of receiving an event."""

    async def receive(self, event: Event) -> AckStatus:
        ...


class Router(Protocol):
    """Resolve an immutable event into subscriber identifiers."""

    async def resolve(self, event: Event) -> Sequence[str]:
        ...


class SubscriberResolver(Protocol):
    """Resolve subscriber identifiers into executable subscribers."""

    async def resolve(self, subscriber_id: str) -> Subscriber:
        ...


class EventStore(Protocol):
    """Durable persistence boundary used by the Event Bus."""

    async def append(self, event: Event) -> None:
        ...

    async def get(self, event_id: str) -> Event | None:
        ...


class LifecycleStore(Protocol):
    """Durable lifecycle transition boundary."""

    async def transition(self, event: Event, state: EventState) -> None:
        ...


class AuditSink(Protocol):
    """Immutable audit sink."""

    async def record(self, event: Event, action: str, detail: str | None = None) -> None:
        ...


class MetricsSink(Protocol):
    """Minimal metrics boundary; concrete exporters remain infrastructure-specific."""

    def increment(self, name: str, value: int = 1) -> None:
        ...

    def observe(self, name: str, value: float) -> None:
        ...


class TraceSink(Protocol):
    """Distributed tracing boundary."""

    async def start(self, event: Event) -> object:
        ...

    async def end(self, span: object, *, error: BaseException | None = None) -> None:
        ...
