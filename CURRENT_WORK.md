# Current Work — Football Research Laboratory

**Last updated:** 5 September 2026  
**Checkpoint:** `HEAD_TO_HEAD_BETBUILDER_V1`

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

The 553-path universe remains the master PulseLive source/evidence universe.

## Team-match source universe — routed and governed

Initial reconciliation began at:

- 26 exposed;
- 164 packaged/source-field uncatalogued;
- 59 raw-only.

The source-universe milestone gate on 5 September 2026 proved:

```text
249 TEAM-MATCH STATISTICAL PATHS
├── 176 canonical/governed + generic access verified
├──   8 governed retained source fields
├──   6 governed restricted source fields
└──  59 raw-only source representations with generic preserved-snapshot route
```

Validation result:

- **Pytest: PASS across 12 milestone modules**;
- packaged/governed: **176 exposed / 8 retained / 6 restricted / 0 uncatalogued**;
- canonical generic access: **176/176 PASS**;
- raw-only pathway: **59/59 ROUTED through preserved PulseLive stats**;
- documentation sync: **PASS**.

The 59 raw-only fields are no longer a pathway-discovery backlog. They remain source-native evidence until semantic promotion is justified, but every one has a governed research route.

Standing missingness rule:

> **A source blank is missing by default. Structural zero requires specific evidence for that concept, representation and period.**

## Player-Match source universe — exhaustively accounted

The decade-wide Player-Match schema union across 2016/17–2025/26 contains **86 observed source fields**.

The same source-universe milestone gate proved:

```text
86 PLAYER-MATCH SOURCE FIELDS
├── 81 exposed for generic research access
├──  4 retained metadata/source-context fields
└──  1 restricted duplicate CSV column

0 observed fields uncatalogued
81/81 exposed fields generic-access PASS
```

Partial-period capability is explicitly preserved rather than discarded. A legitimate field may be exposed even when it exists only in later seasons; outside its observed seasons it remains unavailable/missing and is never coerced to zero.

Examples include expected metrics, carry/progression fields and the 2025/26 physical-distance fields.

A stale Player-Match dribble route was also corrected: `successfulDribbles` / `unsuccessfulDribbles` are not advertised as native Player-Match source fields. Rich Player-Match take-on capability uses the observed `totalContest` / `wonContest` representation, with unsuccessful contests derived from attempts minus successful contests.

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

## Team State and forecasting — first controlled model progression

`Team State V1` is available as a pre-fixture research object with recent-5, recent-10, season-to-date and prior-season windows. Its event-time cutoff is the target fixture kickoff; historical source-publication-time equivalence remains explicitly not yet proven.

The first controlled forecasting challenger is complete:

- frozen Poisson V1 control;
- Adaptive Dixon-Coles V1 selected only on 2017/18–2020/21 development seasons;
- untouched holdout: 2021/22–2025/26;
- Adaptive DC coverage: **1,900/1,900** completed holdout fixtures;
- Poisson V1 coverage: **1,360/1,900**;
- common-population log loss: **1.065515 Poisson / 1.013105 Adaptive DC**;
- common-population Brier: **0.638726 / 0.606504**;
- common-population accuracy: **47.43% / 50.51%**;
- paired log-loss improvement: **+0.052411**.

Robustness closeout strengthened the result:

- Adaptive DC improved log loss in **all five holdout seasons**;
- paired bootstrap 95% interval: **+0.031951 to +0.072532**;
- the Dixon-Coles low-score `rho` correction itself contributed only about **+0.000334** log-loss improvement, so the useful gain is predominantly the adaptive time-varying strength system;
- control status: `CONTROL_FREEZE_SUPPORTED_FOR_NEXT_EXPERIMENT`.

Adaptive DC is therefore the **frozen experimental forecasting control** for the next Team State incremental-information experiment. It is not yet a trusted production model and no betting-market edge is claimed.

## Head-to-Head + BetBuilder Stat Pack V1 — visible product milestone

The first combined analytical matchup product is now implemented on `model/poisson-v1`.

Route:

`/head-to-head/{season}/{fixtureId}`

API:

`/api/v1/head-to-head/{season}/{fixture_id}`

The page is deliberately organised around the workflow:

**fixture → BetBuilder evidence → analytical team profiles → independent model picture → player watchlists**

V1 BetBuilder evidence uses ten fixed, pre-specified team thresholds — five for each side:

- 1+ goal;
- 10+ shots;
- 4+ shots on target;
- 4+ corners;
- 2+ yellow cards.

Each entry pairs:

1. the selected team's recent pre-match hit frequency; and
2. the opponent's recent allowance frequency for the same governed statistic.

The resulting `evidence_index` is explicitly descriptive and **must not be presented as a calibrated betting probability**. Thresholds were fixed before target-match evaluation and are not selected after seeing results.

The same page also exposes:

- recent analytical profiles for both teams from governed pre-kickoff team evidence;
- the frozen Adaptive Dixon-Coles control as a separate probability layer;
- expected goals and leading exact-score probabilities from the forecasting control;
- current-season player watchlists from governed FPL evidence;
- explicit early-season and coverage limitations;
- direct navigation from the existing Matchday workspace.

The Head-to-Head route deliberately avoids the legacy external Player-Match filesystem dependency required by full fixture-detail enrichment and runs from repository-contained governed evidence. The older Matchday fixture-detail path still contains a hard-coded local `Premier-League-Stats` root in `match_stats.py`; this is now explicit portability debt rather than a hidden dependency of Head-to-Head V1.

Validation for this milestone on GitHub Actions:

- **17 Python / regression tests: PASS**;
- **Next.js TypeScript check: PASS**;
- **Next.js production build: PASS**.

## Immediate objective

> **Develop Analytical Profile + Head-to-Head as complementary views over one governed evidence layer, with the BetBuilder Stat Pack at the centre of fixture-specific synthesis.**

Near-term sequence:

1. deepen the analytical team profile beyond the initial recent-match slice using the now-routed 249-field team universe;
2. expand Head-to-Head from fixed V1 thresholds into richer attack-v-opponent-defence evidence while preserving exact coverage and provenance;
3. promote fouls/cards, set-piece and player-market evidence only where source semantics support it;
4. remove the remaining hard-coded local Player-Match filesystem dependency from the legacy Matchday enrichment path;
5. run the pre-registered Adaptive DC + Team State forecasting experiment without allowing model work to displace the scouting/opposition product programme.

Team Scouting, Player Scouting, Opposition Report, Matchday / Fixture Intelligence, Rankings and Research Explorer remain active destinations for the same source universe rather than separate statistical systems.

## Non-negotiables

- Never manufacture semantic equivalence from field-name similarity.
- Never convert source blanks to zero without concept-specific audited approval.
- Never collapse raw source path → source field → canonical variable into one layer.
- Never discard a legitimate variable solely because coverage begins later than 2016/17.
- Never force event/tactical objects through a scalar-variable interface merely for uniformity.
- Never let product surfaces invent independent definitions of governed football concepts.
- Never present a descriptive BetBuilder evidence index as a calibrated probability or guaranteed betting return.
