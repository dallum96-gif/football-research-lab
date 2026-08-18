# Football Research Laboratory — Player-Match Source Bridge

## Status

**Verified on 16 August 2026.**

This document records the audited relationship between the canonical Football Research Laboratory fixture universe and the upstream per-player/per-match source stored under the local Premier League source workspace.

It exists so future sessions do not repeat the identity/fixture discovery work or invent a competing join mechanism.

---

## 1. Scope and governing rule

The purpose of this bridge is to allow player-match source statistics — including passing, chance creation, carrying and related actions — to be attached to the Laboratory's existing canonical fixtures without creating a second fixture identity system or modifying trusted historical data.

The repository's governing architecture remains:

```text
RAW / SOURCE
    ↓
VALIDATED / CANONICAL
    ↓
HISTORICAL STATE
    ↓
RESEARCH / FEATURES / MODELS
    ↓
QUALITY / CONTROL
    ↓
GUI
```

Raw player-match source data remains evidence. The canonical fixture master remains the Laboratory's trusted fixture identity layer.

---

## 2. Canonical fixture identity

The canonical fixture file is:

`fixtures_master_corrected.csv`

Schema:

```text
season
fixture_id
fixture_code
kickoff_time
gameweek
home_team_id
away_team_id
home_score
away_score
```

The canonical fixture identity is:

```text
season + fixture_id
```

There are 3,800 canonical Premier League fixtures covering 2016-17 through 2025-26, 380 per season.

Historical `fixture_code` coverage is not uniform. In the current canonical artifact, `fixture_code` is populated for 2025-26, while historical seasons use the canonical `fixture_id` pathway. Therefore future historical joins must not assume that `fixture_code` is the cross-season fixture key.

---

## 3. Team identity bridge

Canonical fixture team IDs are **season-local Laboratory IDs** and must not be compared directly with upstream PL `team_id` values.

The trusted bridge is:

```text
canonical fixture home_team_id / away_team_id
        ↓
identity/team_seasons.csv
        ↓
verified local_team_id
        ↓
persistent_team_code
        ↓
upstream PL source team_id
```

`identity/team_seasons.csv` records the evidence-backed mapping between season-local source identities and persistent club identities.

Only rows with:

```text
mapping_status = VERIFIED
```

should be used for this bridge.

Do not replace this registry with a global `team_id` assumption or ad hoc string matching.

---

## 4. Existing fixture-to-source resolver

The Laboratory already has an established fixture-to-source mechanism in `match_stats.py`:

```text
fixture_source_match(fixture, identity_rows)
```

The established resolution process is:

1. resolve the canonical fixture's season-local home and away IDs through the verified identity registry;
2. obtain the corresponding persistent/upstream team IDs;
3. convert the canonical kickoff to UTC;
4. inspect upstream `events_stats` records;
5. require the source home team, away team and kickoff to match;
6. reject ambiguity rather than selecting arbitrarily.

This existing mechanism is the authoritative fixture-to-`events_stats` bridge and should be reused rather than recreated.

---

## 5. Player-match source

The upstream player-match source is stored in the local source workspace under:

```text
pl_stats/<club>/players_match_stats/<season>_players_match_stats.csv
```

The source contains, among other fields:

- `season`
- `matchId`
- `gameweek`
- `team_id`
- `team`
- `venue`
- `playerId`
- `pl_code`
- player name/position fields
- passing fields
- chance-creation fields
- shooting fields
- defensive fields
- carrying fields in seasons where supplied

The upstream `players_match_stats.matchId` is a **different namespace** from the upstream `events_stats.matchId` used by `match_stats.py`.

This is expected and is not an error.

A source inspection example from 2019-20 showed:

```text
events_stats matchId       = 1059711
players_match_stats matchId = 8243392
```

for the same Arsenal-side football fixture context.

Therefore the numeric IDs must not be compared directly.

---

## 6. Proven fixture bridge

A read-only audit was run against the full canonical universe using the existing Laboratory fixture resolver and the verified team identity mapping.

The player-match source was then reconciled by:

```text
season
+
verified upstream home team identity
+
verified upstream away team identity
```

The final audit deliberately did **not** use gameweek as a fixture identity key because postponed/rescheduled fixtures can retain historical scheduled gameweek labels in one source while being played under a different actual date/gameweek representation elsewhere.

### Result

| Season | Canonical fixtures | Unique player-match fixture pairs | Missing | Ambiguous |
|---|---:|---:|---:|---:|
| 2016-17 | 380 | 380 | 0 | 0 |
| 2017-18 | 380 | 380 | 0 | 0 |
| 2018-19 | 380 | 380 | 0 | 0 |
| 2019-20 | 380 | 379 | 0 | 0 |
| 2020-21 | 380 | 380 | 0 | 0 |
| 2021-22 | 380 | 380 | 0 | 0 |
| 2022-23 | 380 | 380 | 0 | 0 |
| 2023-24 | 380 | 380 | 0 | 0 |
| 2024-25 | 380 | 380 | 0 | 0 |
| 2025-26 | 380 | 380 | 0 | 0 |
| **Total** | **3,800** | **3,799** | **0** | **0** |

The one exception is the already-documented 2019-20 Manchester City v Arsenal fixture (`fixture_id=275`).

Therefore the audited invariant is:

> **3,799 of 3,800 canonical fixtures map uniquely to a player-match source fixture. The sole remaining fixture is the known verified historical correction case.**

No alternative fixture identity system is required.

---

## 7. The Manchester City v Arsenal exception

The repository already records this as an explicit correction in:

`identity/data_quality/fixture_corrections.csv`

The canonical fixture is:

```text
season:              2019-20
fixture_id:          275
scheduled_kickoff:   2020-03-11T19:30:00Z
actual_kickoff:      2020-06-17T19:15:00Z
home_score:          3
away_score:          0
status:              VERIFIED_CORRECTION
```

The scheduled date was retained in the raw/canonical fixture evidence while the verified correction records the actual restart fixture.

This exception must not be 'fixed' by inventing a generic mapping or by overwriting the canonical historical record. Any player-match enrichment for this fixture must follow the same provenance-preserving correction mechanism.

---

## 8. Why earlier naive audits failed

Several tempting joins were proven incorrect during the audit:

### Do not use raw upstream match IDs

`events_stats.matchId` and `players_match_stats.matchId` belong to different upstream namespaces.

### Do not compare canonical team IDs directly with player-match `team_id`

Canonical fixture team IDs are season-local Laboratory identifiers. They require the verified `team_seasons.csv` bridge first.

### Do not use `fixture_code` as the historical universal key

Historical canonical seasons do not currently populate `fixture_code` in the same way as 2025-26. Historical player data uses the canonical `fixture` / `fixture_id` relationship.

### Do not use gameweek as the final fixture identity

Postponed/rescheduled matches can expose different gameweek labels across source families. Gameweek is useful metadata, not the final identity key for this bridge.

### Do not infer missing source data from a failed join

A failed naive join can be a namespace/pathway error rather than missing evidence. The project quality framework explicitly requires discovery of the existing source mechanism before implementing a replacement.

---

## 9. Historical FPL player fixture relationship

The merged historical FPL player dataset is stored under:

```text
_merged/players/<season>_all_players_gw.csv
```

Historical player rows contain a `fixture` field.

A direct comparison for 2019-20 established:

```text
canonical fixture_id values: 380
unique player fixture values: 380
intersection:                380
```

The historical FPL player `fixture` field therefore maps to the canonical `fixture_id` pathway for that season.

This is distinct from the upstream PL player-match `matchId` namespace.

---

## 10. Verified player-match metric coverage

The audited player-match source contains genuine per-player/per-match passing and related fields throughout the 2016-17 to 2025-26 source archive.

Core passing/creation fields present in the audited schemas include:

```text
totalPass
accuratePass
accurateOwnHalfPasses
accurateOppositionHalfPasses
accurateLongBalls
accurateCross
totalCross
totalLongBalls
totalOppositionHalfPasses
totalOwnHalfPasses
keyPass
bigChanceCreated
goalAssist
```

Temporal availability is field-specific and must be respected. The audit found:

- 2016-17 to 2018-19: core passing, key pass, big chance creation and assist fields;
- 2019-20: progressive carrying fields also present;
- 2020-21: core passing/creation fields present, but the later progressive-carrying fields absent;
- 2021-22: progressive carrying fields present again;
- 2022-23 and 2023-24: expected assists present, progressive carrying fields absent;
- 2024-25 and 2025-26: expected assists and progressive carrying fields present.

The source schema audit found no `successfulDribbles` / `unsuccessfulDribbles` fields in these player-match files and no `throughBall` / `totalThroughBall` fields in the audited target schemas.

Do not imply ten-season coverage for any individual metric merely because the player-match source exists for ten seasons.

---

## 11. Implemented source adapter

The first additive implementation now lives in:

`player_match_stats.py`

Its responsibilities are deliberately narrow:

- discover the audited per-season player-match source files;
- expose source-field/metric availability by season;
- reuse `match_stats.fixture_source_match()` for canonical fixture → upstream team identity;
- resolve the player-match `matchId` by verified upstream home/away team pair;
- deliberately omit gameweek from the final fixture join;
- retrieve raw player-match rows for a canonical fixture;
- aggregate additive player-match fields without changing the existing FPL player-research contract;
- derive pass accuracy as `accuratePass / totalPass * 100` when both components exist;
- preserve `None` for source fields that are genuinely unavailable.

The adapter uses a cached season-level source match-pair index rather than rescanning every source row for every fixture.

The corresponding contract tests live in:

`tests/test-player-match-stats.py`

These test season discovery, metric coverage, fixture-pair resolution, the known exception state, and additive aggregation/pass-accuracy behaviour.

---

## 12. Safe integration principle

The player-match source should be treated as an **additive evidence layer**.

The intended design is:

```text
Canonical fixture
      │
      ├── existing fixture/result/statistics evidence
      │
      └── player-match evidence
             │
             ├── player identity
             ├── match identity
             ├── passing
             ├── creation
             ├── carrying
             └── other source-backed actions
```

Do not:

- replace the canonical fixture master;
- rewrite trusted fixture IDs;
- create a second canonical fixture table;
- silently mutate historical source records;
- infer unavailable metrics;
- use market information in the research layer.

The correct reuse point is the existing research/data seam, with provenance retained.

---

## 13. Validation status

The research baseline immediately before this investigation was:

```text
Core Query Lab:          14/14
Player Research V0.1:     6/6
Player Research V0.2:     6/6
Total:                   26/26
```

The adapter has been committed but the new local test suite still needs to be run in the user's canonical Windows checkout against the real `pl_stats` source tree before it should be treated as production validated.

The project-health gate remains a separate control and retains the known 2019-20 fixture warning.

---

## 14. Required future-session behaviour

When a future task involves player-match source data, passing, chance creation, progressive actions, per-match player enrichment, or a proposed replacement source:

1. read this document;
2. inspect `identity/team_seasons.csv` before assuming team-ID compatibility;
3. reuse `match_stats.fixture_source_match()` for canonical fixture → upstream source resolution;
4. treat `players_match_stats.matchId` as a separate upstream namespace;
5. do not use gameweek as the final fixture identity for postponed/rescheduled fixtures;
6. inspect metric-level season coverage before exposing a statistic;
7. preserve the 2019-20 Manchester City v Arsenal correction and its provenance;
8. preserve the canonical fixture master;
9. validate any new ingestion against the 3,799 + 1 known-exception baseline;
10. follow the project's Non-Destruction Assurance and Risk Strategy Framework before modifying the data layer.

This document is a source-of-truth record of the **audited bridge**, not permission to bypass the existing research/data contracts.
