# FRL Player Profile Universal Rollout V1

**Date:** 15 September 2026  
**Checkpoint:** `PLAYER_PROFILE_UNIVERSAL_ROLLOUT_V1`  
**Status:** Validated feature-branch milestone; not stable `main`

## Objective

Roll the governed current-state Player Profile out to every player in the current 2026/27 Premier League Player directory without pretending that every player's statistical sample is equally reliable.

The product rule is:

> **Every current player gets a Profile. The strength of FRL's statistical claim changes with the evidence available.**

The approved Player Profile composition remains fixed. GKP, DEF, MID and FWD keep their position-specific six-axis analytical templates. The hero remains current-state only; previous seasons remain in History.

## Governed sample states

### `QUALIFIED`

A player is qualified when their pinned Player-Season source minutes meet the dynamic Profile threshold.

- The threshold remains 33% of the maximum league minutes currently available.
- At the pinned 2026/27 checkpoint, 270 league minutes are currently available, so the threshold is 90 minutes.
- Qualified players enter the same-position benchmark population.
- Qualified players receive ranked percentiles and formal ranks.

### `PROVISIONAL`

A player is provisional when they have positive comparable Player-Season minutes but remain below the current threshold.

- Their own observed rates may be positioned indicatively against the **qualified** same-position cohort.
- They do **not** enter that benchmark population.
- Formal ranks are withheld.
- The product explicitly shows the player's sample minutes, current qualification threshold and progress toward that threshold.
- Missing axes remain unavailable rather than being plotted as zero.

This preserves useful early evidence while preventing low-minute players from contaminating the reference population or being presented as if a tiny sample carried the same evidential weight as a qualified sample.

### `INSUFFICIENT_SAMPLE`

A player is insufficient-sample when comparable positive Player-Season minutes/evidence are not available.

- The Player Profile still exists.
- Identity, biography, club context and participation remain available where evidence supports them.
- The analytical rail displays **Statistical profile pending**.
- No comparative percentile, rank or fabricated zero is created.

## Statistical contract

The benchmark is deliberately asymmetric:

- only `QUALIFIED` players enter the benchmark cohort;
- `PROVISIONAL` players are evaluated from outside that cohort;
- `INSUFFICIENT_SAMPLE` players receive no statistical comparison.

No additional arbitrary minimum such as 30 or 45 minutes was introduced. Evidence strength is instead made explicit through the governed state and the dynamic qualification progress.

All existing denominator and missingness rules remain unchanged:

- per-90 axes use the same Player-Season row's `timePlayed`;
- ratio axes use numerator and denominator from that same row;
- source blanks are unavailable, not zero;
- route identity, research identity and portrait/Player-Season identity remain distinct governed relationships.

## Product behaviour

The existing analytical rail now handles all three states.

### Qualified

The existing position-specific radar remains fully ranked.

### Provisional

The existing radar geometry is retained, but the copy is explicit:

- `Provisional [position] profile`;
- `indicative vs qualified PL [position]`;
- minutes / qualification threshold;
- percentage of threshold reached;
- `formal ranks withheld`.

SVG tooltips show indicative percentile placement only and do not expose formal rank numbers.

### Insufficient sample

The analytical rail remains present and explains that the statistical profile is pending rather than falling back to an apparently complete generic football-identity block.

## Current 2026/27 universe validation

The authoritative whole-universe validation run was GitHub Actions run `35029496354` from feature commit:

`382cee5475701cce7d2bc365875dd0623473faf9`

The validator iterated every player returned by `player_research.season_players("2026-27")` and required every record to:

1. build a Player Profile;
2. resolve to one of `GKP`, `DEF`, `MID`, `FWD`;
3. resolve to exactly one governed sample state;
4. satisfy the state-specific ranking/sample invariants.

Result:

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

- 375 players have some comparative analytical output (`QUALIFIED` or usable `PROVISIONAL` evidence);
- 579 players have packaged biography evidence;
- all 654 still have a governed Player Profile surface even when comparative evidence is insufficient.

## Representative acceptance cases

### Qualified

- Martin Ødegaard — MID — 224 source minutes — `QUALIFIED` — ranked six-axis profile.
- Gabriel dos Santos Magalhães — DEF — 270 source minutes — `QUALIFIED` — ranked six-axis profile.
- David Raya Martín — GKP — 270 source minutes — `QUALIFIED` — ranked six-axis profile.
- Kai Havertz — FWD — 258 source minutes — `QUALIFIED` — ranked six-axis profile.

Ødegaard remains **3 appearances / 3 starts / 224 Player-Season minutes** and retains the governed Forward passing calculation `45 / 224 × 90 = 18.0804`.

### Provisional

- Mateo Kovačić — MID — 42 source minutes — `PROVISIONAL` — indicative comparison, no formal ranks.
- Eberechi Eze — MID — 59 source minutes — `PROVISIONAL` — indicative comparison, no formal ranks.

The first test iteration incorrectly assumed Eze lacked comparable evidence; the test was corrected to follow the source rather than forcing a desired category.

## Validation gates

Run `35029496354` passed:

- pinned upstream Player-Season checkout;
- Player Profile source materialisation;
- packaged biography materialisation;
- Python compile;
- approved Profile CSS/portrait composition preservation gate;
- focused regression suite: **30 passed**;
- whole-current-player-universe validation: **654 / 654 profiles**;
- sample-state invariants across all 654 current records;
- TypeScript check;
- Next.js production build;
- documentation-sync gate.

The feature continues to record, rather than silently repair, the unrelated target-branch `team_records_materialization` import blocker. Existing npm dependency vulnerabilities and oversized Player Rankings fetch-cache responses also remain separate technical debt.

## Runtime correction retained

During visual review, React 19 / Next.js 16 surfaced a hydration error because the SVG radar `<title>` contained multiple JSX children. The tooltip is now constructed as one string child. This removed the hydration mismatch / `destination stream closed early` failure without changing radar geometry or Profile styling.

## Integration posture

This checkpoint lives on draft PR #54 / `feat/player-profile-universal-foundation-v1`, targeting `design/bet-builder-reference-v1`.

Stable `main` remains unchanged at `0626878838b0734b7df8d79f966e814db75a61ed`.

Daniel's normal Windows working tree remains separate and protected. The isolated reconciliation worktree remains the correct place for final visual review before any deliberate integration.

## Definition of Done — achieved on feature branch

- every current 2026/27 Player directory record builds a Profile: PASS (`654/654`);
- GKP/DEF/MID/FWD coverage: PASS;
- qualified benchmark population excludes low-minute players: PASS;
- provisional players receive useful but explicitly non-ranked analysis: PASS;
- insufficient-sample players retain useful Profiles without invented comparisons: PASS;
- missing evidence remains missing rather than zero: PASS;
- approved Profile body/portrait composition remains preserved: PASS;
- hero season selector remains absent; History owns prior seasons: PASS;
- regression/typecheck/build/documentation gates: PASS.
