import asyncio
import uuid

from pydantic import BaseModel, Field
from redis import ResponseError
from redis.asyncio import Redis

from app.core.schemas.event import EventStatus
from app.services.bet_service import BetService


class RedisStreamConsumer:
    host: str
    port: int
    username: str | None
    password: str | None
    consumer_name: str
    group: str
    stream: str
    bet_service: BetService
    client: Redis | None
    is_stopped: bool

    class UpdateEventStatusDto(BaseModel):
        event_id: int = Field(..., ge=0)
        event_status: EventStatus = ...

    def __init__(
            self, bet_service: BetService, host: str, port: int,
            username: str | None, password: str | None,
            stream: str, group: str) -> None:
        self.port = port
        self.host = host
        self.username = username
        self.password = password
        self.stream = stream
        self.group = group
        self.consumer_name = uuid.uuid4().hex[:6].upper()

        self.bet_service = bet_service
        self.client = None

        self.is_stopped = True
        self.is_finalized = asyncio.Event()
        self.is_finalized.set()

    async def __group_exists(self) -> bool:
        try:
            groups_info = await self.client.xinfo_groups(self.stream)
            return any(group['name'] == self.group for group in groups_info)
        except ResponseError:
            return False

    async def __create_group(self) -> None:
        if await self.__group_exists():
            return
        await self.client.xgroup_create(
            name=self.stream, id="0", groupname=self.group, mkstream=True)

    async def connect(self) -> None:
        self.client = Redis(
            host=self.host, port=self.port,
            username=self.username, password=self.password, decode_responses=True)
        self.is_stopped = False

    async def start(self) -> None:
        if not self.client:
            raise RuntimeError("Must call connect() before starting.")

        await self.__create_group()
        self.is_finalized.clear()
        while not self.is_stopped:
            try:
                response_msg = await self.client.xreadgroup(
                    groupname=self.group,
                    consumername=self.consumer_name,
                    count=1,
                    noack=False,
                    block=1000,
                    streams={self.stream: ">"})
                for _, messages in response_msg:
                    for message_id, data in messages:
                        update_status_msg = (
                            self.UpdateEventStatusDto.model_validate(data))
                        await self.bet_service.set_event_result(
                            event_id=update_status_msg.event_id,
                            event_status=update_status_msg.event_status)
                        await self.client.xack(self.stream, self.group, message_id)

            except Exception as exc:
                print(f"Error in read messages from Redis: {exc}")

        self.is_finalized.set()

    async def close(self) -> None:
        if not self.client:
            return
        self.is_stopped = True
        await self.is_finalized.wait()
        await self.client.aclose()
        self.client = None

