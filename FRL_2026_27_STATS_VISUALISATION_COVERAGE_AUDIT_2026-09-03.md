# FRL 2026/27 Stats Visualisation Coverage Audit — 3 September 2026

## Purpose

Establish what 2026/27 player and team statistical evidence is actually available, what FRL currently governs, what the product exposes, and which apparent gaps are genuine source gaps versus unconnected source routes.

This audit follows the FRL rule that source-present, connected, governed, comparable and product-ready are distinct states. It does not promote a field merely because a similarly named value exists elsewhere.

## Current release boundary

- FRL branch: `model/poisson-v1`
- Governed 2026/27 FPL source release: `ffe99d25a5bd3a8f70c557748fead332f46ed14f`
- 20 completed fixtures / 360 scheduled fixtures
- 1,236 FPL player × fixture rows
- Current FPL player evidence is source-native and separate from historical Opta/PulseLive `players_match_stats`.

## Player source coverage

The pinned FPL player-fixture schema currently contains:

### Identity / participation

- `element`
- `position`
- `player_code`
- `team_code`
- `fixture_code`
- `minutes`
- `starts`

### Output / scoring

- `goals_scored`
- `assists`
- `clean_sheets`
- `goals_conceded`
- `own_goals`
- `penalties_saved`
- `penalties_missed`
- `yellow_cards`
- `red_cards`
- `saves`

### FPL-native analytical context

- `total_points`
- `bonus`
- `bps`
- `influence`
- `creativity`
- `threat`
- `ict_index`
- `clearances_blocks_interceptions`
- `recoveries`
- `tackles`
- `defensive_contribution`

### Expected metrics

- `expected_goals`
- `expected_assists`
- `expected_goal_involvements`
- `expected_goals_conceded`

### Market / ownership state

- `value`
- `transfers_balance`
- `selected`
- `transfers_in`
- `transfers_out`

## Player product position

The current player aggregation/kernel already connects the large majority of additive on-pitch FPL measures and exposes available governed metrics dynamically through Player Stats and Rankings.

Current notable gaps are therefore narrow rather than wholesale:

1. FPL market/ownership fields are source-present but not yet modelled as analytical player metrics. They require explicit temporal semantics rather than naïve season summation. Likely candidate representations are latest-as-of value/selection plus gameweek movement/time series.
2. `goals_conceded` is aggregated but current analytical exposure is primarily goalkeeper per-90 context. Raw/current-season exposure for appropriate goalkeeper/defender cohorts should be reviewed deliberately.
3. `creativity` is already represented as FPL/ICT creativity. It must not be relabelled as passing, key passes or chance creation without source equivalence.

## Passing: important distinction

The current FPL 2026/27 player schema does **not** contain genuine passing-count variables such as pass attempts, completed passes, long balls, key passes, through balls or crosses.

Passing-adjacent current FPL measures are:

- xA;
- FPL creativity / ICT creativity;
- assists.

These remain distinct concepts. FRL must not call them passing statistics.

## Rich historical PulseLive / PL passing vocabulary

The preserved `pl_stats` source family proves that FRL's underlying ecosystem has a much richer passing representation historically.

### Team-match examples from `events_stats`

The 2025/26 PulseLive team-event schema includes, among many others:

- `totalPass`
- `accuratePass`
- `fwdPass`
- `backwardPass`
- `openPlayPass`
- `successfulOpenPlayPass`
- `totalLongBalls`
- `accurateLongBalls`
- `longPassOwnToOpp`
- `longPassOwnToOppSuccess`
- `totalFinalThirdPasses`
- `successfulFinalThirdPasses`
- `totalThroughBall`
- `accurateThroughBall`
- `totalCross`
- `accurateCross`
- `totalCrossNocorner`
- `accurateCrossNocorner`
- `passesLeft`
- `passesRight`
- `leftsidePass`
- `rightsidePass`
- `totalBackZonePass`
- `accurateBackZonePass`
- `totalFwdZonePass`
- `accurateFwdZonePass`
- `totalOppositionHalfPasses`
- `accurateOppositionHalfPasses`
- possession and progression/territory fields alongside them.

### Player-match examples from `players_match_stats`

The 2025/26 player-match schema includes:

- `totalPass`
- `accuratePass`
- `totalOwnHalfPasses`
- `accurateOwnHalfPasses`
- `totalOppositionHalfPasses`
- `accurateOppositionHalfPasses`
- `totalLongBalls`
- `accurateLongBalls`
- `totalCross`
- `accurateCross`
- `keyPass`
- xA and wider possession/progression context.

This source family is the natural route for genuine team and player passing analysis if current-season acquisition can be extended safely.

## 2026/27 PulseLive gap classification

At the pinned upstream release, the committed historical archive does **not** contain:

- `pl_stats/.../events_stats/2026-27_events_stats.csv`;
- `pl_stats/.../players_match_stats/2026-27_players_match_stats.csv`;
- equivalent 2026/27 rich player-season files.

Therefore current FRL correctly marks team-match passing, shooting, possession and duels unavailable rather than fabricating them.

However, this is not yet proof of genuine source absence.

The upstream repository documentation says the PL/PulseLive archive contains ~180 team-event metrics and is pushed manually at the end of each round, whereas the FPL dataset is the automatically refreshed weekly source. The current 2026/27 upstream commits are FPL-only updates. The live/current PulseLive acquisition route therefore remains the next discovery target.

## Team product position

For 2026/27, currently product-ready team information is primarily canonical-result-derived:

- P/W/D/L;
- GF/GA/GD;
- points;
- PPG;
- goals for/against per match;
- clean-sheet rate;
- failed-to-score rate;
- home/away splits;
- form;
- league standings.

The new League Table product correctly uses this governed seam.

Rich Team Stats family metrics remain hidden for 2026/27 when no approved observations exist. This is correct fail-closed behaviour, not a frontend omission.

## Immediate next actions

1. Validate the existing local/preserved PulseLive acquisition mechanism against one completed 2026/27 fixture.
2. Inspect the raw response for the same team-event and player-match passing fields present historically.
3. If present, preserve a pinned raw snapshot and establish fixture/team/player identity relationships before analytical use.
4. Prove field meanings, missingness and grain against historical representations rather than assuming name equivalence.
5. Materialise governed 2026/27 team-match and player-match evidence only after the source route passes those checks.
6. Then let the existing dynamic Team/Player Stats catalogues expose the newly available passing metrics, adding UI groupings only where necessary.
7. Separately design temporal representations for FPL `value`, `selected` and transfer fields; do not sum them across gameweeks.

## Current conclusion

FRL is **not** missing a passing-stat concept or historical vocabulary. It is missing a currently governed 2026/27 rich PulseLive representation.

The correct next move is source-route recovery/validation, not inventing passing metrics from xA or FPL creativity.
