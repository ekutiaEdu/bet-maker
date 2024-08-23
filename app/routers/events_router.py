from fastapi import APIRouter, Path, Body
from starlette.status import HTTP_200_OK

from app.core.schemas.event import SetEventStatus
from app.repos.bet_repo_in_memory import BetRepoInMemory
from app.services.bet_service import BetService

events_router = APIRouter(prefix="/events", tags=["events"])


@events_router.put("/{event_id}", status_code=HTTP_200_OK)
async def set_event_result(event_id: int = Path(..., ge=0), event_status: SetEventStatus = Body()) -> None:
    repo = BetRepoInMemory()
    await BetService(repo=repo).set_event_result(event_id=event_id, event_result=event_status.new_event_status)
