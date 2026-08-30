# Football Research Laboratory — Project Orientation

**Last reviewed:** 30 August 2026

This is the fast-start guide for a new contributor or new AI coding session.

For repository-memory governance see `FRL_DOCUMENTATION_SYNC_CONTRACT.md`.

## 1. Read order

Before substantive work:

1. read `FRL_MASTER_PROMPT.md`;
2. read this file;
3. read `CURRENT_WORK.md`;
4. inspect `data/frl_documentation_state_v1.json`;
5. inspect the task-relevant contracts, dated audits and implementation;
6. establish current branch/working-tree/upstream state before changing files.

Do not ask the user to reconstruct project information that the repository can establish.

## 2. FRL in one sentence

> **Give us the data and let us ask whatever football question we can think of.**

FRL is intended to become a provenance-aware historical football research and modelling environment, not merely a statistics site, an FPL dashboard or one betting model.

The long-term progression is:

```text
question / hypothesis
    ↓
governed evidence
    ↓
patterns / explanation
    ↓
derived metrics
    ↓
models / evaluation
    ↓
application where justified
```

Betting is a downstream application of validated research, not the definition of the platform.

## 3. Current stable principles

FRL must preserve:

- source provenance;
- canonical fixture and identity semantics;
- source-local identifiers until explicitly reconciled;
- event time, information-availability time and ingestion time as distinct concepts;
- historical/as-of reconstruction without future leakage;
- missingness as missingness rather than implicit zero;
- explicit transformation and derivation rules;
- source/version differences where equivalence is unproven;
- reproducibility and non-destruction during migration.

## 4. Current architectural direction

The lower evidence/identity layers are mature relative to the current analytical layer.

The target analytical spine now being established is:

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

Existing implementation is transitional: useful research logic remains distributed across `query_lab.py`, `query_api.py`, `research_access.py`, specialist team/player modules and `api/frl_api.py`. Do not assume the target spine is already fully implemented merely because it is the current architecture direction.

## 5. Source-routing rule

The source ecosystem can contain several preserved representations of the same football concept.

Therefore:

> **Do not choose a source by field name or first non-null value. Choose a governed representation for the requested concept, grain, period and analytical purpose.**

Read:

- `FRL_SOURCE_NORMALISATION_CONTRACT.md`
- `FRL_DATA_ECOSYSTEM_DISCOVERY_CONTRACT.md`
- `FRL_SOURCE_ROUTE_AUDIT_2026-08-30.md`
- `FRL_SOURCE_RIGHTS_REGISTER.md`

The current source-route audit concludes that the existing direct team-match route is generally strong for established core fields, while expected metrics such as xG demonstrate genuine multi-representation and derived-route cases.

## 6. Trusted data foundation

Important evidence/canonical artefacts include:

- `fixtures_master_corrected.csv` — canonical fixture master;
- `identity/team_seasons.csv` — season-local → persistent club identity;
- `identity/data_quality/fixture_corrections.csv` — explicit correction provenance;
- `data/fixture_match_stats.csv` — packaged direct team-match statistics;
- historical FPL player/gameweek datasets;
- Player-Match / Player-Season source families in the preserved upstream workspace;
- preserved PulseLive fixture snapshots;
- versioned historical-state features.

A source copy is not automatically canonical truth. Grain, identity, missingness, version and provenance are part of the meaning.

## 7. Identity and relationship architecture

Season-local team IDs are not globally stable.

Persistent club identity is separate from source/season-local identity.

The same principle applies to fixtures, players, teams, competitions, events, FPL seasonal identifiers and Player-Match / Player-Season source identifiers.

Read the relevant identity/relationship contracts before changing joins.

Never use fuzzy/display-name matching as a substitute for an established bridge when a governed relationship is required.

## 8. Active frontend / product architecture

Active frontend:

**Next.js + React under `web/`**

Frontend-facing API:

**FastAPI under `api/`**

Streamlit is legacy/reference implementation. It can remain useful as historical behaviour evidence but is not the target architecture for new product work.

Current product rule:

> **Profiles describe entities. Stats analyse entities. Rankings analyse populations. Compare analyses selected entities together. Research tests the questions these surfaces reveal.**

Current completed/frozen-for-now product surfaces and current analytical work are recorded in `CURRENT_WORK.md` rather than hard-coded here.

## 9. Team / Player analytical information architecture

Read `FRL_TEAM_PLAYER_STATS_VISUALISATION_PROTOTYPE.md`.

For teams:

```text
Team Profile
    ↓
Team Stats
    ├── Team View
    ├── League Rankings
    └── Compare later
```

Analytical families currently use the broad structure:

`Overview · Attack · Possession · Passing · Defence · Discipline`

These categories should be populated only where governed capability exists.

Team View and Rankings must ultimately be projections of the same governed result, not separate implementations whose rankings merely happen to agree.

Player analytics can share the interaction shell but require player-specific cohort/population semantics.

## 10. Research-access architecture

Universal Research Access remains an important governed capability-discovery/validation/query layer.

Its completed milestone is preserved in `FRL_BACKEND_CLOSEOUT_2026-08-26.md`.

However, the 30 August source-route review establishes an important distinction:

> a variable being catalogued/connected is not the same as proving FRL is using the strongest analytical representation available anywhere in the preserved ecosystem.

Future capability metadata should distinguish source-present, connected, derivable, governed, comparable and product-ready states.

## 11. Analytical safety

Do not allow product code to invent analytical semantics.

In particular:

- React should not independently define rolling form, last-N populations, ranks or percentiles;
- FastAPI routes should increasingly orchestrate domain services rather than own metric formulas;
- missing source observations must not be silently divided by complete populations;
- ratios/percentages require correct numerator/denominator aggregation;
- ranks require an explicit eligible population and tie/percentile policy;
- partial evidence requires visible coverage/limitations before normal product exposure.

## 12. Historical / as-of discipline

FRL distinguishes event time, information-availability time and ingestion/retrieval time.

Final historical data does not prove that the information was knowable at the earlier prediction/research cutoff.

Historical state and future model evaluation must remain time-safe.

## 13. Quality and validation

`RISK_STRATEGY_FRAMEWORK.md` and `NON_DESTRUCTION_ASSURANCE.md` are the primary quality contracts.

Do not treat an old fixed test count as the eternal current baseline.

For each change:

1. establish current behaviour/state;
2. identify the change surface;
3. predict failure modes;
4. implement the smallest sensible change;
5. run targeted validation;
6. run relevant regression/data/query/frontend gates;
7. report actual output;
8. reconcile standing documentation if the milestone changed project-level state.

## 14. Repository safety

Treat `main` as the stable integration line.

Before changing code:

- inspect branch/upstream/ahead-behind state;
- preserve unrelated local and untracked files;
- do not use `git clean` or `git reset --hard` for ordinary workspace management;
- do not use `git add .` casually;
- do not delete backups/recovery artefacts merely to obtain a clean status;
- prefer reversible, scoped changes.

## 15. Current visual system

The current active Next.js visual language is the warm-light parchment/editorial system documented in `UI_DESIGN_SYSTEM.md`.

Do not infer visual direction from older Streamlit-era examples or historical screenshots.

## 16. Key current files

Start with these when re-entering the project:

1. `FRL_MASTER_PROMPT.md`
2. `PROJECT_ORIENTATION.md`
3. `CURRENT_WORK.md`
4. `data/frl_documentation_state_v1.json`
5. `FRL_DOCUMENTATION_SYNC_CONTRACT.md`
6. `FRL_SOURCE_ROUTE_AUDIT_2026-08-30.md`
7. `FRL_SOURCE_NORMALISATION_CONTRACT.md`
8. `FRL_DATA_ECOSYSTEM_DISCOVERY_CONTRACT.md`
9. `FRL_TEAM_PLAYER_STATS_VISUALISATION_PROTOTYPE.md`
10. `RISK_STRATEGY_FRAMEWORK.md`
11. `NON_DESTRUCTION_ASSURANCE.md`
12. `research_access.py`
13. `query_lab.py`
14. `query_api.py`
15. `match_stats.py`
16. `team_research_stats.py`
17. `team_research_analytics.py`
18. `api/frl_api.py`
19. `web/`
20. `tests/`

Then inspect task-specific contracts/data rather than assuming these files alone define the entire source ecosystem.

## 17. Documentation freshness rule

Repository documentation is operational memory.

Whenever a material milestone changes architecture, active product phase, source routing/capability interpretation, validation interpretation or frontend/design status, reconcile the standing documents before calling the milestone complete.

See `FRL_DOCUMENTATION_SYNC_CONTRACT.md`.

## 18. Final orientation principle

> **Preserve source truth, govern the analytical meaning, keep time honest, and make the repository describe the system that actually exists.**
