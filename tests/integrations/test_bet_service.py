import os
from decimal import Decimal
from importlib import reload
from time import time

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import TypeAdapter
from redis.asyncio import Redis
from sqlalchemy import make_url
from starlette.status import HTTP_200_OK, HTTP_201_CREATED
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

import app.config.config as configuration
from app.core.schemas.bet import Bet
from app.core.schemas.event import Event, EventStatus
from app.infrastructure.db.models.bets import BetsOrm
from app.routers.dto.bet import BetCreatedResult


@pytest.fixture(scope="module")
def postgres_container():
    with PostgresContainer(driver="asyncpg", dbname="test_bet_db", ) as container:
        url = container.get_connection_url()
        print(f"{url=}")
        parsed_url = make_url(url)
        os.environ["POSTGRES_USER"] = str(parsed_url.username)
        os.environ["POSTGRES_PASSWORD"] = str(parsed_url.password)
        os.environ["POSTGRES_HOST"] = str(parsed_url.host)
        os.environ["POSTGRES_PORT"] = str(parsed_url.port)
        os.environ["POSTGRES_DB"] = str(parsed_url.database)
        reload(configuration)
        yield


@pytest.fixture(scope="module", autouse=True)
def redis_container() -> Redis:
    with RedisContainer() as container:
        container.start()
        client = container.get_client()
        host = client.connection_pool.connection_kwargs.get('host')
        port = client.connection_pool.connection_kwargs.get('port')
        os.environ["REDIS_USER"] = ""
        os.environ["REDIS_PASSWORD"] = ""
        os.environ["REDIS_HOST"] = host
        os.environ["REDIS_PORT"] = port
        reload(configuration)
        yield client


@pytest_asyncio.fixture(scope="function")
async def filled_redis(redis_container):
    event_1 = Event(
        id=1, odds=Decimal("1.11"),
        status=EventStatus.pending, deadline=int(time()) + 60)
    redis_container.set(f"event:{event_1.id}", event_1.model_dump_json())

    yield

    redis_container.flushdb()


@pytest_asyncio.fixture(scope="function")
async def empty_db(
        postgres_container):
    from app.infrastructure.db.models.bets import Base
    from app.infrastructure.db.models.database import engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def filled_db(empty_db):
    from app.infrastructure.db.models.database import session_maker
    async with session_maker() as session:
        session.add_all([
            BetsOrm(event_id=1, stake=Decimal("1.11")),
            BetsOrm(event_id=2, stake=Decimal("2.11")),
            BetsOrm(event_id=3, stake=Decimal("3.11"))
        ])
        await session.commit()


@pytest.fixture
def fastapi_app() -> FastAPI:
    from app.main import app
    return app


@pytest.fixture
async def client(fastapi_app: FastAPI) -> AsyncClient:
    async with AsyncClient(
            transport=ASGITransport(app=fastapi_app),
            base_url="http://localhost") as client:
        yield client


@pytest.mark.asyncio(loop_scope="module")
async def test_create_bet_endpoint(empty_db, client, fastapi_app, filled_redis):
    response = await client.post(
        url=fastapi_app.url_path_for("bets:add"),
        json={"event_id": 1, "stake": "100.14"})
    assert response.status_code == HTTP_201_CREATED
    assert BetCreatedResult.model_validate_json(response.text).id == 1


@pytest.mark.asyncio(loop_scope="module")
async def test_get_all_endpoint(filled_db, client, fastapi_app):
    response = await client.get(url=fastapi_app.url_path_for("bets:get_all"))
    assert response.status_code == HTTP_200_OK
    bet_list_adapter = TypeAdapter(list[Bet])
    bets = bet_list_adapter.validate_json(response.text)
    assert len(bets) == 3


@pytest.mark.asyncio(loop_scope="module")
async def test_set_event_status_endpoint(filled_db, client, fastapi_app):
    response = await client.put(
        url=fastapi_app.url_path_for(
            "events:set_event_status", event_id=1), json={"new_event_status": "WIN"})
    assert response.status_code == HTTP_200_OK


@pytest.mark.asyncio(loop_scope="module")
async def test_get_active_events_with_empty_redis(
        filled_db, client, fastapi_app):

    response = await client.get(url=fastapi_app.url_path_for(
        "events:get_all_active_events"))

    event_list_adapter = TypeAdapter(list[Event])
    events = event_list_adapter.validate_json(response.text)
    assert response.status_code == HTTP_200_OK
    assert len(events) == 0


@pytest.mark.asyncio(loop_scope="module")
async def test_get_active_events_with_1_event_in_redis(
        filled_db, client, fastapi_app, filled_redis):

    response = await client.get(url=fastapi_app.url_path_for(
        "events:get_all_active_events"))

    event_list_adapter = TypeAdapter(list[Event])
    events = event_list_adapter.validate_json(response.text)
    assert response.status_code == HTTP_200_OK
    assert len(events) == 1

