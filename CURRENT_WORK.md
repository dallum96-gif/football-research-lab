# Current Work — Football Research Laboratory

**Last updated:** 30 August 2026  
**Checkpoint:** `SOURCE_ROUTE_COVERAGE_AUDIT`

For documentation-governance rules see `FRL_DOCUMENTATION_SYNC_CONTRACT.md` and `data/frl_documentation_state_v1.json`.

## Current platform state

FRL has moved beyond its Universal Research Access backend closeout into product and analytical architecture work.

Current integrated state on `main` includes:

- Next.js + React as the active frontend;
- FastAPI as the frontend-facing API;
- Streamlit retained as legacy/reference only;
- Homepage V1 complete/frozen;
- standalone Fixtures V1 complete/frozen for now;
- Team Profile V1 complete/frozen for now;
- Team Stats Overview implemented as the current analytical/product prototype;
- Team / Player Stats information architecture documented in `FRL_TEAM_PLAYER_STATS_VISUALISATION_PROTOTYPE.md`;
- governed source-routing semantics documented in `FRL_SOURCE_ROUTING_CONTRACT.md`;
- the first preserved-source route audit recorded in `FRL_SOURCE_ROUTE_AUDIT_2026-08-30.md`;
- coverage-aware team-season aggregation and the Poisson zero-score fix integrated in commit `eaef72f`;
- automated repository-memory synchronisation enforced by the documentation-sync GitHub Action.

## Immediate objective

The immediate general objective is:

> **For every meaningful FRL football variable/concept, connect analytical use to the strongest legitimate preserved source route available, maximising trustworthy historical coverage without sacrificing semantics, grain, provenance, temporal validity or comparability.**

This does **not** mean filling every missing value. Maximum trustworthy coverage is preferred over maximum numerical fill-rate.

The source-route review should work by semantic/source family rather than by hand-auditing 1,414 catalogue rows independently.

## Current architectural spine

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

The lower evidence/identity foundation is stronger than the current analytical layer. Do not expand analytical product surfaces faster than the governed variable/metric/population layer can support them.

## Source-routing position

Current evidence indicates that FRL does **not** have a broad source-routing failure.

Established conclusions:

- canonical fixtures/results remain the trusted fixture spine;
- direct `events_stats` / packaged team-match statistics remain a strong default route for ordinary team-match metrics;
- preserved PulseLive snapshots provide important versioned match-centre evidence but do not globally supersede `events_stats`;
- player-match evidence maps to 3,799/3,800 canonical fixtures plus the known 2019-20 correction case, so player → team derivation does not require another identity architecture;
- expected metrics such as xG can have multiple legitimate source representations with materially different historical coverage;
- summed player-match xG is close to but not identical to direct team-match xG, so the two must not be silently coalesced;
- player-season evidence is correct at player-season grain but can contain later/current club attribution and must not be used to manufacture missing fixture-level history;
- FPL remains a distinct source family with FPL-specific semantics;
- timeline, lineup, formation, manager and commentary evidence belongs primarily to the preserved PulseLive match-centre snapshot route;
- rolling form, streaks and splits should be derived once from governed fixture/team evidence rather than recalculated independently in API/UI surfaces.

Future capability metadata should distinguish at least:

`SOURCE_PRESENT → CONNECTED → DERIVABLE → GOVERNED → COMPARABLE → PRODUCT_READY`

## Automated source-route coverage audit

A new read-only empirical audit is being introduced in:

- `scripts/audit_source_routes.py`
- `.github/workflows/source-route-coverage.yml`

The audit uses the already-preserved public `imadeddine-belkat/Premier-League-Stats` archive and makes **no live PulseLive/Premier League API calls**.

It measures:

- source-family schemas and non-empty field observations by season;
- direct team-match fixture coverage for priority statistical fields;
- player-match availability for corresponding concepts;
- direct-vs-player-derived overlap agreement by season;
- candidate source-route classifications for additive/expected metric families.

Its output is diagnostic evidence only. It cannot automatically promote a source representation into a governed metric. Promotion still requires the semantic, missingness, provenance and comparability rules in `FRL_SOURCE_ROUTING_CONTRACT.md`.

## Team / Player product architecture

The current product rule remains:

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

Team View and Rankings must become projections of the same governed metric/population result rather than independent implementations.

For players, the interaction shell may mirror Team Stats, but population/cohort semantics remain player-specific.

## Immediate development sequence

1. **Complete the bounded empirical source-route audit**
   - run the automated decade-wide audit;
   - identify genuine coverage gains;
   - quantify direct-vs-derived equivalence/conflict;
   - classify the important semantic families.
2. **Turn audit findings into governed route decisions**
   - keep strong current routes;
   - introduce better preserved routes only where evidence justifies them;
   - keep non-equivalent source representations distinct;
   - record genuine coverage gaps rather than fabricating history.
3. **Upgrade capability metadata**
   - distinguish source-present / connected / derivable / governed / comparable / product-ready states.
4. **Build the minimum governed analytical kernel**
   - source representation / route decision;
   - metric definition;
   - coverage-aware metric observation;
   - population definition;
   - ranking/tie/percentile policy;
   - shared windows/splits;
   - reusable analysis result.
5. **Refactor Team Stats Overview onto the kernel**
   - preserve the six trusted Overview metrics;
   - use xG as the first explicit multi-representation/derived-route case.
6. **Build League Rankings from the same result**, then selectively expand Team Stats families.
7. **Move Team Profile form/state calculations onto the same analytical service.**
8. **Design player cohort semantics before Player Stats rankings.**

## Validation discipline

Do not use a historical fixed test count as the universal current baseline.

For current work:

- run targeted tests for changed behaviour;
- run relevant backend/research/identity gates;
- run Next.js `typecheck`/`build` where frontend contracts change;
- run `project-health.ps1` when canonical/query/data behaviour may be affected;
- run `python scripts/check_documentation_sync.py` for material milestone/documentation work;
- treat automated source-route reports as evidence, not automatic semantic approval;
- report actual command output rather than repeating historical validation counts.

## Repository discipline

Treat `main` as the stable integration line. Preserve unrelated tracked, untracked, generated, backup and experimental files. Do not use broad staging or destructive cleanup to simplify the workspace.

Source-route audit automation is being developed on a separate branch so it does not disturb local research/recovery artefacts.

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
