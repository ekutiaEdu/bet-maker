import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config.dependencies import get_redis_stream_consumer
from app.infrastructure.db.models.database import create_tables
from app.infrastructure.db.redis.redis_pool import redis_pool
from app.routers.bets_router import bet_router
from app.routers.events_router import events_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    redis_stream_consumer = await get_redis_stream_consumer()
    await redis_stream_consumer.connect()
    asyncio.create_task(redis_stream_consumer.start())

    yield

    await redis_stream_consumer.close()
    await redis_pool.aclose()


app = FastAPI(lifespan=lifespan)

app.include_router(bet_router)
app.include_router(events_router)
