from unittest.mock import MagicMock

import pytest

from f1.domain.models import Driver, Lap, Meeting, Session
from f1.domain.repositories import (
    DriverRepository,
    LapRepository,
    MeetingRepository,
    SessionRepository,
)
from f1.domain.services import F1DashboardService


@pytest.fixture
def repos() -> dict[str, MagicMock]:
    return {
        "meeting_repository": MagicMock(spec=MeetingRepository),
        "session_repository": MagicMock(spec=SessionRepository),
        "lap_repository": MagicMock(spec=LapRepository),
        "driver_repository": MagicMock(spec=DriverRepository),
    }


@pytest.fixture
def service(repos: dict[str, MagicMock]) -> F1DashboardService:
    return F1DashboardService(**repos)


def test_get_meetings_for_year_sorts_and_drops_cancelled(
    service: F1DashboardService,
    repos: dict[str, MagicMock],
    sample_meetings: list[Meeting],
) -> None:
    repos["meeting_repository"].get_meetings.return_value = sample_meetings

    result = service.get_meetings_for_year(2024)

    repos["meeting_repository"].get_meetings.assert_called_once_with(2024)
    assert [m.meeting_key for m in result] == [1229, 1230]


def test_get_top_laps_for_meeting_delegates_to_repositories(
    service: F1DashboardService,
    repos: dict[str, MagicMock],
    sample_laps: list[Lap],
    sample_drivers: list[Driver],
) -> None:
    repos["session_repository"].get_sessions.return_value = [
        Session(session_key=9472, session_name="Race", session_type="Race")
    ]
    repos["lap_repository"].get_laps.return_value = sample_laps
    repos["driver_repository"].get_drivers.return_value = sample_drivers

    result = service.get_top_laps_for_meeting(1229, "Race", top_n=2)

    repos["session_repository"].get_sessions.assert_called_once_with(1229, "Race")
    repos["lap_repository"].get_laps.assert_called_once_with(9472)
    repos["driver_repository"].get_drivers.assert_called_once_with(9472)
    assert [e.driver_acronym for e in result] == ["LEC", "VER"]


def test_get_top_laps_for_meeting_without_session_returns_empty(
    service: F1DashboardService, repos: dict[str, MagicMock]
) -> None:
    repos["session_repository"].get_sessions.return_value = []

    assert service.get_top_laps_for_meeting(1228, "Race") == []
    repos["lap_repository"].get_laps.assert_not_called()
    repos["driver_repository"].get_drivers.assert_not_called()
