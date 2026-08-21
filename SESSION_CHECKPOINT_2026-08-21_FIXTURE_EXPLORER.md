# Fixture Explorer Session Checkpoint — 21 August 2026

This is the durable handoff for the Fixture Explorer work completed during the 20–21 August 2026 session.

## Branch / status

Active development branch:

`feature/next-foundation-spike-2026-08-20`

`main` remains the stable integration line. Do not promote this work to `main` implicitly.

## Architecture

```text
Next.js / React
    ↓ HTTP / JSON
FastAPI (`api/frl_api.py`)
    ↓
trusted `query_api.py`
    ↓
trusted `query_lab.py`
    ↓
canonical/local FRL evidence
```

The frontend must remain a downstream research view. Do not duplicate football business logic in React.

## Canonical identity rules

The core FRL fixture identity remains:

`Fixture = (season, fixture_id)`

`fixture_code` is a source/provider bridge used to connect fixture evidence to player-fixture evidence. It is **not** the canonical FRL fixture identity.

Season-local team identity must be resolved through the verified persistent club identity mechanism when reconstructing a club across seasons. Never infer continuity from display names or numeric coincidence.

## Fixture Explorer interaction grammar

The approved presentation is intentionally restrained:

- Large team name is the primary identity heading.
- A discrete chevron beside the team name indicates the selector.
- No card, pill, border or opaque background is placed behind the team heading.
- Season remains integrated beside the heading using the same quiet typographic selector language.
- Lower selectors belong in the purposeful `Explore fixtures` section and use the same transparent/typographic/underline/chevron language.
- Existing fixture row sizing, typography, spacing and subtle hover treatment are protected visual baselines.

The interaction grammar is:

```text
Opponent → team/fixture context
Score    → canonical fixture landing / match report
Scorers  → display scorer evidence; future player navigation only after canonical player identity is established
```

Do not make the whole fixture row a link. Individual semantic targets are preferred.

## Fixture viewing scope model

The page now distinguishes three concepts:

```text
Team   = research subject
Season = temporal scope
View   = presentation / analytical mode
```

The intended scope options are:

- Team selector: selected club or `All teams`.
- Season selector: selected season or `All seasons`.
- View selector: `All fixtures`, `Single season`, or `Multiple seasons`.

`All teams` is a genuine global fixture-universe scope. It must not be encoded as a fake football club.

`All seasons` uses the verified FRL season list.

Club-scoped multi-season viewing must use the verified persistent club identity to find the same club in each season; seasons without a defensible identity mapping are excluded rather than inferred.

## Global fixture-table semantics

For a selected club, the table remains:

```text
Date | Opponent | Venue | Score | Scorers | Result
```

with W/D/L in `Result`.

For `All teams`, the table becomes:

```text
Date | Fixture | Venue | Score | Scorers | Outcome
```

where `Outcome` represents the neutral match result:

- `Home win`
- `Draw`
- `Away win`

The compact UI may render `H win`, `Draw`, `A win` while retaining the full meaning in the underlying value/title.

Do not let the global wording change the underlying row geometry. Header and row must continue to share the same grid definition.

The fixture table was corrected to six desktop columns after the scorer column was introduced. Preserve this geometry and do not add one-off layout hacks for global mode.

## Scorer provenance

Scorer enrichment was traced to the existing player-fixture evidence path:

```text
fixture (season, fixture_id)
      ↓
fixture_code source bridge
      ↓
season player rows
      ↓
goals_scored
      ↓
query_lab.fixture_scorer_map / fixture_scorers
      ↓
query_api.fixtures()
      ↓
FastAPI Research Result
      ↓
Fixture Explorer
```

Fixture 9 in 2025-26 was directly verified as:

- fixture code `2561903`;
- scorer `Riccardo Calafiori`;
- 1 goal.

Never infer scorer names from the final scoreline.

## Stadium decision

`fixtures_master_corrected.csv` currently exposes no trusted field containing stadium, ground or stadium-name information.

Stadium/ground display is therefore **parked**. Do not introduce or fabricate a stadium field merely to fill the UI.

## Reliability / hydration lesson

The migrated page previously emitted a React hydration warning because initial server/client `disabled` values differed. The initial `loading` and `contextLoading` state was made deterministic (`false`) so first render is stable.

Future changes must preserve deterministic first render.

## Validation state

Validated during the session:

- FastAPI Arsenal fixture Research Result works.
- FastAPI global fixture query works as `fixtures:2025-26:all-teams:all:all:all`.
- Scorer enrichment works in the trusted query layer and through `query_api`.
- `npm run typecheck` passed repeatedly after the incremental frontend patches.
- The desktop fixture grid was corrected to six aligned columns.

Still required at the next checkpoint after the latest scope/UI edits:

```powershell
npm run typecheck
npm run gui-regression
npm run build
```

Also re-check the four main combinations:

```text
Arsenal + 2025-26
Arsenal + All seasons
All teams + 2025-26
All teams + All seasons
```

The final GUI check should verify that the approved Arsenal presentation is unchanged.

## Recovery rule

Never replay an old patch against `web/src/components/FixtureExplorer.tsx` or `web/src/app/globals.css` from memory or from a previous file body.

Local files and GitHub can diverge. Inspect the exact current local/GitHub file and patch the smallest possible surface.

Repository documentation is durable project memory; conversation is working context.
