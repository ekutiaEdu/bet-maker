from fastapi import APIRouter, Path, Body, Depends
from starlette.status import HTTP_200_OK

from app.core.dependencies import get_bet_service
from app.core.schemas.event import SetEventStatus
from app.repos.bet_repo_in_memory import BetRepoInMemory
from app.services.bet_service import BetService

events_router = APIRouter(prefix="/events", tags=["events"])


@events_router.put("/{event_id}", status_code=HTTP_200_OK)
async def set_event_result(
        event_id: int = Path(..., ge=0),
        event_status: SetEventStatus = Body(),
        bet_service: BetService = Depends(get_bet_service)) -> None:
    await bet_service.set_event_result(event_id=event_id, event_status=event_status.new_event_status)
