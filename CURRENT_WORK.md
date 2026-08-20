# Current Work — Football Research Laboratory

**Last updated:** 20 August 2026

## Active branch

`feature/next-foundation-spike-2026-08-20`

This is the current frontend-migration development line, branched from `feature/site-functionality-2026-08-19`. `main` remains the stable integration line.

## Current platform checkpoint

The FRL data-platform work remains deliberately additive and local-first.

The trusted canonical entity, relationship, provenance and temporal contracts remain authoritative and unchanged by the frontend migration.

## Frontend migration checkpoint

The project has formally moved to a **private-first, public-ready React + Next.js frontend migration** strategy.

Authoritative migration document:

- `FRL_MASTER_FRONTEND_MIGRATION_PLAN_V2.md`

Current visual authority:

- `gui/theme.py`
- `GUI_DESIGN_CONTRACT.md`
- `UI_DESIGN_SYSTEM.md`

The current live FRL visual system is the warm light analytical theme; the older dark main-canvas description is historical and must not be used as the basis for new UI work.

## Next.js foundation + Fixture Explorer checkpoint

The reversible migration spike is now present under `web/`, and Fixture Explorer is the first real migrated workspace rather than a static visual clone.

Current stack:

```text
Next.js / React
    ↓ HTTP / JSON
FastAPI (`api/frl_api.py`)
    ↓
existing trusted `query_api.py` seam
    ↓
canonical/local FRL data
```

The frontend must continue to consume research/query results rather than duplicate backend business logic.

### Validated backend seam

FastAPI currently exposes:

- `GET /health`
- `GET /api/v1/seasons`
- `GET /api/v1/teams/{season}`
- `GET /api/v1/fixtures/{season}?team=...`

The fixture endpoint delegates to the existing trusted `query_api.fixtures()` implementation.

The returned Research Result includes, where applicable:

- result data;
- population/sample size;
- active filters;
- season/competition scope;
- canonical fixture references as `(season, fixture_id)`;
- provenance and transformation/query version;
- methodology notes;
- explicit limitations.

The current endpoint does **not** assert historical information-availability snapshots. The frontend must not infer those semantics independently.

### Fixture Explorer current behaviour

The Next workspace now supports:

- real Team + Season context loaded from FastAPI;
- Team chosen from the selected season's trusted team list;
- Season as URL-backed context;
- Team as URL-backed context;
- opponent filter;
- venue filter;
- result filter;
- canonical fixture links `/fixtures/{season}/{fixtureId}`;
- grouped chronological fixture rows;
- W/D/L record summary;
- fail-closed loading/error behaviour;
- Research Result provenance/summary information.

Current visual treatment:

- large team name remains the primary identity heading;
- a discrete chevron beside the team name opens the team selector;
- the team heading itself has no surrounding box, pill, border or background treatment;
- Season remains integrated in the page-heading area using the same quiet selector language;
- lower exploration controls live in a dedicated `Explore` / `Fixture view` section;
- lower selectors use the same transparent, typographic, underline + chevron language as the Season selector;
- fixture rows dominate the page and use restrained hover/interaction states.

The approved selector precedent is now:

```text
Context selector
  → integrated into heading
  → transparent / typographic / subtle underline / discrete chevron

Exploration selector
  → integrated into a purposeful research section
  → same visual language
  → no generic boxed form controls
```

This is a reusable FRL GUI pattern and should be preferred across future Next workspaces.

## Fixture Explorer — next planned capability

The `Explore fixtures` section is deliberately the structural home for richer fixture analysis without disturbing the clean header context.

Planned progression:

1. current opponent/venue/result filters — **implemented**;
2. single-season vs multi-season viewing — **next**;
3. opponent comparison across a selected period — **next-stage extension**;
4. venue/result filtering retained across the selected population — **preserve**;
5. compact time-range/comparison control — **later**;
6. deeper cross-time/team/opponent analysis belongs in Team Research / Research Result surfaces rather than turning Fixture Explorer into a general modelling workspace.

Do not move or overload the existing header Season selector merely to add these capabilities. The header establishes page context; the `Explore` section provides deeper research controls.

## Validation / recovery procedure

For fresh-session recovery:

1. read the Master Prompt and authoritative project documents;
2. establish the active branch and repository state;
3. inspect the current Next/API files before patching;
4. make changes against the exact current GitHub file SHA;
5. never blindly replay an old patch against `web/src/components/FixtureExplorer.tsx` or `web/src/app/globals.css`;
6. sync only the surgical files required for the change;
7. locally validate `npm run typecheck` and `npm run build` for frontend changes;
8. locally validate FastAPI health/API responses when API changes are involved;
9. backend/data/research semantic changes still require the established 26/26 and project-health gates.

### Local development processes

```text
FastAPI → 127.0.0.1:8000
Next.js → localhost:3000
```

Recommended clean start:

```powershell
# terminal 1
cd C:\Users\dlall\football_database\football-research-lab
python -m uvicorn api.frl_api:app --reload --port 8000

# terminal 2
cd C:\Users\dlall\football_database\football-research-lab\web
npm run dev
```

Validation examples:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/fixtures/2025-26?team=Arsenal"
```

Python 3.14 is currently in use locally. The Next API dependency set therefore requires a Pydantic version with Python 3.14 support; the current repository pin is `pydantic==2.13.4`.

## Deployment direction

The FRL is **private-first, public-ready**:

```text
local
  ↓
private shared (initially ~3 invited users beyond the owner)
  ↓
public when explicitly approved
```

Stable, shareable entity and Research Result URLs are part of the long-term frontend contract. Going public should be an access/deployment decision, not a future rewrite of route or research architecture.
