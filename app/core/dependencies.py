from app.repos.bet_repo_abstract import BetRepoAbstract
from app.repos.bet_repo_in_memory import BetRepoInMemory
from app.services.bet_service import BetService

repository = None


async def get_repository() -> BetRepoAbstract:
    global repository
    if not repository:
        repository = BetRepoInMemory()
    return repository


async def get_bet_service() -> BetService:
    return BetService(repo=await get_repository())