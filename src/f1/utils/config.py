"""Configuração tipada, lida de variáveis de ambiente (``.env``) com defaults."""

import os
from datetime import UTC, datetime

from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL: str = os.getenv(
    "LOG_LEVEL", "DEBUG" if ENVIRONMENT == "development" else "INFO"
).upper()

BASE_URL: str = os.getenv("OPENF1_BASE_URL", "https://api.openf1.org/v1")
REQUEST_TIMEOUT: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))

FIRST_YEAR: int = 2023
DEFAULT_YEAR: int = int(os.getenv("DEFAULT_YEAR", "2024"))
TOP_N_LAPS: int = int(os.getenv("TOP_N_LAPS", "5"))
CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))


def available_years() -> list[int]:
    """Lista as temporadas disponíveis na OpenF1 (2023 até o ano corrente).

    Returns:
        Anos em ordem decrescente, do mais recente para o mais antigo.
    """
    current_year = datetime.now(tz=UTC).year
    return list(range(current_year, FIRST_YEAR - 1, -1))
