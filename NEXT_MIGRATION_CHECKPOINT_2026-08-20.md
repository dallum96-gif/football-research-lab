# Next.js Migration Checkpoint — 20 August 2026

This document records the validated state at the first real Fixture Explorer checkpoint. It exists as a recovery aid for future sessions and must be read alongside `CURRENT_WORK.md`, `FRL_MASTER_FRONTEND_MIGRATION_PLAN_V2.md`, `GUI_DESIGN_CONTRACT.md` and the Master Prompt.

## Source of truth

Repository: `dallum96-gif/football-research-lab`

Active migration branch: `feature/next-foundation-spike-2026-08-20`

Stable integration line: `main`

Do not treat the local working tree as authoritative when local and GitHub diverge. Recover the intended state from the migration branch and the authoritative project documents first.

## Architecture checkpoint

```text
Next.js / React
      ↓
HTTP / JSON
      ↓
FastAPI (`api/frl_api.py`)
      ↓
trusted `query_api.py` seam
      ↓
canonical/local FRL data
```

The frontend does not own statistical/business logic.

FastAPI is an adapter/boundary, not a replacement for the trusted Python research/query layer.

Do not copy canonical fixture/team/player data into `web/` merely to make the UI work.

## Validated API surface

```text
GET /health
GET /api/v1/seasons
GET /api/v1/teams/{season}
GET /api/v1/fixtures/{season}?team=...
```

The fixture endpoint delegates to `query_api.fixtures()`.

The response is a Research Result carrying, where applicable:

- result data;
- population/sample size;
- active filters;
- season/competition scope;
- canonical fixture references as `(season, fixture_id)`;
- provenance and transformation/query version;
- methodology notes;
- explicit limitations.

The current fixture endpoint explicitly does **not** assert historical information-availability snapshots.

## Fixture Explorer checkpoint

Route:

```text
/fixtures
```

Fixture landing route already follows:

```text
/fixtures/{season}/{fixtureId}
```

The Fixture Explorer currently provides:

- real Team + Season context from FastAPI;
- URL-backed Team and Season state;
- canonical fixture deep-links;
- opponent filtering;
- venue filtering;
- result filtering;
- chronological month grouping;
- W/D/L summary;
- fail-closed loading/error behaviour;
- Research Result provenance display.

## Approved selector pattern

The most important current visual precedent is the integrated Team/Season treatment.

### Team

The large team name is the page identity.

It is shown once and has a discrete chevron beside it indicating that the heading is interactive.

The team heading must not have:

- a card background;
- a pill;
- a heavy border;
- a generic input appearance.

Clicking the heading/chevron exposes a restrained team choice menu.

### Season

Season remains at heading level, in the space beside the main context, using the same quiet typographic selector grammar.

Do not move it into a large filter panel just to support future analytical features.

### Exploration controls

Opponent, venue and result belong below the header in a purposeful `Explore / Fixture view` section.

They use the same visual language as the Season selector:

- transparent;
- typographic;
- quiet underline/subtle boundary;
- discrete chevron;
- no generic boxed widgets.

This is now the default selector grammar for future Next.js workspaces unless explicitly superseded by a later design-system decision.

## Explore fixtures roadmap

The `Explore fixtures` section is deliberately the home for richer fixture exploration.

Current:

- opponent selector — implemented;
- venue selector — implemented;
- result selector — implemented.

Next:

- single-season vs multi-season viewing.

Then:

- opponent comparison across a selected period;
- retained venue/result filtering across the selected population;
- compact time-range/comparison control.

Deeper cross-time analytical questions should move naturally into Team Research / Research Result surfaces rather than turning Fixture Explorer into a general-purpose modelling page.

Header rule:

> **Header = identity and context. Explore section = deeper analytical control.**

Do not overload the clean header with multi-season/date-range machinery.

## UX rules established during migration

The page should feel like a serious football research record, not a generic SaaS dashboard or a collection of widgets.

The fixture rows should dominate the viewport.

Use restrained accent colour for hierarchy and interaction rather than colouring every control.

Prefer subtle text/entity interactions over large rectangular buttons.

Do not duplicate a visible team name simply because a selector is needed.

Avoid dark main-canvas treatments; the authoritative visual identity is the current warm light theme with dark navigation sidebar.

## Local development

Python 3.14 is currently used locally.

FastAPI:

```powershell
cd C:\Users\dlall\football_database\football-research-lab
python -m uvicorn api.frl_api:app --reload --port 8000
```

Next.js:

```powershell
cd C:\Users\dlall\football_database\football-research-lab\web
npm run dev
```

URLs:

```text
FastAPI: http://127.0.0.1:8000
Next:    http://localhost:3000
Fixture Explorer: http://localhost:3000/fixtures
```

Validation:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/fixtures/2025-26?team=Arsenal"
```

Frontend:

```powershell
npm run typecheck
npm run build
```

## Dependency note

Python 3.14 requires a Pydantic line with compatible `pydantic-core` wheels. The current migration requirement is:

```text
pydantic==2.13.4
```

Do not work around this by installing Visual Studio/Rust merely to compile an older `pydantic-core` unless a future dependency decision explicitly requires it.

## Recovery protocol

When returning to this project after interruption:

1. Read the Master Prompt and authoritative project documents.
2. Read this checkpoint and `CURRENT_WORK.md`.
3. Establish the active Git branch and GitHub state.
4. Fetch the migration branch before assuming local files are current.
5. Inspect the exact current GitHub file SHA before any surgical update.
6. Never replay an old patch based on a stale file body/SHA.
7. Sync only the exact files required locally.
8. For frontend-only work, validate `npm run typecheck` and `npm run build`.
9. For API work, validate `/health` and the relevant endpoint.
10. Backend/data/research semantic changes must still pass the established 26/26 and project-health gates.

## Non-destruction boundary

Do not use the frontend migration as a reason to alter:

- canonical fixture identity;
- season-local vs persistent team identity;
- canonical player identity;
- Player–Fixture grain;
- Team–Fixture relationships;
- provenance semantics;
- temporal/historical-state semantics;
- source precedence;
- Risk Strategy Framework validation requirements.

When a new UI requirement appears, extend the presentation/API boundary rather than weakening the underlying research contracts.
