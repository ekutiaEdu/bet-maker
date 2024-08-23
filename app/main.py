from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.db.database import create_tables
from app.routers.bets_router import bet_router
from app.routers.events_router import events_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(bet_router)
app.include_router(events_router)
