import asyncio
from decimal import Decimal
from time import time

import pytest
from redis.asyncio import Redis
from testcontainers.redis import AsyncRedisContainer

from app.clients.event_client_redis import EventClientRedis
from app.core.schemas.event import Event, EventStatus


@pytest.fixture(scope="module")
def redis_container() -> AsyncRedisContainer:
    with AsyncRedisContainer() as container:
        container.start()

        yield container


@pytest.fixture
async def redis(redis_container) -> Redis:
    redis_client = await redis_container.get_async_client(decode_responses=True)

    yield redis_client

    await redis_client.flushdb()
    await redis_client.aclose()


@pytest.fixture
def events():
    event_1 = Event(
        id=1, odds=Decimal("1.11"),
        status=EventStatus.pending, deadline=int(time()) + 60)
    event_2 = Event(
        id=2, odds=Decimal("2.11"),
        status=EventStatus.pending, deadline=int(time()) + 60)
    return [event_1, event_2]


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize("event_id, is_exist_expected", [(1, True), (2, False)])
async def test_check_event_in_redis_return_true_if_exists(
        redis, event_id, is_exist_expected, events):
    event_client = EventClientRedis(redis=redis)
    await redis.set(f"event:{events[0].id}", events[0].model_dump_json())

    is_exist = await event_client.is_event_active(event_id=event_id)

    assert is_exist == is_exist_expected


@pytest.mark.asyncio(loop_scope="module")
async def test_get_events_handles_empty_redis(redis):
    event_client = EventClientRedis(redis=redis)

    events = await event_client.get_events()

    assert events == []


@pytest.mark.asyncio(loop_scope="module")
async def test_get_events_handles_not_empty_redis(redis, events):
    event_client = EventClientRedis(redis=redis)
    await redis.set(f"event:{events[0].id}", events[0].model_dump_json())
    await redis.set(f"event:{events[1].id}", events[1].model_dump_json())

    actual_events = await event_client.get_events()

    assert len(actual_events) == 2


@pytest.mark.asyncio(loop_scope="module")
async def test_get_events_not_return_expired_event(redis, events):
    event_client = EventClientRedis(redis=redis)
    await redis.set(f"event:{events[0].id}", events[0].model_dump_json(), px=100)
    await redis.set(f"event:{events[1].id}", events[1].model_dump_json())
    await asyncio.sleep(0.1)

    events = await event_client.get_events()

    assert len(events) == 1
