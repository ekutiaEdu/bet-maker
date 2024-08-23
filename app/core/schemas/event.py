from dataclasses import Field
from enum import Enum

from pydantic import BaseModel


class EventStatus(str, Enum):
    WIN = "WIN"
    LOSE = "LOSE"


class SetEventStatus(BaseModel):
    new_event_status: EventStatus = ...
