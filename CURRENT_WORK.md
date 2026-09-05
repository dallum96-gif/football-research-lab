# Current Work — Football Research Laboratory

**Last updated:** 5 September 2026  
**Checkpoint:** `TEAM_MATCH_V2_AND_FIXTURE_CONTEXT_PROVEN_V1`

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

## Product experience decisions

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

## Team-match capability industrialisation — V1 and V2 verified

The initial 249-field reconciliation established:

- **26** `EXISTING_EXPOSED`;
- **164** `EXISTING_SOURCE_FIELD_UNCATALOGUED`;
- **59** `RAW_SNAPSHOT_ONLY`.

Promotion Batch V1 promoted 13 additional team-match fields after source-name review, external semantic corroboration where available, decade-wide packaged coverage, and zero-violation empirical invariant checks for relevant child/parent relationships.

The post-V1 state became:

- **39** `EXISTING_EXPOSED`;
- **151** `EXISTING_SOURCE_FIELD_UNCATALOGUED`;
- **59** `RAW_SNAPSHOT_ONLY`.

The generic-access audit verified **39/39** exposed fields end-to-end and proved the industrialisation pattern:

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

Promotion Batch V2 then promoted six further fields:

- `ballRecovery`;
- `successfulFinalThirdPasses`;
- `totalChippedPass`;
- `totalFinalThirdPasses`;
- `touches`;
- `unsuccessfulTouch`.

V2 evidence included:

- complete **7,600/7,600** numeric observations for all six;
- no negative values;
- direct/current Opta definitions for Ball Recovery, Touches and Unsuccessful Touch;
- direct Opta chipped-pass definition and explicit pass segmentation by final-third zone;
- `successfulFinalThirdPasses <= totalFinalThirdPasses`: **7,600 / 0 violations**;
- `totalChippedPass <= totalPass`: **7,600 / 0**;
- `unsuccessfulTouch <= touches`: **7,600 / 0**;
- `ballRecovery <= touches`: **7,600 / 0** as supporting consistency evidence.

The local V2 gate on 5 September 2026 passed:

- targeted regression suite: **24 passed in 1.71s**;
- reconciliation: **45 exposed / 145 packaged-but-ungoverned / 59 raw-only**;
- exposed-field generic-access audit: **45 PASS / 0 FAIL**;
- `all_exposed_fields_pass_generic_access: true`.

Therefore the current verified team-match baseline is **45/45 generic access**.

The V1 and V2 decisions are recorded in:

- `data/team_match_semantic_promotion_batch_v1.json`;
- `data/team_match_semantic_promotion_batch_v2.json`.

A family-collision bug exposed by `interceptionWon` was fixed during V1: explicit family context takes precedence when the same source field legitimately exists at multiple grains, while aliases remain available in their own family.

## Team-match fields currently held after V2

Four high-value fields are held specifically on blank-versus-zero semantics:

- `blockedPass` — 7,595/7,600 nonblank, no observed zeros;
- `touchesInOppBox` — 7,598/7,600 nonblank, no observed zeros;
- `goalKicks` — 7,579/7,600 nonblank, no observed zeros;
- `lostCorners` — 7,440/7,600 nonblank, no observed zeros.

These must not be promoted merely because the names are clear or blanks are rare. The standing rule in `FRL_TEAM_MATCH_MISSINGNESS_CONTRACT.md` remains:

> **A source blank is missing by default. It may become a structural zero only when the football concept, source representation and audited period provide specific evidence that blank encodes zero occurrences.**

A new read-only corroboration audit is now the active evidence gate:

`scripts/audit_team_match_sparse_zero_candidates.py`

It seeks independent support by:

- comparing each team field with the exact same player-match source field summed to team/fixture grain where that route exists;
- requiring the player route to agree with observed team values before using it to interpret blanks;
- retaining player blanks as missing rather than manufacturing zero sums;
- retesting `lostCorners` against opponent `cornerTaken` using **season + fixture** identity rather than fixture ID alone.

The earlier aggregate `lostCorners` test that returned zero comparable observations was structurally invalid because fixture IDs repeat by season. That result must not be used as semantic evidence.

Two further V2 candidates remain held on semantics rather than missingness:

- `finalThirdEntries`;
- `penAreaEntries`.

The proposed shortcut `penAreaEntries <= finalThirdEntries` produced **35 violations in 7,600 rows**. Therefore penalty-area entries and final-third entries must **not** be treated as simple nested counts on current evidence. This does not invalidate either source field independently; it blocks that proposed semantic relationship.

The 59 raw-snapshot-only team statistics remain a separate route-discovery/raw-routing problem; fuzzy name similarity is discovery evidence only and must not establish equivalence.

## Remaining 123 football/match paths — natural-grain industrialisation

The 123 football/match paths outside the 249 team-statistical block have been triaged:

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

The archive-wide local audit verified this route over all **3,800 preserved fixtures**:

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

> **Preserve the verified 45/45 team-match generic-access baseline, resolve the next high-value missingness/semantic blockers without weakening governance, and begin consuming the archive-wide proven fixture event/tactical-context seam in shared Matchday and Opposition analytical services while continuing the 123-path natural-grain programme.**

This objective deliberately precedes broad supplementary-provider acquisition.

## Immediate execution sequence

### 1. Resolve sparse-zero candidates by independent evidence

- run `tests/test_team_match_sparse_zero_candidates.py`;
- run `scripts/audit_team_match_sparse_zero_candidates.py` across the decade;
- determine whether exact player-match aggregation exists for `blockedPass`, `touchesInOppBox`, `goalKicks` and/or `lostCorners`;
- require corroborating routes to agree with observed team values before using them to interpret blanks;
- retest `lostCorners` against opponent corners using season-aware fixture identity;
- only extend `FRL_TEAM_MATCH_MISSINGNESS_CONTRACT.md` when structural-zero evidence is specific and defensible.

### 2. Continue team-match semantic industrialisation

- preserve the verified **45/45** generic-access gate;
- prioritise direct-definition and complete-coverage candidates;
- keep `finalThirdEntries` / `penAreaEntries` fail-closed until exact semantics are established;
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
- preserve the verified **45/45** exposed team-match generic-access gate;
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
