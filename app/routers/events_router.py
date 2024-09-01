
from fastapi import APIRouter, Body, Depends, Path
from starlette.status import HTTP_200_OK

from app.config.dependencies import get_bet_service
from app.core.schemas.event import Event, SetEventStatus
from app.services.bet_service import BetService

events_router = APIRouter(prefix="/events", tags=["events"])


@events_router.put(
    "/{event_id}", status_code=HTTP_200_OK,
    name="events:set_event_status", deprecated=True)
async def set_event_status(
        event_id: int = Path(..., ge=0),
        event_status: SetEventStatus = Body(...),
        bet_service: BetService = Depends(get_bet_service)) -> None:
    await bet_service.set_event_result(
        event_id=event_id, event_status=event_status.new_event_status)


@events_router.get("/", status_code=HTTP_200_OK, name="events:get_all_active_events")
async def get_all_active_events(
        bet_service: BetService = Depends(get_bet_service)) -> list[Event]:
    return await bet_service.get_active_events()
