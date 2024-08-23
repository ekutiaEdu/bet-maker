from typing import Any

from fastapi import APIRouter, Body, Depends
from starlette.status import HTTP_201_CREATED, HTTP_200_OK

from app.core.dependencies import get_bet_service
from app.core.schemas.bet import Bet, CreateBet
from app.repos.bet_repo_in_memory import BetRepoInMemory
from app.services.bet_service import BetService

bet_router = APIRouter(prefix="/bets", tags=["bets"])


@bet_router.get("/", response_model=list[Bet], status_code=HTTP_200_OK)
async def get_all_bets(bet_service: BetService = Depends(get_bet_service)) -> Any:
    return await bet_service.get_all_bets()


@bet_router.post("/", response_model=int, status_code=HTTP_201_CREATED)
async def add_bet(bet: CreateBet, bet_service: BetService = Depends(get_bet_service)) -> int:
    return await bet_service.create_bet(stake=bet.stake, event_id=bet.event_id)
