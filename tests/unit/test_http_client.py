from unittest.mock import MagicMock

import pytest
import requests

from f1.ingestion.http_client import HttpClient, OpenF1APIError


def _response(status: int = 200, payload: object = None) -> MagicMock:
    response = MagicMock(spec=requests.Response)
    response.status_code = status
    response.json.return_value = payload
    if status >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(f"{status}")
    return response


@pytest.fixture
def session() -> MagicMock:
    return MagicMock(spec=requests.Session)


def test_get_builds_url_and_passes_timeout(session: MagicMock) -> None:
    session.get.return_value = _response(payload=[{"a": 1}])
    client = HttpClient(base_url="https://api.test/v1/", timeout=5, session=session)

    assert client.get("/meetings", params={"year": 2024}) == [{"a": 1}]
    session.get.assert_called_once_with(
        "https://api.test/v1/meetings", params={"year": 2024}, timeout=5
    )


def test_get_returns_empty_list_on_404(session: MagicMock) -> None:
    session.get.return_value = _response(status=404)
    assert HttpClient(session=session).get("laps") == []


def test_get_raises_on_http_error(session: MagicMock) -> None:
    session.get.return_value = _response(status=500)
    with pytest.raises(OpenF1APIError):
        HttpClient(session=session).get("laps")


def test_get_raises_on_network_error(session: MagicMock) -> None:
    session.get.side_effect = requests.ConnectionError("down")
    with pytest.raises(OpenF1APIError, match="down"):
        HttpClient(session=session).get("laps")


def test_get_raises_on_invalid_json(session: MagicMock) -> None:
    response = _response()
    response.json.side_effect = ValueError("bad json")
    session.get.return_value = response
    with pytest.raises(OpenF1APIError):
        HttpClient(session=session).get("laps")


def test_get_raises_when_payload_is_not_a_list(session: MagicMock) -> None:
    session.get.return_value = _response(payload={"detail": "oops"})
    with pytest.raises(OpenF1APIError, match="dict"):
        HttpClient(session=session).get("laps")


def test_default_session_has_retry_policy() -> None:
    client = HttpClient(max_retries=4)
    adapter = client._session.get_adapter("https://api.openf1.org")
    assert adapter.max_retries.total == 4
    assert 429 in adapter.max_retries.status_forcelist
