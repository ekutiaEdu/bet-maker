import enum

from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class Status(enum.Enum):
    PENDING = "pending"
    WON = "won"
    LOST = "lost"


class BetsOrm(Base):
    __tablename__ = "bets"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column()
    stake: Mapped[Numeric] = mapped_column(Numeric(scale=2))
    status: Mapped[str] = mapped_column(default=Status.PENDING.value)
