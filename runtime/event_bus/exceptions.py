"""Typed exceptions for Event Bus runtime failures."""

from __future__ import annotations


class EventBusError(Exception):
    """Base class for all Event Bus runtime errors."""


class EventValidationError(EventBusError):
    """Raised when an event violates its contract."""


class AuthenticationError(EventBusError):
    """Raised when event authentication fails."""


class AuthorizationError(EventBusError):
    """Raised when event authorization fails."""


class RoutingError(EventBusError):
    """Raised when no valid routing decision can be produced."""


class DispatchError(EventBusError):
    """Raised when delivery cannot be completed."""


class RetryExhaustedError(DispatchError):
    """Raised when retry policy is exhausted."""


class ReplayError(EventBusError):
    """Raised when replay cannot be performed."""


class DeadLetterError(EventBusError):
    """Raised when DLQ processing fails."""


class EventBusClosedError(EventBusError):
    """Raised when an operation is attempted on a closed bus."""
