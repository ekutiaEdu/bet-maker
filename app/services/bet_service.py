import time
from decimal import Decimal

from app.clients.event_client_abstract import EventClientAbstract
from app.core.exceptions import BetServiceException, ClientException, EventNotFound
from app.core.schemas.bet import Bet
from app.core.schemas.event import Event, EventStatus
from app.repos.bet_repo_abstract import BetRepoAbstract


class BetService:
    __repo: BetRepoAbstract
    __event_client: EventClientAbstract

    def __init__(
            self, repo: BetRepoAbstract, event_client: EventClientAbstract) -> None:
        self.__repo = repo
        self.__event_client = event_client

    async def create_bet(self, stake: Decimal, event_id: int) -> int:
        if stake.as_tuple().exponent != -2 or stake <= 0:
            raise ValueError()
        if not await self.__event_client.is_event_active(event_id=event_id):
            raise EventNotFound()
        bet_id = await self.__repo.add(stake=stake, event_id=event_id)
        return bet_id

    async def get_all_bets(self) -> list[Bet]:
        return await self.__repo.get_all()

    async def set_event_result(self, event_id: int, event_status: EventStatus) -> int:
        count_updated_bets = await self.__repo.update_bets_statuses_by_event_result(
            event_id=event_id, event_status=event_status)
        return count_updated_bets

    async def get_active_events(self) -> list[Event]:
        try:
            events = await self.__event_client.get_events()
        except ClientException as exc:
            raise BetServiceException() from exc
        return [event for event in events if event.deadline > int(time.time())]
