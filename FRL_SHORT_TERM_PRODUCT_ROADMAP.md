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

### Team Stats Overview + League Rankings

The six-metric Team Stats Overview has moved beyond prototype status onto the shared governed analytical kernel.

League Rankings is now a second projection of the same season analysis result. Team View and Rankings consume the same metric values, population, competition ranks and percentiles; the API and frontend do not maintain a second ranking implementation.

The next Team Stats work is therefore selective analytical-family expansion rather than further Overview/Rankings architecture work.

## Current analytical architecture

The middle analytical layer has now been proven by two product projections:

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
        ├── Team View
        └── League Rankings
```

The 30 August source-route evidence is recorded in `FRL_SOURCE_ROUTE_AUDIT_2026-08-30.md`.

## 1. Source-route governance + repository-memory sync

**Status: substantially complete for the current Team Stats slice.**

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

Further route work should now be triggered by a concrete analytical/product need rather than treated as an unlimited prerequisite.

## 2. Integrate analytical correctness fixes

**Status: complete for the current Overview slice.**

The narrow correctness work identified during the Team Stats review has been integrated and governed:

- missing metric observations are not divided by the complete eligible population;
- coverage distinguishes eligible/observed/missing observations;
- partial xG cannot create misleading full-season xG-overperformance;
- structural-zero semantics are explicit rather than generic parser behaviour;
- current product output does not imply full coverage when evidence is partial.

Continue this discipline when new metric families expose new missingness questions.

## 3. Build the minimum governed analytical kernel

**Status: complete as the minimum reference implementation; expand only through product need.**

Do **not** turn the proven kernel into a generic metric DSL or rewrite the 1,414-variable universe.

The reference slice now establishes the concepts needed by Team View and League Rankings:

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

Rolling windows, last-N, venue splits, streaks and season-to-date state should be defined once as those concepts move onto the kernel.

### `AnalysisResult`

One result capable of powering multiple product projections.

## 4. Team Stats → Team View → Overview

**Status: complete on the shared kernel.**

The initial governed metric slice is:

- points per match;
- goals for per match;
- goals against per match;
- shots per match;
- shots on target per match;
- possession;
- xG as the first multiple-representation / derived-route case.

The current implementation carries:

- value;
- coverage/representation metadata;
- population eligibility;
- rank/percentile where defensible;
- limitations/provenance;
- governed xG route selection.

The frontend presents analytical results rather than calculating them independently.

## 5. Team Stats → League Rankings → Overview

**Status: complete for the six rankable Overview metrics.**

Rankings is implemented as a transpose/projection of the same governed Team Stats season result.

If Team View says a club is fifth for shots, Rankings shows the same club fifth because both consume the same metric/population computation.

Cross-link:

```text
Team View
    → League Rankings

Ranking row
    → Team View for that club
```

The first Rankings surface deliberately excludes xG as a ranked metric because governed xG is currently an observation route, not yet a kernel-declared ranked population metric. The GUI must not invent that ranking independently.

Compare remains later.

## 6. Expand Team Stats analytical families selectively

**Status: next.**

With Overview + Rankings proving the architecture, expand only through governed metrics:

`Attack · Possession · Passing · Defence · Discipline`

Exact metrics should follow governed capability/source-route evidence rather than visual convenience.

For every rankable metric, the same definition/population/result should feed both Team View and League Rankings.

Do not keep a family populated with weak filler simply because the tab exists, and do not create family-specific analytical engines.

## 7. Reuse the analytical state in Team Profile

Move Profile form/last-N/split calculations onto the shared analytical/state service where useful.

The Profile remains curated and lightweight; only the underlying calculation source becomes shared.

This should prove that the kernel removes duplicated concepts rather than becoming another parallel implementation.

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

Belongs inside Team Stats / Team Analytics and is now proven by the League Rankings surface.

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

The governing implementation boundary and incremental-release lifecycle are defined in `FRL_2026_27_INCREMENTAL_SEASON_INTEGRATION_PLAN.md`; that plan does not itself claim that integration has begun.

Avoid current-season-only shortcuts unless source reality genuinely requires them.

## 13. Data Capability Brochure

The human-readable Data Capability Brochure remains valuable, but should follow proven governed metric/source-route slices.

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
1. Source-route governance + documentation sync             ✓
        ↓
2. Integrate correctness / coverage fixes                  ✓
        ↓
3. Minimum governed analytical kernel                      ✓
        ↓
4. Team View → Overview on kernel                          ✓
        ↓
5. League Rankings → Overview from same result             ✓
        ↓
6. Expand Team Stats families selectively                  ← next
        ↓
7. Reuse analytical state in Team Profile
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
