from contextlib import nullcontext as does_not_raise
from decimal import Decimal

import pytest

from app.clients.event_client_abstract import EventClientAbstract
from app.clients.event_client_stab import EventClientStab
from app.core.exceptions import BetServiceException, ClientException, EventNotFound
from app.core.schemas.bet import Bet, BetStatus
from app.core.schemas.event import EventStatus
from app.repos.bet_repo_in_memory import BetRepoInMemory
from app.services.bet_service import BetService


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
def event_client_mock():
    return EventClientStab()


@pytest.fixture
def mock_event_client_with_exception(mocker):
    client_mock = mocker.AsyncMock(spec=EventClientAbstract)
    client_mock.get_events.side_effect = ClientException()
    return client_mock


@pytest.fixture
async def bet_service_with_data(bet_repo_with_data, event_client_mock) -> BetService:
    return BetService(repo=bet_repo_with_data, event_client=event_client_mock)


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
async def test_stake_value_validation(stake, expectation, event_client_mock):
    with (expectation):
        await BetService(
            repo=BetRepoInMemory(),
            event_client=event_client_mock
        ).create_bet(stake=stake, event_id=1)


async def test_bet_valid_stake_save_it(event_client_mock):
    stake = Decimal("100.00")
    repo = BetRepoInMemory()

    bet_id = await (BetService(repo=repo, event_client=event_client_mock)
                    .create_bet(stake=stake, event_id=1))

    assert any(bet.id == bet_id for bet in repo.storage)


async def test_create_bet_for_not_active_event(bet_service_with_data):
    stake = Decimal("100.00")
    event_id_not_exist = 100

    with pytest.raises(EventNotFound):
        await bet_service_with_data.create_bet(stake=stake, event_id=event_id_not_exist)


async def test_get_all_return_all_bets(bet_service_with_data):
    assert len(await bet_service_with_data.get_all_bets()) == 5


async def test_get_all_return_bets_in_proper_format(bet_service_with_data):
    bet = (await bet_service_with_data.get_all_bets())[0]
    assert isinstance(bet, Bet)


async def test_set_event_result_return_proper_changed_event_count(
        bet_service_with_data):
    assert await bet_service_with_data.set_event_result(
        event_id=1, event_status=EventStatus.win) == 2


@pytest.mark.parametrize("event_id, event_status, bet_status",
                         [
                             (1, EventStatus.win, BetStatus.won),
                             (3, EventStatus.lose, BetStatus.lost),
                             (5, EventStatus.win, None),
                         ])
async def test_change_event_result_to_win_leds_to_changing_bets_status(
        event_id, event_status, bet_status, bet_repo_with_data, event_client_mock):
    service = BetService(repo=bet_repo_with_data, event_client=event_client_mock)

    await service.set_event_result(event_id=event_id, event_status=event_status)

    for bet in bet_repo_with_data.storage:
        if bet.event_id == event_id:
            assert bet.status == bet_status
        else:
            assert bet.status == BetStatus.pending


async def test_get_events_return_only_active_events(bet_service_with_data):
    active_events = await bet_service_with_data.get_active_events()
    assert len(active_events) == 3


async def test_get_events_raise_service_exception_in_case_client_exception(
        bet_repo_with_data,
        mock_event_client_with_exception):
    service = BetService(
        repo=bet_repo_with_data, event_client=mock_event_client_with_exception)
    with pytest.raises(BetServiceException):
        await service.get_active_events()


