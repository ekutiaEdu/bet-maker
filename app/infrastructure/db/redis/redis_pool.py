import redis.asyncio as redis

from app.config.config import settings

print(f"{settings.redis_dsn=}")
redis_pool = redis.ConnectionPool.from_url(settings.redis_dsn)
