"""Fábrica de loggers estruturados (substitui o uso de ``print``)."""

import logging
import sys

from f1.utils.config import LOG_LEVEL

_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger configurado com formato padronizado.

    O handler é adicionado apenas uma vez por logger, evitando linhas duplicadas
    quando o módulo é reimportado (comportamento comum no Streamlit).

    Args:
        name: Nome do logger, normalmente ``__name__`` do módulo chamador.

    Returns:
        Logger com saída em ``stdout`` e nível definido por ``LOG_LEVEL``.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(LOG_LEVEL)
        logger.propagate = False
    return logger
