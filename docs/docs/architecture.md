# Arquitetura

```text
Streamlit UI (dashboard.py — composition root)
        │
        ▼
F1DashboardService (domain/services.py)
        │  depende apenas das ABCs (domain/repositories.py)
        ▼
OpenF1*Repository (ingestion/openf1_client.py) ──► HttpClient ──► OpenF1 API
        │
        ▼
Modelos Pydantic (domain/models.py)
        │
        ▼
compute_top_n_laps() (processing/lap_processor.py) ──► list[FastestLapEntry]
        │
        ▼
Tabela + gráfico de barras Plotly (cores oficiais das equipes)
```

## Decisões técnicas

| Decisão | Motivo |
|---|---|
| ABCs de repositório + injeção no serviço | O domínio não conhece HTTP; testes unitários usam mocks sem rede. |
| Funções puras em `processing/` | Regra de ranking testável isoladamente, sem I/O. |
| Pydantic v2 com `extra="ignore"` e `frozen=True` | Contrato explícito do que é consumido da API; campos novos não quebram a ingestão. |
| `HttpClient` com retry (3x, backoff 0,5 s, 429/5xx) e timeout | A OpenF1 aplica rate limit; falhas transitórias são absorvidas. |
| `404` tratado como lista vazia | A OpenF1 responde 404 quando um filtro não encontra registros. |
| `st.cache_resource` (serviço) e `st.cache_data(ttl=3600)` (dados) | Evita refazer ~3 chamadas por etapa a cada interação. |
| Eixo X do gráfico recortado em torno dos tempos | Diferenças de décimos ficariam invisíveis com eixo a partir de zero. |

## Endpoints consumidos

| Endpoint | Filtros | Uso |
|---|---|---|
| `/meetings` | `year` | Lista de etapas |
| `/sessions` | `meeting_key`, `session_name` | Resolve o `session_key` |
| `/laps` | `session_key` | Voltas cronometradas |
| `/drivers` | `session_key` | Nome, sigla, equipe e cor |
