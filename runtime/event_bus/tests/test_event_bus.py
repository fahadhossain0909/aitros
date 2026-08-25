import asyncio
from uuid import uuid4

from runtime.event_bus import (
    AckStatus,
    DeliveryMode,
    Event,
    EventBus,
    EventType,
    RoutingMetadata,
    RuntimeComponent,
    RuntimeEndpoint,
    SecurityMetadata,
    TrustLevel,
)


class Subscriber:
    def __init__(self, status=AckStatus.ACK):
        self.status = status
        self.received = 0

    async def receive(self, event):
        self.received += 1
        return self.status


def make_event():
    return Event.create(
        event_id=uuid4(),
        event_type=EventType.NOTIFICATION,
        source=RuntimeEndpoint(RuntimeComponent.AGENT_HOST, "agent-1"),
        correlation_id=uuid4(),
        payload={"symbol": "BTCUSDT"},
        security=SecurityMetadata(TrustLevel.INTERNAL, True, True),
        routing=RoutingMetadata("market.tick", DeliveryMode.AT_LEAST_ONCE),
    )


def test_publish_delivers_and_completes() -> None:
    async def scenario():
        bus = EventBus()
        subscriber = Subscriber()
        await bus.subscribe("market.tick", "sink", subscriber)
        await bus.start()
        event = make_event()
        await bus.publish(event)
        await bus._queue.join()
        await bus.stop()
        assert subscriber.received == 1
        assert bus._state[str(event.event_id)].value == "completed"

    asyncio.run(scenario())


def test_failed_delivery_is_retried_and_then_dead_lettered() -> None:
    async def scenario():
        from runtime.event_bus.config import EventBusConfig
        from runtime.event_bus.models import RetryPolicy

        bus = EventBus(
            config=EventBusConfig(
                worker_count=1,
                retry_policy=RetryPolicy(
                    max_retries=1,
                    initial_delay_ms=1,
                    max_delay_ms=1,
                ),
            )
        )
        subscriber = Subscriber(AckStatus.NACK)
        await bus.subscribe("market.tick", "sink", subscriber)
        await bus.start()
        event = make_event()
        await bus.publish(event)
        await bus._queue.join()
        await bus.stop()
        assert subscriber.received == 2
        assert bus._state[str(event.event_id)].value == "dead_letter"

    asyncio.run(scenario())
