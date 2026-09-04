# Current Work — Football Research Laboratory

**Last updated:** 4 September 2026  
**Checkpoint:** `PRODUCT_NORTH_STAR_CAPABILITY_LED_V1`

For documentation-governance rules see `FRL_DOCUMENTATION_SYNC_CONTRACT.md` and `data/frl_documentation_state_v1.json`.

## Current platform state

FRL is a governed football research and modelling environment whose active product frontend is **Next.js + React**, with **FastAPI** as the frontend-facing API. Streamlit remains legacy/reference only.

The standing architecture remains centred on:

- canonical fixture, team and player identity rather than source-id coincidence;
- preserved source-native evidence with explicit provenance;
- temporal/as-of reconstruction so FRL can distinguish what is true now from what was knowable at an earlier point;
- explicit missing, partial, unresolved and unavailable states rather than silent zero/fallback behaviour;
- governed source routing and explicit derivations;
- reproducible materialisation from pinned evidence;
- shared analytical services so product surfaces do not invent separate metric definitions, populations, ranks or percentiles.

The durable research North Star remains `FRL_MASTER_PROMPT.md`.

The active product North Star is now recorded in:

`FRL_PRODUCT_NORTH_STAR_AND_EXPERIENCE_ARCHITECTURE_V1.md`

Its product promise is:

> **FRL should make enormous statistical depth feel simple, visual and fluid — whether the user is scouting a player, studying a team, preparing for an opponent, researching a population, or forming an independent view of a fixture.**

## Current development branch state

Active development work for the current Matchday / capability / product-direction sequence is on:

`model/poisson-v1`

As established immediately before this checkpoint, the branch remained cleanly ahead of `main` with the merge base at `main`; development changes must continue to target the development branch explicitly rather than the stable line.

Do not rebase, reset or merge casually merely to simplify branch history.

## 2026/27 living-season state

The governed 2026/27 integration has advanced through the second Premier League gameweek release.

Pinned upstream release integrated for the current branch:

`imadeddine-belkat/Premier-League-Stats@ffe99d25a5bd3a8f70c557748fead332f46ed14f`

Current materialised state at that release boundary includes:

- 380 canonical 2026/27 fixtures;
- 20 completed fixtures;
- 360 scheduled fixtures;
- 1,236 FPL player × fixture rows;
- 614 zero-minute/non-participation rows retained;
- 0 duplicate player-fixture rows;
- 0 unresolved fixture rows;
- 626 player identities represented through explicit verified/source-native verified routes;
- preserved release/source manifests under `data/season_releases/2026-27/`.

The living-season rules remain unchanged:

- FPL is a distinct source family;
- source identifiers are not canonical identities;
- zero-minute rows remain legitimate non-participation evidence;
- missing scores/evidence are not zero;
- later releases supersede through preserved release history rather than erasing earlier state;
- direct, FPL-derived, player-derived and supplementary representations must not be first-non-null coalesced;
- current-season outputs must expose incomplete/as-of populations honestly.

## Current product state

Completed/frozen-for-now product surfaces include:

- Homepage V1;
- standalone Fixtures V1;
- Team Profile V1.

Active/recent analytical surfaces include:

- Team Stats Team View;
- Team Stats League Rankings;
- Player Stats / Player Rankings;
- Player profiles/directories;
- League Table;
- Matchday fixture workspace.

The shared tiled vertical-list language remains a valid FRL Stats interaction pattern.

However, the product is no longer being defined as a sequence of individual stat pages.

The new experience architecture treats the governed football-variable universe as one shared foundation with several lenses:

```text
GOVERNED FOOTBALL EVIDENCE / VARIABLES
               ↓
       SHARED ANALYTICAL LAYER
               ↓
PLAYER / TEAM SCOUTING
OPPOSITION REPORT
MATCHDAY / FIXTURE INTELLIGENCE
STATS / RANKINGS / COMPARE
RESEARCH EXPLORER
```

These must not become separate statistical systems.

## Product experience decisions — 4 September 2026

The following decisions are now active:

### Visual summaries first

The first view should communicate the important football story quickly and visually.

Deep numbers remain available but should not dominate the initial experience.

### Progressive disclosure

FRL uses four information layers:

1. **Glance** — understand the story in seconds;
2. **Explore** — understand major football components/families;
3. **Analyse** — access broader metrics, ranks, distributions, splits and trends;
4. **Research** — inspect provenance, coverage, transformations, populations and temporal semantics.

This is the primary solution to information overload.

### Player Scouting

A player scouting surface should rapidly communicate:

- role/profile;
- strengths;
- weaknesses / comparatively low areas;
- current performance;
- cohort/league context;
- key output.

Player-specific cohort, role and minutes semantics remain mandatory before strong interpretation.

### Team Scouting

Team scouting should explain what kind of team the subject is, how it plays, what it does unusually well/poorly and how those behaviours compare with the league.

### Opposition Report

Opposition Report is a distinct analytical mode.

It should answer:

> **If I were preparing to face this team, what would I need to understand?**

It should organise evidence around football preparation — build-up, progression, chance creation, threat, defensive behaviour, transitions, set pieces, personnel and recent tactical change — rather than source columns.

### Matchday / Fixture Intelligence

The fixture is the entry point.

FRL should answer:

> **What does the evidence tell us about this fixture?**

The initial objective is an independent football view, not replication of a bookmaker interface.

Bet-builder support can emerge by surfacing football phenomena corresponding to common markets (shots, shots on target, saves, tackles, fouls, cards, corners, creation, goals, assists, etc.) while retaining samples and uncertainty.

Bookmaker odds are not required for this initial experience. A future odds layer, if acquired, should answer the separate market-value question and remain explicitly quarantined from ordinary football evidence.

## Full-data capability objective

FRL should curate presentation, **not artificially curate away data capability**.

The September raw PulseLive snapshot audit established:

- 3,800 preserved fixture snapshots;
- 553 distinct scalar raw paths;
- 372 football/match raw paths after capture/provenance metadata is separated;
- 249 team-match statistical raw paths.

These numbers describe source evidence, not 553 independently governed metrics.

The active capability ambition is:

> **Make every legitimate governed football variable research-accessible where evidence permits; let individual product surfaces select only the variables that answer their question well.**

The 249 team-match statistic surface is a particularly attractive industrialisation target because the variables share a common source family and natural analytical grain.

The goal is not 249 bespoke functions or 249 GUI widgets.

The goal is a generic governed route in which additional metrics increasingly become catalogue/governance work rather than new architecture.

## Known capability implications

### Team level

Historical PulseLive team-match evidence is broad and includes rich passing, possession, progression, shooting, chance-creation, defending, duel and goalkeeper variables.

Rich current-season team-match evidence remains a major requirement where the governed 2026/27 source does not currently supply equivalent capability.

### Player level

FRL already has a richer historical player analytical vocabulary than the current-season FPL feed can support.

The current 2026/27 FPL player-GW source does **not** provide genuine detailed passing fields such as attempted/completed passes, key passes, long balls, through balls or progression-by-pass measures.

FPL ICT Creativity must remain an FPL-native variable and must not be relabelled as passing or key-pass evidence.

Rich current-season player-match technical evidence is therefore a high-value demonstrated requirement for Player Scouting, Opposition personnel analysis and Matchday.

## Capability-led acquisition rule

The next data-source phase must **not** begin by browsing providers for the biggest field list.

The sequence is now:

```text
PRODUCT / RESEARCH QUESTION
        ↓
REQUIRED FOOTBALL CAPABILITY
        ↓
CURRENT FRL CAPABILITY CHECK
        ↓
GAP CLASSIFICATION
        ↓
CONNECT / DERIVE / GOVERN IF ALREADY PRESENT
        ↓
ONLY THEN: SUPPLEMENTARY SOURCE EVALUATION
```

The machine-readable product requirements are:

`data/frl_product_capability_requirements_v1.json`

Every apparent gap should be classified before acquisition as one of:

- source present but not connected;
- connected but not governed;
- semantics unresolved;
- identity unresolved;
- derivation not approved;
- insufficient coverage;
- current-season absent;
- historical absent;
- comparability unresolved;
- rights/operational block.

## Immediate objective

The active objective is now:

> **Industrialise FRL's broad football-variable capability and prototype the new scouting/opposition/fixture information hierarchy, then use those product requirements to score genuine capability gaps before evaluating new data sources.**

This objective deliberately precedes broad supplementary-provider acquisition.

## Immediate execution sequence

### 1. Industrialise the 249 team-match-statistic capability

- reconcile raw PulseLive team-match fields with the existing source-field/canonical-variable architecture;
- identify which variables already have governed definitions/routes;
- identify fields that are only source-present;
- classify aggregation semantics;
- classify missingness / sparse-zero semantics;
- record season coverage;
- provide generic research access where semantics are defensible;
- do not promote all 249 fields into the GUI.

### 2. Prototype Player Scouting information hierarchy

Using only already-governed evidence initially:

- design the Glance layer;
- choose visual primitives;
- establish positional/cohort navigation;
- prove smooth drill-down into deeper metrics;
- expose unavailable capability honestly rather than filling space.

### 3. Prototype Team Scouting and Opposition Report

- establish the visual style/profile summary;
- group rich historical team variables into analyst-relevant football questions;
- prove navigation from curated summary → family → full evidence;
- keep Team Profile identity/story distinct.

### 4. Refine Matchday into Fixture Intelligence

- preserve fixture-first navigation;
- organise evidence around matchup questions rather than sportsbook markets;
- identify player/team evidence that maps naturally to common bet-builder phenomena;
- retain model provenance, sample context and uncertainty.

### 5. Score capability gaps

For each experience classify required capabilities as:

`STRONG_NOW · PARTIAL_NOW · HISTORICAL_ONLY · CURRENT_ONLY · SOURCE_PRESENT_NOT_CONNECTED · DEMONSTRATED_GAP · NOT_YET_REQUIRED`

Then prioritise gaps by:

- number of experiences unlocked;
- research/modelling value;
- current-season importance;
- historical-depth value;
- player/team grain importance;
- identity/semantic complexity;
- rights/operational cost;
- provider-lock-in risk.

### 6. Begin requirement-led source evaluation

Only then define exact missing capability bundles and evaluate providers/sources against them.

## Validation discipline

Do not use a historical fixed test count as a universal baseline.

For current work:

- protect source/identity/temporal/missingness contracts;
- prefer generic analytical seams over page-specific extraction;
- run targeted tests for any new capability route;
- run affected query/API/data regressions;
- run Next.js typecheck/build for frontend changes;
- run `project-health.ps1` when canonical/query/data behaviour changes;
- run `python scripts/check_documentation_sync.py` for standing repository-memory changes;
- run `git diff --check` before integration;
- report actual outputs and isolate unrelated legacy failures.

## Repository discipline

Treat `main` / `origin/main` as the stable integration line.

Before staging or integrating work:

- compare ancestry;
- preserve unrelated local/untracked work;
- target the intended development branch explicitly;
- avoid `git clean`, destructive reset and casual broad staging;
- do not rewrite source evidence merely to simplify a product state.

## Standing repository memory

Fresh sessions should use this order:

1. `FRL_MASTER_PROMPT.md`
2. `PROJECT_ORIENTATION.md`
3. `CURRENT_WORK.md`
4. `data/frl_documentation_state_v1.json`
5. `FRL_PRODUCT_NORTH_STAR_AND_EXPERIENCE_ARCHITECTURE_V1.md`
6. `data/frl_product_capability_requirements_v1.json`
7. task-relevant durable contracts / dated audits
8. current implementation

The documentation-sync rule remains mandatory:

> **A milestone that changes current architecture, product phase, source-routing understanding, validation interpretation or frontend/design status is not complete until standing repository memory has been checked for drift.**
