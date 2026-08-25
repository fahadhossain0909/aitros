from datetime import datetime, timezone
from uuid import uuid4

import pytest

from runtime.event_bus.models import (
    DeliveryMode,
    Event,
    EventType,
    RoutingMetadata,
    RuntimeComponent,
    RuntimeEndpoint,
    SecurityMetadata,
    TrustLevel,
)


def make_event(**overrides):
    values = {
        "event_id": uuid4(),
        "event_type": EventType.NOTIFICATION,
        "source": RuntimeEndpoint(RuntimeComponent.AGENT_HOST, "agent-1"),
        "correlation_id": uuid4(),
        "payload": {"value": 1},
        "security": SecurityMetadata(TrustLevel.INTERNAL, True, True),
        "routing": RoutingMetadata("market.tick", DeliveryMode.AT_LEAST_ONCE),
    }
    values.update(overrides)
    return Event.create(**values)


def test_event_creation_uses_contract_version() -> None:
    event = make_event()
    assert event.spec_version == "1.0.0"
    assert event.timestamp.tzinfo == timezone.utc


def test_event_payload_is_not_mutable() -> None:
    event = make_event()
    with pytest.raises(TypeError):
        event.payload["value"] = 2


def test_event_name_matches_contract() -> None:
    event = make_event(event_name="market.tick")
    assert event.event_name == "market.tick"


def test_invalid_event_name_is_rejected() -> None:
    with pytest.raises(ValueError):
        make_event(event_name="1-invalid")


def test_naive_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError):
        make_event(timestamp=datetime.now())
