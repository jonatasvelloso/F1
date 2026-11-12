# OpenF1 API — Resumo

> Fonte: <https://openf1.org/docs/> · Projeto não oficial, sem vínculo com a Fórmula 1.

## 1. Visão geral

- **URL base:** `https://api.openf1.org/v1/{endpoint}`
- **Método:** `GET` com filtros na query string.
- **Dados históricos (2023 em diante):** gratuitos e **sem autenticação**.
- **Dados em tempo real:** exigem **assinatura paga**. O streaming tem um tutorial à parte.
- **Rate limit:** a documentação não informa.

## 2. Formatos de resposta

| Formato | Como usar |
|---|---|
| JSON (padrão) | `https://api.openf1.org/v1/sessions?year=2023` |
| CSV | adicionar `csv=true` → `https://api.openf1.org/v1/sessions?year=2023&csv=true` |

## 3. Filtros

- **Qualquer atributo** pode ser usado como filtro, **exceto arrays**.
- **Operadores:** `=`, `>`, `<`, `>=`, `<=`. Em código, faça URL-encode (ex.: `>=` → `%3E%3D`).
- **Vários valores:** repita o parâmetro → `driver_number=4&driver_number=81`.
- **`latest`:** vale para `meeting_key` e `session_key` e retorna o meeting ou a sessão mais recente/atual.
- **Datas:** `date`, `date_start` e `date_end` aceitam operadores e vários formatos compatíveis com `dateutil.parser.parse`, como `2021-09-10`, `2021-09-10T14:30:20+00:00` e `10 September 2021`.

Exemplos:

```text
/v1/car_data?driver_number=55&session_key=9159&speed>=315
/v1/laps?session_key=9222&driver_number=55&is_pit_out_lap=true&lap_duration>=120
/v1/sessions?date_start>=2023-09-01&date_end<=2023-09-30
```

## 4. Chaves comuns

| Chave | Significado |
|---|---|
| `meeting_key` | Identifica um fim de semana de GP ou de testes |
| `session_key` | Identifica uma sessão (TL1, Quali, Sprint, Corrida…) dentro de um meeting |
| `driver_number` | Número do carro do piloto naquela temporada |
| `date` | Timestamp UTC em ISO 8601 |

**Hierarquia:** `meetings` → `sessions` → dados da sessão (laps, car_data, pit…).
Fluxo típico: achar o `meeting_key`, depois o `session_key`, e por fim filtrar os outros endpoints por `session_key` (+ `driver_number`).

## 5. Frequência de atualização e limitações

| Dado | Frequência |
|---|---|
| `car_data`, `location` | ~3,7 Hz |
| `intervals` | ~a cada 4 s (só corridas) |
| `weather` | a cada 1 min |
| `meetings`, `sessions` | diariamente, à meia-noite UTC |

**Limitações conhecidas**

- A cobertura de `team_radio` caiu muito a partir de 2026.
- A partir de 2026, `stop_duration` (pit) pode não vir ao vivo. Costuma ser preenchido algumas horas depois.
- `overtakes` pode vir incompleto.

## 6. Endpoints — tabela-resumo

| Endpoint | O que traz | Campos principais |
|---|---|---|
| `/car_data` | Telemetria do carro (~3,7 Hz) | `speed`, `rpm`, `n_gear`, `throttle`, `brake`, `drs` |
| `/championship_drivers` *(beta)* | Classificação de pilotos (só corridas) | `points_start/current`, `position_start/current` |
| `/championship_teams` *(beta)* | Classificação de equipes (só corridas) | `team_name`, `points_*`, `position_*` |
| `/drivers` | Dados dos pilotos na sessão | `full_name`, `name_acronym`, `team_name`, `team_colour`, `headshot_url` |
| `/intervals` | Gaps entre carros (só corridas) | `gap_to_leader`, `interval` |
| `/laps` | Dados de cada volta | `lap_number`, `lap_duration`, `duration_sector_1..3`, `st_speed` |
| `/location` | Posição aproximada do carro (x, y, z) | `x`, `y`, `z`, `date` |
| `/meetings` | Fins de semana de GP/testes | `meeting_name`, `circuit_short_name`, `country_name`, `year` |
| `/overtakes` | Ultrapassagens (só corridas) | `overtaking_driver_number`, `overtaken_driver_number`, `position` |
| `/pit` | Passagens pelo pit lane | `lap_number`, `lane_duration`, `stop_duration` |
| `/position` | Posição do piloto ao longo da sessão | `position`, `date` |
| `/race_control` | Bandeiras, safety car, incidentes | `category`, `flag`, `scope`, `message` |
| `/sessions` | Sessões de um meeting | `session_name`, `session_type`, `date_start`, `year` |
| `/session_result` | Resultado final da sessão | `position`, `duration`, `gap_to_leader`, `dnf/dns/dsq` |
| `/starting_grid` | Grid de largada | `position`, `lap_duration` |
| `/stints` | Stints (períodos com o mesmo jogo de pneus) | `compound`, `lap_start`, `lap_end`, `tyre_age_at_start` |
| `/team_radio` | Áudios de rádio piloto–equipe | `recording_url` (MP3) |
| `/weather` | Condições da pista (a cada min) | `air_temperature`, `track_temperature`, `rainfall`, `wind_speed` |

## 7. Detalhes por endpoint

### `/car_data` — telemetria
- `speed` (km/h), `rpm`, `n_gear` (1–8; 0 = neutro), `throttle` (% da potência máxima), `brake` (100 = pressionado, 0 = solto).
- `drs`, conforme a tabela de códigos:

| Código | Significado |
|---|---|
| 0, 1 | DRS desligado |
| 8 | Detectado; elegível ao entrar na zona de ativação |
| 10, 12, 14 | DRS ligado |
| 2, 3, 9 | Desconhecido |

Ex.: `/v1/car_data?driver_number=55&session_key=9159&speed>=315`

### `/championship_drivers` e `/championship_teams` *(beta)*
- `points_start` e `position_start`: valores **antes** da corrida.
- `points_current` e `position_current`: valores **durante ou depois** da corrida. Dependem do momento da consulta.
- Só existem para sessões de corrida.

Ex.: `/v1/championship_drivers?session_key=9839&driver_number=4&driver_number=81`
Ex.: `/v1/championship_teams?session_key=9839&team_name=McLaren`

### `/drivers`
- `broadcast_name`, `first_name`, `last_name`, `full_name`, `name_acronym` (ex.: VER).
- `team_name`, `team_colour` (hex `RRGGBB`), `headshot_url`.
- `country_code`: **depreciado**, com remoção prevista para depois de 2026.

Ex.: `/v1/drivers?driver_number=1&session_key=9158`

### `/intervals`
- `gap_to_leader`: gap para o líder (s). Vem `+1 LAP` quando o piloto levou volta e `null` para o próprio líder.
- `interval`: gap para o carro da frente (s), com as mesmas convenções.

Ex.: `/v1/intervals?session_key=9165&interval>0&interval<0.005`

### `/laps`
- `lap_number` (começa em 1), `lap_duration` (s) e `date_start` (início aproximado da volta).
- `duration_sector_1/2/3` (s).
- `i1_speed`, `i2_speed` (pontos intermediários) e `st_speed` (speed trap), em km/h.
- `is_pit_out_lap`: indica se é volta de saída do pit.
- `segments_sector_1/2/3`: códigos de mini-setor (não disponíveis em corridas):

| Código | Cor |
|---|---|
| 2048 | Amarelo |
| 2049 | Verde |
| 2051 | Roxo |
| 2064 | Pit lane |
| 0 | Indisponível |

Ex.: `/v1/laps?session_key=9161&driver_number=63&lap_number=8`

### `/location`
- `x`, `y`, `z`: coordenadas com origem arbitrária. Mostram o progresso na pista, mas **não** a posição lateral.

Ex.: `/v1/location?session_key=9161&driver_number=81&date>2023-09-16T13:03:35.200&date<2023-09-16T13:03:35.800`

### `/meetings`
- Identificadores: `meeting_key`, `circuit_key`, `country_key`.
- Nomes: `meeting_name`, `meeting_official_name`.
- Circuito e país: `circuit_short_name`, `circuit_type`, `location`, `country_name`, `country_code`, `country_flag`, `circuit_image`.
- `circuit_info_url`: JSON detalhado do circuito (MultiViewer).
- `date_start`, `date_end`, `gmt_offset`, `is_cancelled`, `year`.

Ex.: `/v1/meetings?year=2026&country_name=Singapore`

### `/overtakes`
- `overtaking_driver_number` (quem ultrapassou) e `overtaken_driver_number` (quem foi ultrapassado).
- `position`: posição de quem ultrapassou, depois da manobra.
- Inclui trocas de posição por pit stop e por punição pós-corrida. Pode estar incompleto.

Ex.: `/v1/overtakes?session_key=9636&overtaking_driver_number=63&overtaken_driver_number=4&position=1`

### `/pit`
- `lap_number`.
- `lane_duration`: tempo total no pit lane (s).
- `stop_duration`: tempo com o carro parado (s), disponível a partir do GP dos EUA de 2024.
- `pit_duration`: **depreciado** (alias de `lane_duration`).

Ex.: `/v1/pit?session_key=9877&stop_duration<2.3`

### `/position`
- `position` (começa em 1) e `date` (momento da mudança).

Ex.: `/v1/position?meeting_key=1217&driver_number=40&position<=3`

### `/race_control`
- `category`: `SessionStatus`, `CarEvent`, `Drs`, `Flag`, `SafetyCar`…
- `flag`: `GREEN`, `YELLOW`, `CHEQUERED`, `BLACK AND WHITE`…
- `scope`: `Track`, `Driver`, `Sector`…
- `sector`, `lap_number`, `qualifying_phase` (1, 2 ou 3) e `message`.

Ex.: `/v1/race_control?flag=BLACK AND WHITE&driver_number=1&date>=2023-01-01&date<2023-09-01`

### `/sessions`
- `session_name` (Practice 1, Qualifying, Race…) e `session_type` (Practice, Qualifying, Race).
- `date_start`, `date_end`, `gmt_offset`, `is_cancelled`, `year`.
- Local: `circuit_key`, `circuit_short_name`, `location`, `country_*`.

Ex.: `/v1/sessions?country_name=Belgium&session_name=Sprint%20Qualifying&year=2023`

### `/session_result`
- `position`, `driver_number`, `number_of_laps`.
- `duration`: melhor volta (treino/quali) ou tempo total (corrida). Na quali vem como **array** [Q1, Q2, Q3].
- `gap_to_leader`: em segundos ou `+N LAP(S)`. Na quali também vem como array.
- `dnf`, `dns`, `dsq`: flags booleanas.

Ex.: `/v1/session_result?session_key=7782&position<=3`

### `/starting_grid`
- `position` (posição no grid), `driver_number` e `lap_duration` (volta da quali, em s).

Ex.: `/v1/starting_grid?session_key=7783&position<=3`

### `/stints`
- `stint_number` (começa em 1) e `compound` (SOFT, MEDIUM, HARD…).
- `lap_start` e `lap_end`: primeira e última volta do stint.
- `tyre_age_at_start`: voltas que o pneu já tinha no início do stint.

Ex.: `/v1/stints?session_key=9165&tyre_age_at_start>=3`

### `/team_radio`
- `recording_url` (MP3) e `date`. Nem toda sessão tem rádio.

Ex.: `/v1/team_radio?session_key=9158&driver_number=11`

### `/weather`
- `air_temperature` e `track_temperature` (°C).
- `humidity` (%) e `pressure` (mbar).
- `rainfall`: indica se está chovendo.
- `wind_direction` (0–359°) e `wind_speed` (m/s).

Ex.: `/v1/weather?meeting_key=1208&wind_direction>=130&track_temperature>=52`

## 8. Exemplo rápido em Python

```python
import requests

BASE = "https://api.openf1.org/v1"

# Sessão mais recente
session = requests.get(f"{BASE}/sessions", params={"session_key": "latest"}).json()[0]
print(session["session_name"], session["circuit_short_name"], session["year"])

# Voltas do piloto 1 nessa sessão
laps = requests.get(
    f"{BASE}/laps",
    params={"session_key": session["session_key"], "driver_number": 1},
).json()

# Filtros com operador: monte a URL direto (o requests codificaria o ">=" como parte da chave)
fast = requests.get(
    f"{BASE}/car_data?session_key=9159&driver_number=55&speed>=315"
).json()
```

## 9. Links

- Documentação: <https://openf1.org/docs/>
- Dúvidas: GitHub Discussions do projeto OpenF1
- Bugs: GitHub Issues do projeto OpenF1
