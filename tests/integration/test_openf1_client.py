"""Testes contra a OpenF1 API real. Execute com: ``pytest -m integration``."""

import pytest

from f1.domain.services import F1DashboardService
from f1.ingestion.http_client import HttpClient
from f1.ingestion.openf1_client import (
    OpenF1DriverRepository,
    OpenF1LapRepository,
    OpenF1MeetingRepository,
    OpenF1SessionRepository,
)

pytestmark = pytest.mark.integration

BAHRAIN_2024_MEETING_KEY = 1229


@pytest.fixture(scope="module")
def client() -> HttpClient:
    return HttpClient()


def test_get_meetings_2024_parses_into_models(client: HttpClient) -> None:
    meetings = OpenF1MeetingRepository(client).get_meetings(2024)
    assert len(meetings) >= 20
    assert all(m.year == 2024 for m in meetings)
    assert BAHRAIN_2024_MEETING_KEY in {m.meeting_key for m in meetings}


def test_top_laps_bahrain_2024_race_end_to_end(client: HttpClient) -> None:
    service = F1DashboardService(
        meeting_repository=OpenF1MeetingRepository(client),
        session_repository=OpenF1SessionRepository(client),
        lap_repository=OpenF1LapRepository(client),
        driver_repository=OpenF1DriverRepository(client),
    )
    ranking = service.get_top_laps_for_meeting(BAHRAIN_2024_MEETING_KEY, "Race")
    assert len(ranking) == 5
    durations = [e.lap_duration for e in ranking]
    assert durations == sorted(durations)
    assert all(e.team_colour.startswith("#") for e in ranking)
