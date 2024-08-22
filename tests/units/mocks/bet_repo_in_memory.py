from decimal import Decimal

from app.repos.bet_repo_abstract import BetRepoAbstract


class BetRepoInMemory(BetRepoAbstract):

    storage: list[tuple[int, int, Decimal]]

    def __init__(self):
        self.storage = []

    async def add(self, stake: Decimal, event_id: int) -> int:
        bet_id = len(self.storage)
        self.storage.append((bet_id, event_id, stake))
        return bet_id

    async def get_all(self) -> list[tuple]:
        return self.storage
