"""Audit sink for Event Bus lifecycle and delivery actions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .models import Event


@dataclass(frozen=True, slots=True)
class AuditRecord:
    event_id: str
    action: str
    timestamp: datetime
    detail: str | None = None


class InMemoryAuditSink:
    """Append-only reference audit sink."""

    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    async def record(
        self,
        event: Event,
        action: str,
        detail: str | None = None,
    ) -> None:
        self._records.append(
            AuditRecord(
                event_id=str(event.event_id),
                action=action,
                timestamp=datetime.now(timezone.utc),
                detail=detail,
            )
        )

    async def records(self) -> tuple[AuditRecord, ...]:
        return tuple(self._records)
