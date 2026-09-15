# FRL Player Profile Source-Capability Audit

**Date:** 14 September 2026  
**Status:** Targeted audit and first governed Player-Season promotion
**Scope:** Premier League player-season profile, with Martin Ødegaard (`184029`) as the reference case

## Executive conclusion

The selected-season Player Profile currently understates FRL's preserved player evidence.

The gap is not one generic absence. Several different capability states coexist:

```text
SOURCE_PRESENT
    ↓
CONNECTED
    ↓
DERIVABLE
    ↓
GOVERNED
    ↓
COMPARABLE
    ↓
PRODUCT_READY
```

For historical player profiles, identity and participation are Product-ready, while several richer variables are source-present or already materialised without being consumed by the Profile. This audit now promotes source-native Player-Season `forwardPasses` through an explicit materialised projection and verified identity route. Spatial event data is known to exist in the wider Opta ecosystem, but it is not present in FRL's currently preserved on-ball event route.

## Ødegaard finding

The original midfielder radar labelled `successful_dribbles_per_90` as **Carrying**. This is a semantic error: the source field represents successful contests/take-ons, not ball carrying.

For 2025-26 the existing governed rich projection already contains:

| Variable | Ødegaard value | Current state |
|---|---:|---|
| Ball carries | 348 | Materialised |
| Progressive carries | 18 | Materialised |
| Progressive carry distance | 367.769... | Materialised |
| Total progression | 419.129... | Materialised |
| Accurate opposition-half passes | 485 | Product-connected |
| Successful dribbles | missing in this projection | Source-present elsewhere |

The radar therefore suppressed an actual carrying observation because it required an unrelated take-on observation.

The first correction changed the Carrying dimension to `progressive_carries_per_90`, which fixed the take-on relabelling but exposed genuinely intermittent carry coverage. The product decision that follows this audit is to use **Forward passing** instead of **Carrying** in the six-axis midfielder profile for every season. Progressive carries remain available as their own football concept where observed; they are not relabelled or discarded.

## Governed forward-passing route

The Profile now uses:

```text
preserved Player-Season forwardPasses
    ↓
player_season_source_stats_v1.csv
    ↓
verified player identity route
    ↓
forward_passes
    ↓
forward_passes_per_90
    ↓
qualified same-position percentile
    ↓
Player Profile radar
```

The materialisation is pinned to upstream release `115d889df4e2efab5e7c1d8ca0f3ca86ecfd2ae6` (9 September 2026). It reads the direct club Player-Season resources, deduplicates identical repeated player-season rows, fails on conflicting duplicates and preserves source blanks as unavailable.

Identity is not inferred from player names:

- where the Profile exposes the stable FPL player code, it must exactly equal Player-Season `playerId`;
- historical FPL elements use the existing verified FPL element → Player-Match identity edge, followed by the packaged Player-Match identity → PulseLive `pl_code` edge;
- ambiguous or unresolved attachment fails closed.

Per-90 values use the Profile's governed FPL participation minutes so all six axes share the same cohort and denominator. The source Player-Season numerator can be captured at a slightly different upstream update time in the living season; that as-of limitation remains explicit rather than silently mixing numerator denominators from two products.

This verifies the forward-pass attachment used by Player Profile and Player Stats. It does not claim that FRL's generic Player-Season identity attachment is complete for every source field or every historical player; that broader canonical route remains a separate governance task.

## Current capability boundary

| Capability | Preserved source evidence | Current Product projection | Governance judgement |
|---|---|---|---|
| Accurate opposition-half passing | Player-Match and Player-Season | Connected | Usable with partial-coverage disclosure |
| Forward passes | Player-Season across the core decade and 2026-27 | Connected through a pinned Player-Season projection | Governed, comparable within observed same-season positional cohorts and Product-ready for the Profile |
| Through-balls | Player-Season across the core decade | Not connected | Structural-zero/missingness audit required |
| Successful take-ons | Player-Match `wonContest`; Player-Season `successfulDribbles` | Current-season only in rich projection | Do not label as carrying |
| Attempted take-ons | Player-Match `totalContest`; derivable from Player-Season successful + unsuccessful only after review | Current-season only | Route and missingness proof required |
| Unsuccessful take-ons | Derivable from Player-Match attempts minus wins; Player-Season field is restricted | Current-season derivation only | Keep Player-Season representation fail-closed pending semantic review |
| Ball carries | Player-Match `ballCarriesCount` | Intermittent seasons | Preserve season-specific availability |
| Progressive carries | Player-Match `progressiveBallCarriesCount` | Intermittent seasons | Suitable Carrying representation where observed |
| Pass/event X/Y | Explicitly part of Opta event products | Not found in current FRL event snapshots | Opta-ecosystem source-present; FRL route unproven |
| Continuous player X/Y | Opta Vision tracking product | Not preserved | Separate licensed tracking capability |

## Coverage evidence

The new source-native projection preserves 6,639 unique Player-Season identities:

| Season | Source player rows | Observed `forwardPasses` |
|---|---:|---:|
| 2016-17 | 591 | 501 |
| 2017-18 | 547 | 476 |
| 2018-19 | 558 | 486 |
| 2019-20 | 560 | 473 |
| 2020-21 | 590 | 480 |
| 2021-22 | 667 | 511 |
| 2022-23 | 667 | 523 |
| 2023-24 | 712 | 536 |
| 2024-25 | 632 | 510 |
| 2025-26 | 665 | 490 |
| 2026-27 | 450 | 358 |

These are source rows, not automatically attached Product players. Historical Product coverage can be lower because unresolved identity edges remain unavailable. The radar reports observed and eligible players separately and marks a metric `PARTIAL` when those populations differ.

For Ødegaard, the governed result is:

| Season | Source total | Profile minutes | Forward passes / 90 | Cohort coverage |
|---|---:|---:|---:|---|
| 2025-26 | 264 | 1,363 | 17.4321 | 131/132 qualified midfielders (`PARTIAL`) |
| 2026-27 | 45 | 221 | 18.3258 | 108/108 qualified midfielders (`AVAILABLE`) |

The 2026-27 Profile is consequently complete across all six dimensions. The earlier five-axis/star-shaped rendering was caused by the absent progressive-carry observation, not by a change in percentile geometry.

The tracked rich Player projection has no historical `successful_dribbles` observations for 2016-17 through 2025-26, despite source catalogue and upstream Player-Season evidence. This proves that catalogue discovery did not complete the Product chain.

Carrying coverage is genuinely intermittent in the tracked rich projection:

| Season | Ball carries observed | Progressive carries observed |
|---|---:|---:|
| 2016-17 | 0 | 0 |
| 2017-18 | 0 | 0 |
| 2018-19 | 0 | 0 |
| 2019-20 | 27 | 10 |
| 2020-21 | 0 | 0 |
| 2021-22 | 28 | 16 |
| 2022-23 | 0 | 0 |
| 2023-24 | 0 | 0 |
| 2024-25 | 111 | 111 |
| 2025-26 | 503 | 483 |
| 2026-27 | 0 | 0 |

These are observed player rows in `data/rich_player_season_stats.csv`, not claims about provider-wide possession of the variables.

Within the 2025-26 qualified-midfielder Profile cohort, progressive carries are observed for 222 of 248 eligible players. Ødegaard is observed. The comparison is therefore usable only as a visibly partial population.

## Spatial-data boundary

Stats Perform's Opta event definitions state that each pass is logged with X/Y origin and destination coordinates:

- <https://www.statsperform.com/opta-event-definitions/>

Opta Vision is a separate tracking product containing continuous XY player locations:

- <https://www.statsperform.com/products/opta-vision/>

The Premier League has published Ødegaard heatmaps, shot maps and shot-assist maps, demonstrating that such visual evidence exists in its Opta-supported editorial ecosystem:

- <https://www.premierleague.com/en/news/4267329>

However, those public editorial examples are delivered as finished image assets. FRL's preserved PulseLive event route currently contains goals, cards and substitutions rather than the complete coordinate-bearing on-ball Opta event stream.

The honest state is therefore:

```text
SOURCE_PRESENT_IN_OPTA_ECOSYSTEM
PUBLIC_PULSELIVE_ROUTE_NOT_YET_PROVEN
NOT_CONNECTED_TO_FRL
```

## Promotion order

1. Keep progressive-carry evidence separately available without take-on relabelling.
2. Use the now-governed Player-Season forward-passing route as the first repeatable `SOURCE_PRESENT` → Product promotion pattern.
3. Audit through-ball evidence and prove blank semantics for sparse Player-Season counts before including zero-event players in comparison populations.
4. Reconcile Player-Match `totalContest` / `wonContest` with Player-Season dribble representations while retaining source/grain identity.
5. Extend explicit per-metric source representation and coverage metadata across Player Profile outputs.
6. Probe for a coordinate-bearing public PulseLive/PL event resource; if none is defensibly accessible, record the Opta event-feed requirement as a source/licensing gap.

## Product rule established by this audit

> A missing Profile dimension remains visible as unavailable. It must not become zero, inherit a neighbouring football concept, or suppress every observed dimension.
