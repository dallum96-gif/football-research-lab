# Current Work — Football Research Laboratory

**Last updated:** 30 August 2026  
**Checkpoint:** `EXPECTED_GOALS_PRODUCT_READY`

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
- automated decade-wide source-route, sparse-zero, Overview-missingness and expected-metric audits integrated on `main`;
- field-level team-match missingness governance documented in `FRL_TEAM_MATCH_MISSINGNESS_CONTRACT.md`;
- the audited shot family (`Shots`, `Shots on target`, `Shots off target`, `Blocked shots`) governed as sparse-zero for the preserved direct team-match representation over 2016-17 through 2025-26;
- expected-metric route governance documented in `FRL_EXPECTED_METRIC_ROUTING_CONTRACT.md` and executable in `expected_metric_routing.py`;
- player-derived expected goals materialised as a deployable governed representation for 2022-23 through 2025-26 under `data/player_derived_expected_goals_v1/`, pinned to upstream source commit `1ec7f0dc79055902251cd938650f622b0e79f3cc`;
- `expected_metric_artifact.py` as the product/runtime reader seam for governed player-derived xG;
- xA and xGOT retained as governed/derivable expected-metric routes but deliberately not product-packaged until a consumer needs them;
- coverage-aware team-season aggregation that separately preserves source-observed, structural-zero and genuinely missing populations;
- the Poisson zero-score fix integrated in commit `eaef72f`;
- automated repository-memory synchronisation enforced by the documentation-sync GitHub Action.

## Immediate objective

The immediate product/architecture objective is now:

> **Build the minimum shared analytical kernel required to make Team Stats Team View and League Rankings projections of the same governed metric/population result.**

The source-route objective remains a standing governance principle, but it is no longer necessary to delay the Team Stats kernel for broad additional auditing. Further source/missingness work should be bounded by product or research need.

The next kernel slice should reuse the trusted Team Stats calculations already implemented rather than introduce a large abstract framework.

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

The evidence, identity, route and first missingness layers are now strong enough to support the minimum Team Stats analytical kernel. Product expansion should still reuse governed results rather than reimplementing metric or population logic in API/UI surfaces.

## Source-routing and missingness position

Current evidence indicates that FRL does **not** have a broad source-routing failure.

Established conclusions:

- canonical fixtures/results remain the trusted fixture spine;
- direct `events_stats` / packaged team-match statistics remain a strong default route for ordinary team-match metrics;
- preserved PulseLive snapshots provide important versioned match-centre evidence but do not globally supersede `events_stats`;
- player-match evidence maps to 3,799/3,800 canonical fixtures plus the known 2019-20 correction case, so player → team derivation does not require another identity architecture;
- source blanks are missing by default, but field/source/period evidence can govern a blank as structural zero;
- the direct team-match shot family is governed as sparse-zero for 2016-17 through 2025-26;
- possession retains a genuine known hole for Tottenham Hotspur v Everton on 13 September 2020 and remains missing there;
- saves, offsides, big chances and other sparse-looking counts are **not** zero-normalised merely because their raw coverage looks sparse;
- expected metrics have multiple legitimate source representations and must be routed by metric, season and analytical purpose;
- direct and player-derived expected metrics must not be first-non-null coalesced;
- player-match xG derivation is governed by player shot evidence: blank xG with zero governed shots may be zero, while positive-shot gaps remain missing;
- player-match xA blank-as-zero semantics are strongly corroborated directly against 1,100 overlapping direct team-side xA observations across 2024-25 and 2025-26; all are within 0.01 and the maximum absolute difference is 0.00016532;
- `keyPass > 0` is not a legitimate rule that forces positive xA under this source representation;
- player-match xGOT derivation is governed by player shots-on-target evidence and remains materially partial in several seasons;
- for single-season descriptive expected metrics, a complete direct source-native representation is preferred when available; otherwise the materially stronger governed representation is used without gap-filling from the alternate source;
- for cross-season comparison, representation consistency is part of comparability: 2022-23 through 2025-26 xG/xA comparisons use the player-derived representation consistently rather than switching to direct values in 2025-26;
- no single governed expected-metric representation spans the pre-2022 and post-2022 eras, so FRL must report a historical coverage boundary rather than splice representations;
- player-season evidence is correct at player-season grain but can contain later/current club attribution and must not be used to manufacture missing fixture-level history;
- FPL remains a distinct source family with FPL-specific semantics;
- timeline, lineup, formation, manager and commentary evidence belongs primarily to the preserved PulseLive match-centre snapshot route;
- rolling form, streaks and splits should be derived once from governed fixture/team evidence rather than recalculated independently in API/UI surfaces.

Capability metadata should distinguish at least:

`SOURCE_PRESENT → CONNECTED → DERIVABLE → GOVERNED → COMPARABLE → PRODUCT_READY`

The expected-metric family now demonstrates that distinction concretely: player-derived xG is product-ready, while xA/xGOT remain governed/derivable until required by a product or research surface.

## Expected-metric routing and deployment checkpoint

`expected_metric_routing.py` is the deterministic route-policy seam for the audited expected-metric family.

### Single-season descriptive policy

- xG: player-derived preferred in 2022-23 (380/380), 2023-24 (379/380), 2024-25 (380/380); direct preferred in 2025-26 (380/380);
- xA: player-derived preferred in 2022-23 through 2024-25 (380/380 each); direct preferred in 2025-26 (380/380);
- xGOT: player-derived preferred in 2022-23 (374/380), 2023-24 (336/380), 2024-25 (334/380); direct preferred in 2025-26 (379/380);
- 2016-17 through 2021-22: no governed season-level expected-metric route. Isolated direct observations remain evidence, not a season population.

### Cross-season policy

For a 2022-23 through 2025-26 comparison:

- xG uses player-derived consistently: 1,519/1,520 fixtures;
- xA uses player-derived consistently: 1,520/1,520 fixtures;
- xGOT uses player-derived consistently only with explicit partial-coverage acceptance: 1,365/1,520 fixtures.

Representation mixing is forbidden within one governed season metric, ranking population or cross-season series.

### Deployable xG representation

The developer-local `player_match_stats.py` adapter remains research/reconstruction machinery and is not a production dependency.

Instead, product xG is materialised from the pinned preserved upstream source into:

```text
data/player_derived_expected_goals_v1/
    2022-23.json
    2023-24.json
    2024-25.json
    2025-26.json
    metadata.json
```

Each season file contains 380 canonical fixture positions, ordered by `fixture_id`, with `[home_xg, away_xg]` values. Governed unavailable xG remains `null`; no direct-source fallback is used.

The materialisation workflow rebuilds the representation from the pinned source and byte-compares the tracked season artifacts. The runtime reader validates per-file hashes and fails closed outside the materialised scope.

## Automated empirical audits

Read-only empirical audit infrastructure includes:

- `scripts/audit_source_routes.py` / `.github/workflows/source-route-coverage.yml`;
- `scripts/audit_sparse_zero_semantics.py` / `.github/workflows/sparse-zero-semantics.yml`;
- `scripts/audit_overview_missingness.py` / `.github/workflows/overview-missingness.yml`;
- `scripts/audit_expected_metric_routes.py` / `.github/workflows/expected-metric-route-governance.yml`;
- `scripts/audit_expected_assists_corroboration.py` / `.github/workflows/expected-assists-corroboration.yml`;
- `scripts/materialize_player_derived_expected_metrics.py` / `.github/workflows/materialize-player-derived-expected-metrics.yml` for reproducible expected-metric derivation and product xG materialisation.

The audits/materialisation use already-preserved historical evidence and make no live PulseLive/Premier League API calls.

Audit output remains diagnostic evidence until explicitly promoted by governance. Shot-family missingness and expected-metric routing are the first promoted analytical cases.

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

1. **Build the minimum governed Team Stats analytical kernel**
   - extract the existing Overview metric definitions from the FastAPI endpoint;
   - centralise league population construction;
   - centralise ranking, tie and percentile policy;
   - retain coverage/provenance alongside every metric observation;
   - resolve xG through `expected_metric_routing.py` and `expected_metric_artifact.py` when the governed route is player-derived;
   - retain direct xG when the route policy selects direct team-match evidence;
   - forbid representation coalescing.
2. **Refactor Team Stats Overview onto the shared analysis result**
   - preserve the existing six trusted Overview metrics and API/UI behaviour;
   - make governed xG the first multi-representation metric exercised by product analysis;
   - remove endpoint-local ranking/population calculations once parity is proven.
3. **Build League Rankings from exactly the same analysis result**
   - no second ranking implementation;
   - expose the same metric values, population, rank and percentile used by Team View.
4. **Upgrade capability metadata only where the analytical/product seam needs it**
   - xG is the first `PRODUCT_READY` expected metric;
   - do not block Team Stats on a broad 1,414-variable inventory migration.
5. **Continue bounded source/missingness governance when a concrete product/research metric requires it.**
6. **Selectively expand Team Stats analytical families from the same kernel.**
7. **Move Team Profile form/state calculations onto the same analytical service.**
8. **Design player cohort semantics before Player Stats rankings.**

## Validation discipline

Do not use a historical fixed test count as the universal current baseline.

For current work:

- run targeted tests for changed behaviour;
- use the Team Stats governance regression workflow for changes to team metric missingness/aggregation;
- use the expected-metric routing governance regression workflow for route-policy changes;
- use the expected-metric materialisation workflow for player-derived xG artifact changes;
- run relevant backend/research/identity gates;
- run Next.js `typecheck`/`build` where frontend contracts change;
- run `project-health.ps1` when canonical/query/data behaviour may be affected;
- run `python scripts/check_documentation_sync.py` for material milestone/documentation work;
- treat automated source-route/missingness reports as evidence, not automatic semantic approval;
- report actual command output rather than repeating historical validation counts.

## Repository discipline

Treat `main` as the stable integration line. Preserve unrelated tracked, untracked, generated, backup and experimental files. Do not use broad staging or destructive cleanup to simplify the workspace.

Audit and analytical-governance changes should continue on scoped feature branches and merge only after their relevant validation passes.

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
