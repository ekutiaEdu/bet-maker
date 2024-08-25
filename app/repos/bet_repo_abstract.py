import abc
from decimal import Decimal

from app.core.schemas.bet import Bet
from app.core.schemas.event import EventStatus


class BetRepoAbstract(abc.ABC):
    @abc.abstractmethod
    async def add(self, stake: Decimal, event_id: int) -> int:
        pass

    @abc.abstractmethod
    async def get_all(self) -> list[Bet]:
        pass

    @abc.abstractmethod
    async def update_bets_statuses_by_event_result(
            self, event_id: int, event_status: EventStatus) -> int:
        pass
