import time

from app.clients.event_client_abstract import EventClientAbstract
from app.core.schemas.event import Event, EventStatus


class EventClientStab(EventClientAbstract):

    async def get_events(self) -> list[Event]:
        return [
            Event(id=1, odds="1.11",
                  status=EventStatus.pending, deadline=int(time.time() + 10)),
            Event(id=2, odds="2.11",
                  status=EventStatus.pending, deadline=int(time.time() + 100)),
            Event(id=3, odds="3.11",
                  status=EventStatus.pending, deadline=int(time.time() + 1000)),
            Event(id=4, odds="4.11",
                  status=EventStatus.pending, deadline=int(time.time() - 100))
        ]

    async def is_event_active(self, event_id: int) -> bool:
        return any(event.id == event_id and int(time.time()) < event.deadline
                   for event in await self.get_events())
