import decimal

from app.core.schemas.bet import Bet
from app.repos.bet_repo_abstract import BetRepoAbstract


class BetService:
    __repo: BetRepoAbstract

    def __init__(self, repo: BetRepoAbstract) -> None:
        self.__repo = repo

    async def create_bet(self, stake_str: str, event_id: int) -> int:
        stake = decimal.Decimal(stake_str)
        if stake.as_tuple().exponent != -2 or stake <= 0:
            raise ValueError()
        bet_id = await self.__repo.add(stake=stake, event_id=event_id)
        return bet_id

    async def get_all_bets(self) -> list[Bet]:
        return await self.__repo.get_all()

    async def set_event_result(self, event_id: int, event_result: str) -> int:
        count_updated_bets = await self.__repo.update_bets_statuses_by_event_result(
            event_id=event_id, event_result=event_result)
        return count_updated_bets
