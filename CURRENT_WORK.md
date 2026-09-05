# Current Work — Football Research Laboratory

**Last updated:** 5 September 2026  
**Checkpoint:** `SOURCE_UNIVERSE_TEAM_AND_PLAYER_PROVEN_V1`

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

## Immediate objective

> **Consume the now-routed team and player source universes through shared FRL research/product services. Let analytical/product demand determine which retained/restricted/raw-native representations need deeper semantic promotion next.**

Near-term work should increasingly use these capabilities in Team Scouting, Player Scouting, Opposition Report, Matchday / Fixture Intelligence, Rankings and Research Explorer rather than resuming mass field-by-field promotion without a concrete analytical need.

## Non-negotiables

- Never manufacture semantic equivalence from field-name similarity.
- Never convert source blanks to zero without concept-specific audited approval.
- Never collapse raw source path → source field → canonical variable into one layer.
- Never discard a legitimate variable solely because coverage begins later than 2016/17.
- Never force event/tactical objects through a scalar-variable interface merely for uniformity.
- Never let product surfaces invent independent definitions of governed football concepts.
