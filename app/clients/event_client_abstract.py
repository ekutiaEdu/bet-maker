from abc import ABC, abstractmethod

from app.core.schemas.event import Event


class EventClientAbstract(ABC):
    @abstractmethod
    async def get_events(self) -> list[Event]:
        pass

    @abstractmethod
    async def is_event_active(self, event_id: int) -> bool:
        pass
