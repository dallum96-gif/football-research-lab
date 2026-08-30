# Football Research Laboratory — Expected-Metric Routing Contract

**Status:** Governed analytical source-route contract  
**Date:** 30 August 2026

## Purpose

This contract governs FRL's analytical source-route decisions for:

- expected goals (xG);
- expected assists (xA);
- expected goals on target (xGOT).

It supplements `FRL_SOURCE_ROUTING_CONTRACT.md` and `FRL_TEAM_MATCH_MISSINGNESS_CONTRACT.md`.

The expected-metric family is the first FRL case where the same football concept exists through multiple preserved representations with materially different coverage and non-trivial numerical agreement characteristics.

## Core rule

> **FRL must select an expected-metric representation explicitly by football concept, season and analytical purpose. It must never create a synthetic series by silently taking whichever representation is non-null.**

A stronger-coverage representation is not automatically interchangeable with a source-native representation.

## Governed representations

### Direct team-match representation

Source concept:

```text
events_stats / packaged fixture_match_stats
→ source-native team-match expected metric
```

Representation identifier:

`DIRECT_TEAM_MATCH`

### Player-match-derived team representation

Source concept:

```text
players_match_stats
→ governed player expected-metric observations
→ additive aggregation within one verified team + fixture population
→ derived team-match expected metric
```

Representation identifier:

`PLAYER_MATCH_DERIVED_TEAM_MATCH`

This is a derived representation with its own provenance. It must never be labelled or stored as though it were the direct team-match source value.

## Missingness semantics used by the derived representation

### xG

For player-match `expectedGoals`:

- an explicit numeric value is observed;
- a blank with zero governed `totalShots` is zero xG;
- a blank with positive shots remains missing and makes the affected team-match derivation unavailable;
- player `totalShots` sparse-zero semantics are strongly corroborated against the direct team shot count.

### xA

For player-match `expectedAssists`:

- an explicit numeric value is observed;
- a blank is governed as zero for additive team-match derivation for the audited 2022-23 through 2025-26 representation.

This xA rule is **not** based on claiming `totalAttAssist` and player `keyPass` are equivalent. They are not equivalent enough for that proof.

Instead, the rule is supported directly by representation overlap:

- 2024-25 + 2025-26 provide 1,100 direct team-side xA overlap observations;
- all 1,100 player-summed xA values are within 0.01 of direct xA;
- maximum absolute difference is `0.00016532`;
- seven 2025-26 team sides containing blank player xA with positive `keyPass` still agree with direct xA within 0.01, with maximum absolute difference `0.00000471`.

Therefore positive `keyPass` is not a legitimate rule that forces positive xA under this source representation.

### xGOT

For player-match `expectedGoalsOnTarget`:

- an explicit numeric value is observed;
- a blank with zero governed `onTargetScoringAttempt` is zero xGOT;
- a blank with positive shots on target remains missing and makes the affected team-match derivation unavailable;
- player shots-on-target sparse-zero semantics are strongly corroborated against the direct team shots-on-target count.

## Audited route coverage

All fixture counts below refer to a 380-fixture Premier League season.

| Metric | Season | Direct team-match | Player-derived team-match |
| --- | ---: | ---: | ---: |
| xG | 2022-23 | 2 | 380 |
| xG | 2023-24 | 2 | 379 |
| xG | 2024-25 | 170 | 380 |
| xG | 2025-26 | 380 | 380 |
| xA | 2022-23 | 2 | 380 |
| xA | 2023-24 | 2 | 380 |
| xA | 2024-25 | 170 | 380 |
| xA | 2025-26 | 380 | 380 |
| xGOT | 2022-23 | 1 | 374 |
| xGOT | 2023-24 | 2 | 336 |
| xGOT | 2024-25 | 169 | 334 |
| xGOT | 2025-26 | 379 | 321 |

Before 2022-23, player-match expected-metric fields are not available. A handful of direct expected-metric fixtures exist in some seasons from 2018-19 through 2021-22, but those fragments do not constitute a legitimate season-level analytical population.

## Numerical relationship between representations

### xG

Direct xG and summed player xG are related but demonstrably non-identical.

Large-overlap seasons contain material differences and outliers. Therefore:

> **Do not coalesce direct and player-derived xG.**

### xA

Direct xA and summed player xA agree extremely closely wherever large direct overlap exists, but they remain separately sourced representations.

Therefore:

> **Treat player-derived xA as a strongly corroborated derived representation, not as a silent rewrite of direct xA provenance.**

### xGOT

Direct xGOT and summed player xGOT have strong broad agreement but include representation outliers in audited seasons, while player-derived coverage is materially incomplete.

Therefore:

> **Do not coalesce direct and player-derived xGOT.**

## Single-season descriptive route policy

For one season, prefer a complete source-native direct team-match representation when it exists. Otherwise prefer the governed representation with materially stronger legitimate coverage.

### xG

- 2016-17 through 2021-22: no governed season-level route;
- 2022-23: player-derived preferred, complete;
- 2023-24: player-derived preferred, near-complete (379/380);
- 2024-25: player-derived preferred, complete;
- 2025-26: direct preferred, complete.

### xA

- 2016-17 through 2021-22: no governed season-level route;
- 2022-23: player-derived preferred, complete;
- 2023-24: player-derived preferred, complete;
- 2024-25: player-derived preferred, complete;
- 2025-26: direct preferred, complete.

### xGOT

- 2016-17 through 2021-22: no governed season-level route;
- 2022-23: player-derived preferred, partial (374/380);
- 2023-24: player-derived preferred, partial (336/380);
- 2024-25: player-derived preferred, partial (334/380);
- 2025-26: direct preferred, near-complete (379/380).

A residual gap in the preferred representation must remain missing. Do not fill it from the alternate representation.

## Cross-season route policy

Cross-season comparison has a different requirement from a single-season descriptive view:

> **Representation consistency is part of comparability.**

FRL must not use player-derived xG in 2024-25 and direct xG in 2025-26 merely because each is locally best, then pretend the resulting two-season series is one homogeneous representation.

For comparisons confined to 2022-23 through 2025-26:

- xG: use `PLAYER_MATCH_DERIVED_TEAM_MATCH` consistently; 1,519/1,520 fixtures across the full four-season window;
- xA: use `PLAYER_MATCH_DERIVED_TEAM_MATCH` consistently; 1,520/1,520 fixtures;
- xGOT: use `PLAYER_MATCH_DERIVED_TEAM_MATCH` consistently only when the analysis explicitly accepts partial coverage; 1,365/1,520 fixtures across the full four-season window.

For any requested range that crosses into 2016-17 through 2021-22, there is no single governed expected-metric representation spanning the period. FRL must report the coverage gap rather than splice sparse direct history to the later player-derived representation.

## Representation mixing

For governed expected metrics:

`representation_mixing_allowed = false`

This applies within:

- one team-season total;
- one league ranking population;
- one cross-season comparison series;
- one derived ratio or over/under-performance measure;
- one modelling feature definition, unless a separately versioned model contract explicitly defines and validates a mixed representation.

## Product implications

### Team Stats

A Team Stats metric must expose or internally retain:

- chosen representation;
- coverage status;
- observed/eligible population;
- provenance;
- residual missingness.

A complete direct 2025-26 xG value and a complete player-derived 2025-26 xG value are not interchangeable merely because both cover 380 fixtures.

### Rankings

Every team in a ranking population must be evaluated under the same expected-metric representation and compatible observation rule.

### Research

Research queries may explicitly request a representation. If no representation is specified, FRL may choose the governed route for the declared analytical purpose but must retain that decision in provenance.

### Modelling

Expected-metric features must declare the representation and construction version. A model trained on player-derived xG and evaluated on direct xG is not automatically representation-consistent.

## Deployment boundary

The current `player_match_stats.py` adapter references a developer-local preserved source root. That adapter is valid research/reconstruction machinery but is **not by itself a deployable Team Stats data dependency**.

Before product code consumes player-derived expected metrics, FRL should materialise a deployable governed derivative or provide another preserved source seam with equivalent provenance and reproducibility.

Do not make FastAPI or Next.js silently depend on a developer-specific filesystem path.

## Code policy

`expected_metric_routing.py` is the executable policy representation for the current audited checkpoint.

It must remain:

- deterministic;
- fail-closed for unaudited seasons;
- explicit about analytical purpose;
- incapable of first-non-null fallback;
- explicit that representation mixing is forbidden.

## Final principle

> **Choose one expected-metric representation for one declared analytical purpose, preserve its provenance and coverage, and never hide a representation boundary behind a convenient non-null value.**
