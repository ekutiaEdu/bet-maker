import time

from app.clients.event_client_abstract import EventClientAbstract
from app.core.exceptions import ClientException, EventServiceException
from app.core.schemas.event import Event


class EventService:
    __client: EventClientAbstract

    def __init__(self, client: EventClientAbstract) -> None:
        self.__client = client

    async def get_active_events(self) -> list[Event]:
        try:
            events = await self.__client.get_events()
        except ClientException as exc:
            raise EventServiceException() from exc
        return [event for event in events if event.deadline > int(time.time())]

