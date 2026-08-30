# Current Work — Football Research Laboratory

**Last updated:** 30 August 2026  
**Checkpoint:** `TEAM_STATS_OVERVIEW_KERNEL`

For documentation-governance rules see `FRL_DOCUMENTATION_SYNC_CONTRACT.md` and `data/frl_documentation_state_v1.json`.

## Current platform state

FRL is in governed analytical/product architecture work.

Current integrated state includes:

- Next.js + React as the active frontend and FastAPI as the frontend-facing API;
- Streamlit retained as legacy/reference only;
- Homepage V1, standalone Fixtures V1 and Team Profile V1 complete/frozen for now;
- Team Stats Overview as the active analytical product surface;
- governed source-routing semantics in `FRL_SOURCE_ROUTING_CONTRACT.md`;
- field-level team-match missingness governance in `FRL_TEAM_MATCH_MISSINGNESS_CONTRACT.md`;
- the direct team-match shot family governed as sparse-zero for 2016-17 through 2025-26;
- expected-metric route governance in `FRL_EXPECTED_METRIC_ROUTING_CONTRACT.md` and `expected_metric_routing.py`;
- player-derived xG materialised as a reproducible product-ready representation for 2022-23 through 2025-26 under `data/player_derived_expected_goals_v1/`, pinned to preserved upstream commit `1ec7f0dc79055902251cd938650f622b0e79f3cc`;
- xA and xGOT retained as governed/derivable routes but not product-packaged until a consumer needs them;
- `team_analysis_kernel.py` as the first minimum shared governed analytical kernel;
- Team Stats Overview refactored to consume the shared kernel result for its six league-context metrics and governed xG rather than constructing league populations/ranks inside the API endpoint;
- automated repository-memory synchronisation and targeted analytical regression gates.

## Immediate objective

The immediate objective is now roadmap step **#6**:

> **Build League Rankings as another projection of the same `season_overview_analysis()` result already consumed by Team Stats Team View.**

Do **not** create another metric engine, ranking implementation, percentile formula or league-population builder for Rankings.

The next product path is therefore:

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
        ├── Team Stats Team View   ← integrated
        └── League Rankings        ← next
```

Further source-route/missingness audits should be bounded by concrete product or research need rather than delaying League Rankings.

## Current analytical kernel checkpoint

`team_analysis_kernel.py` deliberately remains small. It currently owns only the responsibilities needed by Team Stats Overview and the next Rankings surface:

- the six trusted Overview metric definitions;
- one Premier League season team population;
- metric value plus coverage/representation metadata;
- competition-rank policy, including ties;
- the existing rank-position percentile policy;
- one reusable season analysis result;
- one Team View projection of that result;
- governed expected-goals route resolution.

The six current Overview metrics are:

1. points per match;
2. goals per match;
3. goals against per match;
4. shots per match;
5. shots on target per match;
6. possession.

The kernel preserves the existing Team Stats ranking/percentile behaviour rather than changing product semantics during the architectural refactor.

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
    ├── League Rankings    ← next shared kernel consumer
    └── Compare later
```

Team View and Rankings must never drift into independent definitions of the same metric or population.

## Immediate development sequence

1. **Build League Rankings from `season_overview_analysis()`**
   - expose the same six metric populations already used by Team View;
   - reuse the exact value, rank, `out_of`, percentile, coverage and representation metadata;
   - do not calculate rank/percentile in the API or frontend;
   - keep missing observations missing and preserve comparable-population size.
2. **Connect the Rankings product surface**
   - preserve the established Team Stats information architecture;
   - make metric/family navigation a presentation concern over the shared result;
   - run frontend typecheck/build where the Next.js contract changes.
3. **Selectively expand Team Stats families from the same kernel**
   - Attack, Possession, Passing, Defence and Discipline only as governed metrics become product-ready;
   - do not create family-specific analytical engines.
4. **Move Team Profile form/state calculations onto the same analytical service where useful.**
5. **Design player cohort/population semantics before Player Stats rankings.**

Additional source/missingness governance continues when a concrete metric requires it; it is no longer a general blocker to the Team Stats roadmap.

## Validation discipline

Do not use a historical fixed test count as a universal baseline.

For current analytical work:

- run the Team analysis kernel regression workflow for kernel/API changes;
- prove Team View values/ranks/percentiles remain projections of the same season result;
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
