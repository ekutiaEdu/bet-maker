import decimal
from decimal import Decimal

import pytest
from contextlib import nullcontext as does_not_raise

from app.services.bet_service import BetService


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
        await BetService().create_bet(stake=stake)

