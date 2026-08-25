"""Dead Letter Queue service for failed event isolation."""

from __future__ import annotations

from uuid import UUID

from .models import DeadLetterRecord, Event


class DeadLetterQueue:
    """In-memory reference DLQ; production adapters can persist records durably."""

    def __init__(self) -> None:
        self._records: dict[UUID, tuple[Event, DeadLetterRecord]] = {}

    async def put(
        self,
        event: Event,
        *,
        reason: str,
        attempts: int,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> DeadLetterRecord:
        from datetime import datetime, timezone

        record = DeadLetterRecord(
            event_id=event.event_id,
            reason=reason,
            failed_at=datetime.now(timezone.utc),
            attempts=attempts,
            last_error_code=error_code,
            last_error_message=error_message,
        )
        self._records[event.event_id] = (event, record)
        return record

    async def get(self, event_id: UUID) -> tuple[Event, DeadLetterRecord] | None:
        return self._records.get(event_id)

    async def list(self) -> tuple[DeadLetterRecord, ...]:
        return tuple(record for _, record in self._records.values())

    async def remove(self, event_id: UUID) -> None:
        self._records.pop(event_id, None)
