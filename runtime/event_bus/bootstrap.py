"""Reference bootstrap wiring for local and test deployments."""

from __future__ import annotations

from .audit import InMemoryAuditSink
from .config import EventBusConfig
from .event_bus import EventBus
from .metrics import InMemoryMetrics


async def create_reference_event_bus(
    config: EventBusConfig | None = None,
) -> EventBus:
    """Construct and start an infrastructure-neutral Event Bus."""
    audit = InMemoryAuditSink()
    metrics = InMemoryMetrics()
    bus = EventBus(config=config, audit=audit, metrics=metrics)
    await bus.start()
    return bus
