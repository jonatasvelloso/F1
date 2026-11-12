"""Modelos de domínio (Pydantic v2) que representam os contratos da OpenF1 API."""

import re
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

DEFAULT_TEAM_COLOUR = "#888888"
_HEX_COLOUR = re.compile(r"^#?([0-9a-fA-F]{6})$")


class SessionName(StrEnum):
    """Nomes de sessão suportados pelo dashboard (valores aceitos pela API)."""

    RACE = "Race"
    QUALIFYING = "Qualifying"
    SPRINT = "Sprint"


class _FrozenModel(BaseModel):
    """Base imutável que ignora campos extras retornados pela API."""

    model_config = ConfigDict(frozen=True, extra="ignore")


class Meeting(_FrozenModel):
    """Etapa (Grande Prêmio ou teste) de uma temporada. Grão: ``meeting_key``."""

    meeting_key: int
    meeting_name: str
    country_name: str
    circuit_short_name: str
    date_start: datetime
    year: int
    is_cancelled: bool = False


class Session(_FrozenModel):
    """Sessão de uma etapa (treino, classificação, corrida). Grão: ``session_key``."""

    session_key: int
    session_name: str
    session_type: str
    meeting_key: int | None = None


class Lap(_FrozenModel):
    """Volta de um piloto em uma sessão. Grão: (``session_key``, piloto, volta)."""

    lap_number: int
    driver_number: int
    lap_duration: float | None = Field(default=None, gt=0)
    is_pit_out_lap: bool = False

    @field_validator("is_pit_out_lap", mode="before")
    @classmethod
    def _null_as_false(cls, value: bool | None) -> bool:
        """A API às vezes retorna ``null``; tratamos como volta normal."""
        return bool(value)


class Driver(_FrozenModel):
    """Piloto inscrito em uma sessão. Grão: (``session_key``, ``driver_number``)."""

    driver_number: int
    full_name: str | None = None
    name_acronym: str | None = None
    team_name: str | None = None
    team_colour: str = DEFAULT_TEAM_COLOUR

    @field_validator("team_colour", mode="before")
    @classmethod
    def _normalize_colour(cls, value: str | None) -> str:
        """Normaliza a cor para ``#RRGGBB``; valores inválidos viram cinza."""
        match = _HEX_COLOUR.match(value or "")
        return f"#{match.group(1).upper()}" if match else DEFAULT_TEAM_COLOUR


class FastestLapEntry(_FrozenModel):
    """Linha do ranking de voltas mais rápidas de uma sessão."""

    rank: int = Field(ge=1)
    driver_number: int
    driver_name: str
    driver_acronym: str
    team_name: str
    team_colour: str
    lap_number: int
    lap_duration: float = Field(gt=0)
