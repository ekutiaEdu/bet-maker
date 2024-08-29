import time

import pytest
from pytest_mock import mocker

from app.clients.event_client_abstract import EventClientAbstract
from app.core.exceptions import ClientException, EventServiceException
from app.core.schemas.event import Event, EventStatus
from app.services.event_service import EventService
from tests.units.mocks.event_client_mock import EventClientMock


@pytest.fixture(scope="function")
def mock_event_client_with_4_events(mocker):
    events = [
        Event(id=1, odds="1.11", status=EventStatus.pending, deadline=int(time.time() + 10)),
        Event(id=2, odds="2.11", status=EventStatus.pending, deadline=int(time.time() + 100)),
        Event(id=3, odds="3.11", status=EventStatus.pending, deadline=int(time.time() + 1000)),
        Event(id=4, odds="4.11", status=EventStatus.pending, deadline=int(time.time() - 100)),]
    client_mock = mocker.AsyncMock(spec=EventClientAbstract)
    client_mock.get_events.return_value = events
    return client_mock


@pytest.fixture(scope="function")
def mock_event_client_with_exception(mocker):
    client_mock = mocker.AsyncMock(spec=EventClientAbstract)
    client_mock.get_events.side_effect = ClientException()
    return client_mock


async def test_get_events_return_only_active_events(mock_event_client_with_4_events):
    service = EventService(client=mock_event_client_with_4_events)
    active_events = await service.get_active_events()
    print(f"{active_events=}")
    assert len(active_events) == 3


async def test_get_events_raise_service_exception_in_case_client_exception(
        mock_event_client_with_exception):
    service = EventService(client=mock_event_client_with_exception)
    with pytest.raises(EventServiceException):
        await service.get_active_events()
