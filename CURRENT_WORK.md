# Current Work — Football Research Laboratory

**Last updated:** 21 August 2026

## Active branch

`feature/next-foundation-spike-2026-08-20`

This is the current frontend-migration development line, branched from `feature/site-functionality-2026-08-19`. `main` remains the stable integration line.

## Current platform checkpoint

The FRL data-platform work remains deliberately additive and local-first.

The trusted canonical entity, relationship, provenance and temporal contracts remain authoritative and unchanged by the frontend migration.

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

FastAPI exposes:

- `GET /health`
- `GET /api/v1/seasons`
- `GET /api/v1/teams/{season}`
- `GET /api/v1/team-seasons?persistent_team_code=...`
- `GET /api/v1/fixtures/{season}?team=...`

The fixture endpoint delegates to the existing trusted `query_api.fixtures()` implementation.

The fixture Research Result carries result data, population/sample size, active filters, temporal/competition scope, canonical fixture references as `(season, fixture_id)`, provenance, methodology and explicit limitations.

The endpoint does not assert historical information-availability snapshots. The frontend must not infer those semantics independently.

## Fixture Explorer current behaviour

The migrated `/fixtures` workspace now has the following durable interaction model:

```text
Team   = research subject
Season = temporal scope
View   = presentation / analytical mode
```

Supported/implemented behaviour includes:

- real Team + Season context from FastAPI;
- URL-backed Team and Season state;
- opponent filtering;
- venue filtering;
- result filtering;
- `All fixtures` / `Single season` / `Multiple seasons` view modes;
- club-scoped multi-season reconstruction using verified persistent team identity;
- an `All teams` global fixture scope at the API level;
- an `All seasons` temporal scope at the API/UI state level;
- chronological month grouping;
- canonical fixture deep-links at `/fixtures/{season}/{fixtureId}`;
- opponent entity/context links;
- score as the vehicle to the canonical fixture landing / match report;
- scorer display sourced from the trusted player-fixture evidence path;
- fail-closed loading/error behaviour;
- Research Result provenance/summary information.

### Scorer provenance

Scorer enrichment is not inferred from scorelines. The verified chain is:

```text
Fixture (season, fixture_id)
      ↓
source fixture_code bridge
      ↓
season player rows with goals_scored
      ↓
query_lab fixture scorer enrichment
      ↓
query_api.fixtures()
      ↓
FastAPI Research Result
      ↓
Fixture Explorer
```

Fixture 9 in 2025-26 was directly verified as fixture code `2561903` with Riccardo Calafiori scoring 1 goal.

The player key is carried for future identity-aware navigation, but player navigation must wait for canonical player-identity resolution rather than treating the source key itself as canonical.

### Global fixture semantics

For a selected club, preserve the normal table semantics:

```text
Date | Opponent | Venue | Score | Scorers | Result
```

with W/D/L in Result.

For `All teams`, the neutral table semantics are:

```text
Date | Fixture | Venue | Score | Scorers | Outcome
```

where Outcome is calculated from the raw home/away scores as `Home win`, `Draw` or `Away win`. The compact UI may render `H win`, `Draw`, `A win` while keeping the full meaning available as metadata/title.

The table now uses six desktop grid columns so the Scorers and Outcome columns remain aligned with the header and do not disturb the established row geometry.

### Visual authority / GUI contract

The current visual treatment is an approved baseline and must not be casually redesigned:

- warm light analytical canvas with dark navigation sidebar;
- large team name as identity heading;
- discrete chevron beside team name;
- no card/pill/border/opaque background behind the team heading;
- Season integrated beside the heading using the same quiet selector language;
- lower Explore controls use transparent/typographic/underline/discrete-chevron treatment;
- fixture rows retain their existing sizing, spacing, typography and subtle hover treatment;
- new functionality should fit inside this visual language rather than add UI chrome.

### Stadium / ground

Stadium name is intentionally parked. `fixtures_master_corrected.csv` currently contains no trusted stadium/ground/venue-name field. Do not invent or infer stadium names, and do not introduce an alternative football-data provider solely to fill this gap while the current source-boundary contract remains active.

## Hydration / reliability lessons

The migrated page previously produced a React hydration warning because initial server/client `disabled` attributes differed. Initial `loading` and `contextLoading` state was made deterministic (`false`). Preserve deterministic first render in future changes.

The team fallback was also changed so the deliberate `team=""` All teams state is not treated as an invalid team and reset to Arsenal.

## Current GUI regression practice

Any new GUI feature must be checked against the existing behaviour, not merely checked for whether the new feature itself renders.

Minimum frontend gate:

```powershell
npm run typecheck
npm run gui-regression
npm run build
```

API changes should additionally validate:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

and the relevant endpoint.

Research/data/backend semantic changes still require the established 26/26 research tests and project-health gate.

## Validation state at session handoff

Validated during the 20–21 August session:

- FastAPI Arsenal fixture Research Result works.
- FastAPI global fixture query works as `fixtures:2025-26:all-teams:all:all:all`.
- `query_lab` scorer enrichment works directly.
- `query_api.fixtures()` carries scorer enrichment.
- `npm run typecheck` passed repeatedly after incremental frontend fixes.
- fixture-row navigation was separated so Opponent and Score are semantic interaction targets without wrapping the whole row in a link.
- desktop six-column fixture grid was corrected after the scorer column was introduced.

After the final All teams/All seasons UI edits, rerun the complete frontend gate before treating the session as fully closed:

```powershell
npm run typecheck
npm run gui-regression
npm run build
```

Then verify:

```text
Arsenal + 2025-26
Arsenal + All seasons
All teams + 2025-26
All teams + All seasons
```

## Recovery / non-destruction procedure

For fresh-session recovery:

1. Read the Master Prompt and authoritative project documents.
2. Read `CURRENT_WORK.md` and `SESSION_CHECKPOINT_2026-08-21_FIXTURE_EXPLORER.md`.
3. Establish the active branch and repository state.
4. Inspect the exact current Next/API/CSS files before patching.
5. Never blindly replay an old patch against `web/src/components/FixtureExplorer.tsx`, `web/src/lib/api.ts`, `api/frl_api.py` or `web/src/app/globals.css`.
6. Prefer the smallest possible change surface.
7. Validate old behaviour as well as new behaviour.
8. Preserve canonical fixture identity, persistent team identity, player identity, Player–Fixture grain, Team–Fixture relationships, provenance and temporal semantics.

Repository documentation is durable project memory; conversation is working context.

## Local development processes

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

Python 3.14 is currently in use locally. The current Pydantic pin is `pydantic==2.13.4`.

## Deployment direction

The FRL remains **private-first, public-ready**. Stable, shareable entity and Research Result URLs remain part of the long-term frontend contract.
