from decimal import Decimal

from app.core.schemas.bet import Bet, BetFull, BetStatus
from app.core.schemas.event import EventStatus
from app.repos.bet_repo_abstract import BetRepoAbstract


class BetRepoInMemory(BetRepoAbstract):
    storage: list[BetFull]

    def __init__(self):
        self.storage = []

    async def add(self, stake: Decimal, event_id: int) -> int:
        bet_id = len(self.storage)
        self.storage.append(
            BetFull(id=bet_id, event_id=event_id, stake=stake, status="pending"))
        return bet_id

    async def get_all(self) -> list[Bet]:
        return self.storage

    async def update_bets_statuses_by_event_result(
            self, event_id: int, event_status: EventStatus) -> int:
        count_updated_bets = 0
        for bet in self.storage:
            if bet.event_id == event_id:
                match event_status:
                    case EventStatus.win:
                        bet.status = BetStatus.won
                    case EventStatus.lose:
                        bet.status = BetStatus.lost
                    case _:
                        raise ValueError("Event status value is invalid.")
                count_updated_bets += 1
        return count_updated_bets


