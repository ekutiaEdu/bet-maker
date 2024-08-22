import abc
from decimal import Decimal


class BetRepoAbstract(abc.ABC):
    @abc.abstractmethod
    async def add(self, stake: Decimal, event_id: int) -> int:
        pass

    @abc.abstractmethod
    async def get_all(self) -> list[tuple]:
        pass
