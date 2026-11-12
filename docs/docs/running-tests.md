# Como Rodar Testes

```powershell
# Unitários (padrão do CI): sem rede, com cobertura
poetry run pytest

# Integração contra a OpenF1 real (opt-in)
poetry run pytest tests/integration -m integration --no-cov

# Relatório HTML de cobertura (abre htmlcov/index.html)
poetry run pytest --cov-report=html
```

## Configuração (`pyproject.toml`)

- `-m "not integration"` está no `addopts`: testes de integração só rodam quando pedidos.
- Cobertura mínima: **80%** (`[tool.coverage.report] fail_under`), acima dos 50% exigidos
  pelo padrão do time. Branch coverage habilitado.
- `filterwarnings = ["error"]`: qualquer warning falha o teste.

## Interpretando a cobertura

A coluna `Missing` lista as linhas não executadas; `BrPart` indica desvios condicionais
cobertos só parcialmente. A UI do Streamlit é testada com `streamlit.testing.v1.AppTest`,
com o serviço mockado.
