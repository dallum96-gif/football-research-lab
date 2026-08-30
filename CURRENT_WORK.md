# Current Work — Football Research Laboratory

**Last updated:** 30 August 2026  
**Checkpoint:** `SOURCE_ROUTING_AND_ANALYTICAL_KERNEL_PREP`

For documentation-governance rules see `FRL_DOCUMENTATION_SYNC_CONTRACT.md` and `data/frl_documentation_state_v1.json`.

## Current platform state

The Universal Research Access backend milestone is complete and remains an important governed research-access foundation. Its dated closeout is preserved in `FRL_BACKEND_CLOSEOUT_2026-08-26.md`.

Since that closeout, FRL has moved materially further into productisation:

- Next.js + React is the active frontend;
- Streamlit is legacy/reference only;
- Homepage V1 is complete/frozen;
- standalone Fixtures V1 is complete/frozen for now;
- Team Profile V1 is complete/frozen for now;
- Team Stats Overview exists as an analytical/product prototype;
- the Team / Player Stats information architecture has been documented in `FRL_TEAM_PLAYER_STATS_VISUALISATION_PROTOTYPE.md`;
- a source-route review has exposed the need for explicit governed source selection between preserved representations;
- the next backend priority is the analytical layer between governed source evidence and product statistics.

## Current architectural position

FRL's lower evidence/identity foundation is stronger than the current analytical layer.

The current direction is:

```text
PRESERVED SOURCE EVIDENCE
        ↓
IDENTITY / RELATIONSHIPS
        ↓
SOURCE REPRESENTATION
        ↓
GOVERNED SOURCE ROUTE
        ↓
GOVERNED VARIABLE
        ↓
METRIC + COVERAGE / MISSINGNESS
        ↓
POPULATION / COMPARABILITY
        ↓
ANALYSIS RESULT
        ↓
FASTAPI
        ↓
NEXT.JS PRODUCT / RESEARCH CONSUMERS
```

Some existing implementation remains transitional and does not yet enforce this whole spine centrally.

The most important current rule is:

> **Do not add more analytical product surface faster than the governed metric/population layer can support it.**

## Source-routing position

The 30 August source-route audit is recorded in:

`FRL_SOURCE_ROUTE_AUDIT_2026-08-30.md`

Main conclusion:

> FRL does not have a broad source-routing failure. It has targeted missed capabilities plus a missing explicit source-routing layer.

Important findings:

- canonical fixtures/results remain the trusted fixture spine;
- direct `events_stats` / packaged team-match statistics remain a strong default route for established core team-match metrics;
- preserved PulseLive snapshots add important versioned match-centre evidence but do not globally supersede `events_stats`;
- expected metrics such as xG can exist through multiple legitimate source representations;
- player-match evidence can support explicit team-match derivations where the football concept and missingness rules permit it;
- a connected variable route is not automatically the strongest analytical capability available anywhere in the preserved ecosystem.

Future capability metadata should distinguish source-present, connected, derivable, governed, comparable and product-ready states.

## Team / Player product architecture

The current product rule is:

> **Profiles describe entities. Stats analyse entities. Rankings analyse populations. Compare analyses selected entities together. Research tests the questions these surfaces reveal.**

For teams:

```text
Team Profile
    ↓
Team Stats
    ├── Team View
    ├── League Rankings
    └── Compare later
```

Initial analytical families remain:

`Overview · Attack · Possession · Passing · Defence · Discipline`

Do not build all families at once. Team View and Rankings should become projections of the same governed metric/population result rather than independent implementations.

For players, the interaction shell can mirror Team Stats, but population semantics must remain player-specific. “Cohort Rankings” / “Population Rankings” is preferable to assuming all league players form one comparable population.

## Known analytical correctness work

A narrow local correctness pass has been implemented/tested outside this documentation branch for two confirmed defects:

1. partial metric observations were previously summed over observed rows but divided by all eligible team matches;
2. Poisson source-fixture filtering could mishandle legitimate zero scores.

The local pass adds coverage-aware aggregation semantics and zero-score regression coverage. It has not been incorporated into this GitHub documentation branch and should be integrated/revalidated before the analytical kernel is treated as current `main` behaviour.

The key methodological consequence remains:

> **missing evidence is not zero, and a partial observation must never be presented or ranked as though it represented a complete population.**

## Immediate development sequence

The preferred near-term sequence is now:

1. **Complete source-route/documentation governance**
   - preserve the source-route audit;
   - establish explicit source-routing semantics;
   - keep standing repository memory synchronised.
2. **Integrate the narrow analytical correctness pass**
   - missing-data denominators / coverage;
   - Poisson zero-score regression;
   - expose partial coverage safely where current product output would otherwise mislead.
3. **Build the minimum governed analytical kernel**
   - source representation / source-route decision;
   - metric definition;
   - coverage-aware metric observation;
   - population definition;
   - ranking/tie/percentile policy;
   - shared windows/splits;
   - one analysis result capable of serving multiple projections.
4. **Refactor Team Stats Overview onto that kernel**
   - preserve the current six strong Overview metrics;
   - use xG as the first multi-representation/derived-route case.
5. **Build League Rankings → Overview**
   - transpose the exact same governed result;
   - cross-link Team View ↔ Rankings.
6. **Move Team Profile form/state calculations onto the same analytical service.**
7. **Expand Team Stats analytical families selectively from governed capability evidence.**
8. **Design player cohort semantics before building Player Stats rankings.**
9. Continue League, Prediction Lab, Match Research and 2026/27 work from the updated roadmap.

## Frontend status

Active frontend:

**Next.js + React (`web/`)**

Frontend-facing API:

**FastAPI (`api/`)**

Streamlit remains in the repository as legacy/reference implementation and historical behaviour evidence. It is not the target for new product work.

Current visual language is the warm-light parchment/editorial system documented in `UI_DESIGN_SYSTEM.md`.

## Validation discipline

Do not use an old fixed test count as the universal current baseline.

Dated closeouts preserve what was validated at those checkpoints. For current work:

- run the targeted tests for the changed behaviour;
- run the relevant backend/research/identity gates;
- run Next.js `typecheck`/`build` where frontend contracts change;
- run `project-health.ps1` when canonical/query/data behaviour may be affected;
- run `python scripts/check_documentation_sync.py` for material milestone/documentation work;
- report actual current command output rather than repeating a historical count.

## Repository discipline

Treat `main` as the stable integration line.

Preserve unrelated tracked, untracked, generated, backup and experimental files. Do not use broad staging or destructive cleanup to simplify the workspace.

At this checkpoint, source/documentation work is intentionally being performed on a separate branch so existing local correctness work and recovery artefacts are not disturbed.

## Standing repository memory

Fresh sessions should use this order:

1. `FRL_MASTER_PROMPT.md`
2. `PROJECT_ORIENTATION.md`
3. `CURRENT_WORK.md`
4. `data/frl_documentation_state_v1.json`
5. task-relevant durable contracts / dated audits
6. current implementation

The documentation-sync rule is mandatory for future material milestones:

> **A milestone that changes current architecture, product phase, source-routing understanding, validation interpretation or frontend/design status is not complete until standing repository memory has been checked for drift.**
