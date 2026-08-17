# Current Work — Football Research Laboratory

**Last updated:** 17 August 2026

This file is intentionally short and volatile. Update it whenever the active task, branch, checkpoint or next step changes.

## Active branch

`design/player-filter-tiles`

This is the active GUI/application-architecture and data-platform design branch.

The branch is the development line and must be compared with `main` before substantive changes. `main` is the stable integration line.

## Stable / validated baseline

Current research gate:

**26/26 tests passing**

Breakdown:

- Query Lab: 14/14
- Player Research V0.1: 6/6
- Player Research V0.2: 6/6

Additional player-match evidence-layer tests currently validated locally:

- Player-Match Source: 6/6
- Player-Match Research: 3/3
- Player Research Passing Integration: 3/3
- Player Research Player-Match: 2/2

The project-health gate remains a separate required control for relevant data-layer changes.

The latest repository-side relationship/platform smoke run is green.

## Governing architecture contracts

The following are required architectural-memory documents for fresh sessions:

- `FRL_DATA_HIERARCHY_RELATIONSHIP_CONTRACT.md`
- `FRL_RELATIONSHIP_INTEGRITY_CONTRACT.md`
- `FRL_DATA_PLATFORM_ARCHITECTURE_V1.md`
- `FRL_DATA_RESIDENCY_LINEAGE_INVENTORY_V1.md`
- `FRL_ANALYTICAL_DATA_LAYOUT_V1.md`

They are governed by:

- `RISK_STRATEGY_FRAMEWORK.md`
- `NON_DESTRUCTION_ASSURANCE.md`
- `DATA_CONSTRUCTION.md`

The hierarchy contract establishes the FRL as a connected football evidence graph rather than a collection of isolated pages.

Core principle:

> **Deep evidence underneath. Simple research experience on top.**

The FRL should preserve as much useful, provenance-aware football evidence as practical, including event-level source evidence, even when the project does not yet know how the information will be used. Retention does not imply trust: retained evidence must still be validated, reconciled, temporally safe and evaluated before promotion into trusted research or modelling features.

The data-platform contract establishes a second architectural boundary:

> **GitHub is the software and research-control plane; it is not the permanent bulk-data warehouse.**

The intended future separation is:

```text
external sources
      ↓
ingestion / source adapters
      ↓
raw immutable snapshots
      ↓
validated source layer
      ↓
canonical FRL entities/events
      ↓
derived state / features
      ↓
analytical engine
      ↓
research / models
      ↓
query_api
      ↓
GUI
```

The first scalable implementation direction is local-first, using columnar datasets such as Parquet and an analytical engine such as DuckDB, with object storage and workflow orchestration introduced only when the demonstrated scale/operational need justifies them.

No bulk-data migration is being performed merely for architectural neatness. Existing trusted CSV artefacts remain in place until an additive, reproducible alternative has passed equivalence checks.

## Data residency & lineage status

`FRL_DATA_RESIDENCY_LINEAGE_INVENTORY_V1.md` records the initial residency and lineage map for the major FRL datasets and source families.

Known tracked canonical/derived datasets include:

- `fixtures_master_corrected.csv` — canonical fixture master;
- `identity/team_seasons.csv` — canonical persistent/season-local team identity registry;
- `identity/data_quality/fixture_corrections.csv` — explicit correction provenance;
- `data/fixture_match_stats.csv` — packaged fixture statistics;
- `features/historical_match_state_v1.csv` and `features/historical_match_state_v2.csv` — derived historical state;
- `_merged/players/*_all_players_gw.csv` — tracked historical Player Research datasets;
- player identity and player-match evidence artefacts.

The richer upstream `pl_stats` player-match and event source families remain a distinct local/source-workspace concern and are not to be confused with canonical FRL data merely because they were used to construct it.

The inventory confirms the key current architecture gap: the original canonical fixture/team build is trusted but not yet represented by one clean end-to-end reproducible rebuild pipeline.

## Relationship-integrity proof status

The first Parquet/DuckDB relationship proof exposed two important schema assumptions and has now been corrected:

1. The season-specific Player Research source CSV does not physically contain `_season`; `player_research._load_season_rows()` derives that context from the loaded season/source file.
2. Fixture `home_team_id` and `away_team_id` are season-local team identifiers and must resolve through `identity/team_seasons.csv` using `local_team_id`, not `club_id` / persistent identity directly.

These semantics are formalised in `FRL_RELATIONSHIP_INTEGRITY_CONTRACT.md` and enforced by `tools/data_platform_proof.py` plus `tests/test-data-platform-proof.py`.

The green repository-side run confirms that the corrected relationship semantics survive temporary Parquet promotion and DuckDB querying without changing production CSV-backed consumers.

## Analytical layout status

`FRL_ANALYTICAL_DATA_LAYOUT_V1.md` now defines the scalable analytical representation beneath the query layer.

The layout is deliberately **not** a universal mega-table. It preserves stable canonical grains:

```text
Fixture        = (season, fixture_id)
Team–Fixture   = (season, fixture_id, persistent_team_code)
Player–Fixture = (season, fixture_id, canonical player identity)
```

with explicit identity bridge datasets and separate derived/materialised analytical layers.

The first materialisation target is deliberately small:

1. `fixtures`
2. `team_fixtures`
3. `player_fixtures` where trusted source coverage permits
4. identity bridges
5. selected historical/season state datasets

No current consumer is to be switched to the analytical layer until equivalence, relationship integrity, provenance, temporal semantics and rollback have been demonstrated.

## Product navigation contract

The primary sidebar is fixed as:

- Home
- Fixtures & Results
- League Table
- Teams
- Players
- Analysis

These are primary workspaces, not a list of every entity or analytical capability.

Contextual/detail views do not become sidebar clutter. In particular:

- Player–Fixture Detail is reached through a player/fixture relationship.
- Form and Streaks are shared analytical services, not a sidebar workspace.
- Matchday Centre, Query, Combined Metrics, Records and future mathematical/statistical models sit under Analysis.

## Current product architecture direction

The intended graph is:

```text
Player ←→ Player–Fixture ←→ Fixture ←→ Team–Fixture ←→ Team
                              ↓
                  shared historical/analytical state
                              ↓
             Research / Query / Models / Matchday
                              ↓
                             GUI
```

Team and Player each have separate profile and statistics/research responsibilities.

### Teams

Two primary views are planned:

**Team Profile** — identity, history, current context, concise form, recent fixtures and connected navigation.

**Team Stats** — season/multi-season statistics, filtering, comparisons, home/away analysis and deeper historical research.

The existing canonical query mechanisms are the safe starting seam: `team_summary`, `team_compare`, `team_form`, `fixtures` and the verified team identity registry.

### Players

Three complementary views:

**Player Profile** — who is this player?

**Player Stats / Research** — what has this player done and how does it compare?

**Player–Fixture Detail** — what did this player do in this specific match?

### Fixtures & Results

Fixture Explorer remains the entry point into the canonical fixture object, with Fixture Landing Page branching into match detail, player performance, player-fixture detail, team context, research and modelling.

### League Table

The League Table is an analytical competition view and should eventually support historical point-in-season views, ranges, home/away splits and navigation into Team Profile/Team Stats.

### Analysis

Analysis is the umbrella for:

- Matchday Centre;
- Prediction Lab;
- Head-to-Head as an existing contextual analytical capability;
- future Query/research tooling;
- comparable-match discovery;
- Combined Metrics;
- Records;
- future mathematical/statistical modelling;
- research consensus / ensembles where justified;
- explicit future market/decision layers.

## Player-match source and identity architecture

For work involving player-match source data, read:

`PLAYER_MATCH_SOURCE_BRIDGE.md`

The established audited principle is that canonical fixture identity remains `season + fixture_id`, and upstream source namespaces must be resolved through existing verified mechanisms rather than compared directly.

The verified player-match enrichment layer is represented by:

- `player_match_stats.py`
- `player_match_research.py`
- `player_research_player_match.py`
- `player_identity_registry.py`
- `player_identity_registry.csv`

The evidence layer is fail-closed. Verified specialist values may override displayed metrics where identity and source evidence are proven; otherwise documented canonical fallback values remain visible and provenance records the absence of specialist verification.

## GUI design contract

`GUI_DESIGN_CONTRACT.md` and `UI_DESIGN_SYSTEM.md` remain governing visual references.

The current redesign direction is compact, editorial and playful without becoming decorative or form-heavy. The primary navigation is deliberately smaller than the application graph.

Players filter work uses the approved light, transparent tile presentation with no dark selector/query surfaces.

## Branch safety contract

- `main` is the stable integration line.
- `design/*`, `feature/*` and other explicit development branches are development lines.
- Never write development or experimental work directly to `main`.
- GitHub write operations must explicitly target the intended development branch.
- Before substantive work, compare the active branch with `main`.
- If the active branch is behind or diverged, inspect the main-only and branch-only commits before merging, rebasing or moving refs.
- Before any destructive ref movement, create a named safety branch at the current tip.
- Integrate to `main` through an explicit validated decision, not by silently moving the `main` ref.

## Non-destruction rule for current work

UI redesign changes should not modify:

- query semantics;
- canonical fixture identity;
- persistent club identity;
- provenance rules;
- research calculations;
- historical data;
- validated evidence-layer contracts.

Data-platform work must not delete or overwrite the only known copy of source evidence or canonical artefacts. Storage migration is additive until equivalence and rollback are proven.

A change is successful only when the new behaviour works and trusted existing behaviour remains intact.

## Verification discipline

Before declaring a substantive change complete:

1. Inspect the relevant current implementation and existing consumer.
2. Identify the narrowest safe change surface.
3. Add targeted regression coverage for new behaviour.
4. Validate Python syntax/structure.
5. Verify the route still exists.
6. Verify existing data still renders.
7. Verify requested controls work.
8. Run the applicable research gate.
9. Run the project-health gate where relevant.
10. Inspect the GitHub Actions result before calling the branch safe.

Do not claim tests or project-health success unless they have actually been executed and passed.

## Fresh-session architecture sequence

The normal fresh-session Master Prompt should now be interpreted as requiring:

```text
read orientation
→ read current work
→ read data construction
→ read risk strategy
→ read non-destruction assurance
→ read UI design system
→ read FRL data hierarchy & organisation contract
→ read FRL relationship integrity contract
→ read FRL data platform architecture v1
→ read FRL data residency & lineage inventory v1
→ read FRL analytical data layout v1
→ establish branch/repository state
→ inspect relevant working/archived/local mechanisms
→ run 26/26
→ run project health
→ only then start substantive work
```

The hierarchy, relationship, data-platform, analytical-layout and residency/lineage contracts are project memory and must not be treated as optional background.

## Immediate next step

**Build the first local analytical materialisation proof.**

Using `FRL_ANALYTICAL_DATA_LAYOUT_V1.md`, select one representative player dataset and one representative fixture/team dataset. Build temporary Parquet representations at the defined grains, query them through DuckDB, and reproduce a small set of existing trusted CSV-backed outputs.

The proof must demonstrate:

- canonical grain preservation;
- identity-bridge preservation;
- relationship integrity;
- temporal semantics where applicable;
- provenance metadata;
- result equivalence;
- non-destruction and clean rollback.

Do not switch any live FRL consumer yet.
