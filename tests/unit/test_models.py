import pytest
from pydantic import ValidationError

from f1.domain.models import (
    DEFAULT_TEAM_COLOUR,
    Driver,
    FastestLapEntry,
    Lap,
    Meeting,
    SessionName,
)


def test_meeting_parses_api_payload_and_ignores_extra_fields() -> None:
    meeting = Meeting.model_validate(
        {
            "meeting_key": 1229,
            "meeting_name": "Bahrain Grand Prix",
            "country_name": "Bahrain",
            "circuit_short_name": "Sakhir",
            "date_start": "2024-02-29T11:30:00+00:00",
            "year": 2024,
            "location": "Sakhir",
        }
    )
    assert meeting.date_start.year == 2024
    assert meeting.is_cancelled is False
    assert not hasattr(meeting, "location")


def test_lap_defaults() -> None:
    lap = Lap(lap_number=1, driver_number=1)
    assert lap.lap_duration is None
    assert lap.is_pit_out_lap is False


def test_lap_null_pit_out_flag_becomes_false() -> None:
    lap = Lap.model_validate(
        {"lap_number": 1, "driver_number": 1, "is_pit_out_lap": None}
    )
    assert lap.is_pit_out_lap is False


def test_lap_rejects_non_positive_duration() -> None:
    with pytest.raises(ValidationError):
        Lap(lap_number=1, driver_number=1, lap_duration=0)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("3671c6", "#3671C6"),
        ("#e8002d", "#E8002D"),
        (None, DEFAULT_TEAM_COLOUR),
        ("not-a-colour", DEFAULT_TEAM_COLOUR),
    ],
)
def test_driver_team_colour_is_normalized(raw: str | None, expected: str) -> None:
    driver = Driver.model_validate({"driver_number": 1, "team_colour": raw})
    assert driver.team_colour == expected


def test_driver_default_colour_when_missing() -> None:
    assert Driver(driver_number=1).team_colour == DEFAULT_TEAM_COLOUR


def test_models_are_immutable() -> None:
    lap = Lap(lap_number=1, driver_number=1)
    with pytest.raises(ValidationError):
        lap.lap_number = 2  # type: ignore[misc]


def test_fastest_lap_entry_rank_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        FastestLapEntry(
            rank=0,
            driver_number=1,
            driver_name="X",
            driver_acronym="X",
            team_name="T",
            team_colour="#000000",
            lap_number=1,
            lap_duration=90.0,
        )


def test_session_name_values_match_api() -> None:
    assert SessionName.RACE == "Race"
    assert SessionName.QUALIFYING == "Qualifying"
