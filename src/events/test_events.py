import asyncio
import collections
import random
from datetime import datetime, timedelta

import pytest

from .dummy import DummyEventBus
from .events import Event, EventBus, EventEntityType, EventEnvironment, EventMessageType, EventOriginDomain
from .exceptions import StopListening

EVENTBUS_INSTANCES = [
    DummyEventBus(),
]


@pytest.mark.parametrize(
    "eventbus_instance",
    EVENTBUS_INSTANCES,
)
@pytest.mark.asyncio
async def test_event_entity_id_matches(eventbus_instance: EventBus) -> None:
    """
    Tests that we receive an event with the same entity_id that we published.
    """

    entity_id = str(random.randint(-100000, 100000))

    async with eventbus_instance as bus:
        event = Event(
            environment=EventEnvironment.DEVELOPMENT,
            published_at=datetime.now(),
            origin_domain=EventOriginDomain.TEST,
            message_type=EventMessageType.TEST,
            entity_type=EventEntityType.TEST,
            entity_id=entity_id,
            extra_data={"test": "test"},
        )
        await bus.publish_event(event, timeout=timedelta(seconds=5))

        entity_ids = set()

        async def _handler(event: Event) -> bool:
            entity_ids.add(event.entity_id)

            if event.entity_id == entity_id:
                raise StopListening(ack=True)

            # Don't ack the event if not ours.
            return False

        async with asyncio.timeout(30):
            await bus.receive_events(EventEnvironment.DEVELOPMENT, _handler)

        assert entity_id in entity_ids


@pytest.mark.parametrize(
    "eventbus_instance",
    EVENTBUS_INSTANCES,
)
@pytest.mark.asyncio
async def test_event_nack_on_error(eventbus_instance: EventBus) -> None:
    """
    Tests that an event is nacked and thus is received multiple times
    when an error occurs in the handler.
    """

    entity_id = str(random.randint(-100000, 100000))

    async with eventbus_instance as bus:
        event = Event(
            environment=EventEnvironment.DEVELOPMENT,
            published_at=datetime.now(),
            origin_domain=EventOriginDomain.TEST,
            message_type=EventMessageType.TEST,
            entity_type=EventEntityType.TEST,
            entity_id=entity_id,
            extra_data={"test": "test"},
        )
        await bus.publish_event(event, timeout=timedelta(seconds=5))

        entity_id_count: collections.Counter[str] = collections.Counter()

        async def _handler(event: Event) -> None:
            entity_id_count.update([event.entity_id])
            raise RuntimeError("Test error")

        # Receive events twice while ignoring the RuntimeError we raise.
        try:
            await bus.receive_events(EventEnvironment.DEVELOPMENT, _handler)
        except RuntimeError:
            pass

        try:
            await bus.receive_events(EventEnvironment.DEVELOPMENT, _handler)
        except RuntimeError:
            pass

        # Check that we received the event at least twice (since it was never acked).
        assert entity_id_count[entity_id] >= 2


@pytest.mark.parametrize(
    "eventbus_instance",
    EVENTBUS_INSTANCES,
)
@pytest.mark.asyncio
async def test_event_ack_on_handled(eventbus_instance: EventBus) -> None:
    """
    Tests that an event is properly acked when handled and is thus not received again after successful handling.
    """

    entity_id = str(random.randint(-100000, 100000))

    async with eventbus_instance as bus:
        event = Event(
            environment=EventEnvironment.DEVELOPMENT,
            published_at=datetime.now(),
            origin_domain=EventOriginDomain.TEST,
            message_type=EventMessageType.TEST,
            entity_type=EventEntityType.TEST,
            entity_id=entity_id,
            extra_data={"test": "test"},
        )
        await bus.publish_event(event, timeout=timedelta(seconds=0.1))

        entity_id_count: collections.Counter[str] = collections.Counter()

        async def _handler(event: Event) -> bool:
            entity_id_count.update([event.entity_id])

            if event.entity_id == entity_id:
                raise StopListening(ack=True)

            # Don't ack the event if not ours.
            return False

        async with asyncio.timeout(30):
            await bus.receive_events(EventEnvironment.DEVELOPMENT, _handler)

        try:
            async with asyncio.timeout(0.1):
                await bus.receive_events(EventEnvironment.DEVELOPMENT, _handler)
                raise AssertionError("Event was received again.")
        except asyncio.exceptions.TimeoutError:
            pass

        assert entity_id_count[entity_id] == 1
