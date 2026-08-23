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
empirical field catalog + semantic registry
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
| Squad/player metadata | player × roster/season | PL / PulseLive `squad` | source player ID → FRL player identity when verified | Available upstream; reusable adapter now added | Validate source→FRL player identity bridge before promotion |
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

### `player_metadata_source.py`

Provides reusable access to `squad` source rows and fields and groups records by source player ID. It deliberately does not promote metadata into the FRL player identity registry until identity reconciliation is verified.

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

## 5. Source-field registry, empirical catalog and coverage

`source_field_registry.py` is the machine-readable **semantic registry** of source-native fields that the FRL has reviewed. Its status vocabulary deliberately separates preservation, reusable access and semantic promotion.

`source_field_catalog.py` is the empirical layer. It scans the approved source families and records:

- source family;
- source field;
- registry status;
- optional FRL semantic field;
- first/last observed season;
- number of seasons present;
- coverage class.

An empirical field may therefore become **searchable before it becomes semantically promoted**. Unknown fields remain `UNCATALOGUED` rather than being silently mapped to a similarly named FRL concept.

`research_field_query.py` consumes the catalog and exposes source-native variables for research while preserving source IDs, fixture/player context, coverage metadata and the temporal warning that retrieval time is not historical availability time.

This is the intended path toward a broad natural-language research interface: **discover the variable first, understand its semantics and coverage, then query it**.

## 6. What is genuinely still missing

### A. Player identity reconciliation for squad metadata

The source adapter now exists. The remaining task is to validate the source player ID → FRL player identity bridge for squad metadata across historical seasons and fail closed on conflicts.

### B. Full semantic classification of the broad field universe

The empirical catalog can expose uncatalogued variables. The next task is to review the stable/high-value fields and add defensible FRL mappings, definitions, units and notes without creating false equivalence.

### C. Fixture-level source metadata execution

The source contains ground, attendance and half-time state. The enrichment path now exists, but full historical execution and validation still need to be run locally against the complete fixture master.

### D. Historical field-coverage results

The coverage audit has been executed against the current ten-season source workspace. Further runs should be made when additional upstream seasons are available so true source coverage remains distinct from FRL coverage.

### E. Live-to-canonical promotion

The current live adapter can retrieve evidence but does not yet persist timestamped snapshots, reconcile them to canonical fixtures, or promote validated post-match state on the Tuesday refresh.

### F. Rate-aware live scheduler/cache

Live requests need endpoint-specific polling intervals, shared caching, backoff on 429/5xx, and a request-budget guard. The reported 300 requests/60 seconds limit is treated as a source constraint to design around, not as a guarantee that every endpoint shares identical behaviour.

## 7. Storage direction

### Source evidence

Prefer immutable/timestamped raw snapshots for live or rapidly changing data. JSON/NDJSON is appropriate for preserving the original source structure.

### Analytical data

Prefer Parquet/DuckDB for repeated analytical scans once a dataset reaches a scale where CSV becomes an inefficient serving representation.

### Canonical CSV

Canonical CSV remains valid for stable, reviewable FRL artefacts such as the fixture master. Adding useful verified columns is acceptable even when no current UI surface consumes them.

## 8. Promotion rule

A source family may be promoted into a canonical FRL representation only after:

- source semantics are documented;
- historical coverage is measured;
- identity/fixture crosswalks are verified;
- sample records are manually checked;
- provenance is retained;
- unresolved/ambiguous states fail closed;
- downstream outputs can be reconciled with the current trusted layer;
- storage and update behaviour are reproducible.

## 9. Immediate implementation order

1. Run the fixture metadata enrichment against the full canonical fixture master and inspect the audit.
2. Validate the squad player-ID → FRL identity bridge.
3. Continue semantic classification of the broad field universe, prioritising stable 10/10 variables and documenting coverage.
4. Build the live snapshot/cache layer on top of `pulselive_live.py`.
5. Add availability-aware historical querying before using broad variables in predictive research.
6. Only then wire selected variables and live states into the website.
