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

## Checklist

- [ ] Lint passou (`poetry run ruff check .`)
- [ ] Testes passaram (`poetry run pytest`)
- [ ] Documentação atualizada (se aplicável)
- [ ] Sem secrets no código

## Padrões

Siga o `.claude/skill.md` do time (na raiz do repositório): type hints obrigatórios, `logging` em vez de
`print`, imports absolutos, funções pequenas e camadas `ingestion/processing/domain/utils`.
