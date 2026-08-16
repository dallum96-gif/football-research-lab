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

## What not to do

- Do not run `git clean` in the full local research workspace.
- Do not run `git reset --hard` to resolve local clutter.
- Do not casually delete untracked research/data files.
- Do not use `git add .` for deployable commits.
- Do not modify the query/data layer for purely visual problems.
- Do not source additional player history merely to make the future profile look complete.
- Do not treat an exploratory UI mock-up as stable production behaviour.

## Immediate next step

Leave the Players workspace at this approved checkpoint.

Next functionality/UI work should move to the next agreed workspace rather than redesigning Players again, unless a regression is found against this checkpoint.