# Current Work — Football Research Laboratory

**Last updated:** 15 September 2026  
**Checkpoint:** `PLAYER_PROFILE_UNIVERSAL_FOUNDATION_V1`

For documentation-governance rules see `FRL_DOCUMENTATION_SYNC_CONTRACT.md` and `data/frl_documentation_state_v1.json`. The dated implementation record for this checkpoint is `FRL_PLAYER_PROFILE_UNIVERSAL_FOUNDATION_V1_2026-09-15.md`. Earlier Player Profile source-capability work remains historical evidence in `FRL_PLAYER_PROFILE_SOURCE_CAPABILITY_AUDIT_2026-09-14.md`; repository reconciliation context remains in `FRL_REPOSITORY_RECONCILIATION_2026-09-13.md`.

## Current platform state

FRL is a governed football research and modelling environment. The active frontend is **Next.js + React**, with **FastAPI** as the frontend-facing API. Python remains authoritative for source routing, identity, temporal semantics, provenance, analytical definitions and modelling. Streamlit is legacy/reference only.

Standing rules remain unchanged:

- source identifiers are evidence, not universal canonical identifiers;
- canonical fixture/team/player relationships must be explicit and governed;
- preserved source-native evidence retains provenance and release context;
- temporal/as-of reconstruction must remain explicit;
- missing/partial/unresolved/unavailable states are not silently converted to zero;
- derived rates must use a semantically justified denominator from a compatible representation;
- populations/cohorts, tie rules and percentile rules must be explicit;
- product surfaces consume governed analytical services rather than inventing browser-side football semantics.

The durable research North Star remains `FRL_MASTER_PROMPT.md`. The durable product architecture remains `FRL_PRODUCT_NORTH_STAR_AND_EXPERIENCE_ARCHITECTURE_V1.md`.

## Repository / branch state

Stable `main` remains at:

`0626878838b0734b7df8d79f966e814db75a61ed`

The active product/reference branch remains:

`design/bet-builder-reference-v1`

Draft PR: **#53 — UI: premium FRL shell, Matchday builder and Fixtures reference design**.

The Player Profile industrialisation work is isolated on:

`feat/player-profile-universal-foundation-v1`

That feature branch was created from tracked `design/bet-builder-reference-v1` head `11a42f68cf7c4c0eab2b1ea0286cddf3337cbda3`. The target branch remained at that commit during this milestone. The feature branch is a **validated integration candidate for the experimental/reference branch**, not stable integrated state.

Important boundary: repository state described here is tracked remote state. Daniel's live local Windows working tree may contain newer committed or uncommitted work and has not been inspected by this milestone. Do not merge/rebase/destructively reconcile it by assumption.

## Active product phase

FRL remains in a substantial product/reference-design phase over the governed evidence layer. Current work spans Fixtures/Matchday, Team Profile/Team Stats, Player Profile/Player Stats, Rankings/Compare and controlled modelling.

The Player Profile has now crossed an important boundary: the Ødegaard first-draft page is retained as the **universal visual/profile composition reference**, while the evidence path beneath it has been industrialised so that route identity, research identity, Player-Season identity, portrait identity, club context, biography and analytical denominator are no longer assumed to be the same thing.

This does **not** mean every positional analytical profile is solved. MID V1 is governed; DEF/FWD/GKP comparison templates remain future research/governance work.

## Current visual direction

The intended FRL visual language remains **dark, premium, editorial and football-first**.

Current direction:

- near-black / charcoal structural surfaces;
- warm ivory / cream primary text;
- muted greys for secondary hierarchy;
- restrained coral/orange as the main brand/action emphasis;
- green/olive used semantically or as a supporting signal rather than default decoration;
- no lime-green visual language;
- typography, spacing, thin rules and composition should carry more of the design than dashboard chrome.

The Player Profile milestone did not modify the global shell, primary/secondary navigation, shared page header, global tokens or AppShell. The Ødegaard profile body remains the visual reference for the universal Player Profile composition.

## Preserved source capability — validated foundation

The preserved PulseLive archive contains **3,800 Premier League fixture snapshots** across 2016/17–2025/26.

Master preserved source universe:

```text
553 MASTER SNAPSHOTTED RAW SOURCE PATHS
├── 181 capture / provenance paths
└── 372 football / match paths
    ├── 249 team-match statistical paths
    └── 123 other football / match paths
```

The validated team-match milestone remains:

```text
249 TEAM-MATCH STATISTICAL PATHS
├── 176 canonical/governed + generic access verified
├──   8 governed retained source fields
├──   6 governed restricted source fields
└──  59 raw-only source representations with governed preserved-snapshot route
```

The Player-Match source universe remains exhaustively accounted:

```text
86 PLAYER-MATCH SOURCE FIELDS
├── 81 exposed for generic research access
├──  4 retained metadata/source-context fields
└──  1 restricted duplicate CSV column
```

Standing missingness rule:

> **A source blank is missing by default. Structural zero requires specific evidence for that concept, representation and period.**

## 2026/27 living-season evidence

The latest formally documented living-season source used by the Player Profile milestone is pinned upstream evidence from `imadeddine-belkat/Premier-League-Stats` at:

`115d889df4e2efab5e7c1d8ca0f3ca86ecfd2ae6`

The last formally validated broader rich Player capability checkpoint remains:

- 387 participating players with minutes greater than zero;
- 79/83 Player product capabilities runtime-supported through GW1–3;
- unavailable quartet: `ball_carries`, `progressive_carries`, `progressive_carry_distance`, `total_progression`.

The Player Profile milestone does not reinterpret take-ons as carrying and does not promote missing carrying evidence by proxy.

## Player Profile universal foundation

Checkpoint:

`PLAYER_PROFILE_UNIVERSAL_FOUNDATION_V1`

The Profile now has an explicit relationship seam instead of treating a route ID as a universal player key.

### Identity and navigation

- FPL/seasonal route identity, Player-Match/research identity and Player-Season/portrait identity remain distinct.
- Current Ødegaard route `2026-27/184029` and historical route `2024-25/13` both resolve to research identity `player_match:547410` while retaining their correct seasonal route codes.
- season/history navigation uses each season option's actual route code;
- portrait lookup uses the verified portrait/source identity rather than assuming the route code is the image ID;
- unresolved identity remains explicit and fails closed rather than falling back to fuzzy matching.

### One Player-Season Profile representation

The governed Player Profile projection is:

- runtime module: `player_profile_source_projection.py`;
- materialised evidence: `data/player_profile_source_stats_v1.csv`;
- provenance: `data/player_profile_source_stats_v1.metadata.json`;
- source grain: Player-Season;
- seasons: 2016/17 through 2026/27;
- 2026/27 source rows: 450;
- pinned upstream release: `115d889df4e2efab5e7c1d8ca0f3ca86ecfd2ae6`.

Profile participation preserves source-native `gamesPlayed`, `starts` and `timePlayed`. When all three are observed, the Profile uses them as one block. If any member of that block is unavailable, the Profile falls back as one block to the existing FPL player-fixture aggregate; it does not construct a hybrid participation row.

All six MID V1 per-90 dimensions use source-native Player-Season totals divided by that same Player-Season row's `timePlayed`:

- Goal threat — `expectedGoals`;
- Chance creation — `expectedAssists`;
- Advanced passing — `successfulPassesOppositionHalf`;
- Forward passing — `forwardPasses`;
- Recoveries — `recoveries`;
- Ball winning — `tacklesWon`.

For the pinned 2026/27 checkpoint, Ødegaard is **3 appearances, 3 starts, 224 Player-Season minutes**. His Forward passing value is **45 / 224 × 90 = 18.0804 per 90**. The previously surfaced 145-minute tracked FPL aggregate is stale for this Profile checkpoint and is not mixed into the source-native Profile representation.

This correction is deliberately scoped to Player Profile. It does not silently redefine every existing Player Stats/rich Player-Match per-90 calculation; broader denominator-provenance review remains separate work.

### Biography

Runtime biography now reads only the packaged projection:

- `data/player_profile_biography_v1.csv`;
- `data/player_profile_biography_v1.metadata.json`;
- materialiser: `scripts/materialize_player_profile_biography.py`.

The product no longer requires Daniel's local `C:\Users\...` upstream checkout at runtime. A verified Profile source-player identity is the join authority; display-name agreement is corroborative rather than a second join key. No fuzzy identity join was introduced. Conflicting stable biographical facts for the same verified source identity are withheld.

### Club context

- single-club seasons resolve directly;
- multi-club seasons use the latest unique canonical fixture observation where available;
- if temporal evidence cannot resolve the current/primary club, the Profile withholds it rather than choosing alphabetically or guessing.

Transfer-context regressions cover latest-club resolution and unresolved multi-club withholding.

### Position-specific analysis

The page/profile composition is universal, but analytical templates are position-specific.

- MID V1: governed and available subject to minutes/coverage/identity;
- DEF/FWD/GKP: universal profile remains available, comparative template deliberately unavailable pending separate research and governance.

Do not mechanically reuse Ødegaard's six-axis midfielder template for other positions.

## Validation status

The feature workflow `Player Profile Universal Foundation` passed on commit `ba11bb1fcfc1242f130e2d32bd91dc20320d0438`, after which GitHub Actions materialised the governed evidence at `11b27f726d8869f8da7c5da58fd3d0e05e2a4cc7`.

Current implementation gates at that checkpoint:

- pinned upstream checkout: PASS;
- Player Profile source materialisation: PASS;
- packaged biography materialisation: PASS;
- changed Python module compile: PASS;
- focused Player Profile regression suite: **26 passed**;
- universal acceptance matrix: PASS;
- historical/current Ødegaard identity continuity: PASS;
- current Ødegaard participation contract: **3 / 3 / 224** from `PLAYER_PROFILE_SOURCE_STATS_V1`;
- six-axis MID comparison: PASS;
- Next.js TypeScript check: PASS;
- Next.js production build: PASS.

The acceptance matrix covers current Ødegaard, historical-route Ødegaard, Gabriel, a low-minute MID (Eze), David Raya and Kai Havertz. It verifies non-MID profiles remain usable while MID-only comparison is withheld.

Validation also surfaced two external/base-state observations that are **not silently repaired inside this milestone**:

1. `api/frl_api.py` on the target/reference branch imports `team_records_materialization`, but the tracked module is absent. Full `api.player_stats` package collection therefore remains a target-branch integration blocker outside Player Profile scope.
2. `npm install` reports three critical-severity dependency vulnerabilities in the existing frontend dependency graph. Typecheck/build still pass; dependency-security review remains separate technical debt rather than being hidden by this feature.

## Team State and forecasting

`Team State V1` remains available as a pre-fixture research object with recent-5, recent-10, season-to-date and prior-season windows. Historical source-publication-time equivalence remains explicitly unproven.

Adaptive Dixon-Coles V1 remains the frozen **experimental forecasting control** from the earlier controlled evaluation. It is not a trusted production model and no betting-market edge is claimed.

## Head-to-Head / Matchday / BetBuilder evidence

The governed Head-to-Head and BetBuilder work remains part of the active product programme.

The key interpretation rule is unchanged:

> **`evidence_index` is descriptive evidence synthesis, not a calibrated betting probability.**

Football evidence, model output, market price and staking/strategy remain distinct layers.

## Immediate objective

> **Finish documentation and PR closeout for `PLAYER_PROFILE_UNIVERSAL_FOUNDATION_V1`, then review it as an integration candidate into `design/bet-builder-reference-v1` without assuming Daniel's local Windows state is identical to tracked GitHub.**

After that:

1. reconcile the feature candidate with any newer local-only Player Profile work before merge;
2. resolve or explicitly carry the target-branch API import blocker;
3. keep Ødegaard's body composition as the Player Profile visual reference while stress-testing it across clubs/portrait availability;
4. research and govern DEF/FWD/GKP analytical templates independently;
5. separately audit broader Player Stats/rich Player-Match denominator provenance rather than silently inheriting the Profile fix;
6. continue Fixture Intelligence, Team analytical profiles, Rankings/Compare, Research Explorer and controlled modelling from the governed evidence layer.

## Non-negotiables

- Never manufacture semantic equivalence from field-name similarity.
- Never convert source blanks to zero without concept-specific audited approval.
- Never collapse route ID, Player-Match identity, Player-Season identity and portrait identity into one key by coincidence.
- Never mix a source-native numerator with a different representation's denominator without explicit equivalence proof.
- Never guess a primary club in an unresolved multi-club season.
- Never use display-name/fuzzy matching as a substitute for a governed identity relationship.
- Never force a MID analytical template onto DEF/FWD/GKP merely for visual uniformity.
- Never let product surfaces invent independent definitions of governed football concepts.
- Never present descriptive BetBuilder evidence as calibrated probability or guaranteed betting return.
- Never treat this feature branch, PR #53, or uninspected local work as stable integrated `main` state without explicit validation and integration evidence.
