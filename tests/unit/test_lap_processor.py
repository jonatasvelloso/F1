import pytest

from f1.domain.models import DEFAULT_TEAM_COLOUR, Driver, Lap
from f1.processing.lap_processor import (
    build_driver_index,
    compute_top_n_laps,
    filter_valid_laps,
    format_lap_time,
)


def test_filter_valid_laps_removes_untimed_and_pit_out(sample_laps: list[Lap]) -> None:
    valid = filter_valid_laps(sample_laps)
    assert len(valid) == 6
    assert all(lap.lap_duration is not None for lap in valid)
    assert not any(lap.is_pit_out_lap for lap in valid)


def test_filter_valid_laps_empty() -> None:
    assert filter_valid_laps([]) == []


def test_build_driver_index(sample_drivers: list[Driver]) -> None:
    index = build_driver_index(sample_drivers)
    assert set(index) == {1, 16, 44}
    assert index[16].name_acronym == "LEC"


def test_compute_top_n_laps_orders_by_duration(
    sample_laps: list[Lap], sample_drivers: list[Driver]
) -> None:
    ranking = compute_top_n_laps(sample_laps, sample_drivers, top_n=3)
    assert [e.rank for e in ranking] == [1, 2, 3]
    assert [e.lap_duration for e in ranking] == [90.7, 90.9, 91.0]
    assert [e.driver_acronym for e in ranking] == ["LEC", "VER", "HAM"]
    assert ranking[0].team_colour == "#E8002D"


def test_compute_top_n_laps_ignores_pit_out_lap_even_if_fastest(
    sample_laps: list[Lap], sample_drivers: list[Driver]
) -> None:
    ranking = compute_top_n_laps(sample_laps, sample_drivers, top_n=10)
    assert 85.0 not in [e.lap_duration for e in ranking]


def test_compute_top_n_laps_allows_same_driver_twice(
    sample_laps: list[Lap], sample_drivers: list[Driver]
) -> None:
    ranking = compute_top_n_laps(sample_laps, sample_drivers, top_n=5)
    assert len(ranking) == 5
    assert [e.driver_acronym for e in ranking].count("VER") == 2


def test_compute_top_n_laps_returns_fewer_when_not_enough_laps(
    sample_drivers: list[Driver],
) -> None:
    laps = [Lap(lap_number=1, driver_number=1, lap_duration=90.0)]
    assert len(compute_top_n_laps(laps, sample_drivers, top_n=5)) == 1


def test_compute_top_n_laps_tie_breaks_by_lap_number(
    sample_drivers: list[Driver],
) -> None:
    laps = [
        Lap(lap_number=10, driver_number=1, lap_duration=90.0),
        Lap(lap_number=3, driver_number=16, lap_duration=90.0),
    ]
    ranking = compute_top_n_laps(laps, sample_drivers, top_n=2)
    assert [e.lap_number for e in ranking] == [3, 10]


def test_compute_top_n_laps_unknown_driver_gets_fallbacks() -> None:
    laps = [Lap(lap_number=1, driver_number=99, lap_duration=90.0)]
    (entry,) = compute_top_n_laps(laps, drivers=[], top_n=1)
    assert entry.driver_name == "#99"
    assert entry.driver_acronym == "99"
    assert entry.team_name == "Desconhecido"
    assert entry.team_colour == DEFAULT_TEAM_COLOUR


def test_compute_top_n_laps_driver_with_missing_fields() -> None:
    laps = [Lap(lap_number=1, driver_number=7, lap_duration=90.0)]
    (entry,) = compute_top_n_laps(laps, [Driver(driver_number=7)], top_n=1)
    assert entry.driver_name == "#7"
    assert entry.team_name == "Desconhecido"


def test_compute_top_n_laps_empty_input() -> None:
    assert compute_top_n_laps([], [], top_n=5) == []


@pytest.mark.parametrize("top_n", [0, -1])
def test_compute_top_n_laps_rejects_invalid_top_n(top_n: int) -> None:
    with pytest.raises(ValueError, match="top_n"):
        compute_top_n_laps([], [], top_n=top_n)


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (92.608, "1:32.608"),
        (59.9999, "1:00.000"),
        (5.1, "0:05.100"),
        (120.0, "2:00.000"),
    ],
)
def test_format_lap_time(seconds: float, expected: str) -> None:
    assert format_lap_time(seconds) == expected
