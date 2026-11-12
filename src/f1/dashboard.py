"""Dashboard Streamlit: top voltas mais rápidas por etapa (composition root + UI).

Execução: ``poetry run streamlit run src/f1/dashboard.py``.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from f1.domain.models import FastestLapEntry, Meeting, SessionName
from f1.domain.services import F1DashboardService
from f1.ingestion.http_client import HttpClient, OpenF1APIError
from f1.ingestion.openf1_client import (
    OpenF1DriverRepository,
    OpenF1LapRepository,
    OpenF1MeetingRepository,
    OpenF1SessionRepository,
)
from f1.processing.lap_processor import format_lap_time
from f1.utils.config import CACHE_TTL_SECONDS, DEFAULT_YEAR, TOP_N_LAPS, available_years
from f1.utils.logger import get_logger

logger = get_logger(__name__)

SESSION_LABELS: dict[str, SessionName] = {
    "Corrida": SessionName.RACE,
    "Classificação": SessionName.QUALIFYING,
    "Sprint": SessionName.SPRINT,
}
_CHART_PADDING_SECONDS = 0.3


# ---------------------------------------------------------------- composition root
@st.cache_resource
def get_service() -> F1DashboardService:
    """Monta o serviço com os repositórios da OpenF1 (singleton por processo)."""
    client = HttpClient()
    return F1DashboardService(
        meeting_repository=OpenF1MeetingRepository(client),
        session_repository=OpenF1SessionRepository(client),
        lap_repository=OpenF1LapRepository(client),
        driver_repository=OpenF1DriverRepository(client),
    )


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def load_meetings(year: int) -> list[Meeting]:
    """Etapas da temporada, com cache de ``CACHE_TTL_SECONDS``."""
    return get_service().get_meetings_for_year(year)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def load_top_laps(meeting_key: int, session_name: str) -> list[FastestLapEntry]:
    """Ranking de voltas da sessão, com cache de ``CACHE_TTL_SECONDS``."""
    return get_service().get_top_laps_for_meeting(
        meeting_key, session_name, top_n=TOP_N_LAPS
    )


# ---------------------------------------------------------------- apresentação
def entries_to_dataframe(entries: list[FastestLapEntry]) -> pd.DataFrame:
    """Converte o ranking em tabela pronta para exibição.

    Args:
        entries: Ranking de voltas mais rápidas.

    Returns:
        DataFrame com colunas em português e tempo no formato ``M:SS.mmm``.
    """
    return pd.DataFrame(
        {
            "Posição": [e.rank for e in entries],
            "Piloto": [e.driver_name for e in entries],
            "Equipe": [e.team_name for e in entries],
            "Volta": [e.lap_number for e in entries],
            "Tempo": [format_lap_time(e.lap_duration) for e in entries],
        }
    )


def build_lap_chart(entries: list[FastestLapEntry]) -> go.Figure:
    """Gráfico de barras horizontais com as cores oficiais das equipes.

    O eixo X é recortado em torno dos tempos para evidenciar as diferenças de
    décimos de segundo, que seriam invisíveis com o eixo começando em zero.

    Args:
        entries: Ranking de voltas mais rápidas (não vazio).

    Returns:
        Figura Plotly com a volta mais rápida no topo.
    """
    durations = [e.lap_duration for e in entries]
    figure = go.Figure(
        go.Bar(
            x=durations,
            y=[f"{e.rank}. {e.driver_acronym} · V{e.lap_number}" for e in entries],
            orientation="h",
            marker_color=[e.team_colour for e in entries],
            text=[format_lap_time(d) for d in durations],
            textposition="outside",
            customdata=[[e.driver_name, e.team_name] for e in entries],
            hovertemplate="%{customdata[0]} (%{customdata[1]})<br>"
            "%{text}<extra></extra>",
        )
    )
    figure.update_layout(
        height=80 + 40 * len(entries),
        margin={"l": 0, "r": 0, "t": 10, "b": 0},
        xaxis={
            "title": "Tempo de volta (s)",
            "range": [
                min(durations) - _CHART_PADDING_SECONDS,
                max(durations) + _CHART_PADDING_SECONDS * 2,
            ],
        },
        yaxis={"autorange": "reversed"},
        showlegend=False,
    )
    return figure


# ---------------------------------------------------------------- UI
def render_meeting(meeting: Meeting, session_name: str) -> None:
    """Renderiza um ``st.expander`` com tabela e gráfico de uma etapa."""
    title = (
        f"{meeting.date_start:%d/%m} · {meeting.meeting_name} "
        f"— {meeting.circuit_short_name} ({meeting.country_name})"
    )
    with st.expander(title):
        try:
            entries = load_top_laps(meeting.meeting_key, session_name)
        except OpenF1APIError:
            st.error("Não foi possível carregar as voltas desta etapa.")
            return
        if not entries:
            st.info("Sessão sem voltas cronometradas para esta etapa.")
            return
        table_col, chart_col = st.columns([2, 3])
        table_col.dataframe(entries_to_dataframe(entries), hide_index=True)
        chart_col.plotly_chart(
            build_lap_chart(entries),
            key=f"chart-{meeting.meeting_key}-{session_name}",
        )


def main() -> None:
    """Ponto de entrada do Streamlit."""
    st.set_page_config(page_title="F1 · Voltas mais rápidas", page_icon="🏁")
    st.title(f"🏁 Top {TOP_N_LAPS} voltas mais rápidas por etapa")

    years = available_years()
    with st.sidebar:
        st.header("Filtros")
        year = st.selectbox(
            "Temporada",
            years,
            index=years.index(DEFAULT_YEAR) if DEFAULT_YEAR in years else 0,
        )
        session_label = st.radio("Sessão", list(SESSION_LABELS))
        st.caption("Fonte: [OpenF1 API](https://openf1.org)")
    session_name = SESSION_LABELS[session_label].value

    try:
        with st.spinner("Carregando etapas..."):
            meetings = load_meetings(year)
    except OpenF1APIError:
        st.error("Falha ao consultar a OpenF1 API. Tente novamente em instantes.")
        return

    if not meetings:
        st.warning(f"Nenhuma etapa encontrada para {year}.")
        return

    logger.info("Renderizando: year=%s session=%s", year, session_name)
    st.caption(f"{len(meetings)} etapas · sessão: {session_label}")
    for meeting in meetings:
        render_meeting(meeting, session_name)


if __name__ == "__main__":
    main()
