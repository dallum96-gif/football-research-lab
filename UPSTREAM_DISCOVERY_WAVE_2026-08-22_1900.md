# FRL Upstream Discovery Wave — 2026-08-22 ~19:00

## Confirmed in this wave

### Legacy PulseLive fixture textstream
- `GET /football/fixtures/{fixture_id}/textstream/{language}`
- Returns fixture information and a textstream/events payload.
- Historical evidence shows event/commentary text can be retrieved from the fixture textstream resource.
- Language handling can affect whether fixture events are returned.

### Direct fixture statistics
- Historical PulseLive/footballapi clients use `GET /football/stats/match/{matchID}`.
- Response contains match statistics keyed by the participating team IDs.
- This is a direct match-stat resource and should be preserved independently of downstream CSV summaries.

### Gameweek resources
- `GET /football/compseasons/{SeasonID}/gameweeks`
- Returns season gameweek objects with gameweek number, date range, match count, status and identifiers.
- Gameweek is therefore a first-class source resource, not merely a derived integer on fixtures.

### Legacy player-stat vocabulary
- The published PulseLive API client documentation describes 150+ player stat attributes.
- The vocabulary includes granular finishing-location buckets such as `att_goal_high_centre`, `att_goal_low_left`, `att_ibox_goal`, `att_ibox_miss`, `att_obox_goal`, etc.
- It also includes passing, possession, duel, defensive, goalkeeping, set-piece and spatial/territorial metrics.
- `total_distance_in_m` is explicitly present in the older player-stat vocabulary.

## Shot-map status

### Established
- Rich shot-location information exists in the historical player-stat vocabulary through categorical spatial finishing metrics.

### Not yet established
- A direct Premier League/PulseLive public endpoint returning true shot-by-shot XY coordinates (`player_x`, `player_y`, goal-mouth coordinates, etc.) has not yet been proven.
- Third-party Opta-derived products expose such XY shot data, but that does not establish the public PL/PulseLive route.

## Manager/staff status

- Historical season/team staff resource is established at:
  `/football/teams/{team_id}/compseasons/{season_id}/staff`
- Current richer manager-history endpoint remains not yet established.

## Injury / transfer status

- Direct Premier League/PulseLive injury history endpoint: not yet established.
- Direct Premier League/PulseLive player transfer-history endpoint: not yet established.
- FPL provides player availability/status signals and FPL manager transfer history, but these are distinct from a Premier League injury/transfer ledger.

## Interpretation rule

Do not collapse:
- categorical shot-location metrics into a true XY shot map;
- FPL transfer history into football-player transfer history;
- availability signals into confirmed injury history;
- a historical legacy endpoint into a currently live endpoint without verification.

All remain separate capabilities until source lineage is established.
