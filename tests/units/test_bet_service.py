from decimal import Decimal

import pytest
from contextlib import nullcontext as does_not_raise

from app.core.schemas.bet import Bet, BetStatus
from app.services.bet_service import BetService
from app.repos.bet_repo_in_memory import BetRepoInMemory


@pytest.fixture
async def bet_repo_with_data() -> BetRepoInMemory:
    repo = BetRepoInMemory()
    await repo.add(stake=Decimal("1.01"), event_id=1)
    await repo.add(stake=Decimal("2.01"), event_id=2)
    await repo.add(stake=Decimal("3.01"), event_id=3)
    await repo.add(stake=Decimal("1.02"), event_id=1)
    await repo.add(stake=Decimal("2.02"), event_id=2)
    return repo


@pytest.fixture
async def bet_service_with_data(bet_repo_with_data) -> BetService:
    return BetService(repo=bet_repo_with_data)


@pytest.mark.parametrize("stake, expectation",
                         [
                             (Decimal("1.75"), does_not_raise()),
                             (Decimal("1.01"), does_not_raise()),
                             (Decimal("0.10"), does_not_raise()),
                             (Decimal("0.1"), pytest.raises(ValueError)),
                             (Decimal("0"), pytest.raises(ValueError)),
                             (Decimal("0.00"), pytest.raises(ValueError)),
                             (Decimal("-1.12"), pytest.raises(ValueError)),
                             (Decimal("1.234"), pytest.raises(ValueError)),
                         ])
async def test_stake_value_validation(stake, expectation):
    with expectation as e:
        await BetService(repo=BetRepoInMemory()).create_bet(stake=stake, event_id=0)


async def test_bet_valid_stake_save_it():
    stake = Decimal("100.00")
    repo = BetRepoInMemory()

    bet_id = await BetService(repo=repo).create_bet(stake=stake, event_id=0)

    assert any(bet.bet_id == bet_id for bet in repo.storage)


async def test_get_all_return_all_bets(bet_service_with_data):
    assert len(await bet_service_with_data.get_all_bets()) == 5


async def test_get_all_return_bets_in_proper_format(bet_service_with_data):
    bet = (await bet_service_with_data.get_all_bets())[0]
    assert isinstance(bet, Bet)


async def test_set_event_result_return_proper_changed_event_count(bet_service_with_data):
    assert await bet_service_with_data.set_event_result(event_id=1, event_result="win") == 2


@pytest.mark.parametrize("event_id, event_result, bet_status",
                         [
                             (1, "win", BetStatus.won),
                             (3, "lose", BetStatus.lost),
                             (5, "win", None),
                         ])
async def test_change_event_result_to_win_leds_to_changing_bets_status(
        event_id, event_result, bet_status, bet_repo_with_data):
    service = BetService(repo=bet_repo_with_data)

    await service.set_event_result(event_id=event_id, event_result=event_result)

    for bet in bet_repo_with_data.storage:
        if bet.event_id == event_id:
            assert bet.status == bet_status
        else:
            assert bet.status == BetStatus.pending
