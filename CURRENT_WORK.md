# Current Work — Football Research Laboratory

**Last updated:** 16 August 2026

This file is intentionally short and volatile. Update it whenever the active task, branch, checkpoint or next step changes.

## Active branch

`redesign-github-sync`

This is the current development branch for the GUI redesign work.

Do not assume `main` contains these changes. Establish branch state before changing code.

## Stable / validated baseline

Current research gate:

**26/26 tests passing**

Breakdown:

- Query Lab: 14/14
- Player Research V0.1: 6/6
- Player Research V0.2: 6/6

Project health gate remains the required data-quality verification alongside the research gate.

## Approved Players UI checkpoint — 16 August 2026

The Players Research workspace is now considered an **approved visual/functional checkpoint** for the redesign.

Preserved requirements:

- Season & scope starts collapsed.
- Advanced conditions starts collapsed.
- Useful player data appears before advanced configuration.
- Player detail starts collapsed.
- No separate Sort By control exists.
- Statistic headings are plain text-style controls, not navigation links.
- Clicking a sortable statistic changes row ordering only.
- Clicking the same statistic again reverses ordering.
- Sorting occurs client-side without a Streamlit rerun.
- Table uses the approved white/surface FRL background.
- Table typography follows the League Table / Overview visual benchmark.
- Player-name typography remains compact and restrained.
- Position is centred; numeric statistics are right-aligned.
- Deprecated `use_container_width` is absent from the Players UI.
- Deprecated `st.components.v1.html` has been removed from the Players table renderer; the current renderer uses the supported `st.iframe` signature.

This checkpoint is the visual source of truth for future Players changes. Functional additions must not alter its typography, sizing, spacing, colour, background, alignment or border treatment unless explicitly requested.

## GUI design contract

`GUI_DESIGN_CONTRACT.md` is the governing visual contract.

Additional rule established during Players work:

> The application uses one consistent typography system. A component must not invent its own font family, font hierarchy or sizing scheme when an approved FRL component already establishes the visual language.

Behavioural changes must preserve approved typography and layout unless the user explicitly requests a visual change.

## Non-destruction rule for current work

The 26/26 baseline is the pre-change research contract.

UI redesign changes should not modify:

- query semantics;
- canonical fixture identity;
- persistent club identity;
- provenance rules;
- research calculations;
- test expectations;
- historical data.

A UI change is successful only when the new presentation works and trusted existing behaviour remains intact.

## Player-match source bridge — verified 16 August 2026

For any work involving player-match source data, passing, chance creation, progressive actions, per-match player enrichment or source replacement, read:

`PLAYER_MATCH_SOURCE_BRIDGE.md`

The bridge has been audited against the full 3,800-fixture canonical universe. The established result is:

- 3,799 canonical fixtures map uniquely to player-match source fixtures;
- 0 missing player-match pairs among fixtures resolvable through the existing source mechanism;
- 0 ambiguous player-match pairs;
- the sole canonical exception is the already-documented 2019-20 Manchester City v Arsenal fixture 275, whose scheduled and actual kickoff are represented through the project's explicit correction/provenance mechanism.

Important identity rules established by the audit:

- canonical fixture IDs remain `season + fixture_id`;
- canonical season-local team IDs must be translated through `identity/team_seasons.csv`;
- `events_stats.matchId` and `players_match_stats.matchId` are different upstream namespaces and must not be compared directly;
- historical gameweek is metadata, not the final identity key for postponed/rescheduled fixtures;
- the existing `match_stats.fixture_source_match()` resolver is the trusted canonical-fixture → upstream-event mechanism and should be reused.

No canonical data or application code was modified during the audit.

## Player identity enrichment — current architecture decision

Player-match enrichment has a second identity problem separate from fixture reconciliation. Do not join `players_match_stats.playerId` directly to FPL `element`/`player_code` values.

The read-only audit established a deterministic season-level anchor set using:

`normalized player name + verified seasonal persistent team identity`

The latest audited baseline produced:

- **1,798 exact 1:1 player-season anchors**;
- **0 ambiguous player-season anchors**;
- **935 unresolved player-season records** requiring further identity evidence.

The source and FPL identifiers are separate namespaces. In `player_research.py`, `seasonal_player_id()` deliberately prefers `player_code` (falling back to `element`/`id`), while the external source has its own `playerId`; neither identifier is assumed equivalent to the other. Cross-season propagation may therefore occur only from **already-proven FPL-code → source-playerId anchors**.

The cross-season audit must use this rule:

> same proven FPL player code → unique previously proven source player ID → verify that source player ID is present for the current season and verified team.

Name-only propagation, fuzzy matching, or club-name-only matching is not sufficient for a production identity merge. Remaining cases must stay explicitly unresolved until stronger evidence exists.

Relevant audit/test files:

- `player_identity_audit.py`
- `tests/test-player-identity-audit.py`
- `player_identity_crossseason_audit.py`
- `tests/test-player-identity-crossseason.py`

The cross-season test was updated to match the current ID-anchor model rather than the earlier name-based prototype.

This identity layer is intended to become shared infrastructure for:

- Player Research metrics;
- future player profile pages;
- fixture pages with player-level actions;
- provenance and evidence displays.

Do not create a permanent crosswalk file until the cross-season propagation audit and unresolved-player review establish the evidence standard.

## Current product task

Redesign the user interface so the Football Research Laboratory feels like a professional football research product rather than a conventional Streamlit dashboard.

Target qualities:

- professional
- elegant
- pretty
- intuitive
- natural
- restrained
- data-led
- not AI-generated-looking

Design reference in spirit:

**StatsBomb analytical clarity + Football Manager information depth + modern application usability.**

Do not copy either product literally.

## Current navigation / workspace direction

Current conceptual navigation:

- Explore: League Table, Fixtures
- Research: Players
- Analysis: Head-to-Head, Form & Streaks
- Modelling: Prediction Lab
- Evidence: Data Quality, Provenance
- Future utility: Squads

Keep navigation compact, text-first and visually consistent.

## Important current files

- `gui/theme.py` — visual system
- `gui/ui_shell.py` — navigation shell and workspace routing
- `gui/app_redesign.py` — redesign preview entry point
- `gui/player_research_ui.py` — approved Players workspace
- `GUI_DESIGN_CONTRACT.md` — governing UI contract
- `README.md` — current project orientation and validation baseline
- `PLAYER_MATCH_SOURCE_BRIDGE.md` — verified player-match source identity/fixture bridge

The trusted backend boundary remains:

`query_lab.py` → `query_api.py` → GUI

## Verification discipline

Before declaring a GUI change complete:

1. Verify Python syntax/compilation.
2. Verify the route still exists.
3. Verify existing data still renders.
4. Verify requested controls work.
5. Verify no deprecated Streamlit APIs were introduced.
6. Verify the approved visual contract has not changed unintentionally.
7. Run the **26/26** research gate.
8. Run the project-health gate where relevant.

Do not claim 26/26 or project-health success unless the local checks have actually been executed and passed.

Do not add a new identity source or permanent crosswalk without a read-only audit and an explicit evidence threshold.

## What not to do

- Do not run `git clean` in the full local research workspace.
- Do not run `git reset --hard` to resolve local clutter.
- Do not casually delete untracked research/data files.
- Do not use `git add .` for deployable commits.
- Do not modify the query/data layer for purely visual problems.
- Do not source additional player history merely to make the future profile look complete.
- Do not treat an exploratory UI mock-up as stable production behaviour.
- Do not promote fuzzy or name-only player matches to verified identity.

## Immediate next step

Finish the read-only player identity audit. Validate the corrected cross-season anchor test, run the cross-season propagation audit, and classify the 935 unresolved player-season records into evidence-backed resolutions versus genuinely unresolved cases.

Only after the identity layer is sufficiently proven should Passing metrics be exposed in the Players UI or used to power future player profiles and fixture-level player enrichment.
