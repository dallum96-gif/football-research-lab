# Football Research Laboratory — Source Family / Relationship Bridge Map V1

**Status:** Active architecture map / additive implementation
**Date:** 21 August 2026

## Purpose

This document maps the source families the FRL already uses, the relationship bridges that connect them to canonical FRL identities, and the remaining generalisation/missing-data work needed for the broader data platform.

The key principle is:

```text
source-native evidence
        ↓
verified relationship bridge
        ↓
FRL identity / fixture key
        ↓
broad reusable adapter
        ↓
selected analytical/query/UI consumers
```

The presence of a source field does not require a UI representation. Conversely, the absence of a UI representation is not evidence that the backend should discard the field.

## 1. Current source families

| Family | Grain | Source | Existing bridge | Current FRL status | Next action |
|---|---|---|---|---|---|
| Fixture master | fixture | FRL canonical | season + fixture_id | Canonical | Retain as authoritative identity layer |
| Team-match events | team × match | PL / PulseLive `events_stats` | `fixture_source_match()` via verified identities + UTC kickoff | Broad source evidence already preservable | Use `source_family_adapters.team_match_source_rows()` for reusable access |
| Player-match | player × match | PL / PulseLive `players_match_stats` | canonical fixture → source match → source player ID | Broad evidence builder exists; curated metrics exist too | Use common adapter; expand metric registry only when needed |
| Player-season | player × season | PL / PulseLive `players_stats` | source player ID + source team context | Broad evidence builder exists | Use common adapter and retain source-native fields |
| Squad/player metadata | player × roster/season | PL / PulseLive `squad` | source player ID → FRL player identity when verified | Available upstream; not fully promoted | Add reusable source adapter + identity validation |
| Live match | match/event/lineup/stats/commentary | current PulseLive SDP | source match ID only until reconciliation | New live evidence path | `pulselive_live.py`; no direct canonical writes |

## 2. Existing bridges that must remain authoritative

### Team / fixture bridge

`match_stats.fixture_source_match()` resolves a canonical fixture using:

1. season;
2. verified persistent home-team identity;
3. verified persistent away-team identity;
4. UTC kickoff.

Ambiguous matches fail closed. A source `matchId` is evidence, not a substitute for canonical fixture identity.

### Player / fixture bridge

`player_match_stats.player_match_id_for_fixture()` first resolves the canonical fixture to verified source home/away team IDs, then resolves the player-match source `matchId`. Gameweek is deliberately not used as the primary relationship key because rescheduled fixtures can move between source gameweeks.

### FPL / PL player bridge

The upstream repository documents the same Opta/PulseLive player identifier as `player_code` in FPL data and `playerId` / `pl_code` in PL data. The FRL should continue to use explicit identity mappings rather than names.

## 3. Reusable adapters now introduced

### `source_family_adapters.py`

Provides a common access layer over the existing verified bridges:

- `resolve_source_match()`
- `fixture_metadata()`
- `team_match_source_rows()`
- `team_match_source_fields()`
- `player_match_source_rows()`
- `player_match_source_fields()`
- `player_match_records()`
- `player_season_source_rows()`
- `player_season_source_fields()`
- `source_field_inventory()`

These functions preserve source-native records and keep FRL relationship fields separate.

### `pulselive_live.py`

Provides a thin current-SDP evidence adapter for:

- match
- events
- lineups
- stats
- commentary

The adapter records retrieval time and response headers and does not promote source IDs to FRL identity.

## 4. Fixture master enrichment

The canonical fixture CSV is allowed to carry verified source-backed metadata without requiring those fields to appear in the UI.

`enrich_fixture_master_source_metadata.py` adds:

- `source_match_id`
- `stadium`
- `attendance`
- `half_time_home_score`
- `half_time_away_score`
- `source_home_result`
- `source_away_result`
- `source_kickoff`
- `source_metadata_status`

The enrichment is additive and produces `identity/data_quality/fixture_source_metadata_audit.csv`.

A source-backed field must not overwrite the core fixture identity or corrected kickoff semantics. The existing correction/provenance mechanism remains authoritative for canonical historical interpretation.

## 5. What is genuinely still missing

### A. General player-season access

The raw player-season source exists and an evidence builder exists, but a reusable query-safe adapter is needed for arbitrary source fields without creating one-off code per metric.

### B. General squad/player-metadata access

The source contains preferred foot, nationality, DOB, height, weight, join date, loan status and source position. A reusable adapter and verified player identity bridge are needed before promotion into the FRL player layer.

### C. Fixture-level source metadata

The source contains ground, attendance and half-time state. The enrichment path now exists, but full historical execution and validation still need to be run locally against the complete fixture master.

### D. Rich player-match metric registry

The source contains substantially more player-match fields than the current curated metric registry. The common adapter preserves all source fields; the next step is an explicit field registry marking each field as retained, exposed, derived, restricted, or unknown.

### E. Live-to-canonical promotion

The current live adapter can retrieve evidence but does not yet persist timestamped snapshots, reconcile them to canonical fixtures, or promote validated post-match state on the Tuesday refresh.

### F. Rate-aware live scheduler/cache

Live requests need endpoint-specific polling intervals, shared caching, backoff on 429/5xx, and a request-budget guard. The reported 300 requests/60 seconds limit is treated as a source constraint to design around, not as a guarantee that every endpoint shares identical behaviour.

## 6. Storage direction

### Source evidence

Prefer immutable/timestamped raw snapshots for live or rapidly changing data. JSON/NDJSON is appropriate for preserving the original source structure.

### Analytical data

Prefer Parquet/DuckDB for repeated analytical scans once a dataset reaches a scale where CSV becomes an inefficient serving representation.

### Canonical CSV

Canonical CSV remains valid for stable, reviewable FRL artefacts such as the fixture master. Adding useful verified columns is acceptable even when no current UI surface consumes them.

## 7. Promotion rule

A source family may be promoted into a canonical FRL representation only after:

- source semantics are documented;
- historical coverage is measured;
- identity/fixture crosswalks are verified;
- sample records are manually checked;
- provenance is retained;
- unresolved/ambiguous states fail closed;
- downstream outputs can be reconciled with the current trusted layer;
- storage and update behaviour are reproducible.

## 8. Immediate implementation order

1. Run the fixture metadata enrichment against the full canonical fixture master and inspect the audit.
2. Add a player-metadata adapter for `squad` and connect it to the player identity registry without promoting fields to canonical GUI state.
3. Extend the player-match metric registry from the complete source schema rather than adding fields opportunistically.
4. Add historical field-coverage reports for team-match, player-match, player-season and squad families.
5. Build the live snapshot/cache layer on top of `pulselive_live.py`.
6. Only then wire selected variables and live states into the website.
