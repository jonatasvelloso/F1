from unittest.mock import MagicMock

import pytest

from f1.ingestion.http_client import HttpClient
from f1.ingestion.openf1_client import (
    OpenF1DriverRepository,
    OpenF1LapRepository,
    OpenF1MeetingRepository,
    OpenF1SessionRepository,
)


@pytest.fixture
def client() -> MagicMock:
    return MagicMock(spec=HttpClient)


def test_meeting_repository(client: MagicMock) -> None:
    client.get.return_value = [
        {
            "meeting_key": 1229,
            "meeting_name": "Bahrain Grand Prix",
            "country_name": "Bahrain",
            "circuit_short_name": "Sakhir",
            "date_start": "2024-02-29T11:30:00+00:00",
            "year": 2024,
        }
    ]
    (meeting,) = OpenF1MeetingRepository(client).get_meetings(2024)
    client.get.assert_called_once_with("meetings", params={"year": 2024})
    assert meeting.meeting_key == 1229


def test_session_repository(client: MagicMock) -> None:
    client.get.return_value = [
        {"session_key": 9472, "session_name": "Race", "session_type": "Race"}
    ]
    (session,) = OpenF1SessionRepository(client).get_sessions(1229, "Race")
    client.get.assert_called_once_with(
        "sessions", params={"meeting_key": 1229, "session_name": "Race"}
    )
    assert session.session_key == 9472


def test_lap_repository(client: MagicMock) -> None:
    client.get.return_value = [
        {"lap_number": 1, "driver_number": 1, "lap_duration": None},
        {"lap_number": 2, "driver_number": 1, "lap_duration": 96.296},
    ]
    laps = OpenF1LapRepository(client).get_laps(9472)
    client.get.assert_called_once_with("laps", params={"session_key": 9472})
    assert [lap.lap_duration for lap in laps] == [None, 96.296]


def test_driver_repository(client: MagicMock) -> None:
    client.get.return_value = [
        {"driver_number": 1, "full_name": "Max VERSTAPPEN", "team_colour": "3671c6"}
    ]
    (driver,) = OpenF1DriverRepository(client).get_drivers(9472)
    client.get.assert_called_once_with("drivers", params={"session_key": 9472})
    assert driver.team_colour == "#3671C6"
