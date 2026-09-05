# Current Work — Football Research Laboratory

**Last updated:** 5 September 2026  
**Checkpoint:** `TEAM_MATCH_V7_AND_FIXTURE_CONTEXT_PROVEN_V1`

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

The durable research North Star remains `FRL_MASTER_PROMPT.md`. The active product North Star remains `FRL_PRODUCT_NORTH_STAR_AND_EXPERIENCE_ARCHITECTURE_V1.md`.

## Full-source capability hierarchy

The preserved PulseLive archive contains **3,800 Premier League fixture snapshots** across 2016/17–2025/26.

```text
553 MASTER SNAPSHOTTED RAW SOURCE PATHS
├── 181 capture / provenance paths
└── 372 football / match paths
    ├── 249 team-match statistical paths
    └── 123 other football / match paths
```

The 553-path universe remains the master source/evidence universe.

## Team-match capability — V1 through V7 verified

Initial reconciliation:

- 26 exposed;
- 164 packaged/source-field uncatalogued;
- 59 raw-only.

Verified current state after V7:

```text
249 TEAM-MATCH STATISTICAL PATHS
├── 176 governed + generic research access verified
├── 14 packaged/source-field exceptional residue
└── 59 raw-only route-discovery/raw-routing work
```

The combined local milestone gate on 5 September 2026 passed:

- **Pytest: PASS across 11 milestone test modules**;
- reconciliation: **176 exposed / 14 uncatalogued / 59 raw-only**;
- generic access: **176/176 PASS**;
- documentation sync: **PASS**.

V5–V7 demonstrated that exact source/provider definitions can be applied in coherent bulk families rather than treating every legacy field as a separate research project. Across the accelerated phase, the verified baseline moved from **64 to 176 exposed fields** without changing the missingness standard.

Standing missingness rule:

> **A source blank is missing by default. Structural zero requires specific evidence for that concept, representation and period.**

No new structural-zero rules were introduced by V5, V6 or V7.

### Remaining 14 packaged fields

```text
attOboxOwnGoal
expectedGoalsFreekick
expectedGoalsOnTargetConceded
fiftyFifty
freekickTotal
keeperGoals
putThrough
redCard
subsGoals
successfulFiftyFifty
successfulPutThrough
totalDistance
winningGoal
yellowCard
```

These are an **exception set, not a normal promotion backlog**. They include:

- expected-metric fields that belong under the expected-metric routing contract;
- duplicate/overlapping card representations requiring reconciliation against `totalRedCard` / `totalYelCard` and event evidence;
- competition-specific `putThrough` fields;
- physical/tracking data (`totalDistance`);
- a small number of legacy concepts still lacking sufficiently direct PulseLive-specific semantic evidence.

Do not spend time forcing these into the scalar exposed count merely to reach a round number.

## Fixture event & tactical context — archive-wide proven

`fixture_context_research.py` provides governed natural-grain access to fixture events and tactical context.

Archive-wide proof:

- Event route: **3,800 PASS / 0 FAIL**;
- Tactical-context route: **3,800 PASS / 0 FAIL**;
- normalised events: **50,182**;
- lineup-player rows: **145,637**;
- formation context: **7,600/7,600 team-sides**;
- manager rows: **7,728**.

Unresolved identities remain explicit and are never guessed.

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

FPL remains a distinct source family. FPL ICT Creativity must never be relabelled as detailed passing/key-pass evidence.

## Immediate objective

> **Preserve the verified 176/176 team-match baseline and use the governed capability in FRL product/research services. Treat the 14 packaged residue fields and 59 raw-only paths as exception/routing work to resume when there is a concrete analytical need.**

Near-term product work should consume the proven evidence through shared Team Scouting, Opposition Report, Matchday / Fixture Intelligence, Rankings and Research Explorer services rather than continuing promotion work for its own sake.

## Non-negotiables

- Never manufacture semantic equivalence from field-name similarity.
- Never convert source blanks to zero without concept-specific audited approval.
- Never collapse raw source path → source field → canonical variable into one layer.
- Never force event/tactical objects through a scalar-variable interface merely for uniformity.
- Never let product surfaces invent independent definitions of governed football concepts.
