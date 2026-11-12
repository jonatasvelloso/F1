"""Contratos (ABCs) de acesso a dados — o domínio não conhece a infraestrutura."""

from abc import ABC, abstractmethod

from f1.domain.models import Driver, Lap, Meeting, Session


class MeetingRepository(ABC):
    """Fonte de etapas de uma temporada."""

    @abstractmethod
    def get_meetings(self, year: int) -> list[Meeting]:
        """Retorna as etapas da temporada ``year``."""


class SessionRepository(ABC):
    """Fonte de sessões de uma etapa."""

    @abstractmethod
    def get_sessions(self, meeting_key: int, session_name: str) -> list[Session]:
        """Retorna as sessões da etapa com o nome informado."""


class LapRepository(ABC):
    """Fonte de voltas de uma sessão."""

    @abstractmethod
    def get_laps(self, session_key: int) -> list[Lap]:
        """Retorna todas as voltas da sessão."""


class DriverRepository(ABC):
    """Fonte de pilotos de uma sessão."""

    @abstractmethod
    def get_drivers(self, session_key: int) -> list[Driver]:
        """Retorna os pilotos inscritos na sessão."""
