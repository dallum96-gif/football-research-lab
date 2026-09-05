# Current Work — Football Research Laboratory

**Last updated:** 5 September 2026  
**Checkpoint:** `TEAM_MATCH_V4_AND_FIXTURE_CONTEXT_PROVEN_V1`

For documentation-governance rules see `FRL_DOCUMENTATION_SYNC_CONTRACT.md` and `data/frl_documentation_state_v1.json`.

## Current platform state

FRL is a governed football research and modelling environment. The active product frontend is **Next.js + React**, with **FastAPI** as the frontend-facing API. Streamlit is legacy/reference only.

Standing architecture:

- canonical fixture, team and player identity rather than source-ID coincidence;
- preserved source-native evidence with explicit provenance;
- temporal/as-of reconstruction;
- explicit missing, partial, unresolved and unavailable states rather than silent zero/fallback behaviour;
- governed source routing and explicit derivations;
- reproducible materialisation from pinned evidence;
- shared analytical services so product surfaces do not invent separate metric definitions, populations, ranks or percentiles.

The durable research North Star remains `FRL_MASTER_PROMPT.md`.

The active product North Star is `FRL_PRODUCT_NORTH_STAR_AND_EXPERIENCE_ARCHITECTURE_V1.md`:

> **FRL should make enormous statistical depth feel simple, visual and fluid — whether the user is scouting a player, studying a team, preparing for an opponent, researching a population, or forming an independent view of a fixture.**

## Development branch

Active development is on `model/poisson-v1`.

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

Completed/frozen-for-now surfaces include Homepage V1, standalone Fixtures V1 and Team Profile V1.

Active/recent analytical surfaces include:

- Team Stats Team View;
- Team Stats League Rankings;
- Player Stats / Player Rankings;
- Player profiles/directories;
- League Table;
- Matchday fixture workspace.

The shared tiled vertical-list language remains a valid FRL Stats interaction pattern.

The product experience architecture remains:

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

Interaction principles:

- visual summaries first;
- progressive disclosure: Glance → Explore → Analyse → Research;
- scouting surfaces explain football style, role, strengths, weaknesses and context rather than dumping metrics;
- Matchday remains fixture-first and football-first, not sportsbook-first;
- odds, if acquired later, remain a separate price/value layer.

## Full-source capability hierarchy

The preserved PulseLive archive contains **3,800 Premier League fixture snapshots** across 2016/17–2025/26.

The master raw-source hierarchy is:

```text
553 MASTER SNAPSHOTTED RAW SOURCE PATHS
├── 181 capture / provenance paths
└── 372 football / match paths
    ├── 249 team-match statistical paths
    └── 123 other football / match paths
```

The **553-path universe is the master source/evidence universe**. The 372 football paths and 249 team-stat paths are subsets, not competing North Stars.

Master objective:

> **Understand, preserve and appropriately route the full 553-path source universe, while promoting legitimate football capabilities into governed analytical access and retaining provenance paths as evidence infrastructure.**

## Team-match capability industrialisation — V1 through V4 verified

Initial reconciliation:

- 26 exposed;
- 164 packaged/source-field uncatalogued;
- 59 raw-snapshot-only.

### V1

V1 promoted 13 fields using semantic review, external corroboration and empirical invariants where appropriate. Post-V1 generic access passed **39/39**.

It established the reusable industrialisation route:

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

It also exposed and fixed the family-collision rule: explicit family context is authoritative when the same source field genuinely exists at multiple grains.

### V2

V2 promoted six fields:

- `ballRecovery`;
- `successfulFinalThirdPasses`;
- `totalChippedPass`;
- `totalFinalThirdPasses`;
- `touches`;
- `unsuccessfulTouch`.

The V2 evidence stack combined complete decade-wide numeric observation, no negatives, direct/strong Opta concept support and zero-violation subset checks where asserted. Generic access passed **45/45** after promotion.

The proposed `penAreaEntries <= finalThirdEntries` nesting shortcut was falsified by **35 violations in 7,600 rows**. That falsifies the relationship assumption; it does not prove either source field invalid.

### V3 — coverage-aware exposure

V3 established an important governance separation:

> **Semantic validity, missingness semantics and research accessibility are separate dimensions.**

It promoted:

- `blockedPass`;
- `touchesInOppBox`;
- `goalKicks`.

These fields can be safely queried even though occasional historical blanks remain genuine missing values. No new structural-zero rule was introduced.

The standing missingness rule remains:

> **A source blank is missing by default. Structural zero requires specific evidence for that concept, representation and period.**

### V4 — scaled evidence-backed promotion

The post-V3 evidence matrix split the remaining packaged fields by semantic support, coverage shape, relationship opportunities and prior holds rather than treating full coverage as a promotion gate.

The V4 evidence stack audited **18 child≤parent relationships across the decade**. All **18/18** were empirically consistent with zero violations and no negative-value violations.

V4 promoted 16 fields:

- `accurateChippedPass`;
- `accurateCross`;
- `accurateFlickOn`;
- `accurateGoalKicks`;
- `accurateKeeperThrows`;
- `accurateLaunches`;
- `accurateLayoffs`;
- `accurateLongBalls`;
- `blockedCross`;
- `keeperThrows`;
- `lostCorners`;
- `totalFlickOn`;
- `totalLaunches`;
- `totalLayoffs`;
- `totalLongBalls`;
- `wonCorners`.

Authoritative Opta / Premier League concept evidence supports the promoted families, including launches, flick-ons, lay-offs, long balls, goalkeeper throws, crosses, goal kicks, blocked crosses and corners.

#### `lostCorners` semantic resolution

The earlier comparison against opponent `cornerTaken` produced 145 mismatches. That comparison is **not** a valid equality invariant.

Opta directly defines **Corner Lost** for the team conceding the corner and explicitly states that Corner Won/Lost and Corner Taken use different collection criteria, so their aggregate totals may differ.

Therefore:

- `lostCorners` is now governed as the source-native Corner Lost / corners-conceded concept;
- it is **not** defined as opponent `cornerTaken`;
- its 160 historical blanks remain missing;
- the prior opponent-equality assumption is retired.

#### V4 local verification

On 5 September 2026:

- targeted V4/V3/V2/resolver/generic-access regression suite: **28 passed** on two consecutive runs;
- reconciliation: **64 exposed / 126 packaged-but-ungoverned / 59 raw-only**;
- generic-access audit: **64 PASS / 0 FAIL**;
- query audit: **64 PASS / 0 FAIL**;
- `all_exposed_fields_pass_generic_access: true`.

The current verified team-match state is therefore:

```text
249 TEAM-MATCH STATISTICAL PATHS
├── 64 governed + generic research access verified
├── 126 packaged/source-field but not yet governed
└── 59 raw-snapshot-only route-discovery/raw-routing work
```

Controlled promotion manifests:

- `data/team_match_semantic_promotion_batch_v1.json`;
- `data/team_match_semantic_promotion_batch_v2.json`;
- `data/team_match_semantic_promotion_batch_v3.json`;
- `data/team_match_semantic_promotion_batch_v4.json`.

Current important holds include:

- `redCard` — reconcile against already-exposed `totalRedCard` and governed card events before exposing another aggregate;
- `subsMade` — reconcile against governed substitution events;
- `accurateBackZonePass` / `accurateFwdZonePass` — relationship evidence exists but zone semantics need direct corroboration;
- `accurateCornersIntobox` — relationship evidence exists but exact corner-into-box semantics remain unresolved;
- `accurateKeeperSweeper` — sparse coverage and exact keeper-sweeper semantics need direct definition review;
- `accuratePullBack` / `accurateThroughBall` — relationship evidence alone is insufficient;
- `successfulFiftyFifty` / `successfulPutThrough` — relationship evidence alone is insufficient;
- `accurateThrows` — zero-violation relationship evidence exists but exact throw semantics are not yet governed;
- `effectiveBlockedCross` — `effective` qualifier remains undefined;
- `finalThirdEntries` / `penAreaEntries` — direct semantics remain unresolved, and their simple nested relationship is explicitly rejected.

The 59 raw-only team statistics remain a separate routing problem. Fuzzy name similarity is discovery evidence only and must not establish equivalence.

## Remaining 123 football/match paths — natural-grain industrialisation

The 123 football paths outside the team-statistical block were triaged as:

- 58 Events;
- 10 Managers;
- 17 Match Context;
- 16 Player Lineup Context;
- 6 Team Lineup Context;
- 16 Team-Match Context.

Priority split:

- 46 P0;
- 49 P1;
- 28 P2.

Key architectural rule:

> **123 raw paths do not imply 123 independent analytical variables.**

Goal/card/substitution attributes form coherent event objects. Lineup identity, role, formation, manager and match context likewise belong at their natural grains.

## Fixture Event & Tactical Context — archive-wide proven

`fixture_context_research.py` connects preserved PulseLive evidence to verified fixture/team/player relationships and the existing source-native event/lineup normalisation.

```text
CANONICAL FIXTURE
      ↓
VERIFIED PULSELIVE SOURCE MATCH
      ↓
PRESERVED SNAPSHOT
      ↓
NORMALISED EVENTS + LINEUP / FORMATION / MANAGER CONTEXT
      ↓
EXPLICIT PULSELIVE → PLAYER-MATCH SOURCE IDENTITY DECISIONS
      ↓
FIXTURE-CONTEXT RESEARCH RESULT
```

Archive-wide proof:

- Event route: **3,800 PASS / 0 FAIL**;
- Tactical-context route: **3,800 PASS / 0 FAIL**;
- normalised events: **50,182**;
  - 10,787 goals;
  - 14,269 cards;
  - 25,126 substitutions;
- event primary-player bridge: 49,625 verified / 287 unresolved;
- event secondary-player bridge: 32,443 verified / 101 unresolved;
- lineup-player rows: 145,637;
- lineup-player bridge: 144,645 verified / 992 unresolved;
- formation context: **7,600/7,600 team-sides**;
- manager rows: 7,728.

Unresolved identities remain explicit and are never guessed.

Proof manifest: `data/fixture_context_research_capability_v1.json`.

This seam is now infrastructure ready to be consumed by Matchday / Fixture Intelligence and Opposition Report rather than re-parsed page by page.

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

Every apparent gap should first be classified as source-present-not-connected, connected-but-not-governed, semantics unresolved, identity unresolved, derivation not approved, insufficient coverage, current-season absent, historical absent, comparability unresolved or rights/operational block.

Machine-readable requirements: `data/frl_product_capability_requirements_v1.json`.

## Immediate objective

> **Preserve the verified 64/64 team-match generic-access baseline, resolve high-value evidence/reconciliation tasks across the remaining 126 packaged team-stat fields, continue evidence-led routing for the 59 raw-only team-stat paths, and consume the archive-wide proven fixture event/tactical-context seam through shared Matchday and Opposition analytical services.**

This deliberately precedes broad supplementary-provider acquisition.

## Immediate execution sequence

### 1. Reconcile aggregate fields against the event seam

Prioritise concepts where FRL has two independent representations:

- reconcile `redCard` against already-exposed `totalRedCard` and card-event evidence;
- reconcile `subsMade` against the governed 25,126 substitution events;
- classify differences by source definition rather than forcing equality;
- promote only where the exact aggregate concept is defensible.

### 2. Refresh the remaining 126 packaged team-stat evidence matrix

- regenerate the capability queue after V4;
- remove V1–V4 promotions from active review;
- preserve direct-definition and relationship-only holds;
- prioritise authoritative-definition research for the largest remaining semantic families;
- use empirical relationships as supporting evidence only;
- continue coverage-aware exposure where semantics are strong and blanks can remain missing.

### 3. Continue raw-only route discovery for the 59

- distinguish identity aliases from statistics;
- test exact/safe packaged equivalence only with direct evidence;
- route genuinely raw-only evidence directly where appropriate;
- retain semantically unresolved paths as unresolved;
- do not weaken semantic-conflict guards or use increasingly permissive fuzzy matching.

### 4. Consume the fixture-context seam through shared analytical services

- preserve coherent Goal/Card/Substitution objects;
- preserve lineup/role, formation and manager context at natural grain;
- quantify unresolved identity rather than guessing it;
- expose the seam to Matchday / Opposition Report through shared services;
- add game-state/tactical derivations only through explicit governed rules.

### 5. Prototype Player Scouting information hierarchy

Using governed evidence only:

- design the Glance layer;
- choose visual primitives;
- establish positional/cohort navigation;
- prove smooth drill-down;
- expose unavailable capability honestly.

### 6. Prototype Team Scouting and Opposition Report

- create visual style/profile summaries;
- organise governed team variables around analyst-relevant football questions;
- integrate formation/event/personnel context from the shared fixture seam;
- prove curated summary → family → full evidence navigation;
- keep Team Profile identity/story distinct.

### 7. Refine Matchday into Fixture Intelligence

- preserve fixture-first navigation;
- organise evidence around matchup questions;
- integrate event chronology and tactical context from the shared seam;
- identify player/team evidence mapping naturally to common market phenomena without becoming odds-first;
- retain sample context, provenance and uncertainty.

### 8. Score capability gaps and evaluate supplementary sources only after internal capability is classified

Use:

`STRONG_NOW · PARTIAL_NOW · HISTORICAL_ONLY · CURRENT_ONLY · SOURCE_PRESENT_NOT_CONNECTED · DEMONSTRATED_GAP · NOT_YET_REQUIRED`

## Validation discipline

Do not use a historical fixed test count as a universal baseline.

For current work:

- protect source/identity/temporal/missingness contracts;
- preserve the verified **64/64** exposed team-match generic-access gate;
- preserve the **3,800/3,800** fixture event/tactical-context archive-wide gate;
- prefer generic analytical seams over page-specific extraction;
- run targeted tests for new capability routes;
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
- do not rewrite source evidence merely to simplify product state.

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
