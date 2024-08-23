from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator, ConfigDict


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


class CreateBet(BaseModel):
    event_id: int = Field(..., ge=0)
    stake: Decimal = Field(..., decimal_places=2, gt=0, examples=["100.12"])

    @field_validator("stake")
    @classmethod
    def check_stake(cls, v: Decimal):
        if v.as_tuple().exponent != -2:
            raise ValueError("The number must have exactly two decimal places.")
        return v
