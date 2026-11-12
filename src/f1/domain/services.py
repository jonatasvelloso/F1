"""Serviço de aplicação que orquestra repositórios e regras de processamento."""

from f1.domain.models import FastestLapEntry, Meeting
from f1.domain.repositories import (
    DriverRepository,
    LapRepository,
    MeetingRepository,
    SessionRepository,
)
from f1.processing.lap_processor import compute_top_n_laps
from f1.utils.config import TOP_N_LAPS
from f1.utils.logger import get_logger

logger = get_logger(__name__)


class F1DashboardService:
    """Casos de uso do dashboard, desacoplados da fonte de dados por injeção."""

    def __init__(
        self,
        meeting_repository: MeetingRepository,
        session_repository: SessionRepository,
        lap_repository: LapRepository,
        driver_repository: DriverRepository,
    ) -> None:
        self._meetings = meeting_repository
        self._sessions = session_repository
        self._laps = lap_repository
        self._drivers = driver_repository

    def get_meetings_for_year(self, year: int) -> list[Meeting]:
        """Lista as etapas não canceladas da temporada, em ordem cronológica.

        Args:
            year: Temporada desejada.

        Returns:
            Etapas ordenadas por ``date_start``.
        """
        meetings = [m for m in self._meetings.get_meetings(year) if not m.is_cancelled]
        logger.info("Etapas carregadas: year=%s total=%s", year, len(meetings))
        return sorted(meetings, key=lambda m: m.date_start)

    def get_top_laps_for_meeting(
        self, meeting_key: int, session_name: str, top_n: int = TOP_N_LAPS
    ) -> list[FastestLapEntry]:
        """Calcula as ``top_n`` voltas mais rápidas de uma sessão da etapa.

        Args:
            meeting_key: Chave da etapa.
            session_name: Nome da sessão (ex.: ``"Race"``, ``"Qualifying"``).
            top_n: Quantidade de voltas no ranking.

        Returns:
            Ranking ordenado pelo tempo de volta; vazio se a etapa não tiver a
            sessão (ex.: testes de pré-temporada) ou se não houver voltas válidas.
        """
        sessions = self._sessions.get_sessions(meeting_key, session_name)
        if not sessions:
            logger.warning(
                "Sessão inexistente: meeting_key=%s session=%s",
                meeting_key,
                session_name,
            )
            return []

        session_key = sessions[0].session_key
        laps = self._laps.get_laps(session_key)
        drivers = self._drivers.get_drivers(session_key)
        ranking = compute_top_n_laps(laps, drivers, top_n=top_n)
        logger.info(
            "Ranking calculado: session_key=%s laps=%s entries=%s",
            session_key,
            len(laps),
            len(ranking),
        )
        return ranking
