"""Repositórios concretos que traduzem respostas da OpenF1 em modelos de domínio."""

from f1.domain.models import Driver, Lap, Meeting, Session
from f1.domain.repositories import (
    DriverRepository,
    LapRepository,
    MeetingRepository,
    SessionRepository,
)
from f1.ingestion.http_client import HttpClient


class OpenF1MeetingRepository(MeetingRepository):
    """Etapas via endpoint ``/meetings``."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_meetings(self, year: int) -> list[Meeting]:
        """Retorna as etapas da temporada ``year``."""
        rows = self._client.get("meetings", params={"year": year})
        return [Meeting.model_validate(row) for row in rows]


class OpenF1SessionRepository(SessionRepository):
    """Sessões via endpoint ``/sessions``."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_sessions(self, meeting_key: int, session_name: str) -> list[Session]:
        """Retorna as sessões da etapa com o nome informado."""
        rows = self._client.get(
            "sessions",
            params={"meeting_key": meeting_key, "session_name": session_name},
        )
        return [Session.model_validate(row) for row in rows]


class OpenF1LapRepository(LapRepository):
    """Voltas via endpoint ``/laps``."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_laps(self, session_key: int) -> list[Lap]:
        """Retorna todas as voltas da sessão."""
        rows = self._client.get("laps", params={"session_key": session_key})
        return [Lap.model_validate(row) for row in rows]


class OpenF1DriverRepository(DriverRepository):
    """Pilotos via endpoint ``/drivers``."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_drivers(self, session_key: int) -> list[Driver]:
        """Retorna os pilotos inscritos na sessão."""
        rows = self._client.get("drivers", params={"session_key": session_key})
        return [Driver.model_validate(row) for row in rows]
