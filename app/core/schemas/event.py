from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class EventStatus(str, Enum):
    pending = "PENDING"
    win = "WIN"
    lose = "LOSE"


class SetEventStatus(BaseModel):
    new_event_status: EventStatus = ...


class Event(BaseModel):
    id: int = Field(..., ge=0)
    odds: Decimal = Field(..., ge=0, decimal_places=2)
    status: EventStatus = ...
    deadline: int = Field(..., ge=0)

