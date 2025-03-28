class EventBusException(Exception):
    pass


class EventPublishTimeout(EventBusException):
    pass


class StopListening(Exception):
    """
    This exception tells the receive_events function to stop listening and return.
    Set ack to False if you do not wish to ack the current event.
    """

    def __init__(self, ack: bool = True) -> None:
        self.ack = ack
