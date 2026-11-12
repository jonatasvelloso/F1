from datetime import UTC, datetime

import pytest

from f1.domain.models import Driver, Lap, Meeting


@pytest.fixture
def sample_laps() -> list[Lap]:
    return [
        Lap(lap_number=1, driver_number=1, lap_duration=None),  # sem tempo
        Lap(lap_number=2, driver_number=1, lap_duration=91.5),
        Lap(lap_number=3, driver_number=1, lap_duration=90.9),
        Lap(lap_number=2, driver_number=16, lap_duration=91.2),
        Lap(lap_number=3, driver_number=16, lap_duration=85.0, is_pit_out_lap=True),
        Lap(lap_number=4, driver_number=16, lap_duration=90.7),
        Lap(lap_number=2, driver_number=44, lap_duration=92.1),
        Lap(lap_number=3, driver_number=44, lap_duration=91.0),
    ]


@pytest.fixture
def sample_drivers() -> list[Driver]:
    return [
        Driver(
            driver_number=1,
            full_name="Max VERSTAPPEN",
            name_acronym="VER",
            team_name="Red Bull Racing",
            team_colour="3671C6",
        ),
        Driver(
            driver_number=16,
            full_name="Charles LECLERC",
            name_acronym="LEC",
            team_name="Ferrari",
            team_colour="E8002D",
        ),
        Driver(
            driver_number=44,
            full_name="Lewis HAMILTON",
            name_acronym="HAM",
            team_name="Mercedes",
            team_colour="27F4D2",
        ),
    ]


@pytest.fixture
def sample_meetings() -> list[Meeting]:
    base = {"country_name": "Bahrain", "circuit_short_name": "Sakhir", "year": 2024}
    return [
        Meeting(
            meeting_key=1230,
            meeting_name="Saudi Arabian Grand Prix",
            date_start=datetime(2024, 3, 7, tzinfo=UTC),
            **base,
        ),
        Meeting(
            meeting_key=1229,
            meeting_name="Bahrain Grand Prix",
            date_start=datetime(2024, 2, 29, tzinfo=UTC),
            **base,
        ),
        Meeting(
            meeting_key=9999,
            meeting_name="Cancelled Grand Prix",
            date_start=datetime(2024, 4, 1, tzinfo=UTC),
            is_cancelled=True,
            **base,
        ),
    ]
