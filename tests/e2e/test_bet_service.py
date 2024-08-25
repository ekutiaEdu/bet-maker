
import pytest
import requests
from config.config import settings
from starlette.status import HTTP_200_OK, HTTP_201_CREATED
from testcontainers.compose import DockerCompose


@pytest.fixture(scope="module")
def urls():
    base_url = f"http://localhost:{settings.SERVICE_EXTERNAL_PORT}"
    return {
        "docs": f"{base_url}/docs",
        "bets": f"{base_url}/bets",
        "events": f"{base_url}/events",
    }


@pytest.fixture(scope="module")
def service(urls):
    with DockerCompose(
            context=".",
            compose_file_name="docker-compose.yaml",
            build=True, pull=True, keep_volumes=False) as service:
        service.wait_for(url=urls["docs"])
        yield service


@pytest.mark.timeout(20)
def test_scenario_1(service, urls):
    event_id = 0

    response = requests.post(
        url=urls["bets"], json={"event_id": event_id, "stake": "3.14"}, timeout=3)
    assert response.status_code == HTTP_201_CREATED
    bet_id = response.json()["id"]

    response = requests.get(url=urls["bets"], timeout=3)
    assert response.status_code == HTTP_200_OK
    created_bet = next((bet for bet in response.json() if bet["id"] == bet_id), None)
    assert created_bet and created_bet["status"] == "pending"

    response = requests.put(
        url=f"{urls['events']}/{event_id}", json={"new_event_status": "WIN"}, timeout=3)
    assert response.status_code == HTTP_200_OK
    response = requests.get(url=urls["bets"], timeout=3)
    updated_bet = next((bet for bet in response.json() if bet["id"] == bet_id), None)
    assert updated_bet and updated_bet["status"] == "won"
