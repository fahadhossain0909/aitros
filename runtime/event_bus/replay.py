"""Replay service for immutable event re-execution."""

from __future__ import annotations

from uuid import UUID, uuid4

from .exceptions import ReplayError
from .interfaces import EventStore
from .models import Event, ReplayContext


class ReplayManager:
    """Creates replay contexts without mutating historical events."""

    def __init__(self, store: EventStore) -> None:
        self._store = store

    async def create_context(
        self,
        event_id: UUID,
        *,
        requested_by: str,
        reason: str,
    ) -> ReplayContext:
        event = await self._store.get(str(event_id))
        if event is None:
            raise ReplayError(f"event not found: {event_id}")
        return ReplayContext(
            replay_id=uuid4(),
            original_event_id=event.event_id,
            requested_by=requested_by,
            reason=reason,
        )

    async def load_original(self, event_id: UUID) -> Event:
        event = await self._store.get(str(event_id))
        if event is None:
            raise ReplayError(f"event not found: {event_id}")
        return event
