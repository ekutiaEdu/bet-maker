from app.clients.event_client_stab import EventClientStab
from app.infrastructure.db.database import session_maker
from app.repos.bet_repo_abstract import BetRepoAbstract
from app.repos.bet_repo_db import BetRepoDb
from app.repos.bet_repo_in_memory import BetRepoInMemory
from app.services.bet_service import BetService

repository = None


async def get_repository() -> BetRepoAbstract:
    global repository
    if not repository:
        repository = BetRepoInMemory()
    return repository


async def get_bet_service() -> BetService:
    async with session_maker() as session:
        yield BetService(repo=BetRepoDb(session=session), event_client=EventClientStab())
