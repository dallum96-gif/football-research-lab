# Current Work — Football Research Laboratory

**Last updated:** 5 September 2026  
**Checkpoint:** `TEAM_MATCH_V6_AND_FIXTURE_CONTEXT_PROVEN_V1`

For documentation-governance rules see `FRL_DOCUMENTATION_SYNC_CONTRACT.md` and `data/frl_documentation_state_v1.json`.

## Current platform state

FRL is a governed football research and modelling environment. The active frontend is **Next.js + React**, with **FastAPI** as the frontend-facing API. Streamlit is legacy/reference only.

Standing rules:

- canonical fixture/team/player identity, never source-ID coincidence;
- preserved source-native evidence with provenance;
- temporal/as-of reconstruction;
- explicit missing/partial/unresolved/unavailable states rather than silent zero or fallback behaviour;
- governed source routing and explicit derivation;
- reproducible materialisation from pinned evidence;
- shared analytical services so product surfaces do not invent separate definitions or populations.

The durable research North Star remains `FRL_MASTER_PROMPT.md`. The active product North Star remains `FRL_PRODUCT_NORTH_STAR_AND_EXPERIENCE_ARCHITECTURE_V1.md`:

> **FRL should make enormous statistical depth feel simple, visual and fluid — whether the user is scouting a player, studying a team, preparing for an opponent, researching a population, or forming an independent view of a fixture.**

## Development branch

Active development is on `model/poisson-v1`. `main` / `origin/main` remains the stable integration line. Do not casually reset, rebase or merge merely to simplify history.

## 2026/27 living-season state

Pinned upstream release currently integrated:

`imadeddine-belkat/Premier-League-Stats@ffe99d25a5bd3a8f70c557748fead332f46ed14f`

Materialised state:

- 380 canonical fixtures;
- 20 completed / 360 scheduled;
- 1,236 FPL player × fixture rows;
- 614 zero-minute/non-participation rows retained;
- 0 duplicate player-fixture rows;
- 0 unresolved fixture rows;
- 626 player identities through explicit verified/source-native verified routes.

FPL remains a distinct source family. FPL ICT Creativity must never be relabelled as detailed passing/key-pass evidence. Rich current-season team/player technical evidence remains a genuine product capability gap.

## Product state

Completed/frozen-for-now surfaces include Homepage V1, standalone Fixtures V1 and Team Profile V1. Active/recent analytical surfaces include Team Stats, Player Stats / Rankings, Player profiles/directories, League Table and Matchday.

Experience architecture:

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

Interaction principles remain visual-first, progressively disclosed and football-first rather than sportsbook-first.

## Full-source capability hierarchy

The preserved PulseLive archive contains **3,800 Premier League fixture snapshots** across 2016/17–2025/26.

```text
553 MASTER SNAPSHOTTED RAW SOURCE PATHS
├── 181 capture / provenance paths
└── 372 football / match paths
    ├── 249 team-match statistical paths
    └── 123 other football / match paths
```

The **553-path universe is the master source/evidence universe**. The 372 and 249 figures are analytical subsets.

Master objective:

> **Understand, preserve and appropriately route the full 553-path source universe, while promoting legitimate football capabilities into governed analytical access and retaining provenance paths as evidence infrastructure.**

## Team-match capability industrialisation — V1 through V6 verified

Initial reconciliation was:

- 26 exposed;
- 164 packaged/source-field uncatalogued;
- 59 raw-only.

The reusable architecture is:

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

### V1–V4

V1 promoted 13 fields and established generic source-native access plus explicit family disambiguation. V2 promoted six more using complete decade-wide observation, direct semantics and subset checks where appropriate. V3 proved that **semantic validity, missingness semantics and research accessibility are separate governance dimensions**: partial historical coverage can remain reusable when blanks remain missing. V4 promoted 16 fields using authoritative definitions plus decade-wide relationship evidence where relevant.

The standing missingness rule remains:

> **A source blank is missing by default. Structural zero requires specific evidence for that concept, representation and period.**

`lostCorners` is governed as the provider-native Corner Lost / corners-conceded concept. It is **not** defined as opponent `cornerTaken`; the earlier equality assumption is retired because Opta documents different collection criteria for Corner Won/Lost versus Corner Taken.

### V5 — bulk exact-definition promotion

V5 stopped treating every legacy field as a separate research project. An exact legacy Opta F9 field-reference dictionary was used to resolve coherent families in bulk.

V5 promoted **49 fields**, including:

- contest/dribble concepts (`totalContest`, `wonContest`, `challengeLost`);
- directional/zone passing (`totalBackZonePass`, `accurateBackZonePass`, `totalFwdZonePass`, `accurateFwdZonePass`, `leftsidePass`, `rightsidePass`, `passesLeft`, `passesRight`);
- through balls, pull-backs, throws and corner-into-box distributions;
- keeper-sweeper actions and high claims;
- possession regain/loss zones;
- `finalThirdEntries` and `penAreaEntries` as independently defined concepts with **no nesting assumption**;
- shot assists, defensive errors, blocks, saves and substitution count.

### V6 — remaining directly documented families

V6 promoted **54 additional fields** from the remaining packaged set using the same exact-definition approach across:

- direct free-kick attempts/outcomes;
- penalties and penalty goalkeeping;
- shot provenance (corner, fast-break, open-play, set-play, one-on-one);
- goal and shot-assist families;
- goalkeeper claims/punches;
- card-event qualifiers;
- own goals;
- possession loss;
- shot/post locations and other directly documented source concepts.

No new structural-zero rule was introduced in either V5 or V6.

### Verified V6 baseline

On 5 September 2026 the combined local milestone validator passed:

- **Pytest: PASS across 10 milestone test modules**;
- reconciliation: **167 exposed / 23 packaged-but-ungoverned / 59 raw-only**;
- generic access: **167/167 PASS**;
- documentation sync: **PASS**.

Current verified team-match state:

```text
249 TEAM-MATCH STATISTICAL PATHS
├── 167 governed + generic research access verified
├── 23 packaged/source-field but deliberately unresolved
└── 59 raw-only route-discovery/raw-routing work
```

Controlled promotion manifests:

- `data/team_match_semantic_promotion_batch_v1.json`;
- `data/team_match_semantic_promotion_batch_v2.json`;
- `data/team_match_semantic_promotion_batch_v3.json`;
- `data/team_match_semantic_promotion_batch_v4.json`;
- `data/team_match_semantic_promotion_batch_v5.json`;
- `data/team_match_semantic_promotion_batch_v6.json`.

### Remaining 23 packaged fields

```text
attFreekickPost
attIboxOwnGoal
attLgCentre
attLgLeft
attLgRight
attOboxOwnGoal
attemptsIbox
attemptsObox
expectedGoalsFreekick
expectedGoalsOnTargetConceded
fiftyFifty
freekickTotal
keeperGoals
ptsDroppedWinningPos
ptsGainedLosingPos
putThrough
redCard
subsGoals
successfulFiftyFifty
successfulPutThrough
totalDistance
winningGoal
yellowCard
```

These are now a **residue**, not a generic semantic backlog. They fall into a small number of specific unresolved classes:

1. **overlap/reconciliation:** `redCard`, `yellowCard` versus already-governed `totalRedCard` / `totalYelCard` and card-event evidence;
2. **competition-specific:** `putThrough`, `successfulPutThrough` are documented as Bundesliga-specific and remain fail-closed for Premier League use;
3. **newer expected/physical metrics:** `expectedGoalsFreekick`, `expectedGoalsOnTargetConceded`, `totalDistance` require their appropriate modern/physical routing contracts rather than legacy-name promotion;
4. **legacy fields lacking exact definition in the current reference:** long-range shot zones, own-goal shot-location fields, `attFreekickPost`, `freekickTotal`, `fiftyFifty`, `successfulFiftyFifty`, `keeperGoals`, `subsGoals`, `winningGoal`, and points-state metrics;
5. **inside/outside-box aggregate attempts:** `attemptsIbox` / `attemptsObox` remain held until their exact aggregate representation is directly established rather than inferred from related shot-location families.

The 59 raw-only team statistics remain a separate routing problem. Fuzzy name similarity is discovery evidence only and must not establish equivalence.

## Remaining 123 football/match paths — natural-grain industrialisation

The 123 football paths outside the team-statistical block were triaged as:

- 58 Events;
- 10 Managers;
- 17 Match Context;
- 16 Player Lineup Context;
- 6 Team Lineup Context;
- 16 Team-Match Context.

Key architectural rule:

> **123 raw paths do not imply 123 independent analytical variables.**

Goal/card/substitution attributes form coherent event objects. Lineup identity, role, formation, manager and match context likewise belong at their natural grains.

## Fixture Event & Tactical Context — archive-wide proven

`fixture_context_research.py` connects preserved PulseLive evidence to verified fixture/team/player relationships and source-native event/lineup normalisation.

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

Unresolved identities remain explicit and are never guessed. Proof manifest: `data/fixture_context_research_capability_v1.json`.

## Capability-led acquisition rule

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

Do not browse providers merely for the biggest field list.

## Immediate objective

> **Preserve the verified 167/167 team-match generic-access baseline, resolve the 23-field packaged residue only through appropriate evidence/reconciliation routes, continue routing the 59 raw-only team-stat paths, and consume the proven fixture event/tactical-context seam through shared Matchday and Opposition analytical services.**

## Immediate execution sequence

1. **Resolve the 23-field residue by exception class, not another generic promotion queue.** Reconcile card overlaps against aggregates/events; keep Bundesliga-specific fields excluded; route expected/physical metrics through their dedicated contracts; seek direct definitions for the remaining legacy fields.
2. **Continue raw-only route discovery for the 59.** Distinguish identity aliases from statistics, test exact equivalence only with direct evidence, and retain unresolved paths as unresolved.
3. **Consume fixture context through shared analytical services.** Preserve Goal/Card/Substitution objects and lineup/formation/manager context at natural grain; add game-state/tactical derivations only through explicit governed rules.
4. **Prototype Player Scouting, Team Scouting and Opposition Report information hierarchies** using governed evidence only.
5. **Refine Matchday into Fixture Intelligence** around matchup questions, provenance, sample context and uncertainty.
6. **Score demonstrated capability gaps** before supplementary source acquisition.

## Non-negotiables

- Never manufacture semantic equivalence from field-name similarity.
- Never convert source blanks to zero without concept-specific audited approval.
- Never collapse raw source path → source field → canonical variable into one layer.
- Never force event/tactical objects through a scalar-variable interface merely for uniformity.
- Never let product surfaces invent independent definitions of governed football concepts.
