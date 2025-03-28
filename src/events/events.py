from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
from enum import StrEnum
from traceback import TracebackException

from pydantic import BaseModel

from .exceptions import StopListening

logger = logging.getLogger(__name__)


class EventEnvironment(StrEnum):
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"


class EventOriginDomain(StrEnum):
    ECOMMERCE = "ecommerce"
    WAREHOUSE = "warehouse"
    MARKETING = "marketing"
    ANIMALS = "animals"
    TEST = "test"


class EventMessageType(StrEnum):
    TEST = "test"


class EventEntityType(StrEnum):
    TEST = "test"


class Event(BaseModel):
    environment: EventEnvironment
    published_at: datetime
    origin_domain: EventOriginDomain
    message_type: EventMessageType
    entity_type: EventEntityType
    entity_id: str
    extra_data: dict[str, str]

    id: str | None = None


class EventBus(ABC):
    @abstractmethod
    async def __aenter__(self) -> EventBus:
        return self

    @abstractmethod
    async def __aexit__(
        self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackException
    ) -> None:
        pass

    @abstractmethod
    async def publish_event(self, event: Event, timeout: timedelta = timedelta(seconds=3)) -> None:
        """
        Publish an event to the event bus within the given timeline.
        Will raise an EventPublishTimeout on timeout.
        """

        pass

    @abstractmethod
    async def acknowledge_event(self, event: Event) -> None:
        """
        Acknowledge that an event from the event bus was handled.
        """

        pass

    @abstractmethod
    async def nacknowledge_event(self, event: Event) -> None:
        """
        Acknowledge that an event from the event bus was not handled.
        """

        pass

    @abstractmethod
    async def _pull_events(self, environment: EventEnvironment) -> list[Event]:
        """
        Pull events from the event bus.
        This method should not block indefinitely and only return a limited number of events. Preferably one.
        """

        pass

    async def receive_events(
        self, environment: EventEnvironment, callback: Callable[[Event], Awaitable[bool | None]]
    ) -> None:
        """
        Infinite loop that waits for events from the event bus and passes them into the provided callback.
        Will automatically ack handled events and nack events that raise exceptions.

        Callbacks may return `False` to manually nack the event.
        Only `None`, `False` & `True` are allowed as return values, any others will raise `ValueError`.

        Callbacks may raise `StopListening` to stop the event listener.
        """

        while True:
            events = await self._pull_events(environment)
            for event in events:
                try:
                    should_ack = await callback(event)
                    match should_ack:
                        case None | True:
                            await self.acknowledge_event(event)
                        case False:
                            await self.nacknowledge_event(event)
                        case _:
                            raise ValueError("Callback should return a boolean or None")
                except StopListening as err:
                    logger.debug("StopListening received, returning...")
                    if err.ack:
                        await self.acknowledge_event(event)
                    else:
                        await self.nacknowledge_event(event)
                    return
                except Exception as err:
                    await self.nacknowledge_event(event)
                    raise err

            # Sleep a bit to allow asyncio to handle other tasks.
            # This ensures that the loop will not block indefinitely if _pull_events if not awaiting anything.
            await asyncio.sleep(0.1)
