# F1 — OpenF1 Analytics

Dashboard Streamlit que mostra, para cada etapa de uma temporada, as **5 voltas mais
rápidas** de uma sessão (Corrida, Classificação ou Sprint), com o piloto, a equipe e o
número da volta. Os dados vêm da [OpenF1 API](https://openf1.org/docs/) (2023 em diante).

## Regra de negócio

- **Grão do ranking:** volta. Um mesmo piloto pode ocupar mais de uma posição.
- **Voltas válidas:** com `lap_duration` preenchido e que não sejam volta de saída do box
  (`is_pit_out_lap = false`).
- **Desempate:** menor `lap_number` primeiro.
- **Etapas:** canceladas são descartadas; etapas sem a sessão escolhida (ex.: testes de
  pré-temporada) aparecem com aviso de "sem voltas".

## Links rápidos

- [Arquitetura](architecture.md)
- [Como rodar local](running-locally.md)
- [Como rodar testes](running-tests.md)
