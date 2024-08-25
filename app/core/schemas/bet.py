from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class BetStatus(str, Enum):
    pending = 'pending'
    won = 'won'
    lost = 'lost'


class Bet(BaseModel):
    id: int = Field(..., ge=0)
    status: BetStatus = ...

    model_config = ConfigDict(from_attributes=True)


class BetFull(Bet):
    stake: Decimal = Field(..., decimal_places=2)
    event_id: int = Field(..., ge=0)
