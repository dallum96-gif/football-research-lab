# Current Work — Football Research Laboratory

**Last updated:** 5 September 2026  
**Checkpoint:** `TEAM_MATCH_V3_AND_FIXTURE_CONTEXT_PROVEN_V1`

For documentation-governance rules see `FRL_DOCUMENTATION_SYNC_CONTRACT.md` and `data/frl_documentation_state_v1.json`.

## Current platform state

FRL is a governed football research and modelling environment whose active product frontend is **Next.js + React**, with **FastAPI** as the frontend-facing API. Streamlit remains legacy/reference only.

Standing architecture:

- canonical fixture, team and player identity rather than source-ID coincidence;
- preserved source-native evidence with explicit provenance;
- temporal/as-of reconstruction so FRL can distinguish what is true now from what was knowable earlier;
- explicit missing, partial, unresolved and unavailable states rather than silent zero/fallback behaviour;
- governed source routing and explicit derivations;
- reproducible materialisation from pinned evidence;
- shared analytical services so product surfaces do not invent separate metric definitions, populations, ranks or percentiles.

The durable research North Star remains `FRL_MASTER_PROMPT.md`.

The active product North Star is `FRL_PRODUCT_NORTH_STAR_AND_EXPERIENCE_ARCHITECTURE_V1.md`:

> **FRL should make enormous statistical depth feel simple, visual and fluid — whether the user is scouting a player, studying a team, preparing for an opponent, researching a population, or forming an independent view of a fixture.**

## Development branch

Active development is on:

`model/poisson-v1`

`main` / `origin/main` remains the stable integration line. Do not casually rebase, reset or merge merely to simplify history.

## 2026/27 living-season state

Pinned upstream release currently integrated:

`imadeddine-belkat/Premier-League-Stats@ffe99d25a5bd3a8f70c557748fead332f46ed14f`

Materialised state at that release boundary:

- 380 canonical fixtures;
- 20 completed;
- 360 scheduled;
- 1,236 FPL player × fixture rows;
- 614 zero-minute/non-participation rows retained;
- 0 duplicate player-fixture rows;
- 0 unresolved fixture rows;
- 626 player identities through explicit verified/source-native verified routes;
- preserved release/source manifests under `data/season_releases/2026-27/`.

Living-season rules remain unchanged:

- FPL is a distinct source family;
- source identifiers are not canonical identities;
- zero-minute rows are legitimate non-participation evidence;
- missing evidence is not zero;
- later releases supersede through preserved release history rather than erasing earlier state;
- direct, FPL-derived, player-derived and supplementary representations must not be first-non-null coalesced;
- current-season outputs must expose incomplete/as-of populations honestly.

## Product state

Completed/frozen-for-now surfaces include:

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

The product is not a sequence of isolated stat pages. The experience architecture is:

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

### Product interaction principles

- **Visual summaries first.** The first view should communicate the football story quickly.
- **Progressive disclosure.** Glance → Explore → Analyse → Research.
- **Player Scouting.** Role/profile, strengths, weaknesses, current form, cohort context and key output.
- **Team Scouting.** Explain what kind of team it is, how it plays and what it does unusually well/poorly.
- **Opposition Report.** Answer: *If I were preparing to face this team, what would I need to understand?*
- **Matchday / Fixture Intelligence.** Answer: *What does the evidence tell us about this fixture?* Football-first, not sportsbook-first.
- Odds, if acquired later, remain a separate price/value layer rather than contaminating football evidence.

## Full-source capability hierarchy

The September raw PulseLive snapshot audit established:

- 3,800 preserved fixture snapshots;
- **553 distinct scalar raw paths — the master snapshotted source universe**;
- **181 capture/provenance paths — evidence infrastructure**;
- **372 football/match raw paths — football-capability subset**;
- **249 team-match statistical raw paths — first industrialisation block**;
- **123 additional football/match paths — events, lineups, managers, identity and match/team context**.

```text
553 MASTER SNAPSHOTTED RAW SOURCE PATHS
├── 181 capture / provenance
└── 372 football / match
    ├── 249 team-match statistics
    └── 123 other football / match paths
```

These are source-evidence paths, not 553 independently governed metrics.

Master objective:

> **Understand, preserve and appropriately route the full 553-path source universe, while promoting legitimate football capabilities into governed analytical access and retaining provenance paths as evidence infrastructure.**

Football-capability objective:

> **Make every legitimate governed football variable research-accessible where evidence permits; let individual product surfaces select only the variables that answer their question well.**

## Team-match capability industrialisation — V1, V2 and V3 verified

The initial 249-field reconciliation was:

- **26** exposed;
- **164** packaged/source-field uncatalogued;
- **59** raw-snapshot-only.

### Promotion Batch V1

V1 promoted 13 fields after semantic review, external corroboration where available, decade-wide packaged coverage, and zero-violation empirical invariants where relevant.

Post-V1:

- **39 exposed**;
- **151 packaged-but-ungoverned**;
- **59 raw-only**.

Generic access passed **39/39**.

This proved the industrialisation pattern:

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

A family-collision bug exposed by `interceptionWon` was fixed during V1: explicit family context now takes precedence when the same field legitimately exists at multiple grains.

### Promotion Batch V2

V2 promoted:

- `ballRecovery`;
- `successfulFinalThirdPasses`;
- `totalChippedPass`;
- `totalFinalThirdPasses`;
- `touches`;
- `unsuccessfulTouch`.

Evidence included complete **7,600/7,600** numeric coverage for all six, no negatives, strong Opta concept support, and zero-violation subset checks where asserted.

Local V2 gate:

- **24 passed in 1.71s**;
- reconciliation **45 / 145 / 59**;
- generic access **45 PASS / 0 FAIL**.

### Sparse-zero audit and missingness decision

Four high-value fields were investigated because they were almost complete but contained occasional blanks and no observed numeric zeros:

- `blockedPass` — 7,595/7,600 nonblank;
- `touchesInOppBox` — 7,598/7,600;
- `goalKicks` — 7,579/7,600;
- `lostCorners` — 7,440/7,600.

The standing contract remains:

> **A source blank is missing by default. It may become a structural zero only when the football concept, source representation and audited period provide specific evidence that blank encodes zero occurrences.**

The corroboration audit found **no exact player-match corroboration route** for any of the four fields, so no new structural-zero rule was approved.

The corrected season+fixture `lostCorners` opponent comparison produced:

- 7,438 observed pairs;
- 7,293 exact matches;
- 145 mismatches;
- all 160 `lostCorners` blanks paired with blank opponent `cornerTaken`.

Therefore `lostCorners` is **not** governed as equivalent to opponent corners and remains fail-closed.

### Promotion Batch V3 — coverage-aware exposure

V3 established a crucial separation:

> **Reusable research exposure does not require complete historical coverage when the generic seam preserves genuine missingness.**

V3 promoted:

- `blockedPass`;
- `touchesInOppBox`;
- `goalKicks`.

For all three, blanks remain explicitly `BLANK_IS_MISSING`; no structural-zero interpretation was introduced.

Local V3 gate on 5 September 2026:

- targeted regression suite: **25 passed in 0.61s**;
- reconciliation: **48 exposed / 142 packaged-but-ungoverned / 59 raw-only**;
- exposed-field generic-access audit: **48 PASS / 0 FAIL**;
- `all_exposed_fields_pass_generic_access: true`.

Therefore the current verified team-match baseline is:

```text
249 TEAM-MATCH STATISTICAL PATHS
├── 48 governed + generic research access verified
├── 142 packaged/source-field but not yet governed
└── 59 raw-snapshot-only route-discovery/raw-routing work
```

The V1/V2/V3 decisions are recorded in:

- `data/team_match_semantic_promotion_batch_v1.json`;
- `data/team_match_semantic_promotion_batch_v2.json`;
- `data/team_match_semantic_promotion_batch_v3.json`.

Still held prominently:

- `lostCorners` — semantic/opponent-route conflicts;
- `finalThirdEntries` — exact entry semantics unresolved;
- `penAreaEntries` — exact semantics unresolved and the proposed `penAreaEntries <= finalThirdEntries` shortcut was falsified by **35 violations in 7,600 rows**.

The 59 raw-only statistics remain a separate routing problem. Fuzzy name similarity is discovery evidence only and must not establish equivalence.

## Remaining 123 football/match paths — natural-grain industrialisation

The 123 paths outside the team-statistical block were triaged as:

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

Key architectural decision:

> **123 raw paths do not imply 123 independent variables.**

For example, `goals[].playerId`, `.time`, `.assistPlayerId` and `.goalType` are attributes of one coherent goal-event observation. The same principle applies to cards, substitutions, lineups/roles, formations, managers and match context.

## Fixture Event & Tactical Context — archive-wide proven

FRL already contained source-native PulseLive normalisation in `pulselive_fixture_evidence.py`. `fixture_context_research.py` now connects that normalisation to verified fixture and player relationships:

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

Archive-wide proof over all **3,800 preserved fixtures**:

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
- formation context: **7,600/7,600 team-sides**;
- manager rows: **7,728**.

Unresolved identity evidence remains explicit and is never guessed.

This is a major capability foundation for Matchday / Fixture Intelligence and Opposition Report: event chronology, player involvement, formation, role and manager context can be consumed through a governed fixture-level seam rather than rebuilt page by page.

Proof manifest: `data/fixture_context_research_capability_v1.json`.

## Known capability implications

### Team level

Historical PulseLive team-match evidence is broad across passing, possession, progression, shooting, chance creation, defending, duels and goalkeeping.

The principal current-season gap remains rich governed 2026/27 team-match evidence where the current source does not provide equivalent depth.

### Player level

FRL has a richer historical player analytical vocabulary than the current 2026/27 FPL feed.

The current FPL player-GW source does **not** provide genuine detailed passing fields such as attempted/completed passes, key passes, long balls, through balls or progression-by-pass measures.

FPL ICT Creativity must remain FPL-native and must never be relabelled as passing or key-pass evidence.

Rich current-season player-match technical evidence remains a high-value demonstrated gap for Player Scouting, Opposition personnel analysis and Matchday.

## Capability-led acquisition rule

Do not browse providers merely for the biggest field list.

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

Every apparent gap should first be classified as one of:

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

Machine-readable product requirements: `data/frl_product_capability_requirements_v1.json`.

## Immediate objective

> **Preserve the verified 48/48 team-match generic-access baseline, scale semantic/aggregation governance across the remaining 142 packaged team-stat fields without weakening missingness rules, continue evidence-led routing for the 59 raw-only team-stat paths, and begin consuming the archive-wide proven fixture event/tactical-context seam in shared Matchday and Opposition analytical services.**

This deliberately precedes broad supplementary-provider acquisition.

## Immediate execution sequence

### 1. Refresh and rank the remaining 142 packaged team-stat fields

- rerun the team-match capability queue against the 48-field registry;
- remove V1/V2/V3 fields from active promotion candidates;
- preserve explicit holds such as `lostCorners`, `finalThirdEntries` and `penAreaEntries`;
- rank remaining fields by semantic clarity, direct external support, empirical coverage, missingness, aggregation semantics and product value;
- build the next evidence batch without auto-promotion.

### 2. Continue raw-only route discovery for the 59

- distinguish identity aliases from statistics;
- test exact/safe packaged equivalence only with direct evidence;
- route genuinely raw-only evidence directly where appropriate;
- retain semantically unresolved paths as unresolved;
- do not weaken the semantic-conflict guard or rely on increasingly permissive fuzzy matching.

### 3. Consume the fixture-context seam through shared analytical services

- preserve coherent Goal/Card/Substitution objects;
- preserve lineup/role, formation and manager context at natural grain;
- quantify unresolved identity rather than guessing it;
- expose the seam to Matchday / Opposition Report through shared services rather than page-specific parsing;
- add higher-order game-state/tactical derivations only through explicit governed rules.

### 4. Prototype Player Scouting information hierarchy

Using governed evidence only:

- design the Glance layer;
- choose visual primitives;
- establish positional/cohort navigation;
- prove smooth drill-down;
- expose unavailable capability honestly.

### 5. Prototype Team Scouting and Opposition Report

- create the visual style/profile summary;
- group rich historical team variables around analyst-relevant football questions;
- integrate formation/event/personnel context from the shared fixture-context seam;
- prove curated summary → family → full evidence navigation;
- keep Team Profile identity/story distinct.

### 6. Refine Matchday into Fixture Intelligence

- preserve fixture-first navigation;
- organise evidence around matchup questions rather than sportsbook markets;
- integrate event chronology and tactical context from the shared seam;
- identify player/team evidence mapping naturally to common market phenomena without becoming odds-first;
- retain sample context, provenance and uncertainty.

### 7. Score capability gaps

Classify each requirement as:

`STRONG_NOW · PARTIAL_NOW · HISTORICAL_ONLY · CURRENT_ONLY · SOURCE_PRESENT_NOT_CONNECTED · DEMONSTRATED_GAP · NOT_YET_REQUIRED`

Prioritise by experiences unlocked, research/modelling value, current-season importance, historical depth, grain, identity/semantic complexity, rights/operational cost and provider-lock-in risk.

### 8. Begin requirement-led source evaluation

Only after the above should exact missing capability bundles be used to evaluate supplementary providers/sources.

## Validation discipline

Do not use a historical fixed test count as a universal baseline.

For current work:

- protect source/identity/temporal/missingness contracts;
- preserve the verified **48/48** exposed team-match generic-access gate;
- preserve the **3,800/3,800** fixture event/tactical-context archive-wide gate;
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

Before staging or integrating:

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
