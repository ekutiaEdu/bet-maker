from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class CreateBet(BaseModel):
    event_id: int = Field(..., ge=0)
    stake: Decimal = Field(..., decimal_places=2, gt=0, examples=["100.12"])

    @field_validator("stake")
    @classmethod
    def check_stake(cls, v: Decimal):
        if v.as_tuple().exponent != -2:
            raise ValueError("The number must have exactly two decimal places.")
        return v


class BetCreatedResult(BaseModel):
    id: int = Field(..., ge=0)