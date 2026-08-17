# Football Research Laboratory — Analytical Data Layout V1

**Status:** Architectural contract / implementation blueprint
**Date:** 17 August 2026
**Governing documents:** `FRL_DATA_HIERARCHY_RELATIONSHIP_CONTRACT.md`, `FRL_RELATIONSHIP_INTEGRITY_CONTRACT.md`, `FRL_DATA_PLATFORM_ARCHITECTURE_V1.md`, `DATA_CONSTRUCTION.md`, `RISK_STRATEGY_FRAMEWORK.md`, `NON_DESTRUCTION_ASSURANCE.md`

## 1. Purpose

This document defines how trusted FRL data should be represented in the scalable analytical layer.

The purpose is not to create a second football database or to reproduce every GUI page as a table. The purpose is to provide a stable, queryable analytical representation of the same canonical football graph already defined by the FRL contracts.

The analytical layer must remain:

- additive;
- reproducible;
- provenance-aware;
- relationship-safe;
- temporally defensible;
- independent of any single GUI;
- independent of any single predictive model.

## 2. Core layout principle

**One dataset = one clearly defined grain.**

A table may contain many columns, but its rows must represent one unambiguous unit.

The primary grains are:

```text
Fixture
    (season, fixture_id)

Team–Fixture
    (season, fixture_id, team identity)

Player–Fixture
    (season, fixture_id, player identity)

Player–Season
    (season, persistent player identity)

Team–Season
    (season, persistent team identity)

Event
    (season, fixture_id, source/event identity)
```

The exact persistent-player and persistent-team keys remain governed by the identity contracts. Source-local identifiers may coexist as evidence attributes but must not silently replace canonical identities.

## 3. Canonical analytical entities

### 3.1 `fixtures`

**Grain:** `(season, fixture_id)`

Purpose:

- canonical fixture identity;
- competition context;
- kickoff chronology;
- gameweek;
- home/away canonical team references;
- score/result where known;
- fixture provenance and correction metadata.

Conceptual columns include:

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

The canonical fixture remains the backbone of the research graph.

### 3.2 `team_fixtures`

**Grain:** `(season, fixture_id, persistent_team_code)`

One fixture therefore creates up to two team-fixture rows.

Purpose:

- provide a symmetrical home/away analytical grain;
- hold team-specific match statistics;
- expose venue role (`HOME` / `AWAY`);
- support rolling form, opponent context and season state without repeatedly reshaping fixture rows.

Conceptual columns include:

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
...team match statistics...
```

Source/local team IDs must resolve through the verified season-local identity bridge.

### 3.3 `player_fixtures`

**Grain:** `(season, fixture_id, canonical player identity)`

Purpose:

- preserve individual player match evidence;
- support player research;
- support player influence analysis;
- connect player performance directly to fixtures and teams;
- allow player-match source evidence to be retained without making it the canonical fixture identity.

Conceptual columns include:

```text
season
fixture_id
persistent_player_code where available
source_player_id where verified
fpl_element where applicable
team_local_id
persistent_team_code
venue_role
starting_status
minutes
...player event/statistics...
identity_status
source_snapshot_id
```

The dataset may contain multiple source/statistic families for the same player-fixture relationship, but any source-specific grain must be declared explicitly.

## 4. Identity layer inside analytical data

Identity is not duplicated as an ad-hoc lookup in every dataset.

The analytical layer should expose explicit bridge/reference datasets such as:

```text
team_identity
player_identity
fixture_identity
source_identity_bridge
```

### Team identity rule

Fixture source/local team IDs are **season-scoped**. They must resolve through:

```text
(season, local_team_id)
        ↓
verified team_seasons registry
        ↓
persistent_team_code / persistent club identity
```

A numeric match between unrelated IDs is never sufficient evidence of identity.

### Player identity rule

Player source identifiers must resolve through the relevant verified identity registry. For FPL-based enrichment, the verified promotion key is:

```text
(season, fpl_element)
        ↓
verified source player identity
```

Unresolved or conflicting identities remain unavailable rather than being guessed.

## 5. Event data

Where rich event-level data is available, it should be retained at its native or explicitly normalised grain rather than prematurely collapsing it into summary statistics.

Examples may include:

```text
passes
shots
carries
tackles
interceptions
clearances
recoveries
duels
fouls
cards
substitutions
possession events
keeper actions
attacking actions
location / timestamp data where available
```

Every event dataset must retain a stable route to its fixture and, where relevant, player/team identity.

A useful event should not be discarded merely because no current FRL page displays it.

## 6. Source evidence versus canonical analytical data

The analytical layer must distinguish:

```text
RAW / SOURCE EVIDENCE
        ↓
VALIDATED SOURCE
        ↓
CANONICAL FRL DATA
        ↓
DERIVED ANALYTICAL DATA
```

A columnar copy of a source file does not become canonical merely because it is stored in Parquet.

Promotion into the canonical layer requires the established identity, validation, provenance and temporal rules.

## 7. Derived analytical datasets

Derived datasets should be built from canonical grains rather than from GUI-specific exports.

Examples include:

### `team_match_state`

One row per team-fixture with as-of state entering or following the fixture, depending on explicit temporal semantics.

### `player_season_metrics`

One row per persistent player-season with documented aggregation rules.

### `team_season_metrics`

One row per persistent team-season with documented aggregation rules.

### `historical_state`

Time-aware snapshots capable of reconstructing league/team/player state at specified points.

### `research_population`

Explicit rows representing the population returned by a research query, with a documented query/version identifier.

### `model_features`

Model-ready feature matrices with feature definitions, cutoff dates, source/canonical versions and model-input versions.

Derived rows must retain enough metadata to trace their provenance back to the canonical inputs.

## 8. Avoid wide-table collapse

The FRL should **not** attempt to create one enormous universal table containing every player, team, fixture and event field.

That would make the system harder to reason about, easier to corrupt and less reusable.

Instead:

```text
small number of stable canonical grains
        ↓
well-defined joins
        ↓
purpose-built analytical views/materialisations
```

A broad query can combine datasets at runtime or through explicitly versioned derived views.

## 9. Views versus materialised datasets

Use a **query/view** when:

- the result is cheap to calculate;
- the logic is highly reusable;
- the result should always reflect current canonical data;
- materialising it would create unnecessary duplication.

Use a **materialised Parquet dataset** when:

- the calculation is expensive;
- the same result is reused repeatedly;
- the population is intentionally versioned;
- reproducibility benefits from preserving the derived result;
- a modelling workflow requires a fixed feature snapshot.

The choice must remain explicit.

## 10. Partitioning direction

The first implementation should favour simple, predictable partitioning.

Likely partition dimensions include:

```text
season
competition
source family where genuinely necessary
```

Do not partition by every possible filter. Excessive partitioning creates operational complexity without necessarily improving analytical performance.

Large event datasets may require more granular partitioning later based on actual benchmark results.

## 11. Provenance columns

Where appropriate, analytical datasets should retain metadata fields such as:

```text
source_snapshot_id
source_family
ingestion_version
validation_version
identity_mapping_version
canonical_version
feature_version
created_at
as_of_time
information_cutoff_time
```

Not every table needs every field, but every promoted dataset must have a documented provenance path.

## 12. Temporal contract

The analytical layout must distinguish between:

**event time** — when the football event happened;

**knowledge/as-of time** — the state being reconstructed;

**information availability time** — when information about the event/state could reasonably have been available to the intended researcher or model.

A model feature must never silently incorporate information from after its declared information cutoff.

This is a structural data concern, not merely a modelling concern.

## 13. Query architecture

DuckDB should initially query the analytical Parquet layer directly.

The GUI should continue to consume the established FRL query/application seam rather than directly embedding DuckDB queries throughout pages.

Target shape:

```text
Parquet datasets
      ↓
DuckDB / analytical query layer
      ↓
query_api / research services
      ↓
GUI + modelling services
```

This preserves the ability to replace the analytical engine later without rebuilding the application.

## 14. Relationship-safe examples

A fixture-level research question should normally follow:

```text
fixtures
   ↓
team_fixtures
   ↓
player_fixtures
```

A player question should normally follow:

```text
player_identity
   ↓
player_fixtures
   ↓
player_season_metrics
   ↓
research / model
```

A team question should normally follow:

```text
team_identity
   ↓
team_fixtures
   ↓
team_season_metrics
   ↓
historical state / research / model
```

A comparable-match query should normally resolve to:

```text
research criteria
   ↓
canonical fixture population
   ↓
fixture / team / player analytical context
   ↓
result + evidence links
```

## 15. Implementation rule

The first implementation should **not** materialise every planned dataset immediately.

Start with:

1. `fixtures`
2. `team_fixtures`
3. `player_fixtures` where trusted source coverage permits
4. identity bridge datasets
5. one or two derived historical/season state datasets

Prove these against the existing trusted FRL outputs before expanding the analytical layer.

## 16. Non-destruction rule

No analytical representation may replace the existing trusted data until:

- row/grain equivalence is demonstrated;
- canonical-key integrity is demonstrated;
- relationship integrity is demonstrated;
- identity behaviour is demonstrated;
- temporal semantics are demonstrated;
- provenance is preserved;
- current consumers remain valid;
- rollback is straightforward.

The analytical layer is **additive until proven equivalent**.

## 17. Long-term capability

This layout is deliberately designed to support future FRL capabilities including:

- rich fixture landing pages;
- deep player/team research;
- event-level exploration;
- combined metrics;
- records;
- comparable-match research;
- historical/as-of queries;
- player influence analysis;
- Elo and other rating systems;
- Poisson and Monte Carlo models;
- simulation and ensemble approaches;
- market/decision analysis;
- future natural-language research queries.

The layout is not itself the research model. It is the stable analytical substrate beneath those models.

## 18. Guiding principle

> **Preserve the graph at canonical grains, materialise only what earns its place, and make every derived layer traceable back to the evidence that produced it.**
