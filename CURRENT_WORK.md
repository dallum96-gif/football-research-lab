# Current Work — Football Research Laboratory

**Last updated:** 30 August 2026  
**Checkpoint:** `TEAM_STATS_RANKINGS_FAMILY_EXPANSION_V1`

For documentation-governance rules see `FRL_DOCUMENTATION_SYNC_CONTRACT.md` and `data/frl_documentation_state_v1.json`.

The future 2026/27 living-season expansion is governed by `FRL_2026_27_INCREMENTAL_SEASON_INTEGRATION_PLAN.md`. That integration has not yet started and does not alter the current analytical checkpoint recorded below.

## Current platform state

FRL is in governed analytical/product architecture work.

Current integrated state includes:

- Next.js + React as the active frontend and FastAPI as the frontend-facing API;
- Streamlit retained as legacy/reference only;
- Homepage V1, standalone Fixtures V1 and Team Profile V1 complete/frozen for now;
- Team Stats Team View and League Rankings as paired analytical product surfaces over one shared season analysis result;
- governed source-routing semantics in `FRL_SOURCE_ROUTING_CONTRACT.md`;
- field-level team-match missingness governance in `FRL_TEAM_MATCH_MISSINGNESS_CONTRACT.md`;
- the direct team-match shot family governed as sparse-zero for 2016-17 through 2025-26;
- expected-metric route governance in `FRL_EXPECTED_METRIC_ROUTING_CONTRACT.md` and `expected_metric_routing.py`;
- player-derived xG materialised as a reproducible product-ready representation for 2022-23 through 2025-26 under `data/player_derived_expected_goals_v1/`, pinned to preserved upstream commit `1ec7f0dc79055902251cd938650f622b0e79f3cc`;
- xA and xGOT retained as governed/derivable routes but not product-packaged until a consumer needs them;
- `team_analysis_kernel.py` as the shared governed Team Stats analytical kernel;
- Team Stats Team View consuming the shared kernel result for its six Overview league-context metrics and governed xG;
- League Rankings consuming the same kernel-owned season populations, values, competition ranks, percentiles, coverage and representation metadata without recomputing ranking logic in FastAPI or Next.js;
- League Rankings Overview presented as six compact headline ranking cards, while non-Overview families use metric sub-headings and one full league ranking for the selected metric;
- Possession grouped under the Passing family in the Rankings information architecture rather than maintained as a separate top-level family;
- Corners per match as the first family-only rankable metric, exposed under Attack without becoming a seventh Team View Overview card;
- automated repository-memory synchronisation and targeted analytical/frontend regression gates.

## Immediate objective

The immediate objective remains selective Team Stats family expansion:

> **Add useful rankable team metrics from the same shared kernel only when their route, missingness and population semantics are product-ready.**

Do **not** create family-specific metric engines, ranking implementations, percentile formulas or league-population builders.

The current product path is therefore:

```text
GOVERNED SOURCE / VARIABLE
        ↓
METRIC OBSERVATION + COVERAGE
        ↓
SEASON POPULATION
        ↓
SHARED RANK / PERCENTILE POLICY
        ↓
season_overview_analysis()
        ├── Team Stats Team View   ← integrated six-metric Overview
        └── League Rankings        ← integrated Overview + family metrics
                 ↓
        selective family expansion ← current
```

Further source-route/missingness audits should be bounded by the concrete metric being productised rather than becoming a general blocker.

## Current analytical kernel checkpoint

`team_analysis_kernel.py` keeps Overview deliberately compact while allowing additional family-level ranking metrics.

It owns:

- the six trusted Overview metric definitions;
- additional rankable family metrics that must not automatically become Overview cards;
- one Premier League season team population;
- metric value plus coverage/representation metadata;
- competition-rank policy, including ties;
- the existing rank-position percentile policy;
- one reusable season analysis result;
- Team View projection of that result;
- League Rankings API projection of the same result;
- governed expected-goals route resolution.

The six current Overview metrics are:

1. points per match;
2. goals per match;
3. goals against per match;
4. shots per match;
5. shots on target per match;
6. possession.

The current additional family-only ranking metric is:

7. corners per match — shown under Attack in League Rankings.

The kernel therefore currently exposes seven rankable metrics to League Rankings while Team View Overview remains six metrics. Corners retains source-native missingness/coverage semantics; missing observations are not silently normalised to zero.

The kernel preserves the existing Team Stats ranking/percentile behaviour rather than changing product semantics during expansion. The frontend displays kernel-owned ranks and does not calculate them.

### Governed xG in product analysis

Single-season xG route policy remains:

- 2016-17 through 2021-22: no governed season-level xG route;
- 2022-23: player-derived, 380/380 fixtures;
- 2023-24: player-derived, 379/380 fixtures;
- 2024-25: player-derived, 380/380 fixtures;
- 2025-26: direct team-match, 380/380 fixtures.

The Team Stats kernel applies that route rather than reading one fixed xG column.

The 2023-24 player-derived gap remains missing. The kernel does not fill it from direct xG, and xG overperformance remains withheld for affected incomplete team populations.

For 2025-26 the single-season route deliberately selects the complete source-native direct representation.

xG remains a governed Team View observation but is not yet declared a League Rankings metric. Rankings must not invent an xG league rank independently.

## Source-routing and missingness standing position

The broad source ecosystem is sufficiently understood to proceed with the analytical product layer.

Standing conclusions remain:

- canonical fixtures/results are the trusted fixture spine;
- direct packaged team-match statistics remain the strong default for ordinary team metrics;
- PulseLive snapshots are versioned match-centre evidence, not a universal replacement statistics source;
- player-match evidence can responsibly derive selected team-match concepts where explicitly governed;
- source blank means missing by default;
- structural zero is an explicit field/source/period exception, not a generic parser rule;
- possession retains the known genuine Tottenham Hotspur v Everton hole on 13 September 2020;
- saves, offsides, big chances and other sparse-looking fields are not zero-normalised without evidence;
- corners are currently rankable with their observed coverage preserved; blanks are not converted to zero;
- direct and player-derived expected metrics are distinct representations and must never be first-non-null coalesced;
- representation consistency is part of cross-season comparability;
- no single governed expected-metric representation spans the pre-2022 and post-2022 periods;
- player-season evidence must not be used to manufacture fixture-level historical state;
- FPL remains a distinct source family;
- timeline/lineup/formation/manager/commentary evidence belongs primarily to preserved match-centre snapshot routes.

Capability semantics should continue to distinguish:

`SOURCE_PRESENT → CONNECTED → DERIVABLE → GOVERNED → COMPARABLE → PRODUCT_READY`

Player-derived xG is the first expected metric to reach `PRODUCT_READY`; xA/xGOT remain governed/derivable.

## Team Stats architecture

The product rule remains:

> **Profiles describe entities. Stats analyse entities. Rankings analyse populations. Compare analyses selected entities together. Research tests the questions these surfaces reveal.**

For teams:

```text
Team Profile
    ↓
Team Stats
    ├── Team View          ← shared kernel consumer
    ├── League Rankings    ← shared kernel consumer
    └── Compare later
```

Team View and Rankings must never drift into independent definitions of the same metric or population.

League Rankings currently uses:

- endpoint: `/api/v1/team-stats/{season}/rankings`;
- GUI workspace: `/team-stats/rankings`;
- top-level sections: Overview, Attack, Passing, Defence and Discipline;
- Possession as a metric within Passing;
- six Overview cards;
- metric sub-headings within non-Overview families;
- one full 20-team ranking beneath the selected metric;
- seven currently rankable metrics in the backend: six Overview metrics plus corners per match;
- competition-rank ties preserved;
- unsupported seasons rejected explicitly;
- rank and percentile never recalculated in React.

## Immediate development sequence

1. **Continue selectively expanding Team Stats families from the same kernel**
   - prioritise useful football/research/betting metrics with defensible coverage semantics;
   - Passing, Defence and Discipline should be populated only as specific underlying fields are audited and declared product-ready;
   - do not add conceptual intermediate taxonomies that are not required by the product hierarchy.
2. **Keep Overview curated while family rankings become richer**
   - additional family metrics must not automatically become Team View Overview cards;
   - one metric definition and one governed population should feed every product surface that exposes the same concept;
   - preserve missingness, coverage and representation metadata.
3. **Move Team Profile form/state calculations onto the same analytical service where useful.**
4. **Design player cohort/population semantics before Player Stats rankings.**
5. **Resume wider research/modelling product work once the shared analytical pattern is proven across more Team Stats families.**

Additional source/missingness governance continues when a concrete metric requires it; it is no longer a general blocker to the Team Stats roadmap.

## Validation discipline

Do not use a historical fixed test count as a universal baseline.

For current analytical work:

- run the Team analysis kernel regression workflow for kernel/API changes;
- prove Team View and League Rankings values/ranks/percentiles remain projections of the same season result;
- run the Team Stats League Rankings workflow for Rankings API/UI changes, including Next.js typecheck and production build;
- use the Team Stats governance regression workflow for missingness/aggregation changes;
- use expected-metric routing/materialisation gates for xG route/artifact changes;
- run backend/research/identity gates when their contracts are touched;
- run Next.js `typecheck` and `build` for frontend contract changes;
- run `project-health.ps1` when canonical/query/data behaviour may be affected;
- run documentation sync for milestone-sensitive changes;
- report actual validation output rather than historical test-count claims.

## Repository discipline

Treat `main` as the stable integration line. Preserve unrelated tracked, untracked, generated, backup and experimental files. Do not use destructive cleanup or broad staging to simplify work.

Use scoped feature branches and merge only after the relevant validation gates pass.

## Standing repository memory

Fresh sessions should use this order:

1. `FRL_MASTER_PROMPT.md`
2. `PROJECT_ORIENTATION.md`
3. `CURRENT_WORK.md`
4. `data/frl_documentation_state_v1.json`
5. task-relevant durable contracts / dated audits
6. current implementation

The documentation-sync rule remains mandatory:

> **A milestone that changes current architecture, product phase, source-routing understanding, validation interpretation or frontend/design status is not complete until standing repository memory has been checked for drift.**
