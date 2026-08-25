"""Domain models for the AITOS Event Bus."""

from .dispatch import AckStatus, DeliveryResult, DispatchPlan, DispatchSummary
from .event import (
    SPEC_VERSION,
    DeliveryMode,
    Event,
    EventMetadata,
    EventType,
    RoutingMetadata,
    RuntimeComponent,
    RuntimeEndpoint,
    SecurityMetadata,
    TraceMetadata,
    TrustLevel,
)
from .lifecycle import (
    EventState,
    InvalidLifecycleTransition,
    can_transition,
    is_terminal,
    transition,
)
from .reliability import (
    DeadLetterRecord,
    ReplayContext,
    RetryContext,
    RetryPolicy,
    RetryStrategy,
)

__all__ = [
    "AckStatus",
    "DeadLetterRecord",
    "DeliveryMode",
    "DeliveryResult",
    "DispatchPlan",
    "DispatchSummary",
    "Event",
    "EventMetadata",
    "EventState",
    "EventType",
    "InvalidLifecycleTransition",
    "ReplayContext",
    "RoutingMetadata",
    "RetryContext",
    "RetryPolicy",
    "RetryStrategy",
    "RuntimeComponent",
    "RuntimeEndpoint",
    "SPEC_VERSION",
    "SecurityMetadata",
    "TraceMetadata",
    "TrustLevel",
    "can_transition",
    "is_terminal",
    "transition",
]
