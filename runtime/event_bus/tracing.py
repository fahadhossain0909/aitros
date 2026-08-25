"""Distributed tracing boundary for the Event Bus."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from .models import Event


@dataclass(frozen=True, slots=True)
class TraceSpan:
    trace_id: str
    span_id: str
    event_id: str


class InMemoryTraceSink:
    """Reference tracing sink; replace with OpenTelemetry in deployment."""

    async def start(self, event: Event) -> TraceSpan:
        trace_id = event.trace.trace_id if event.trace else str(uuid4())
        span_id = event.trace.span_id if event.trace else str(uuid4())
        return TraceSpan(trace_id, span_id, str(event.event_id))

    async def end(self, span: object, *, error: BaseException | None = None) -> None:
        return None
