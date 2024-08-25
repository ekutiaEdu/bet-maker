from enum import Enum

from pydantic import BaseModel


class EventStatus(str, Enum):
    win = "WIN"
    lose = "LOSE"


class SetEventStatus(BaseModel):
    new_event_status: EventStatus = ...
