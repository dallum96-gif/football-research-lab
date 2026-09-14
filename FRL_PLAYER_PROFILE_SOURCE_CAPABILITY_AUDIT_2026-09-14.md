# FRL Player Profile Source-Capability Audit

**Date:** 14 September 2026  
**Status:** Targeted audit and first product-semantics correction  
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

For historical player profiles, identity and participation are Product-ready, while several richer variables are source-present or already materialised without being consumed by the Profile. Spatial event data is known to exist in the wider Opta ecosystem, but it is not present in FRL's currently preserved on-ball event route.

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

The first correction changes the Carrying dimension to `progressive_carries_per_90`. A missing dimension is now retained as unavailable rather than deleting the entire profile or plotting zero.

## Current capability boundary

| Capability | Preserved source evidence | Current Product projection | Governance judgement |
|---|---|---|---|
| Accurate opposition-half passing | Player-Match and Player-Season | Connected | Usable with partial-coverage disclosure |
| Forward passes | Player-Season across the core decade | Not connected to Player Profile | First promotion candidate |
| Through-balls | Player-Season across the core decade | Not connected | Structural-zero/missingness audit required |
| Successful take-ons | Player-Match `wonContest`; Player-Season `successfulDribbles` | Current-season only in rich projection | Do not label as carrying |
| Attempted take-ons | Player-Match `totalContest`; derivable from Player-Season successful + unsuccessful only after review | Current-season only | Route and missingness proof required |
| Unsuccessful take-ons | Derivable from Player-Match attempts minus wins; Player-Season field is restricted | Current-season derivation only | Keep Player-Season representation fail-closed pending semantic review |
| Ball carries | Player-Match `ballCarriesCount` | Intermittent seasons | Preserve season-specific availability |
| Progressive carries | Player-Match `progressiveBallCarriesCount` | Intermittent seasons | Suitable Carrying representation where observed |
| Pass/event X/Y | Explicitly part of Opta event products | Not found in current FRL event snapshots | Opta-ecosystem source-present; FRL route unproven |
| Continuous player X/Y | Opta Vision tracking product | Not preserved | Separate licensed tracking capability |

## Coverage evidence

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

1. Expose existing progressive-carry evidence without take-on relabelling.
2. Audit and connect Player-Season forward passing and through-ball evidence.
3. Prove blank semantics for sparse Player-Season count fields before including zero-event players in comparison populations.
4. Reconcile Player-Match `totalContest` / `wonContest` with Player-Season dribble representations while retaining source/grain identity.
5. Add per-metric source representation and coverage metadata to Player Profile outputs.
6. Probe for a coordinate-bearing public PulseLive/PL event resource; if none is defensibly accessible, record the Opta event-feed requirement as a source/licensing gap.

## Product rule established by this audit

> A missing Profile dimension remains visible as unavailable. It must not become zero, inherit a neighbouring football concept, or suppress every observed dimension.

