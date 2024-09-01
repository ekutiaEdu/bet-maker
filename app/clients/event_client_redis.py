import json

from redis.asyncio import Redis

from app.clients.event_client_abstract import EventClientAbstract
from app.core.schemas.event import Event


class EventClientRedis (EventClientAbstract):

    __redis: Redis

    def __init__(self, redis: Redis):
        self.__redis = redis

    async def is_event_active(self, event_id: int) -> bool:
        response = await self.__redis.get(name=f"event:{event_id}")
        return bool(response)

    async def get_events(self) -> list[Event]:
        keys = await self.__redis.keys('event:*')
        values = await self.__redis.mget(keys)
        events = []
        for value in values:
            event = Event.model_validate(json.loads(value))
            events.append(event)
        return events
