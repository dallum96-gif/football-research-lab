# FRL contributor instructions

These rules apply to all work in this repository. Linked contracts remain authoritative.

Repository-memory governance is defined in `FRL_DOCUMENTATION_SYNC_CONTRACT.md`.

## Re-enter the project before changing it

- Treat stable `main` and `dallum96-gif/football-research-lab` as the authoritative integrated state. Do not assume another branch, worktree, backup or archived implementation is integrated.
- At the start of substantive work, check current branch, working tree, remotes, upstream and ahead/behind state; fetch before relying on remote state.
- Read `FRL_MASTER_PROMPT.md`, `PROJECT_ORIENTATION.md`, `CURRENT_WORK.md` and `data/frl_documentation_state_v1.json` before assuming current product/architecture state.
- Inspect relevant implementation, durable contracts and dated audits before proposing a material change.
- Historical status/closeout documents are checkpoint evidence, not automatic statements of current state.
- Do not ask the user to reconstruct information recoverable from the repository, working implementation, relevant history or known preserved source ecosystem.
- State objective, definition of done, change surface, validation plan and whether the task is research/audit work or implementation work. Do not silently broaden scope.

## Preserve FRL's governing purpose

- FRL is a provenance-aware historical football research environment, not one dashboard, metric or betting model.
- Research/explanation precede downstream modelling, market and betting decisions.
- Preserve evidence broadly enough that future questions do not require rebuilding the database around today's favourite metric.

## Current analytical architecture direction

The target analytical spine is:

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

Existing code remains transitional. Reuse trusted seams while migrating toward the target architecture; do not assume every layer already exists centrally.

## Active frontend / API

- Next.js + React under `web/` is the active frontend.
- FastAPI under `api/` is the frontend-facing Python boundary.
- Python remains authoritative for source routing, identity, temporal, provenance, statistical, analytical and modelling semantics.
- Streamlit is legacy/reference implementation unless a task explicitly concerns it.
- Do not add browser-side reads of source files or source-specific storage paths.
- Do not duplicate football/research calculations in TypeScript merely because the page can calculate them locally.

## Source discovery and routing

- Follow `FRL_DATA_ECOSYSTEM_DISCOVERY_CONTRACT.md` before declaring evidence absent or acquiring another source.
- Read `FRL_SOURCE_NORMALISATION_CONTRACT.md`, `FRL_SOURCE_ROUTE_AUDIT_2026-08-30.md` and `FRL_SOURCE_RIGHTS_REGISTER.md` before changing source selection/acquisition.
- A field existing does not prove a research metric exists.
- A metric being connected does not prove the connected source is the strongest representation preserved anywhere in the ecosystem.
- Do not implement “first non-null source wins”.
- Select source representation using football concept + requested grain + competition/period/as-of context + analytical purpose.
- Preserve source/version identity when representations differ or equivalence is unproven.
- When a capability is not found, inspect current/archived consumers, repository datasets, local upstream/source workspaces, raw snapshots, source-family variants, identity bridges and derived datasets before designing a substitute.

## Capability-state discipline

Where relevant distinguish:

```text
SOURCE_PRESENT
CONNECTED
DERIVABLE
GOVERNED
COMPARABLE
PRODUCT_READY
```

Do not collapse these into a single “available” flag.

## Fixture/result seams

- Fixture identity within the current Premier League universe remains `(season, fixture_id)`; preserve canonical deep links and do not create a second fixture universe.
- Before adding another competition, explicitly resolve the future competition component of global fixture identity.
- Fixture Explorer lives at `web/src/components/FixtureExplorer.tsx`; result workspace lives under `web/src/app/fixtures/[season]/[fixtureId]/`.
- Canonical fixture detail/statistics use established Python query/statistics seams; optional event/lineup/formation/manager evidence uses governed source relationships/snapshots.
- Preserve known corrections and their additive provenance.
- Missing optional evidence is a valid state; never fabricate it.

## Identity, relationship, temporal and provenance rules

- Read `DATA_CONSTRUCTION.md`, identity/relationship contracts and `PLAYER_MATCH_SOURCE_BRIDGE.md` before changing joins.
- Source identifiers are evidence, not canonical identifiers.
- Keep season-local team identity distinct from persistent club identity.
- Keep FPL seasonal identity, Player-Match source identity, Player-Season identity and canonical/research player identity distinct unless an explicit bridge says otherwise.
- Player identity, team membership and fixture identity are separate relationships.
- Preserve event time, information-availability time and ingestion/retrieval time as distinct concepts.
- Historical/as-of results may use only information available at the relevant cutoff.
- Preserve source lineage, transformation/version metadata, limitations, coverage and correction history.

## Missingness, aggregation and population rules

- Missing evidence is not zero.
- Aggregates should expose eligible/observed/missing populations where coverage can vary.
- Do not divide partial observed totals by complete populations unless that is explicitly the metric definition.
- Percentages/ratios generally require correct numerator/denominator aggregation rather than averaging displayed percentages.
- Player → team derivation requires concept-specific aggregation proof and governed identity/coverage.
- A rank/percentile requires an explicit eligible population, coverage rules, tie policy and percentile method.
- Do not rank partial/incomparable observations as though they were complete and equivalent.

## Team / Player product architecture

Current rule:

> **Profiles describe entities. Stats analyse entities. Rankings analyse populations. Compare analyses selected entities together. Research tests the questions these surfaces reveal.**

Read `FRL_TEAM_PLAYER_STATS_VISUALISATION_PROTOTYPE.md`.

Team View and League Rankings should ultimately be projections of the same governed analytical result.

Player rankings require player-specific cohorts/minutes/role semantics rather than blindly copying team league populations.

## Source acquisition and rights guardrails

- A public endpoint, public repository or downloadable file does not itself prove unrestricted bulk reuse/redistribution/commercial rights.
- Prefer already-preserved evidence and explicitly licensed/open sources where practical.
- Do not make recurring large-scale direct API extraction a foundational dependency unless intended use is permitted/reviewed.
- Preserve already-acquired evidence/provenance without inferring redistribution rights.
- Derived FRL data can inherit upstream rights dependencies.

## Change and repository safety

- Prefer the smallest sensible, reversible change at an established seam.
- Follow `NON_DESTRUCTION_ASSURANCE.md` and `RISK_STRATEGY_FRAMEWORK.md`.
- Do not modify canonical data, identity registries, schemas or architecture merely to simplify a UI task unless the task genuinely requires it.
- Preserve unrelated tracked/untracked/generated/experimental/backup/worktree content.
- Avoid broad staging, destructive cleanup, force/history rewriting or deletion merely to obtain a tidy status.
- Surface uncertainty, conflicts and incomplete coverage. “Not found” is not automatically “absent”.

## Validation

Choose checks proportionate to the change:

- targeted unit/regression tests first;
- relevant research-access/identity/query/data gates;
- Next.js `typecheck` / `build` for frontend contracts;
- `project-health.ps1` where canonical/query/data behaviour may be affected;
- `python scripts/check_documentation_sync.py` for documentation/milestone state.

Dated validation counts are historical checkpoints. Report actual current command output; never claim a gate passed unless it was run for the relevant state.

## Documentation synchronisation

Repository documentation is operational memory.

Whenever a milestone materially changes current architecture, active product phase, source-routing/capability interpretation, validation interpretation, frontend status or design language:

1. reconcile relevant living documents;
2. check affected durable contracts for contradiction;
3. update `data/frl_documentation_state_v1.json` when the checkpoint changes;
4. run the documentation-sync gate;
5. leave historical checkpoint records intact unless they are factually erroneous about their own date.

A material milestone is not complete until this reconciliation has happened.
