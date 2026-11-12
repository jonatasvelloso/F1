# Como Contribuir

1. Crie uma branch a partir da `main` (merge direto na `main` é proibido).
2. Instale os hooks: `poetry run pre-commit install`.
3. Antes de abrir o PR:

    ```powershell
    poetry run ruff check .
    poetry run ruff format --check .
    poetry run pytest
    ```

4. Abra o PR com as seções **O que foi feito**, **Por que foi feito**, **Como testar** e
   o checklist abaixo. Não aprove o próprio PR.

## CI (GitHub Actions)

O workflow [`.github/workflows/ci.yml`](https://github.com/jonatasvelloso/F1/blob/main/.github/workflows/ci.yml)
roda em todo push para `main`/`dev` e em todo PR para `main`:

| Job | O que valida |
|---|---|
| `lint` | `ruff check .` e `ruff format --check .` |
| `pre-commit` | todos os hooks do `.pre-commit-config.yaml` (higiene de arquivos, YAML/TOML, `detect-secrets`, `poetry check --lock`), exceto ruff (já coberto por `lint`) |
| `tests` | `pytest` unitário com cobertura mínima de 80% (relatórios como artefato) |
| `docs` | `mkdocs build --strict` (na `main`, também empacota o `site/` para o Pages) |
| `deploy-docs` | publica a documentação no [GitHub Pages](https://jonatasvelloso.github.io/F1/) — só em push (ou disparo manual) na `main`, depois de `lint`, `pre-commit`, `tests` e `docs` passarem |
| `integration` | testes contra a OpenF1 real — só no agendamento semanal ou manualmente (*Run workflow* → `run-integration`) |

O setup comum (Poetry 2.5.1 via pipx, Python do `.python-version`, cache do `.venv`) fica
na action composta `.github/actions/setup-poetry`. Um PR só pode ser mergeado com
`lint`, `pre-commit`, `tests` e `docs` verdes.

## Pre-commit

```powershell
poetry run pre-commit install          # instala o hook no .git (uma vez por clone)
poetry run pre-commit run --all-files  # roda todos os hooks manualmente
```

Os hooks corrigem sozinhos espaços em branco, fim de arquivo e lint do Ruff. Quando isso
acontece o commit é abortado: revise as mudanças, faça `git add` e commite de novo. O hook
`no-commit-to-branch` impede commits direto na `main`.

## Checklist

- [ ] Lint passou (`poetry run ruff check .`)
- [ ] Testes passaram (`poetry run pytest`)
- [ ] Documentação atualizada (se aplicável)
- [ ] Sem secrets no código

## Padrões

Siga o `.claude/skill.md` do time (na raiz do repositório): type hints obrigatórios, `logging` em vez de
`print`, imports absolutos, funções pequenas e camadas `ingestion/processing/domain/utils`.
