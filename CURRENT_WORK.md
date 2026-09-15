# Current Work — Football Research Laboratory

**Last updated:** 15 September 2026  
**Checkpoint:** `PLAYER_PROFILE_UNIVERSAL_ROLLOUT_V1`

For documentation-governance rules see `FRL_DOCUMENTATION_SYNC_CONTRACT.md` and `data/frl_documentation_state_v1.json`. The dated Player Profile records are:

- `FRL_PLAYER_PROFILE_UNIVERSAL_FOUNDATION_V1_2026-09-15.md`;
- `FRL_PLAYER_PROFILE_POSITIONAL_RADARS_V1_2026-09-15.md`;
- `FRL_PLAYER_PROFILE_UNIVERSAL_ROLLOUT_V1_2026-09-15.md`.

Earlier source-capability work remains historical evidence in `FRL_PLAYER_PROFILE_SOURCE_CAPABILITY_AUDIT_2026-09-14.md`; repository reconciliation context remains in `FRL_REPOSITORY_RECONCILIATION_2026-09-13.md`.

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

Its relevant tracked base for the Player Profile line is:

`11a42f68cf7c4c0eab2b1ea0286cddf3337cbda3`

Draft PR **#54** carries the Player Profile work on:

`feat/player-profile-universal-foundation-v1`

PR #54 targets `design/bet-builder-reference-v1`, not stable `main`. It remains a **draft integration candidate**.

Daniel's normal Windows working tree is separate, newer in multiple product areas and protected. It was externally safety-snapshotted at:

`C:\Users\dlall\football_database\frl-local-safety-20260915-215837`

The isolated reconciliation worktree is:

`C:\Users\dlall\football_database\frl-player-profile-reconcile`

The original Windows working copy must not be destructively reset, cleaned, rebased or overwritten.

## Active Player Profile phase

The Player Profile is now a validated **universal current-player surface** over the current 2026/27 Player directory.

The approved Ødegaard page remains the universal visual/profile composition reference. The page shell is universal; analytical concepts remain position-specific for **GKP, DEF, MID and FWD**.

Player Profile is intentionally a **current-state surface**:

- the hero season selector is removed;
- current routes retain the season identifier as part of the FRL route contract;
- previous-season/career exploration belongs in **History**;
- History preserves governed season-specific route identities where route IDs changed across seasons.

No global shell, AppShell, primary/secondary navigation, shared header or global token redesign is part of this milestone.

## Governed Player Profile source

The Player Profile source is pinned to:

`imadeddine-belkat/Premier-League-Stats@115d889df4e2efab5e7c1d8ca0f3ca86ecfd2ae6`

Profile projection:

- runtime: `player_profile_source_projection.py`;
- materialised evidence: `data/player_profile_source_stats_v1.csv`;
- metadata: `data/player_profile_source_stats_v1.metadata.json`;
- grain: Player-Season;
- seasons: 2016/17 through 2026/27;
- 2026/27 source rows: 450.

Per-90 Profile axes use source-native numerators divided by the same Player-Season row's `timePlayed`. Ratio axes use same-row numerator and denominator fields. Source blanks remain unavailable rather than becoming zero.

Profile participation uses source-native `gamesPlayed`, `starts` and `timePlayed` as one atomic block when all are available; otherwise it falls back as one block to the governed FPL player-fixture aggregate rather than constructing a hybrid row.

At the pinned checkpoint Ødegaard remains **3 appearances / 3 starts / 224 Player-Season minutes**. Forward passing remains **45 / 224 × 90 = 18.0804 per 90**.

## Identity, biography and club context

- seasonal route identity, Player-Match/research identity and Player-Season/portrait identity remain distinct;
- current Ødegaard `2026-27/184029` and historical Ødegaard `2024-25/13` resolve to the same research identity `player_match:547410` while retaining their correct route IDs;
- portrait lookup uses verified portrait/source identity rather than assuming route ID = portrait ID;
- packaged biography runtime uses `data/player_profile_biography_v1.csv` and its metadata rather than Daniel's external source checkout;
- multi-club context uses temporal evidence where available and withholds unresolved primary-club context rather than guessing;
- fuzzy/display-name matching is not used as a substitute for governed identity relationships.

## Position-specific analytical templates

The governed six-axis templates remain:

**GKP** — Shot stopping · Save rate · Save volume · Claiming · Smothering · Distribution  
**DEF** — Aerial duels · Tackling · Interceptions · Clearances · Recoveries · Progression  
**MID** — Goal threat · Chance creation · Advanced passing · Forward passing · Recoveries · Ball winning  
**FWD** — Goal threat · Scoring · Chance creation · Shot volume · Box presence · Shot accuracy

DEF Tackling uses `totalTackles / timePlayed * 90`. FWD Shot accuracy uses `shotsOnTargetIncGoals / totalShots`.

## Universal rollout sample-state contract

Checkpoint:

`PLAYER_PROFILE_UNIVERSAL_ROLLOUT_V1`

Every current Player directory record gets a Profile, but the strength of the statistical claim changes with evidence.

### `QUALIFIED`

- Player-Season source minutes meet the dynamic Profile threshold.
- Threshold remains 33% of maximum league minutes available so far.
- At the pinned current state, 270 minutes are available and the threshold is **90 minutes**.
- Only qualified players enter the same-position benchmark population.
- Qualified players receive formal ranks and ranked percentile profiles.

### `PROVISIONAL`

- Player has positive comparable Player-Season minutes but is below the threshold.
- Player does **not** enter the qualified benchmark population.
- Observed rates may be placed indicatively against that qualified cohort.
- Formal ranks are withheld.
- Product copy explicitly shows sample minutes, qualification threshold/progress and provisional status.
- Missing axes remain unavailable, not zero.

### `INSUFFICIENT_SAMPLE`

- Comparable positive Player-Season evidence is unavailable.
- The Player Profile remains available.
- The analytical rail says **Statistical profile pending**.
- No percentile, rank or fabricated zero is created.

No extra arbitrary 30/45-minute cutoff was added. Evidence strength is represented explicitly through the governed state and dynamic qualification threshold.

## Universal 2026/27 validation

Authoritative rollout run:

`35029496354`

Feature commit validated:

`382cee5475701cce7d2bc365875dd0623473faf9`

The validator iterated every record returned by `player_research.season_players("2026-27")`.

```text
654 CURRENT PLAYER DIRECTORY RECORDS
└── 654 PLAYER PROFILES VALIDATED
    ├── 253 QUALIFIED
    ├── 128 PROVISIONAL
    └── 273 INSUFFICIENT_SAMPLE
```

Position coverage:

```text
GKP   71
DEF  214
MID  291
FWD   78
TOTAL 654
```

At this checkpoint:

- 375 players have some comparative analytical output;
- 579 players have packaged biography evidence;
- all 654 current directory records build a governed Profile.

Representative provisional cases include Mateo Kovačić at 42 source minutes and Eberechi Eze at 59. Both are compared indicatively against the qualified MID cohort and expose no formal axis ranks.

## Validation status

The rollout run passed:

- pinned Player-Season checkout: PASS;
- Player Profile source materialisation: PASS;
- packaged biography materialisation: PASS;
- Python compile: PASS;
- approved Profile CSS/portrait composition guard: PASS;
- focused Player Profile regressions: **30 passed**;
- whole-current-player-universe validation: **654 / 654 PASS**;
- GKP/DEF/MID/FWD coverage: PASS;
- `QUALIFIED` / `PROVISIONAL` / `INSUFFICIENT_SAMPLE` invariants: PASS;
- current Ødegaard 3 / 3 / 224 contract: PASS;
- cross-season Ødegaard History route identity: PASS;
- hero season-selector-absent contract: PASS;
- Next.js TypeScript check: PASS;
- Next.js production build: PASS;
- documentation sync: PASS.

The earlier React/Next development hydration issue has been resolved. Its cause was an SVG `<title>` constructed from multiple JSX children in the radar tooltip; the tooltip is now one string child, eliminating the hydration mismatch / `destination stream closed early` error without changing radar geometry or styling.

## Known separate integration / technical debt

These are not silently absorbed into Player Profile:

1. The tracked target branch still imports `team_records_materialization` from `api/frl_api.py` while the module is absent from tracked GitHub. Daniel's Windows tree contains a local untracked copy; reconciliation remains deliberate future work.
2. `npm install` reports three critical-severity dependency vulnerabilities in the existing frontend dependency graph. Typecheck/build pass; security remediation remains separate.
3. The Players landing page can emit Next fetch-cache warnings because some Player Rankings responses exceed the 2 MB Next data-cache limit. This is separate from Player Profile and remains a performance/cache task.

## Preserved broader FRL foundation

The preserved PulseLive archive remains **3,800 Premier League fixture snapshots** across 2016/17–2025/26.

The standing source universe remains:

```text
553 MASTER SNAPSHOTTED RAW SOURCE PATHS
├── 181 capture / provenance paths
└── 372 football / match paths
    ├── 249 team-match statistical paths
    └── 123 other football / match paths
```

The Player-Match source universe remains exhaustively accounted at 86 fields: 81 generically exposed, 4 retained metadata/source-context fields and 1 restricted duplicate CSV column.

`Team State V1` remains descriptive/pre-fixture research infrastructure. Adaptive Dixon-Coles V1 remains an experimental forecasting control, not a trusted production model. BetBuilder `evidence_index` remains descriptive evidence synthesis rather than calibrated betting probability.

## Immediate objective

> **Visually review one qualified, one provisional and one insufficient-sample Player Profile in the isolated reconciliation worktree, then assess draft PR #54 for deliberate integration into `design/bet-builder-reference-v1` while preserving Daniel's newer Windows product work.**

Recommended review set:

- qualified: Martin Ødegaard `2026-27/184029`;
- provisional: Mateo Kovačić `2026-27/91651`;
- insufficient: select an actual current route from the validated universe rather than assuming a named player belongs to that state.

After that:

1. deliberately reconcile final tracked PR changes with the protected Windows state;
2. resolve or explicitly carry the `team_records_materialization` target-branch blocker;
3. separately address the >2 MB Player Rankings fetch-cache warnings;
4. separately audit broader Player Stats / rich Player-Match denominator provenance;
5. continue Fixture Intelligence, Team analytical profiles, Rankings/Compare, Research Explorer and controlled modelling from the governed evidence layer.

## Non-negotiables

- Never convert missing source evidence to zero without concept-specific proof.
- Never let provisional players contaminate qualified benchmark populations.
- Never expose formal rank language for a provisional Profile.
- Never create comparative claims for an insufficient-sample Profile.
- Never collapse route, research and portrait identities into one key by coincidence.
- Never guess unresolved primary club context.
- Never use fuzzy name matching as identity governance.
- Never mechanically reuse one position's analytical concepts for another merely for visual uniformity.
- Never reintroduce hero season switching without an explicit product decision; History owns previous seasons at this checkpoint.
- Never treat draft PR #54, the experimental reference branch or Daniel's local working state as stable integrated `main` without explicit validation and integration evidence.
