# Football Research Laboratory — Short-Term Product Roadmap

**Status:** Active near-term planning document  
**Created:** 29 August 2026  
**Last updated:** 30 August 2026

For repository-memory governance see `FRL_DOCUMENTATION_SYNC_CONTRACT.md`.

## Purpose

This document records the current priority sequence for turning FRL's governed evidence/research foundation into a coherent analytical product.

It is deliberately revisable and should not be treated as a permanent architecture contract.

Current-state detail belongs in `CURRENT_WORK.md`.

## Governing product principle

> **The GUI should be a window into the research environment, not a collection of disconnected football pages.**

Current information-architecture rule:

> **Profiles describe entities. Stats analyse entities. Rankings analyse populations. Compare analyses selected entities together. Research tests the questions these surfaces reveal.**

## Completed / substantially completed milestones

The following items have progressed beyond the state described in the original 29 August roadmap:

### Fixture Workspace V1

Rich fixture/result product work has been operationalised sufficiently to move on from fixture-first product development.

Standalone Fixtures V1 is frozen for now.

### Variable Capability Inventory

The machine-readable capability inventory exists and documents a broad governed/connected variable universe.

Important refinement from the 30 August source-route review:

> the capability inventory describes governed registries and connected research/model seams; it should not be interpreted as proof that each connected route is the strongest representation anywhere in the preserved ecosystem.

### Team Profile V1

Team Profile V1 is complete/frozen for now with the intended entity-description role.

### Team Stats Overview prototype

A first Team Stats Overview prototype exists with six core metric cards, trend/split presentation and league-context concepts.

It is a product/architecture prototype rather than the final analytical implementation.

## Current architectural prerequisite

Before expanding Team Stats into additional families, FRL needs to strengthen the middle analytical layer:

```text
source representation / route
        ↓
governed variable
        ↓
metric + coverage / missingness
        ↓
population / comparability
        ↓
analysis result
        ↓
Team View / Rankings / later Compare
```

The 30 August source-route evidence is recorded in `FRL_SOURCE_ROUTE_AUDIT_2026-08-30.md`.

## 1. Source-route governance + repository-memory sync

### Objective

Make sure FRL builds analytical products from the strongest defensible preserved source route while keeping all standing repository documentation in sync with the architecture that actually exists.

### Deliverables

- dated preserved-source route audit;
- explicit source-route classification;
- source-routing extension to the source-normalisation contract;
- refreshed current/orientation/design/risk documentation;
- automated documentation-sync gate;
- living documentation state manifest.

### Key route statuses

```text
KEEP_CURRENT_ROUTE
BETTER_EXISTING_ROUTE
DERIVED_ROUTE_PREFERRED
MULTIPLE_SOURCE_REPRESENTATIONS
SEMANTIC_REVIEW_REQUIRED
COVERAGE_GAP
```

## 2. Integrate analytical correctness fixes

Before the new kernel becomes authoritative, integrate and validate the narrow correctness work identified during the Team Stats review:

- missing metric observations must not be divided by the complete eligible population;
- coverage must distinguish eligible/observed/missing observations;
- partial xG must not create misleading full-season xG-overperformance;
- legitimate zero-score fixtures must remain in Poisson source populations;
- current product output must not imply full coverage when evidence is partial.

Keep this pass narrow. Do not hide it inside a broad refactor.

## 3. Build the minimum governed analytical kernel

Do **not** build a generic metric DSL or rewrite the 1,414-variable universe.

Prove the architecture with a small reference slice.

Initial objects/concepts should cover:

### `SourceRepresentation`

Which preserved evidence/version/grain is being used?

### `SourceRouteDecision`

Why is that representation appropriate for the requested concept, period and purpose?

### `MetricDefinition`

Stable metric identity, meaning, grain, unit, direction, aggregation, required inputs and version.

### `MetricObservation`

Value plus eligible/observed/missing coverage, provenance and limitations.

### `PopulationDefinition`

Competition/season/as-of scope, eligible entities, exclusions and coverage/minimum rules.

### `PopulationContext`

Rank, tie policy, percentile method and distribution context.

### Shared temporal/state service

Rolling windows, last-N, venue splits, streaks and season-to-date state should be defined once.

### `AnalysisResult`

One result capable of powering multiple product projections.

## 4. Team Stats → Team View → Overview

Refactor the current prototype onto the governed analytical kernel.

Initial metric slice:

- points per match;
- goals for per match;
- goals against per match;
- shots per match;
- shots on target per match;
- possession;
- xG as the first multiple-representation / derived-route case.

Requirements:

- value;
- metric/source version;
- coverage;
- population eligibility;
- rank/percentile where defensible;
- limitations/provenance;
- shared split/trend logic.

The frontend should present analytical results rather than calculate them independently.

## 5. Team Stats → League Rankings → Overview

Build Rankings as a transpose/projection of the same governed Team Stats result.

If Team View says a club is fifth for shots, Rankings must show the same club fifth because both consume the same metric/population computation.

Cross-link:

```text
Team View metric
    → View ranking

Ranking row
    → Analyse team
```

Compare remains later.

## 6. Reuse the analytical state in Team Profile

Move Profile form/last-N/split calculations onto the shared analytical/state service.

The Profile remains curated and lightweight; only the underlying calculation source becomes shared.

This proves that the kernel removes duplicated concepts rather than becoming another parallel implementation.

## 7. Expand Team Stats analytical families selectively

Only after Overview + Rankings prove the architecture:

`Attack · Possession · Passing · Defence · Discipline`

Exact metrics should follow governed capability/source-route evidence rather than visual convenience.

Do not keep a family populated with weak filler simply because the tab exists.

## 8. Player Profile / Player Stats

Player work should reuse the same high-level analytical shell without assuming identical population semantics.

Likely modes:

```text
Player View | Cohort Rankings | Compare later
```

Before rankings, govern:

- position/role cohorts;
- minimum minutes;
- per-90 eligibility;
- source/player identity;
- role changes;
- team-possession/context effects where relevant.

Potential analytical families remain provisional:

`Overview · Shooting · Creation · Possession · Defending · Discipline`

## 9. League workspace

Separate two concepts:

### Team Rankings within a league

Belongs inside Team Stats / Team Analytics.

### League as an analytical entity

League Stats should focus on league-level phenomena such as:

- scoring environment;
- home advantage;
- distributions;
- disciplinary environment;
- historical trends;
- season-over-season context.

League Table remains a navigational/competition-state product surface.

## 10. Prediction Lab

Productise modelling only after the analytical/source/population layer is sufficiently trustworthy.

Start with the existing Poisson model but expose:

- expected goals;
- outcome probabilities;
- correct-score distribution;
- model version;
- inputs;
- historical evaluation/calibration where available;
- prediction-time/as-of information;
- limitations.

Known Poisson correctness issues should be fixed/tested before productisation.

## 11. Head-to-Head / Match Research

Build a research workspace that combines governed descriptive evidence, analytical context and model output without presenting repeated historical patterns as automatically predictive.

The intended progression is:

```text
observation
    ↓
context
    ↓
comparison
    ↓
question
    ↓
hypothesis
    ↓
research test
```

## 12. 2026/27 data

Extend the governed data pipeline to the 2026/27 season as an extension of the same identity/source/temporal architecture.

Avoid current-season-only shortcuts unless source reality genuinely requires them.

## 13. Data Capability Brochure

The human-readable Data Capability Brochure remains valuable, but should follow the first governed metric/source-route slice.

Reason:

> it is more useful to explain not only what fields FRL has, but what FRL can responsibly calculate, compare and expose.

The brochure should distinguish:

- source-present;
- connected;
- derivable;
- governed;
- comparable;
- product-ready capability.

## 14. Cross-league expansion

Preserve the source-normalisation and competition-aware architecture now, but do not let hypothetical multi-league infrastructure displace the current Premier League analytical work.

Before ingesting a second competition, canonical fixture identity should explicitly resolve the competition dimension rather than relying indefinitely on `(season, fixture_id)` as a globally unique identity.

See `FUTURE_LEAGUE_COMBINE_PLAN.md`.

## 15. Current preferred sequence

```text
1. Source-route governance + documentation sync
        ↓
2. Integrate correctness / coverage fixes
        ↓
3. Minimum governed analytical kernel
        ↓
4. Team View → Overview on kernel
        ↓
5. League Rankings → Overview from same result
        ↓
6. Reuse analytical state in Team Profile
        ↓
7. Expand Team Stats families selectively
        ↓
8. Player Profile / Player Stats cohort semantics
        ↓
9. League workspace
        ↓
10. Prediction Lab
        ↓
11. Match Research
        ↓
12. 2026/27 extension / cross-league preparation as operationally required
```

## 16. Working rule

When selecting work, ask:

> Does this increase the trustworthiness/reusability of FRL's analytical environment or deliver one of the agreed product projections from that environment?

If not, record it rather than letting it silently displace the current sequence.

And whenever a milestone changes this sequence or the architecture supporting it, reconcile the standing repository memory before calling the milestone complete.
