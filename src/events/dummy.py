from __future__ import annotations

import collections
from datetime import timedelta
from traceback import TracebackException

from .events import Event, EventBus, EventEnvironment


class DummyEventBus(EventBus):
    """
    A dummy event bus, used for testing & development.
    """

    def __init__(self) -> None:
        self.events: collections.defaultdict[EventEnvironment, list[Event]] = collections.defaultdict(list)

    async def __aenter__(self) -> DummyEventBus:
        return self

    async def __aexit__(
        self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackException
    ) -> None:
        """
        Clean up the event bus.
        """

        pass

    async def publish_event(self, event: Event, timeout: timedelta = timedelta(seconds=3)) -> None:
        """
        Publish an event to the event bus within the given timeline.
        Will raise an EventPublishTimeout on timeout.
        """

        self.events[event.environment].append(event)

    async def acknowledge_event(self, event: Event) -> None:
        """
        Acknowledge that an event from the event bus was handled.
        """

        self.events[event.environment].remove(event)

    async def nacknowledge_event(self, event: Event) -> None:
        """
        Acknowledge that an event from the event bus was not handled.
        """

        pass

    async def _pull_events(self, environment: EventEnvironment) -> list[Event]:
        """
        Pull events from the event bus.
        This method should not block indefinitely and only return a limited number of events. Preferably one.
        """

        return self.events[environment]
