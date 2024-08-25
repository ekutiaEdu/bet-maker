from typing import Any

from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from app.config.dependencies import get_bet_service
from app.core.schemas.bet import Bet
from app.routers.dto.bet import BetCreatedResult, CreateBet
from app.services.bet_service import BetService

bet_router = APIRouter(prefix="/bets", tags=["bets"])


@bet_router.get(
    "/", response_model=list[Bet], status_code=HTTP_200_OK, name="bets:get_all")
async def get_all_bets(
        bet_service: BetService = Depends(get_bet_service)) -> Any:
    return await bet_service.get_all_bets()


@bet_router.post(
    "/", response_model=BetCreatedResult, status_code=HTTP_201_CREATED, name="bets:add")
async def add_bet(
        bet: CreateBet,
        bet_service: BetService = Depends(get_bet_service)) -> BetCreatedResult:
    bet_id = await bet_service.create_bet(stake=bet.stake, event_id=bet.event_id)
    return BetCreatedResult(id=bet_id)
