# Football Research Laboratory

A provenance-aware historical football research and modelling platform, currently centred on ten seasons of Premier League evidence.

## Returning to the project

Start here:

1. `FRL_MASTER_PROMPT.md`
2. `PROJECT_ORIENTATION.md`
3. `CURRENT_WORK.md`
4. `data/frl_documentation_state_v1.json`

Repository-memory rules are defined in `FRL_DOCUMENTATION_SYNC_CONTRACT.md`.

Dated audits/closeouts are historical checkpoint evidence. Do not treat an older status document or test count as current merely because it remains in the repository.

## Current product stack

Active frontend:

- **Next.js + React** under `web/`

Frontend-facing backend:

- **FastAPI** under `api/`

Research/data logic remains Python-authoritative.

Streamlit code remains in the repository as legacy/reference implementation. It is not the target architecture for new UI work.

## Current architectural direction

```text
preserved source evidence
    ↓
identity / relationships
    ↓
source representation
    ↓
governed source route
    ↓
governed variable
    ↓
metric + coverage / missingness
    ↓
population / comparability
    ↓
analysis result
    ↓
FastAPI
    ↓
Next.js / Research consumers
```

The current implementation is transitional: older query/research seams remain valuable and should be migrated rather than casually rewritten.

## Core evidence / governance

Important foundations include:

- `fixtures_master_corrected.csv` — canonical fixture spine;
- `identity/team_seasons.csv` — season-local to persistent club identity;
- `identity/data_quality/fixture_corrections.csv` — correction provenance;
- `data/fixture_match_stats.csv` — packaged team-match statistics;
- `research_access.py` — Universal Research Access;
- `FRL_SOURCE_NORMALISATION_CONTRACT.md` — source meaning / multi-source rules;
- `FRL_SOURCE_ROUTE_AUDIT_2026-08-30.md` — current preserved-source routing evidence;
- `RISK_STRATEGY_FRAMEWORK.md` — quality architecture;
- `NON_DESTRUCTION_ASSURANCE.md` — migration/change safety.

## Product information architecture

Current rule:

> **Profiles describe entities. Stats analyse entities. Rankings analyse populations. Compare analyses selected entities together. Research tests the questions these surfaces reveal.**

The Team / Player Stats proposal is recorded in `FRL_TEAM_PLAYER_STATS_VISUALISATION_PROTOTYPE.md`.

Current product status and next sequence belong in `CURRENT_WORK.md` and `FRL_SHORT_TERM_PRODUCT_ROADMAP.md`.

## Frontend development

From `web/`:

```powershell
npm install
npm run dev
```

Useful checks:

```powershell
npm run typecheck
npm run build
```

## Python validation

Run the tests/gates appropriate to the change rather than relying on an old fixed baseline count.

Examples include:

```powershell
python -m pytest -q
.\project-health.ps1
python scripts\check_documentation_sync.py
```

Use targeted tests first where the full suite is unnecessary or depends on external/local source workspaces.

Dated closeout documents preserve historical validated checkpoints.

## Source discovery

Failure to find a field in one source, resolver or repository path is not proof that FRL lacks it.

Follow `FRL_DATA_ECOSYSTEM_DISCOVERY_CONTRACT.md` and inspect the relevant preserved source ecosystem before acquiring a replacement.

A connected source route is not automatically the strongest analytical representation available.

## Data-quality principles

- source identifiers remain source-local until reconciled;
- season-local team identity is distinct from persistent club identity;
- explicit corrections retain provenance;
- missing evidence is not zero;
- source/version differences remain visible when equivalence is unproven;
- derived metrics inherit source, coverage and temporal limitations;
- historical/as-of analysis must avoid future leakage.

## Git / workspace safety

Preserve unrelated tracked, untracked, generated, backup and research work. Avoid broad staging, destructive cleanup, history rewriting or deletion merely to obtain a tidy working tree. Prefer scoped, reversible changes.

## Repository

`dallum96-gif/football-research-lab`

Fresh clone:

```powershell
git clone https://github.com/dallum96-gif/football-research-lab.git
cd football-research-lab
```

Then read the repository-memory documents before assuming the current development state.

## Documentation-sync rule

> **A material milestone is not complete until the standing repository memory has been checked for drift.**

See `FRL_DOCUMENTATION_SYNC_CONTRACT.md`.
