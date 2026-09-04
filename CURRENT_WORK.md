# Current Work — Football Research Laboratory

**Last updated:** 4 September 2026  
**Checkpoint:** `FIXTURE_CONTEXT_ARCHIVE_WIDE_PROVEN_V1_TEAM_MATCH_V2_PENDING`

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

The active product North Star is recorded in:

`FRL_PRODUCT_NORTH_STAR_AND_EXPERIENCE_ARCHITECTURE_V1.md`

Its product promise is:

> **FRL should make enormous statistical depth feel simple, visual and fluid — whether the user is scouting a player, studying a team, preparing for an opponent, researching a population, or forming an independent view of a fixture.**

The master PulseLive source-capability hierarchy is recorded in:

`FRL_553_SOURCE_CAPABILITY_UNIVERSE_V1.md`

## Current development branch state

Active development work for the current Matchday / capability / product-direction sequence is on:

`model/poisson-v1`

Development changes must continue to target the development branch explicitly rather than the stable `main` line. Do not rebase, reset or merge casually merely to simplify branch history.

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

The experience architecture treats the governed football-variable universe as one shared foundation with several lenses:

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

### Visual summaries first

The first view should communicate the important football story quickly and visually. Deep numbers remain available but should not dominate the initial experience.

### Progressive disclosure

FRL uses four information layers:

1. **Glance** — understand the story in seconds;
2. **Explore** — understand major football components/families;
3. **Analyse** — access broader metrics, ranks, distributions, splits and trends;
4. **Research** — inspect provenance, coverage, transformations, populations and temporal semantics.

### Player Scouting

A player scouting surface should rapidly communicate role/profile, strengths, weaknesses/comparatively low areas, current performance, cohort/league context and key output. Player-specific cohort, role and minutes semantics remain mandatory before strong interpretation.

### Team Scouting

Team scouting should explain what kind of team the subject is, how it plays, what it does unusually well/poorly and how those behaviours compare with the league.

### Opposition Report

Opposition Report is a distinct analytical mode answering:

> **If I were preparing to face this team, what would I need to understand?**

It should organise evidence around football preparation — build-up, progression, chance creation, threat, defensive behaviour, transitions, set pieces, personnel and recent tactical change — rather than source columns.

### Matchday / Fixture Intelligence

The fixture is the entry point. FRL should answer:

> **What does the evidence tell us about this fixture?**

The initial objective is an independent football view, not replication of a bookmaker interface. Bet-builder support can emerge by surfacing football phenomena corresponding to common markets while retaining samples and uncertainty. Bookmaker odds are not required for this initial experience and, if acquired later, should remain quarantined from ordinary football evidence.

## Full-source capability hierarchy

FRL should curate presentation, **not artificially curate away data or evidence capability**.

The September raw PulseLive snapshot audit established:

- 3,800 preserved fixture snapshots;
- **553 distinct scalar raw paths — the master snapshotted source universe**;
- **181 capture/provenance paths — evidence infrastructure**;
- **372 football/match raw paths — the football-capability subset**;
- **249 team-match statistical raw paths — the first industrialisation block**;
- **123 additional football/match paths — events, lineups, managers, identity and match/team context**.

```text
553 MASTER SNAPSHOTTED RAW SOURCE PATHS
├── 181 capture / provenance
└── 372 football / match
    ├── 249 team-match statistics
    └── 123 other football / match paths
```

These numbers describe source evidence, not 553 independently governed metrics.

The master source objective is:

> **Understand, preserve and appropriately route the full 553-path source universe, while promoting legitimate football capabilities into governed analytical access and retaining provenance paths as evidence infrastructure.**

The active football-capability ambition inside that master universe is:

> **Make every legitimate governed football variable research-accessible where evidence permits; let individual product surfaces select only the variables that answer their question well.**

## Team-match capability industrialisation — verified V1 baseline

The initial 249-field reconciliation established:

- **26** `EXISTING_EXPOSED`;
- **164** `EXISTING_SOURCE_FIELD_UNCATALOGUED`;
- **59** `RAW_SNAPSHOT_ONLY`.

Promotion Batch V1 then promoted 13 additional team-match fields after source-name review, external semantic corroboration where available, decade-wide packaged coverage, and zero-violation empirical invariant checks for relevant child/parent relationships.

The verified post-V1 reconciliation is:

- **39** `EXISTING_EXPOSED`;
- **151** `EXISTING_SOURCE_FIELD_UNCATALOGUED`;
- **59** `RAW_SNAPSHOT_ONLY`.

The generic-access audit verified **39/39 exposed team-match statistical fields** end-to-end:

- all 39 are discoverable as exposed;
- all 39 resolve at explicit `team_match` grain;
- all 39 execute against observed historical fixture evidence through the shared generic query route;
- all 39 return source-field-consistent results;
- no per-metric extractor is required.

This proves the industrialisation pattern:

```text
SOURCE FIELD
    ↓
SEMANTIC GOVERNANCE
    ↓
DISCOVERY
    ↓
EXPLICIT GRAIN RESOLUTION
    ↓
GENERIC RESEARCH RETRIEVAL
```

A family-collision bug exposed by `interceptionWon` was also fixed: explicit family context now takes precedence when the same source field legitimately exists at multiple grains, while aliases remain available in their own family.

The 59 raw-snapshot-only team statistics remain a separate route-discovery/raw-routing problem; fuzzy name similarity is discovery evidence only and must not establish equivalence.

The V1 decision and evidence are recorded in `data/team_match_semantic_promotion_batch_v1.json`.

## Team-match Promotion Batch V2 — registry promoted, local gate pending

The V2 review queue narrowed the 151 packaged-but-ungoverned fields into explicit evidence lanes. The V2 empirical audit then evaluated the strongest immediate candidates across all **7,600 historical team-match rows**.

Six fields have now been promoted in `source_field_registry.py`, pending the local regression/reconciliation gate:

- `ballRecovery`;
- `successfulFinalThirdPasses`;
- `totalChippedPass`;
- `totalFinalThirdPasses`;
- `touches`;
- `unsuccessfulTouch`.

Promotion evidence includes:

- complete 7,600/7,600 numeric observations for all six;
- no negative values;
- direct/current Opta definitions for Ball Recovery, Touches and Unsuccessful Touch;
- direct Opta chipped-pass definition and explicit pass segmentation by final-third zone;
- `successfulFinalThirdPasses <= totalFinalThirdPasses`: 7,600 comparisons / 0 violations;
- `totalChippedPass <= totalPass`: 7,600 / 0;
- `unsuccessfulTouch <= touches`: 7,600 / 0;
- `ballRecovery <= touches`: 7,600 / 0 as supporting consistency evidence.

The validated baseline remains **39/39** until the local V2 regression and generic-access audits are rerun. If the gate passes, reconciliation should become **45 exposed / 145 packaged-but-ungoverned / 59 raw-only** and the generic-access baseline should become **45/45**.

Fields deliberately held after V2 include:

- `blockedPass`, `touchesInOppBox`, `goalKicks`, `lostCorners` — direct or plausible concepts, but occasional blanks combined with no observed zeros require explicit sparse-zero/blank semantics;
- `finalThirdEntries`, `penAreaEntries` — complete numeric coverage, but exact entry semantics remain unresolved.

A proposed shortcut was explicitly falsified rather than silently accepted:

- `penAreaEntries <= finalThirdEntries` produced **35 violations in 7,600 rows**.

Therefore penalty-area entries and final-third entries must **not** be treated as simple nested counts on current evidence. This does not invalidate either source field independently; it blocks that proposed semantic relationship.

The V2 decision is recorded in `data/team_match_semantic_promotion_batch_v2.json` and supporting terminology in `data/team_match_semantic_evidence_v2.json`.

## Remaining 123 football/match paths — natural-grain industrialisation

The 123 football/match paths outside the 249 team-statistical block have now been triaged:

- 58 Events;
- 10 Managers;
- 17 Match Context;
- 16 Player Lineup Context;
- 6 Team Lineup Context;
- 16 Team-Match Context.

Priority split:

- **46 P0**;
- **49 P1**;
- **28 P2**.

The key architecture decision is that **123 raw paths do not imply 123 independent variables**. Paths such as `goals[].playerId`, `goals[].time`, `goals[].assistPlayerId` and `goals[].goalType` belong to one coherent goal-event observation. The same principle applies to cards, substitutions, player-lineup role, team formation, manager context and match context.

The programme therefore industrialises natural-grain evidence objects rather than raw JSON paths.

## Fixture Event & Tactical Context — archive-wide proven

FRL already contained source-native PulseLive normalisation in `pulselive_fixture_evidence.py`. A governed reusable seam now connects that normalisation to verified fixture and player relationships in `fixture_context_research.py`:

```text
CANONICAL FIXTURE
      ↓
VERIFIED PULSELIVE SOURCE MATCH
      ↓
PRESERVED SNAPSHOT
      ↓
NORMALISED EVENTS + LINEUP / FORMATION / MANAGER CONTEXT
      ↓
EXPLICIT PULSELIVE → PLAYER-MATCH IDENTITY DECISIONS
      ↓
FIXTURE-CONTEXT RESEARCH RESULT
```

The archive-wide local audit has verified this route over all **3,800 preserved fixtures**:

- Event route: **3,800 PASS / 0 FAIL**;
- Tactical-context route: **3,800 PASS / 0 FAIL**;
- normalised events: **50,182**;
  - 10,787 goals;
  - 14,269 cards;
  - 25,126 substitutions;
- event primary-player bridge: 49,625 verified / 287 unresolved;
- event secondary-player bridge: 32,443 verified / 101 unresolved;
- lineup-player rows: **145,637**;
- lineup-player bridge: 144,645 verified / 992 unresolved;
- formation context available for **7,600/7,600 team-sides**;
- manager rows: **7,728**.

Unresolved identity evidence remains explicit and is never guessed.

This is a major capability result for Matchday / Fixture Intelligence and Opposition Report: event chronology, player involvement, formation, role and manager context can be consumed through a governed fixture-level seam rather than reconstructed independently by each product surface.

The archive-wide proof is recorded in `data/fixture_context_research_capability_v1.json`.

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

The machine-readable product requirements are `data/frl_product_capability_requirements_v1.json`.

Every apparent gap should be classified before acquisition as source present but not connected; connected but not governed; semantics unresolved; identity unresolved; derivation not approved; insufficient coverage; current-season absent; historical absent; comparability unresolved; or rights/operational block.

## Immediate objective

The active objective is now:

> **Verify Team-Match Promotion Batch V2 through the proven 45-field generic-access gate, then scale semantic/missingness governance across the remaining team-stat fields while extending the proven fixture event/tactical-context seam into Matchday, Opposition Report and the broader 123-path natural-grain programme.**

This objective deliberately precedes broad supplementary-provider acquisition.

## Immediate execution sequence

### 1. Verify Team-Match Promotion Batch V2

- run targeted V2 registry/resolver tests;
- rerun 249-field reconciliation;
- require the expected **45 / 145 / 59** split before marking V2 verified;
- rerun exposed-team generic access and require **45/45**;
- update V2 manifest from pending to verified only after that gate passes.

### 2. Continue team-match semantic and missingness industrialisation

- preserve the verified generic-access architecture;
- prioritise direct-definition and complete-coverage candidates;
- investigate sparse-zero semantics before exposing no-zero/occasionally-blank fields;
- continue to fail closed on ambiguous qualifiers and falsified assumptions;
- investigate the 59 raw-only fields by route/source evidence rather than increasingly permissive fuzzy matching.

### 3. Extend the proven fixture-context object model

- preserve coherent Goal/Card/Substitution event objects;
- preserve player lineup/role, formation and manager context at natural grain;
- quantify and classify unresolved identity cases rather than guessing them;
- add higher-order game-state/tactical derivations only through explicit governed rules;
- expose the seam to Matchday / Opposition Report through shared analytical services rather than page-specific parsing.

### 4. Prototype Player Scouting information hierarchy

Using only already-governed evidence initially:

- design the Glance layer;
- choose visual primitives;
- establish positional/cohort navigation;
- prove smooth drill-down into deeper metrics;
- expose unavailable capability honestly rather than filling space.

### 5. Prototype Team Scouting and Opposition Report

- establish the visual style/profile summary;
- group rich historical team variables into analyst-relevant football questions;
- integrate formation/event/personnel context from the shared fixture-context seam;
- prove navigation from curated summary → family → full evidence;
- keep Team Profile identity/story distinct.

### 6. Refine Matchday into Fixture Intelligence

- preserve fixture-first navigation;
- organise evidence around matchup questions rather than sportsbook markets;
- integrate event chronology and tactical context from the shared governed seam;
- identify player/team evidence that maps naturally to common bet-builder phenomena;
- retain model provenance, sample context and uncertainty.

### 7. Score capability gaps

For each experience classify required capabilities as:

`STRONG_NOW · PARTIAL_NOW · HISTORICAL_ONLY · CURRENT_ONLY · SOURCE_PRESENT_NOT_CONNECTED · DEMONSTRATED_GAP · NOT_YET_REQUIRED`

Then prioritise gaps by experiences unlocked, research/modelling value, current-season importance, historical depth, player/team grain, identity/semantic complexity, rights/operational cost and provider-lock-in risk.

### 8. Begin requirement-led source evaluation

Only then define exact missing capability bundles and evaluate providers/sources against them.

## Validation discipline

Do not use a historical fixed test count as a universal baseline.

For current work:

- protect source/identity/temporal/missingness contracts;
- preserve the verified **39/39** exposed team-match generic-access gate until V2 is locally proven, then advance explicitly to 45/45;
- preserve the **3,800/3,800** fixture event/tactical-context route as an archive-wide regression gate;
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
6. `FRL_553_SOURCE_CAPABILITY_UNIVERSE_V1.md`
7. `FRL_372_FOOTBALL_CAPABILITY_EXECUTION_PLAN_V1.md`
8. `data/frl_product_capability_requirements_v1.json`
9. task-relevant durable contracts / dated audits
10. current implementation

The documentation-sync rule remains mandatory:

> **A milestone that changes current architecture, product phase, source-routing understanding, validation interpretation or frontend/design status is not complete until standing repository memory has been checked for drift.**
