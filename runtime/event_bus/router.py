"""Routing service for Event Bus topic subscriptions."""

from __future__ import annotations

from collections import defaultdict

from .models import Event


class TopicRouter:
    """Deterministic in-memory topic router for the reference runtime."""

    def __init__(self) -> None:
        self._subscriptions: dict[str, set[str]] = defaultdict(set)

    def subscribe(self, topic: str, subscriber_id: str) -> None:
        if not topic.strip() or not subscriber_id.strip():
            raise ValueError("topic and subscriber_id must not be empty")
        self._subscriptions[topic].add(subscriber_id)

    def unsubscribe(self, topic: str, subscriber_id: str) -> None:
        self._subscriptions.get(topic, set()).discard(subscriber_id)

    async def resolve(self, event: Event) -> tuple[str, ...]:
        return tuple(sorted(self._subscriptions.get(event.routing.topic, set())))

    def subscribers(self, topic: str) -> tuple[str, ...]:
        return tuple(sorted(self._subscriptions.get(topic, set())))
