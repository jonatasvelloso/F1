"""Cliente HTTP resiliente (timeout + retry com backoff) para a OpenF1 API."""

from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from f1.utils.config import BASE_URL, MAX_RETRIES, REQUEST_TIMEOUT
from f1.utils.logger import get_logger

logger = get_logger(__name__)

RETRY_STATUS_CODES = (429, 500, 502, 503, 504)
BACKOFF_FACTOR = 0.5
HTTP_NOT_FOUND = 404


class OpenF1APIError(RuntimeError):
    """Falha ao consultar a OpenF1 API (rede, HTTP ou payload inesperado)."""


class HttpClient:
    """Wrapper de ``requests.Session`` com retry e timeout padronizados."""

    def __init__(
        self,
        base_url: str = BASE_URL,
        timeout: float = REQUEST_TIMEOUT,
        max_retries: int = MAX_RETRIES,
        session: requests.Session | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = session or self._build_session(max_retries)

    @staticmethod
    def _build_session(max_retries: int) -> requests.Session:
        """Cria a sessão com política de retry para 429/5xx."""
        retry = Retry(
            total=max_retries,
            backoff_factor=BACKOFF_FACTOR,
            status_forcelist=RETRY_STATUS_CODES,
            allowed_methods=frozenset({"GET"}),
            respect_retry_after_header=True,
        )
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries=retry))
        session.mount("http://", HTTPAdapter(max_retries=retry))
        return session

    def get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Executa um GET e retorna a lista de registros JSON.

        A OpenF1 responde ``404`` quando o filtro não encontra registros; esse caso
        é tratado como resultado vazio, não como erro.

        Args:
            path: Endpoint relativo, ex.: ``"meetings"``.
            params: Filtros de query string.

        Returns:
            Lista de objetos JSON retornados pela API.

        Raises:
            OpenF1APIError: Em falha de rede, status HTTP de erro ou payload que não
                seja uma lista.
        """
        url = f"{self._base_url}/{path.lstrip('/')}"
        logger.debug("GET %s params=%s", url, params)
        try:
            response = self._session.get(url, params=params, timeout=self._timeout)
            if response.status_code == HTTP_NOT_FOUND:
                return []
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            logger.error("Falha na OpenF1 API: url=%s erro=%s", url, exc)
            msg = f"Falha ao consultar {url}: {exc}"
            raise OpenF1APIError(msg) from exc

        if not isinstance(payload, list):
            msg = f"Payload inesperado de {url}: {type(payload).__name__}"
            raise OpenF1APIError(msg)
        return payload
