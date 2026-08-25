"""Canonical domain model for AITOS Runtime events."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping
from uuid import UUID


SPEC_VERSION = "1.0.0"
_EVENT_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{2,99}$")


class EventType(StrEnum):
    COMMAND = "command"
    QUERY = "query"
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    BROADCAST = "broadcast"
    WORKFLOW = "workflow"
    AGENT = "agent"
    MEMORY = "memory"
    CONTEXT = "context"
    REGISTRY = "registry"
    GOVERNANCE = "governance"
    SECURITY = "security"
    AUDIT = "audit"
    SYSTEM = "system"
    ERROR = "error"


class RuntimeComponent(StrEnum):
    EVENT_BUS = "event_bus"
    WORKFLOW_ENGINE = "workflow_engine"
    AGENT_HOST = "agent_host"
    CONTEXT_ENGINE = "context_engine"
    MEMORY_ENGINE = "memory_engine"
    REGISTRY = "registry"
    SCHEDULER = "scheduler"
    PLUGIN = "plugin"
    API_GATEWAY = "api_gateway"
    EXTERNAL = "external"


class TrustLevel(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    TRUSTED = "trusted"
    PRIVILEGED = "privileged"
    SYSTEM = "system"


class DeliveryMode(StrEnum):
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"


@dataclass(frozen=True, slots=True)
class RuntimeEndpoint:
    component: RuntimeComponent
    instance: str
    agent_id: str | None = None

    def __post_init__(self) -> None:
        if not self.instance.strip():
            raise ValueError("endpoint instance must not be empty")


@dataclass(frozen=True, slots=True)
class RoutingMetadata:
    topic: str
    delivery_mode: DeliveryMode
    partition: int | None = None
    priority: int = 50
    ttl_seconds: int | None = None

    def __post_init__(self) -> None:
        if not self.topic.strip():
            raise ValueError("routing topic must not be empty")
        if not 0 <= self.priority <= 100:
            raise ValueError("routing priority must be between 0 and 100")
        if self.partition is not None and self.partition < 0:
            raise ValueError("routing partition must be non-negative")
        if self.ttl_seconds is not None and self.ttl_seconds < 0:
            raise ValueError("routing TTL must be non-negative")


@dataclass(frozen=True, slots=True)
class SecurityMetadata:
    trust_level: TrustLevel
    authenticated: bool
    authorized: bool
    signature: str | None = None
    hash: str | None = None


@dataclass(frozen=True, slots=True)
class TraceMetadata:
    trace_id: str
    span_id: str
    parent_span_id: str | None = None

    def __post_init__(self) -> None:
        if not self.trace_id.strip() or not self.span_id.strip():
            raise ValueError("trace_id and span_id must not be empty")


@dataclass(frozen=True, slots=True)
class EventMetadata:
    schema_version: str | None = None
    producer_version: str | None = None
    runtime_version: str | None = None
    labels: Mapping[str, str] = field(default_factory=dict)
    extra: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "labels", MappingProxyType(dict(self.labels)))
        object.__setattr__(self, "extra", MappingProxyType(dict(self.extra)))


@dataclass(frozen=True, slots=True)
class Event:
    """Immutable event matching runtime/contracts/event_contract.json."""

    spec_version: str
    event_id: UUID
    event_type: EventType
    source: RuntimeEndpoint
    timestamp: datetime
    correlation_id: UUID
    payload: Mapping[str, Any]
    security: SecurityMetadata
    routing: RoutingMetadata
    event_name: str | None = None
    causation_id: UUID | None = None
    workflow_id: str | None = None
    task_id: str | None = None
    destination: RuntimeEndpoint | None = None
    metadata: EventMetadata = field(default_factory=EventMetadata)
    trace: TraceMetadata | None = None

    def __post_init__(self) -> None:
        if self.spec_version != SPEC_VERSION:
            raise ValueError(
                f"unsupported event contract version: {self.spec_version}"
            )
        if self.timestamp.tzinfo is None:
            raise ValueError("event timestamp must be timezone-aware")
        if self.event_name is not None and not _EVENT_NAME_PATTERN.fullmatch(
            self.event_name
        ):
            raise ValueError("event_name does not match the runtime contract")
        if not isinstance(self.payload, Mapping):
            raise TypeError("event payload must be a mapping")
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))

    @classmethod
    def create(
        cls,
        *,
        event_id: UUID,
        event_type: EventType,
        source: RuntimeEndpoint,
        correlation_id: UUID,
        payload: Mapping[str, Any],
        security: SecurityMetadata,
        routing: RoutingMetadata,
        event_name: str | None = None,
        timestamp: datetime | None = None,
        **kwargs: Any,
    ) -> "Event":
        return cls(
            spec_version=SPEC_VERSION,
            event_id=event_id,
            event_type=event_type,
            source=source,
            timestamp=timestamp or datetime.now(timezone.utc),
            correlation_id=correlation_id,
            payload=payload,
            security=security,
            routing=routing,
            event_name=event_name,
            **kwargs,
        )
