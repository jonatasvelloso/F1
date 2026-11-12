"""Regras de limpeza e ranqueamento de voltas (funções puras, sem I/O)."""

from f1.domain.models import DEFAULT_TEAM_COLOUR, Driver, FastestLapEntry, Lap

_UNKNOWN = "Desconhecido"
_SECONDS_PER_MINUTE = 60


def filter_valid_laps(laps: list[Lap]) -> list[Lap]:
    """Remove voltas sem tempo cronometrado e voltas de saída do box.

    Args:
        laps: Voltas brutas de uma sessão.

    Returns:
        Apenas voltas com ``lap_duration`` preenchido e ``is_pit_out_lap=False``.
    """
    return [
        lap for lap in laps if lap.lap_duration is not None and not lap.is_pit_out_lap
    ]


def build_driver_index(drivers: list[Driver]) -> dict[int, Driver]:
    """Indexa os pilotos por número do carro.

    Args:
        drivers: Pilotos de uma sessão.

    Returns:
        Dicionário ``driver_number -> Driver`` (em duplicatas, vence o último).
    """
    return {driver.driver_number: driver for driver in drivers}


def compute_top_n_laps(
    laps: list[Lap], drivers: list[Driver], top_n: int = 5
) -> list[FastestLapEntry]:
    """Ranqueia as ``top_n`` voltas mais rápidas da sessão.

    O ranking é por volta, não por piloto: um mesmo piloto pode aparecer mais de
    uma vez. Empates são desfeitos pelo número da volta (a mais antiga primeiro).

    Args:
        laps: Voltas brutas da sessão.
        drivers: Pilotos da sessão, usados para enriquecer o ranking.
        top_n: Quantidade de voltas a retornar.

    Returns:
        Entradas do ranking ordenadas pelo tempo de volta crescente.

    Raises:
        ValueError: Se ``top_n`` for menor que 1.
    """
    if top_n < 1:
        msg = f"top_n deve ser >= 1, recebido {top_n}"
        raise ValueError(msg)

    driver_index = build_driver_index(drivers)
    fastest = sorted(
        filter_valid_laps(laps), key=lambda lap: (lap.lap_duration, lap.lap_number)
    )[:top_n]

    entries: list[FastestLapEntry] = []
    for rank, lap in enumerate(fastest, start=1):
        driver = driver_index.get(lap.driver_number)
        entries.append(
            FastestLapEntry(
                rank=rank,
                driver_number=lap.driver_number,
                driver_name=(driver and driver.full_name) or f"#{lap.driver_number}",
                driver_acronym=(driver and driver.name_acronym)
                or str(lap.driver_number),
                team_name=(driver and driver.team_name) or _UNKNOWN,
                team_colour=driver.team_colour if driver else DEFAULT_TEAM_COLOUR,
                lap_number=lap.lap_number,
                lap_duration=lap.lap_duration,
            )
        )
    return entries


def format_lap_time(seconds: float) -> str:
    """Formata segundos no padrão de cronometragem da F1 (``M:SS.mmm``).

    Args:
        seconds: Duração da volta em segundos.

    Returns:
        Tempo formatado, ex.: ``92.608 -> "1:32.608"``.
    """
    minutes, remainder = divmod(round(seconds, 3), _SECONDS_PER_MINUTE)
    return f"{int(minutes)}:{remainder:06.3f}"
