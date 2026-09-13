# FRL Repository Reconciliation — 13 September 2026

**Status:** dated reconciliation checkpoint  
**Scope:** tracked remote repository state, living documentation drift, active product/design branch and validation interpretation  
**Repository-memory contract:** `FRL_DOCUMENTATION_SYNC_CONTRACT.md`

## Purpose

This checkpoint reconciles FRL's standing repository memory with the product and design work that progressed after the 7 September documentation checkpoint.

It is deliberately a dated record. Future living documents may supersede its current-state statements while this file remains as evidence of what was established on 13 September 2026.

## Repository state established

At the start of this reconciliation:

- stable `main` was at `0626878838b0734b7df8d79f966e814db75a61ed` (`style: expand matchday bet builder workspace`, 9 September 2026);
- `design/analyst-workspace-v1` had advanced to `6af8e469917ac9b3b1d36decd5a3fb0c162b5303` (`style: label foul and yellow-card leaders`);
- active reference branch `design/bet-builder-reference-v1` was at `ce8fa1493553923306cd0011c6146f821101b66e` (`feat: apply curated stadium visual overrides`, 10 September 2026);
- draft PR #53 remained open against `design/analyst-workspace-v1`;
- the active reference branch was 79 commits ahead of its merge base and 4 commits behind the then-current `design/analyst-workspace-v1` head;
- PR #53 changed 116 tracked files before this documentation reconciliation.

This means the reference branch is an active product/design experiment, not a clean merge candidate.

## Important scope boundary

This reconciliation is authoritative for the tracked remote state that could be verified through GitHub.

It does **not** claim visibility into Daniel's live local Windows working tree or any uncommitted local changes. Local development may be newer than the remote head. A later integration step must therefore establish live local `git status`, upstream state and diff before merging or deleting anything.

## What had drifted

### Current-work documentation

`CURRENT_WORK.md` still described the 7 September Player-rich / Analytical Profile + Head-to-Head checkpoint as the immediate product state. That capability checkpoint remains useful evidence, but it no longer described the active product/design work.

### Product roadmap

`FRL_SHORT_TERM_PRODUCT_ROADMAP.md` still named reconciliation/industrialisation of the 249 team-match-statistic source surface as the next highest-priority task even though that milestone had subsequently been completed and recorded in `CURRENT_WORK.md`.

### Visual system

`UI_DESIGN_SYSTEM.md` still treated the earlier warm parchment palette and permanent dark sidebar as the active design authority. The active product branch had already introduced a two-level top-navigation shell, premium Fixtures/result work, Matchday reference work and richer Team Profile presentation.

The latest accepted FRL design direction has also moved toward a darker premium/editorial visual language: near-black/charcoal structure, warm ivory/cream text, muted greys and restrained coral/orange emphasis. Green/olive remains semantic/supporting rather than a default decorative brand colour; lime-green styling is not part of the desired FRL identity.

The codebase is mid-migration: legacy warm root tokens still exist in `web/src/app/globals.css` and some older surfaces. Those tokens are implementation debt during migration, not permission to resurrect the old design direction on new work.

### PR #53 description

PR #53 described itself primarily as a presentation prototype and claimed that no fixture data/query/research logic or API contracts had changed.

That wording was too strong for the actual branch surface. The branch includes tracked changes in supporting backend and research-access code, including `api/frl_api.py`, `api/fixture_evidence.py`, `api/player_performance.py`, `fixture_research_access.py`, new `fixture_metadata_evidence.py`, `club_profile_registry.py`, reference club-profile data and new tests.

This does **not** prove that public API semantics were intentionally broken. It does mean the PR must be reviewed and validated as a product branch with supporting backend/evidence changes, not represented as CSS-only or frontend-only work.

## Active product/reference work now represented

The active branch contains, among other work:

- a restrained two-level top navigation shell replacing the permanent sidebar for the reference experience;
- a premium Fixtures experience and fixture-result workspace;
- a Matchday Bet Builder reference route;
- Team Profile / Team Overview reference work;
- club crest and stadium imagery support;
- a governed club-profile reference registry plus visual overrides;
- supporting fixture-evidence, player-performance and runtime/API work;
- new regression/registry tests for the added evidence paths.

The durable analytical architecture remains unchanged in principle: Python remains authoritative for identity, provenance, temporal semantics, source routing, analytical meaning and modelling; the Next.js product should consume governed results rather than inventing football semantics in the browser.

## Preserved validated analytical checkpoints

This reconciliation does not invalidate the earlier data/research milestones. The latest standing evidence still includes:

- 553 preserved PulseLive raw paths, including 249 team-match statistical paths;
- the governed team-match milestone with 176 canonical/governed generic-access fields, 8 retained fields, 6 restricted fields and 59 preserved raw-only routed representations;
- an 86-field Player-Match source universe with 81 exposed research fields, 4 retained fields and 1 restricted duplicate;
- archive-wide fixture event/tactical routing across 3,800 Premier League fixture snapshots;
- the last formally validated rich current-season Player checkpoint at 79/83 product capabilities through GW1–3;
- Team State V1 plus Adaptive Dixon-Coles V1 as an experimental forecasting control, not a trusted production betting model;
- Head-to-Head / BetBuilder evidence as descriptive governed football evidence, with `evidence_index` explicitly not a calibrated probability.

Later local/current-season work must be revalidated before it replaces those standing checkpoint claims.

## Validation state

No GitHub Actions workflow run was attached to the pre-reconciliation active reference head `ce8fa1493553923306cd0011c6146f821101b66e`.

Therefore the current reference branch must **not** be described as fully validated.

Before integration, validation should include at least:

1. base-branch reconciliation and conflict review;
2. targeted Python/regression tests for changed backend/evidence seams;
3. club-profile/reference-data validation;
4. Next.js `npm run typecheck`;
5. Next.js `npm run build`;
6. `project-health.ps1` where canonical/query/data behaviour is implicated and a suitable local environment is available;
7. `python scripts/check_documentation_sync.py --base-ref <appropriate-base>`;
8. explicit review of API compatibility for the large `api/frl_api.py` diff.

No historical pass count should substitute for those current-state checks.

## Documentation decisions from this reconciliation

Living documentation should now follow these rules:

- the 7 September analytical milestone remains historical/validated evidence, not the current product phase;
- the active reference product work is represented explicitly and separately from stable `main`;
- the visual language is dark premium/editorial in current direction, with legacy warm tokens treated as migration debt rather than design authority;
- Fixtures, result, Matchday and Team Profile are open product/design work and must not be described as frozen merely because an older document said so;
- PR #53 is a mixed product/frontend/supporting-backend branch and must be validated accordingly;
- local-only/uncommitted work must never be silently claimed as integrated remote repository state.

## Immediate next sequence

1. keep the living docs and documentation manifest aligned with this checkpoint;
2. reconcile the active reference branch with the four newer base-branch commits before integration;
3. establish the live local working-tree state before any merge/rebase that could affect uncommitted work;
4. run current validation gates;
5. resolve any API/backend regressions or design-token migration issues;
6. only then consider PR #53 an integration candidate;
7. continue the product programme from the governed evidence layer: Fixture Intelligence / Matchday, Team and Player analytical profiles, Rankings/Compare and Research Explorer.

## Closing interpretation

The governing project shape has not changed: FRL remains a provenance-aware football research environment whose product surfaces expose governed evidence.

What changed is the active product phase. By 13 September, FRL had moved beyond the earlier source-industrialisation milestone into a substantial product/reference-design programme. Repository memory must reflect that without converting an experimental branch into a false claim of stable integration.
