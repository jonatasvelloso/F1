import pytest

from f1.dashboard import build_lap_chart, entries_to_dataframe
from f1.domain.models import Driver, FastestLapEntry, Lap
from f1.processing.lap_processor import compute_top_n_laps


@pytest.fixture
def entries(
    sample_laps: list[Lap], sample_drivers: list[Driver]
) -> list[FastestLapEntry]:
    return compute_top_n_laps(sample_laps, sample_drivers, top_n=3)


def test_entries_to_dataframe(entries: list[FastestLapEntry]) -> None:
    df = entries_to_dataframe(entries)
    assert list(df.columns) == ["Posição", "Piloto", "Equipe", "Volta", "Tempo"]
    assert df.iloc[0]["Piloto"] == "Charles LECLERC"
    assert df.iloc[0]["Tempo"] == "1:30.700"


def test_build_lap_chart_uses_team_colours_and_zoomed_axis(
    entries: list[FastestLapEntry],
) -> None:
    figure = build_lap_chart(entries)
    (bar,) = figure.data
    assert list(bar.marker.color) == ["#E8002D", "#3671C6", "#27F4D2"]
    low, high = figure.layout.xaxis.range
    durations = [e.lap_duration for e in entries]
    assert 0 < low < min(durations)
    assert max(durations) < high
