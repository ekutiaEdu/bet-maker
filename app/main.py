from fastapi import FastAPI

from app.routers.bets_router import bet_router
from app.routers.events_router import events_router

app = FastAPI()

app.include_router(bet_router)
app.include_router(events_router)
