# Como Rodar Local

## Pré-requisitos

- Python 3.12.7 (via [pyenv-win](https://github.com/pyenv-win/pyenv-win))
- [Poetry](https://python-poetry.org/) 2.x — `pip install` direto é proibido

## Instalação

```powershell
poetry env use (pyenv which python)   # cria .venv/ no projeto (poetry.toml)
poetry install --with dev
Copy-Item .env.example .env           # opcional: os defaults já funcionam
```

## Executar o dashboard

```powershell
poetry run streamlit run src/f1/dashboard.py
```

Abra <http://localhost:8501>. Na barra lateral, escolha a **temporada** e a **sessão**;
cada etapa aparece em um painel expansível com a tabela e o gráfico.

!!! note "Primeira carga"
    A primeira carga de uma temporada faz cerca de 3 chamadas por etapa à OpenF1 e pode
    levar alguns segundos. Os resultados ficam em cache por `CACHE_TTL_SECONDS` (1 h).

## Variáveis de ambiente

Veja `.env.example`. Principais: `DEFAULT_YEAR`, `TOP_N_LAPS`, `REQUEST_TIMEOUT_SECONDS`,
`ENVIRONMENT` (controla o nível de log padrão).

## Documentação

```powershell
poetry install --with docs
poetry run mkdocs serve -f docs/mkdocs.yml
```
