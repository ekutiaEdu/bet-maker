import decimal
from decimal import Decimal

import pytest
from contextlib import nullcontext as does_not_raise

from app.services.bet_service import BetService
from tests.units.mocks.bet_repo_in_memory import BetRepoInMemory


@pytest.mark.parametrize("stake, expectation",
                         [
                             ("1.75", does_not_raise()),
                             ("1.01", does_not_raise()),
                             ("0.10", does_not_raise()),
                             ("0.1", pytest.raises(ValueError)),
                             ("0", pytest.raises(ValueError)),
                             ("0.00", pytest.raises(ValueError)),
                             ("-1.12", pytest.raises(ValueError)),
                             ("1.234", pytest.raises(ValueError)),
                         ])
async def test_stake_value_validation(stake, expectation):
    with expectation as e:
        await BetService(repo=BetRepoInMemory()).create_bet(stake_str=stake, event_id=0)


async def test_bet_valid_stake_save_it():
    stake = "100.00"
    repo = BetRepoInMemory()
    bet_id = await BetService(repo=repo).create_bet(stake_str=stake, event_id=0)
    assert any(bet[0] == bet_id for bet in repo.storage)


async def test_get_all_return_all_bets():
    bet_service = BetService(repo=BetRepoInMemory())
    await bet_service.create_bet(stake_str="1.11", event_id=1)
    await bet_service.create_bet(stake_str="2.22", event_id=2)
    await bet_service.create_bet(stake_str="3.33", event_id=3)
    assert len(await bet_service.get_all_bets()) == 3
