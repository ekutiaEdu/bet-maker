from decimal import Decimal

from pydantic import TypeAdapter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas.bet import Bet
from app.core.schemas.event import EventStatus
from app.infrastructure.db.models.bets import BetsOrm
from app.repos.bet_repo_abstract import BetRepoAbstract


class BetRepoDb(BetRepoAbstract):
    __session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self.__session = session

    async def add(self, stake: Decimal, event_id: int) -> int:
        new_bet = BetsOrm(event_id=event_id, stake=stake)
        async with self.__session.begin():
            self.__session.add(new_bet)
        return new_bet.id

    async def get_all(self) -> list[Bet]:
        stmt = select(BetsOrm)
        result = await self.__session.execute(stmt)

        bet_list_adapter = TypeAdapter(list[Bet])
        return bet_list_adapter.validate_python(result.scalars().all())

    async def update_bets_statuses_by_event_result(self, event_id: int, event_status: EventStatus) -> int:
        stmt = select(BetsOrm).where(BetsOrm.event_id == event_id)
        async with self.__session.begin():
            result = await self.__session.execute(stmt)
            for bet in result.scalars().all():
                bet.status = "won" if event_status == EventStatus.win else "lost"
            count_updated_bets = len(result.all())
        return count_updated_bets
