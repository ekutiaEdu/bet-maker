import asyncio

import pytest
from redis import Redis
from testcontainers.redis import RedisContainer

from app.core.schemas.event import EventStatus
from app.infrastructure.redis_stream_consumer import RedisStreamConsumer
from app.services.bet_service import BetService


@pytest.fixture(scope="module")
def redis() -> Redis:
    with RedisContainer() as container:
        container.start()
        yield container.get_client()


@pytest.fixture
def bet_service_mock(mocker) -> BetService:
    return mocker.AsyncMock(spec=BetService)


def test_create_connection(redis):
    redis.ping()


@pytest.mark.asyncio(loop_scope="module")
async def test_consumer_lifecycle(redis, bet_service_mock):
    host = redis.connection_pool.connection_kwargs.get('host')
    port = redis.connection_pool.connection_kwargs.get('port')
    consumer = RedisStreamConsumer(
        bet_service=bet_service_mock,
        host=host, port=port, username=None, password=None,
        stream="test_stream", group="test_group")
    await consumer.connect()
    asyncio.create_task(consumer.start())
    await consumer.close()


@pytest.mark.asyncio(loop_scope="module")
async def test_getting_message_from_stream(redis, bet_service_mock):

    host = redis.connection_pool.connection_kwargs.get('host')
    port = redis.connection_pool.connection_kwargs.get('port')
    consumer = RedisStreamConsumer(
        bet_service=bet_service_mock,
        host=host, port=port, username=None, password=None,
        stream="test_stream", group="test_group")
    await consumer.connect()
    asyncio.create_task(consumer.start())
    await asyncio.sleep(0.1)

    redis.xadd(
        name="test_stream", fields={"event_id": 0, "event_status": EventStatus.win})
    await asyncio.sleep(0.1)
    await consumer.close()

    bet_service_mock.set_event_result.assert_awaited_once()

