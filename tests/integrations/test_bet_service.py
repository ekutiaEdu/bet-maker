import os
from decimal import Decimal
from importlib import reload

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import TypeAdapter
from sqlalchemy import make_url
from starlette.status import HTTP_200_OK, HTTP_201_CREATED
from testcontainers.postgres import PostgresContainer

import app.config.config as configuration
from app.core.schemas.bet import Bet
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


@pytest_asyncio.fixture(scope="function")
async def empty_db(
        postgres_container):
    from app.infrastructure.db.database import engine
    from app.infrastructure.db.models.bets import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def filled_db(empty_db):
    from app.infrastructure.db.database import session_maker
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
async def test_create_bet_endpoint(empty_db, client, fastapi_app):
    response = await client.post(
        url=fastapi_app.url_path_for("bets:add"),
        json={"event_id": 0, "stake": "100.14"})
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
