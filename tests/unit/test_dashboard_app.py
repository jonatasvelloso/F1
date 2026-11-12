from collections.abc import Iterator
from pathlib import Path

import pytest
import streamlit as st
from pytest_mock import MockerFixture
from streamlit.testing.v1 import AppTest

from f1.domain.models import Driver, Lap, Meeting
from f1.domain.services import F1DashboardService
from f1.ingestion.http_client import OpenF1APIError
from f1.processing.lap_processor import compute_top_n_laps
from f1.utils.config import available_years

DASHBOARD = Path(__file__).parents[2] / "src" / "f1" / "dashboard.py"


@pytest.fixture(autouse=True)
def _clear_streamlit_cache() -> Iterator[None]:
    st.cache_data.clear()
    st.cache_resource.clear()
    yield
    st.cache_data.clear()


def _run() -> AppTest:
    return AppTest.from_file(str(DASHBOARD), default_timeout=30).run()


def test_dashboard_renders_one_expander_per_meeting(
    mocker: MockerFixture,
    sample_meetings: list[Meeting],
    sample_laps: list[Lap],
    sample_drivers: list[Driver],
) -> None:
    mocker.patch.object(
        F1DashboardService, "get_meetings_for_year", return_value=sample_meetings[:2]
    )
    mocker.patch.object(
        F1DashboardService,
        "get_top_laps_for_meeting",
        side_effect=[compute_top_n_laps(sample_laps, sample_drivers), []],
    )

    app = _run()

    assert not app.exception
    assert len(app.expander) == 2
    assert len(app.dataframe) == 1
    assert app.info[0].value.startswith("Sessão sem voltas")


def test_dashboard_shows_error_when_api_fails(mocker: MockerFixture) -> None:
    mocker.patch.object(
        F1DashboardService, "get_meetings_for_year", side_effect=OpenF1APIError("x")
    )
    app = _run()
    assert not app.exception
    assert "OpenF1" in app.error[0].value


def test_dashboard_warns_when_season_is_empty(mocker: MockerFixture) -> None:
    mocker.patch.object(F1DashboardService, "get_meetings_for_year", return_value=[])
    app = _run()
    assert not app.exception
    assert "Nenhuma etapa" in app.warning[0].value


def test_dashboard_shows_error_per_meeting_when_laps_fail(
    mocker: MockerFixture, sample_meetings: list[Meeting]
) -> None:
    mocker.patch.object(
        F1DashboardService, "get_meetings_for_year", return_value=sample_meetings[:1]
    )
    mocker.patch.object(
        F1DashboardService,
        "get_top_laps_for_meeting",
        side_effect=OpenF1APIError("x"),
    )
    app = _run()
    assert not app.exception
    assert "voltas desta etapa" in app.error[0].value


def test_available_years_starts_in_2023_and_is_descending() -> None:
    years = available_years()
    assert years[-1] == 2023
    assert years == sorted(years, reverse=True)
