from decimal import Decimal

from app.core.schemas.bet import Bet, BetStatus, BetFull
from app.repos.bet_repo_abstract import BetRepoAbstract


class BetRepoInMemory(BetRepoAbstract):
    storage: list[BetFull]

    def __init__(self):
        self.storage = []

    async def add(self, stake: Decimal, event_id: int) -> int:
        bet_id = len(self.storage)
        self.storage.append(BetFull(bet_id=bet_id, event_id=event_id, stake=stake, status="pending"))
        return bet_id

    async def get_all(self) -> list[Bet]:
        return self.storage

    async def update_bets_statuses_by_event_result(self, event_id: int, event_result: str) -> int:
        count_updated_bets = 0
        for bet in self.storage:
            if bet.event_id == event_id:
                match event_result:
                    case "win":
                        bet.status = BetStatus.won
                    case "lose":
                        bet.status = BetStatus.lost
                    case _:
                        raise ValueError("Event result valur is invalid.")
                count_updated_bets += 1
        return count_updated_bets


