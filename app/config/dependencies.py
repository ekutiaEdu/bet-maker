from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.event_client_redis import EventClientRedis
from app.config.config import settings
from app.infrastructure.db.models.database import session_maker
from app.infrastructure.db.redis.redis_pool import redis_pool
from app.infrastructure.redis_stream_consumer import RedisStreamConsumer
from app.repos.bet_repo_db import BetRepoDb
from app.services.bet_service import BetService


async def get_bet_service() -> BetService:
    async with session_maker() as session:
        redis_client = await Redis.from_pool(connection_pool=redis_pool)
        event_client = EventClientRedis(redis=redis_client)

        yield BetService(
            repo=BetRepoDb(session=session), event_client=event_client)

        await redis_client.aclose()


async def get_redis_stream_consumer(session: AsyncSession, redis_client: Redis) -> RedisStreamConsumer:
    bet_service = BetService(
        repo=BetRepoDb(session=session),
        event_client=EventClientRedis(redis=redis_client))
    return RedisStreamConsumer(
        bet_service=bet_service,
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        username=settings.REDIS_USER,
        password=settings.REDIS_PASSWORD,
        stream=settings.REDIS_EVENTS_STREAM,
        group="bet-maker-group"
    )
