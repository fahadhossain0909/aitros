"""Lifecycle service with audit-aware state transitions."""

from __future__ import annotations

from .exceptions import EventValidationError
from .interfaces import AuditSink
from .models import Event, EventState, can_transition


class LifecycleManager:
    """Centralizes lifecycle transition validation."""

    def __init__(self, audit: AuditSink | None = None) -> None:
        self._audit = audit
        self._states: dict[str, EventState] = {}

    def state(self, event: Event) -> EventState:
        return self._states.get(str(event.event_id), EventState.CREATED)

    async def transition(self, event: Event, target: EventState) -> EventState:
        current = self.state(event)
        if current is target:
            return current
        if not can_transition(current, target):
            raise EventValidationError(
                f"invalid lifecycle transition: {current.value} -> {target.value}"
            )
        self._states[str(event.event_id)] = target
        if self._audit is not None:
            await self._audit.record(event, "lifecycle", target.value)
        return target
