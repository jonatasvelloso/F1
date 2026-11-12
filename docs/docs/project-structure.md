# Estrutura do Projeto

```text
src/f1/
├── ingestion/
│   ├── http_client.py        # requests.Session com retry/timeout; OpenF1APIError
│   └── openf1_client.py      # repositórios concretos (Meeting, Session, Lap, Driver)
├── processing/
│   └── lap_processor.py      # filter_valid_laps, build_driver_index,
│                             # compute_top_n_laps, format_lap_time
├── domain/
│   ├── models.py             # Pydantic: Meeting, Session, Lap, Driver, FastestLapEntry
│   ├── repositories.py       # ABCs dos repositórios
│   └── services.py           # F1DashboardService
├── utils/
│   ├── config.py             # variáveis de ambiente tipadas (.env)
│   └── logger.py             # get_logger(name)
└── dashboard.py              # app Streamlit (composition root + UI)

tests/
├── conftest.py               # fixtures: sample_laps, sample_drivers, sample_meetings
├── unit/                     # sem rede: modelos, processamento, serviço, HTTP, UI
└── integration/              # OpenF1 real (marcados com @pytest.mark.integration)

docs/                         # esta documentação (MkDocs Material)
```
