import decimal

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

    async def get_all_bets(self) -> list[tuple]:
        return await self.__repo.get_all()
