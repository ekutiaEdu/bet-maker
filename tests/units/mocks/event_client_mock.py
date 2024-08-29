from app.clients.event_client_abstract import EventClientAbstract
from app.core.schemas.event import Event


class EventClientMock(EventClientAbstract):

    events_storage: list[Event]

    def __init__(self, events: list[Event]) -> None:
        self.events_storage = events

    async def get_events(self) -> list[Event]:
        return self.events_storage

