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

## Next.js foundation spike

The first reversible migration spike is now present under `web/`.

It currently proves:

- Next.js + React application structure;
- current FRL light-theme tokens;
- typed Research Result contract;
- one Research Result driving both a table and an interactive Plotly chart;
- canonical fixture references retaining `(season, fixtureId)` context;
- a typed frontend API boundary that leaves business logic in Python.

The spike intentionally uses static demo data and does **not** replace Streamlit, `query_api.py`, `query_lab.py` or the trusted canonical data layer.

## Validation still required locally

Because the repository connector cannot execute the user's Node environment, the next local validation must prove:

1. `npm install` completes in `web/`;
2. `npm run typecheck` passes;
3. `npm run build` passes;
4. the demo page renders;
5. selecting a chart point changes the exact table/detail selection;
6. the current FRL colour system and typography are visually faithful;
7. the production API adapter can later connect to the existing Python research/query seam without duplicating business logic.

The existing Python 26/26 research regression baseline and project-health gate remain mandatory for substantive backend/data changes. This frontend spike is presentation-only and must not modify those research semantics.

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
