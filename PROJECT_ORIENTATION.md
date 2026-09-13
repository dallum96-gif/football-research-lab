# Football Research Laboratory — Project Orientation

**Last reviewed:** 13 September 2026

This is the fast-start guide for a new contributor or AI coding/research session.

For repository-memory governance see `FRL_DOCUMENTATION_SYNC_CONTRACT.md`.

## 1. Recovery order

Before substantive work:

1. read `FRL_MASTER_PROMPT.md`;
2. read this file;
3. read `CURRENT_WORK.md`;
4. inspect `data/frl_documentation_state_v1.json`;
5. follow `AGENTS.md`;
6. establish the current branch / upstream / ahead-behind / working-tree state;
7. inspect task-relevant contracts, dated audits and implementation;
8. run validation appropriate to the actual change.

Do not ask Daniel to reconstruct project information that the repository, connected GitHub state or relevant project history can establish.

Historical chats and dated repository documents are valuable evidence of reasoning and previous state, but they do not automatically override current implementation or current governing documentation.

## 2. FRL in one sentence

> **Give us the data and let us ask whatever football question we can think of.**

FRL is a provenance-aware historical football research and modelling environment, not merely a statistics site, FPL dashboard or one betting model.

The durable progression is:

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

Betting is a downstream application of research, not the definition of the platform.

## 3. Stable principles

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

## 4. Analytical architecture direction

The target analytical spine remains:

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

Existing code is transitional. Useful logic remains distributed across established query/research modules and specialist services. Reuse trusted seams; do not rewrite merely to make the architecture diagram look cleaner.

## 5. Source-routing rule

The preserved ecosystem may contain several representations of the same football concept.

Therefore:

> **Do not choose a source by field name or first non-null value. Choose a governed representation for the requested concept, grain, period and analytical purpose.**

Read as needed:

- `FRL_SOURCE_NORMALISATION_CONTRACT.md`
- `FRL_DATA_ECOSYSTEM_DISCOVERY_CONTRACT.md`
- `FRL_SOURCE_ROUTE_AUDIT_2026-08-30.md`
- `FRL_SOURCE_RIGHTS_REGISTER.md`

A field being present does not prove a research metric exists, and a connected route does not prove it is the strongest preserved representation.

Useful capability states remain:

```text
SOURCE_PRESENT
CONNECTED
DERIVABLE
GOVERNED
COMPARABLE
PRODUCT_READY
```

## 6. Trusted evidence foundation

Important evidence/canonical artefacts include:

- `fixtures_master_corrected.csv` — canonical fixture master;
- `identity/team_seasons.csv` — season-local → persistent club identity;
- `identity/data_quality/fixture_corrections.csv` — explicit correction provenance;
- `data/fixture_match_stats.csv` — packaged direct team-match statistics;
- historical FPL player/gameweek evidence;
- Player-Match / Player-Season source families;
- preserved PulseLive fixture snapshots;
- governed historical-state/model artefacts.

A source copy is evidence, not automatically canonical truth. Grain, identity, missingness, version and provenance are part of the meaning.

## 7. Current validated capability foundation

The standing source-universe checkpoints include:

- 3,800 preserved Premier League fixture snapshots for 2016/17–2025/26;
- 553 master raw source paths;
- 249 team-match statistical paths reconciled, including 176 canonical/governed generic-access fields, 8 retained fields, 6 restricted fields and 59 preserved raw-only governed routes;
- 86 observed Player-Match source fields, with 81 exposed for generic research access;
- archive-wide governed fixture event/tactical-context routing;
- the last formally validated rich current-season Player checkpoint at 79/83 product capabilities through GW1–3.

Read `CURRENT_WORK.md` for current interpretation and do not silently replace these validated claims with newer local/experimental state until it is revalidated.

## 8. Identity and relationships

Season-local team IDs are not globally stable. Persistent club identity is separate from source/season-local identity.

The same discipline applies to fixtures, players, teams, competitions, FPL seasonal identity and Player-Match / Player-Season source identity.

Never join numeric IDs across source families by coincidence and never use fuzzy/display-name matching as a substitute for a governed bridge where one is required.

## 9. Active frontend / API

Active frontend:

**Next.js + React under `web/`**

Frontend-facing API:

**FastAPI under `api/`**

Python remains authoritative for source routing, identity, temporal semantics, provenance, statistical definitions, analytical semantics and modelling.

Streamlit is legacy/reference implementation.

Current durable product rule:

> **Profiles describe entities. Stats analyse entities. Rankings analyse populations. Compare analyses selected entities together. Research tests the questions these surfaces reveal.**

## 10. Current product phase

The current product/reference work has progressed beyond the earlier team-source-industrialisation phase.

`design/bet-builder-reference-v1` / draft PR #53 contains active reference work across:

- global shell/navigation;
- Fixtures;
- fixture result workspace;
- Matchday / Bet Builder;
- Team Profile / Team Overview;
- club crest/stadium identity assets;
- supporting backend/evidence/reference seams.

It is an active experimental branch, not a validated integration candidate. It is also behind newer commits on its current base and requires reconciliation before integration.

See `FRL_REPOSITORY_RECONCILIATION_2026-09-13.md` and `CURRENT_WORK.md`.

## 11. Current visual direction

The intended visual language is now **dark, premium, editorial, analytical and football-first**.

Use `UI_DESIGN_SYSTEM.md` and `FRL_LUXURY_DESIGN_CONSTITUTION.md` as current design authority.

The codebase still contains older warm parchment-era root tokens and mixed-generation surfaces. Treat those as migration state, not as permission to resurrect the superseded palette on new work.

Current high-level direction:

- near-black / charcoal structure;
- warm ivory / cream primary text;
- muted greys;
- restrained coral/orange emphasis;
- green/olive used semantically rather than as default branding;
- no lime-green brand language;
- two-level top navigation for the active reference shell rather than a permanent sidebar assumption.

## 12. Team / Player analytical information architecture

Read `FRL_TEAM_PLAYER_STATS_VISUALISATION_PROTOTYPE.md` for the analytical interaction model.

Team View and Team Rankings should be projections of the same governed analytical result, not separate implementations that happen to agree.

Player analytics may share interaction patterns but require player-specific cohort, minutes and role semantics.

The signature vertical-list / multi-tile pattern remains useful for statistical browsing, but it is a component language rather than the whole product architecture.

## 13. Analytical safety

Do not allow product code to invent analytical semantics.

In particular:

- React should not independently define rolling form, last-N populations, ranks or percentiles;
- FastAPI should increasingly orchestrate domain services rather than own ad hoc formulas;
- missing observations must not be silently divided by complete populations;
- ratios/percentages require correct numerator/denominator aggregation;
- ranks require explicit eligible populations and tie/percentile policies;
- partial evidence requires visible coverage/limitations;
- descriptive BetBuilder evidence must not be presented as calibrated betting probability.

## 14. Historical / as-of discipline

FRL distinguishes:

- event time;
- information-availability time;
- ingestion/retrieval time.

Final historical data does not prove that information was knowable at an earlier research/prediction cutoff.

Historical state and model evaluation must remain time-safe.

## 15. Research / modelling discipline

Adaptive Dixon-Coles V1 is currently an **experimental forecasting control**, not a trusted production betting model.

Model work should separate:

- historical association;
- predictive improvement;
- out-of-sample performance;
- calibration;
- market price;
- edge/expected value;
- staking/strategy.

The next controlled model progression should follow the preregistered Team State incremental-information experiment rather than unconstrained backtest search.

## 16. Quality and validation

`RISK_STRATEGY_FRAMEWORK.md` and `NON_DESTRUCTION_ASSURANCE.md` are the primary quality contracts.

For substantial work:

1. establish objective and definition of done;
2. inspect current behaviour/state;
3. define the change surface and non-goals;
4. predict failure modes;
5. implement the smallest sensible change;
6. run targeted validation;
7. run relevant regression/data/query/frontend gates;
8. perform a convergence check against the objective;
9. reconcile standing documentation when project-level state changes.

Do not treat old fixed test counts as current evidence.

## 17. Repository safety

Treat `main` as the stable integration line.

Before changing/integrating code:

- inspect branch/upstream/ahead-behind state;
- inspect Daniel's live local working tree when local changes may exist;
- preserve unrelated tracked/untracked/generated/backup work;
- do not use `git clean` or `git reset --hard` for ordinary workspace management;
- do not stage broadly with `git add .` without understanding the change surface;
- prefer reversible, scoped changes.

## 18. Key re-entry files

Start with:

1. `FRL_MASTER_PROMPT.md`
2. `PROJECT_ORIENTATION.md`
3. `CURRENT_WORK.md`
4. `data/frl_documentation_state_v1.json`
5. `AGENTS.md`
6. `FRL_REPOSITORY_RECONCILIATION_2026-09-13.md`
7. `FRL_DOCUMENTATION_SYNC_CONTRACT.md`
8. `RISK_STRATEGY_FRAMEWORK.md`
9. `NON_DESTRUCTION_ASSURANCE.md`
10. task-relevant source/identity/analytical/design contracts and implementation.

Do not assume this list alone defines the full preserved source ecosystem.

## 19. Documentation freshness

Repository documentation is operational memory.

Whenever a material milestone changes architecture, active product phase, source-routing/capability interpretation, validation interpretation or frontend/design language, reconcile the standing documents before calling the milestone complete.

## Final orientation principle

> **Preserve source truth, govern the analytical meaning, keep time honest, and make the repository describe the system that actually exists.**
