"""Event lifecycle state model and transition errors."""

from __future__ import annotations

from enum import StrEnum


class EventState(StrEnum):
    CREATED = "created"
    VALIDATED = "validated"
    AUTHENTICATED = "authenticated"
    AUTHORIZED = "authorized"
    ENRICHED = "enriched"
    PERSISTED = "persisted"
    ROUTED = "routed"
    QUEUED = "queued"
    DISPATCHED = "dispatched"
    DELIVERED = "delivered"
    ACKNOWLEDGED = "acknowledged"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY_PENDING = "retry_pending"
    DEAD_LETTER = "dead_letter"


class InvalidLifecycleTransition(ValueError):
    """Raised when an event attempts an invalid lifecycle transition."""


_TERMINAL = {EventState.COMPLETED, EventState.DEAD_LETTER}

_TRANSITIONS: dict[EventState, frozenset[EventState]] = {
    EventState.CREATED: frozenset({EventState.VALIDATED, EventState.FAILED}),
    EventState.VALIDATED: frozenset(
        {EventState.AUTHENTICATED, EventState.FAILED}
    ),
    EventState.AUTHENTICATED: frozenset(
        {EventState.AUTHORIZED, EventState.FAILED}
    ),
    EventState.AUTHORIZED: frozenset({EventState.ENRICHED, EventState.FAILED}),
    EventState.ENRICHED: frozenset({EventState.PERSISTED, EventState.FAILED}),
    EventState.PERSISTED: frozenset({EventState.ROUTED, EventState.FAILED}),
    EventState.ROUTED: frozenset({EventState.QUEUED, EventState.FAILED}),
    EventState.QUEUED: frozenset({EventState.DISPATCHED, EventState.FAILED}),
    EventState.DISPATCHED: frozenset(
        {EventState.DELIVERED, EventState.RETRY_PENDING, EventState.FAILED}
    ),
    EventState.DELIVERED: frozenset(
        {EventState.ACKNOWLEDGED, EventState.RETRY_PENDING, EventState.FAILED}
    ),
    EventState.ACKNOWLEDGED: frozenset({EventState.COMPLETED, EventState.FAILED}),
    EventState.RETRY_PENDING: frozenset(
        {EventState.QUEUED, EventState.DISPATCHED, EventState.DEAD_LETTER}
    ),
    EventState.FAILED: frozenset({EventState.RETRY_PENDING, EventState.DEAD_LETTER}),
    EventState.COMPLETED: frozenset(),
    EventState.DEAD_LETTER: frozenset(),
}


def can_transition(current: EventState, target: EventState) -> bool:
    """Return whether the lifecycle contract permits the transition."""
    return target in _TRANSITIONS[current]


def transition(current: EventState, target: EventState) -> EventState:
    """Validate and return a lifecycle transition."""
    if not can_transition(current, target):
        raise InvalidLifecycleTransition(
            f"invalid lifecycle transition: {current.value} -> {target.value}"
        )
    return target


def is_terminal(state: EventState) -> bool:
    """Return whether an event state is terminal."""
    return state in _TERMINAL
