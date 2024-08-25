from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.config.config import settings
from app.infrastructure.db.models.bets import Base

engine = create_async_engine(settings.pg_dsn)
session_maker = async_sessionmaker(expire_on_commit=False, bind=engine)


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
