# Football Research Laboratory — Analytical Data Layout V1

**Status:** Architectural contract / implementation blueprint  
**Date:** 17 August 2026  
**Governing documents:** `FRL_DATA_HIERARCHY_RELATIONSHIP_CONTRACT.md`, `FRL_RELATIONSHIP_INTEGRITY_CONTRACT.md`, `FRL_DATA_PLATFORM_ARCHITECTURE_V1.md`, `DATA_CONSTRUCTION.md`, `RISK_STRATEGY_FRAMEWORK.md`, `NON_DESTRUCTION_ASSURANCE.md`

## 1. Purpose

This document defines how trusted FRL data should be represented in the scalable analytical layer.

The purpose is not to create a second football database or to reproduce every GUI page as a table. The purpose is to provide a stable, queryable analytical representation of the same canonical football graph already defined by the FRL contracts.

The analytical layer must remain additive, reproducible, provenance-aware, relationship-safe, temporally defensible, independent of any single GUI, and independent of any single predictive model.

## 2. Core layout principle

**One dataset = one clearly defined grain.**

Primary grains:

```text
Fixture        = (season, fixture_id)
Team–Fixture   = (season, fixture_id, persistent_team_code)
Player–Fixture = (season, fixture_id, canonical player identity)
Player–Season  = (season, persistent player identity)
Team–Season    = (season, persistent team identity)
Event          = (season, fixture_id, source/event identity)
```

## 3. Foundational analytical datasets

### `fixtures`

Grain: `(season, fixture_id)`.

This is the canonical fixture object and contains competition context, chronology, gameweek, home/away team bridges, score/result where known, and provenance/correction metadata.

Conceptual fields:

```text
season
fixture_id
fixture_code / source_match_id where available
kickoff_time
gameweek
home_persistent_team_code
away_persistent_team_code
home_local_team_id
away_local_team_id
home_score
away_score
result
provenance_version
correction_status
```

### `team_fixtures`

Grain: `(season, fixture_id, persistent_team_code)`.

One fixture produces up to two rows. This is the preferred analytical grain for symmetric team analysis, venue splits, rolling context and team-level modelling features.

Conceptual fields:

```text
season
fixture_id
persistent_team_code
local_team_id
venue_role
opponent_persistent_team_code
result
points
for_goals
against_goals
team match statistics
```

Team-local IDs must always resolve through the verified season-local team registry.

### `player_fixtures`

Grain: `(season, fixture_id, canonical player identity)`.

This is the direct player-to-fixture evidence layer. It may contain source-specific fields and should preserve source identity, team identity, venue role, starting status, minutes and event/statistics fields.

The exact player-fixture source bridge remains governed by `PLAYER_MATCH_SOURCE_BRIDGE.md` and may initially be materialised from the local source workspace rather than the tracked repository.

## 4. Identity rule inside the analytical layer

Identity is explicit, not implied by numeric coincidence.

```text
fixture season-local team id
        ↓
(season, local_team_id)
        ↓
verified team_seasons registry
        ↓
persistent_team_code / persistent club identity
```

For FPL-derived player enrichment:

```text
(season, fpl_element)
        ↓
verified player identity registry
        ↓
canonical player identity
```

Unresolved or conflicting mappings remain unavailable/fail-closed.

## 5. Event data

Rich event data should remain at native or explicitly documented analytical grain. Useful event evidence must not be discarded merely because no current page displays it.

Every event dataset must retain a stable route back to its fixture and, where appropriate, player/team identity.

## 6. Source and derived separation

Raw source data is evidence. Canonical data is the trusted FRL entity/relationship layer. Derived data is a reproducible analytical product, never a new source of truth.

Every derived dataset should retain enough lineage to identify the canonical rows and transformation version that produced it.

## 7. Storage direction

Preferred first implementation:

```text
canonical/derived CSVs
        ↓
local Parquet materialisation
        ↓
DuckDB analytical queries
```

This is additive. Existing CSV-backed consumers remain authoritative until equivalence is established.

Later, identical Parquet datasets may live in object storage without changing the analytical semantics.

## 8. Migration rule

A materialisation is not accepted merely because row counts and columns match. It must also preserve:

- canonical keys;
- relationship semantics;
- identity bridges;
- provenance;
- temporal semantics;
- fail-closed behaviour;
- trusted query outputs.

No production consumer is switched to the analytical layer until those checks pass.

## 9. Visualisation is a first-class research output

Data visualisation is a major part of the FRL, not merely decorative presentation.

The analytical layer should deliberately make it easy to create:

- publication-quality charts and trend views;
- interactive tables and sortable/rankable views;
- team/player/fixture comparisons;
- distributions and uncertainty views;
- rolling and historical-state visualisations;
- head-to-head and matchup comparisons;
- scatter plots, relationship plots and feature exploration;
- model calibration/performance visualisations;
- research-population summaries;
- timeline and event visualisations where event data supports them;
- bespoke visual research tools where a football question benefits from a custom representation.

Visualisations are **research views over trusted data**, not independent analytical authorities. A chart, table or comparison tool must preserve the same provenance, population, filters, time semantics and uncertainty as the underlying research result.

The GUI may make visualisations beautiful, playful and highly browsable, but appearance must never change the meaning of the underlying data.

Prefer reusable visualisation-ready analytical outputs over repeatedly transforming raw files inside individual UI components.

The architecture should keep the visualisation layer replaceable so the FRL is not tied to one charting library or rendering technology.

## 10. Initial implementation scope

The first practical materialisation is intentionally narrow:

1. `fixtures`;
2. `team_fixtures`;
3. representative player-fixture materialisation only when the audited player-match source bridge is available in the execution environment.

Do not manufacture player-fixture rows from unrelated season-level player CSVs. Season-level player data is not player-fixture data.

## 11. North Star alignment

The analytical layer exists to make increasingly rich research possible without rebuilding the foundations:

- arbitrary football queries;
- fixture/team/player exploration;
- combined metrics;
- historical reconstruction;
- comparable-match research;
- player/team influence analysis;
- mathematical and predictive models;
- future natural-language research;
- rich data visualisation and interactive comparison.

The governing principle remains:

> **Preserve the evidence broadly, keep the research experience simple, and make every analytical layer replaceable.**
