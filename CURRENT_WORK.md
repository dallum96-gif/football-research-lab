# Current Work — Football Research Laboratory

**Last updated:** 15 September 2026  
**Checkpoint:** `PLAYER_PROFILE_POSITIONAL_RADARS_V1`

For documentation-governance rules see `FRL_DOCUMENTATION_SYNC_CONTRACT.md` and `data/frl_documentation_state_v1.json`. The dated implementation records for the current Player Profile line are `FRL_PLAYER_PROFILE_UNIVERSAL_FOUNDATION_V1_2026-09-15.md` and `FRL_PLAYER_PROFILE_POSITIONAL_RADARS_V1_2026-09-15.md`. Earlier source-capability work remains historical evidence in `FRL_PLAYER_PROFILE_SOURCE_CAPABILITY_AUDIT_2026-09-14.md`; repository reconciliation context remains in `FRL_REPOSITORY_RECONCILIATION_2026-09-13.md`.

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

Its relevant tracked head for this Player Profile work remains:

`11a42f68cf7c4c0eab2b1ea0286cddf3337cbda3`

Draft PR **#54** carries the Player Profile foundation and positional-radar candidate on:

`feat/player-profile-universal-foundation-v1`

PR #54 targets `design/bet-builder-reference-v1`, not stable `main`. It remains a **draft integration candidate** rather than stable integrated state.

Daniel's Windows working state has now been inspected. The normal working copy is on `design/bet-builder-reference-v1` at the same `11a42f68...` tracked base, with substantial newer tracked and untracked local product work. It was externally safety-snapshotted at:

`C:\Users\dlall\football_database\frl-local-safety-20260915-215837`

An isolated reconciliation worktree was created at:

`C:\Users\dlall\football_database\frl-player-profile-reconcile`

The overlap audit found no path collision between the tracked PR #54 Player Profile changes and Daniel's local tracked/untracked product work. The original Windows working copy remains separate and must not be destructively reset, rebased or overwritten.

## Active product phase

The Player Profile has crossed two related boundaries:

1. the Ødegaard first-draft page remains the **universal visual/profile composition reference** while identity, biography, club context, participation provenance and portrait identity are governed underneath it;
2. the analytical rail is now position-aware, with separately governed six-axis templates for **GKP, DEF, MID and FWD**.

Player Profile is intentionally a **current-state surface**. The hero no longer exposes a season selector. Prior-season/career exploration belongs in the separate **History** view, which retains governed season-specific route identities where they differ.

The Player Profile milestone did not redesign the global shell, primary/secondary navigation, shared page header, global tokens or AppShell.

## Current visual direction

The intended FRL visual language remains **dark, premium, editorial and football-first**:

- near-black / charcoal structural surfaces;
- warm ivory / cream primary text;
- muted greys for secondary hierarchy;
- restrained coral/orange as the main brand/action emphasis;
- green/olive used semantically or as a supporting signal rather than default decoration;
- typography, spacing, thin rules and composition carry more of the design than dashboard chrome.

The approved Player Profile body/portrait composition is preserved. Positional-radar work changes analytical content and copy inside the existing right-hand rail rather than redesigning the page.

## Preserved source capability — standing validated foundation

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

## Player Profile source representation

The governed Profile source is pinned to:

`imadeddine-belkat/Premier-League-Stats@115d889df4e2efab5e7c1d8ca0f3ca86ecfd2ae6`

The Profile projection is:

- runtime module: `player_profile_source_projection.py`;
- materialised evidence: `data/player_profile_source_stats_v1.csv`;
- provenance: `data/player_profile_source_stats_v1.metadata.json`;
- projection version: `PLAYER_PROFILE_SOURCE_STATS_V1`;
- source grain: Player-Season;
- seasons: 2016/17 through 2026/27;
- 2026/27 source rows: 450;
- metadata schema: `1.2.0`.

Profile participation preserves source-native `gamesPlayed`, `starts` and `timePlayed`. When all three are observed, the Profile uses them as one block. If any member is unavailable, the Profile falls back as one block to the governed FPL player-fixture aggregate; it does not construct a hybrid participation row.

All per-90 Profile dimensions divide a source-native numerator by that same Player-Season row's `timePlayed`. Ratio metrics use numerator and denominator fields from the same Player-Season row. Source blanks remain unavailable rather than becoming zero.

For the pinned current checkpoint, Ødegaard is **3 appearances, 3 starts, 224 Player-Season minutes**. His Forward passing value remains **45 / 224 × 90 = 18.0804 per 90**. The older 145-minute tracked FPL aggregate is not displayed as current Profile evidence.

## Identity, biography and club context

### Identity and navigation

- FPL/seasonal route identity, Player-Match/research identity and Player-Season/portrait identity remain distinct.
- Current Ødegaard route `2026-27/184029` and historical route `2024-25/13` both resolve to research identity `player_match:547410` while retaining their correct seasonal route codes.
- History navigation uses each season's actual route code.
- Portrait lookup uses verified portrait/source identity rather than assuming route code = image ID.
- unresolved identity fails closed rather than falling back to fuzzy matching.

### Biography

Runtime biography uses packaged evidence only:

- `data/player_profile_biography_v1.csv`;
- `data/player_profile_biography_v1.metadata.json`;
- materialiser: `scripts/materialize_player_profile_biography.py`.

The product no longer requires Daniel's external local source checkout at runtime. Verified source-player identity is the join authority; display-name agreement is corroboration, not an identity join.

### Club context

- single-club seasons resolve directly;
- multi-club seasons use the latest unique canonical fixture observation where available;
- unresolved multi-club primary context is withheld rather than guessed.

## Position-specific Player Profile radars

Checkpoint:

`PLAYER_PROFILE_POSITIONAL_RADARS_V1`

The page composition is universal; the analytical football concepts are position-specific.

### GKP — `GKP_PROFILE_V1`

- Shot stopping — `(expectedGoalsOnTargetConceded - goalsConceded) / timePlayed * 90`
- Save rate — `savesMade / (savesMade + goalsConceded)`
- Save volume — `savesMade / timePlayed * 90`
- Claiming — `(catches + punches) / timePlayed * 90`
- Smothering — `goalkeeperSmother / timePlayed * 90`
- Distribution — `gkSuccessfulDistribution / (gkSuccessfulDistribution + gkUnsuccessfulDistribution)`

### DEF — `DEF_PROFILE_V1`

- Aerial duels — `aerialDuelsWon / aerialDuels`
- Tackling — `totalTackles / timePlayed * 90`
- Interceptions — `interceptions / timePlayed * 90`
- Clearances — `totalClearances / timePlayed * 90`
- Recoveries — `recoveries / timePlayed * 90`
- Progression — `forwardPasses / timePlayed * 90`

The universal DEF Tackling concept deliberately uses total tackle volume rather than requiring `tacklesWon`; this removed a false-looking N/A for Gabriel while preserving source semantics.

### MID — `MID_PROFILE_V1`

- Goal threat — `expectedGoals / timePlayed * 90`
- Chance creation — `expectedAssists / timePlayed * 90`
- Advanced passing — `successfulPassesOppositionHalf / timePlayed * 90`
- Forward passing — `forwardPasses / timePlayed * 90`
- Recoveries — `recoveries / timePlayed * 90`
- Ball winning — `tacklesWon / timePlayed * 90`

### FWD — `FWD_PROFILE_V1`

- Goal threat — `expectedGoals / timePlayed * 90`
- Scoring — `goals / timePlayed * 90`
- Chance creation — `expectedAssists / timePlayed * 90`
- Shot volume — `totalShots / timePlayed * 90`
- Box presence — `totalTouchesInOppositionBox / timePlayed * 90`
- Shot accuracy — `shotsOnTargetIncGoals / totalShots`

Shot accuracy replaced the initial `successfulDribbles / 90` 1v1 axis. A universal FWD cohort contains both central and wide forwards, so shot accuracy is more generally applicable while still using same-row source-native evidence. The materialised projection now explicitly includes `shotsOnTargetIncGoals`; 2026/27 has 140 observed player rows for that field versus 204 observed `totalShots` rows.

## Current Profile time scope

The Profile hero represents **now**.

- the hero season selector is removed;
- the current route still carries the living-season identifier as part of FRL's route contract;
- the History view remains the deliberate place for career/previous-season exploration;
- cross-season identity relationships remain governed even though the hero no longer advertises season switching.

Do not reintroduce a season dropdown into the hero simply because historical data exists.

## Validation status

The authoritative feature run for the positional-radar/current-state checkpoint executed from feature commit `31c98d6d2988a9a6a44137e0a367040b167cfe8a` and completed successfully. GitHub Actions then materialised the updated governed evidence at:

`a2e3ecd` — `data: materialize player profile foundation evidence`

Current gates:

- pinned upstream checkout: PASS;
- Player Profile source materialisation: PASS;
- packaged biography materialisation: PASS;
- changed Python module compile: PASS;
- approved Profile CSS/portrait composition guard: PASS;
- focused Player Profile regression suite: **29 passed**;
- four-position acceptance matrix: PASS;
- GKP representative David Raya: **6/6 observed dimensions**;
- DEF representative Gabriel: **6/6 observed dimensions**;
- MID representative Martin Ødegaard: **6/6 observed dimensions**;
- FWD representative Kai Havertz: **6/6 observed dimensions**;
- current Ødegaard participation: **3 / 3 / 224** from `PLAYER_PROFILE_SOURCE_STATS_V1`;
- low-minute MID fail-closed threshold case: PASS;
- History route identity continuity (`2024-25/13` Ødegaard): PASS;
- season-selector-absent current-state product contract: PASS;
- Next.js TypeScript check: PASS;
- Next.js production build: PASS;
- documentation sync: PASS.

Two pre-existing/base observations remain outside this milestone:

1. `api/frl_api.py` on the tracked target/reference branch imports `team_records_materialization`, but that module is absent from tracked GitHub. Daniel's Windows tree does contain an untracked local copy. Full clean API integration therefore still needs deliberate reconciliation rather than invention inside Player Profile.
2. `npm install` reports three critical-severity dependency vulnerabilities in the existing frontend dependency graph. Typecheck/build pass; dependency-security review remains separate technical debt.

The Next development screenshots also showed a red **“1 Issue”** dev indicator. Production build is green, but that development-runtime issue has not yet been inspected and remains an explicit visual/runtime follow-up before final integration.

## Team State, forecasting and BetBuilder evidence

`Team State V1` remains a pre-fixture research object with recent-5, recent-10, season-to-date and prior-season windows. Historical source-publication-time equivalence remains explicitly unproven.

Adaptive Dixon-Coles V1 remains the frozen **experimental forecasting control**. It is not a trusted production model and no betting-market edge is claimed.

The Head-to-Head / Matchday / BetBuilder interpretation rule remains:

> **`evidence_index` is descriptive evidence synthesis, not a calibrated betting probability.**

Football evidence, model output, market price and staking/strategy remain distinct layers.

## Immediate objective

> **Visually review the completed GKP / DEF / MID / FWD Profile radars in the isolated reconciliation worktree, confirm the season selector is absent and investigate the Next development “1 Issue” indicator before deciding whether draft PR #54 is ready for integration.**

After that:

1. reconcile any final tracked PR changes with Daniel's protected local Windows state without destructive cleanup;
2. resolve or explicitly carry the target-branch `team_records_materialization` integration blocker;
3. keep the approved Player Profile body/portrait composition fixed while stress-testing other clubs and portrait availability;
4. separately audit broader Player Stats/rich Player-Match denominator provenance rather than silently inheriting the Profile rules;
5. continue Fixture Intelligence, Team analytical profiles, Rankings/Compare, Research Explorer and controlled modelling from the governed evidence layer.

## Non-negotiables

- Never manufacture semantic equivalence from field-name similarity.
- Never convert source blanks to zero without concept-specific audited approval.
- Never collapse route ID, Player-Match identity, Player-Season identity and portrait identity into one key by coincidence.
- Never mix a source-native numerator with a different representation's denominator without explicit equivalence proof.
- Never guess a primary club in an unresolved multi-club season.
- Never use display-name/fuzzy matching as a substitute for a governed identity relationship.
- Never mechanically reuse one position's analytical concepts for another position merely for visual uniformity.
- Never reintroduce Profile hero season switching without an explicit product decision; History owns previous seasons at this checkpoint.
- Never let product surfaces invent independent definitions of governed football concepts.
- Never present descriptive BetBuilder evidence as calibrated probability or guaranteed betting return.
- Never treat draft PR #54, the experimental reference branch, or Daniel's local working state as stable integrated `main` without explicit validation and integration evidence.
