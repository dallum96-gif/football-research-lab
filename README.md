# Football Research Lab

A provenance-aware research application for historical Premier League and FPL data.

## Returning to the project

For a fast reconstruction of the project's architecture, quality principles, current branch work and UI direction, start with:

1. `PROJECT_ORIENTATION.md`
2. `CURRENT_WORK.md`
3. `PROJECT_VISION.md`

`CURRENT_WORK.md` is the short, changeable checkpoint. `PROJECT_STATUS.md` contains historical project status and may be out of date; use it for history rather than as the sole statement of current state.

## Stable architecture

- `query_lab.py` — core research/query layer
- `query_api.py` — API wrapper used by the GUI
- `gui/app.py` — production Streamlit interface
- `identity/team_seasons.csv` — season-local identities and persistent club mapping
- `fixtures_master_corrected.csv` — corrected fixture master
- `identity/data_quality/fixture_corrections.csv` — fixture correction provenance

## Current stable GUI

The production interface should be treated separately from work on feature branches. Do not infer that a branch feature is present in `main` without checking the branch and commit history.

Historically, the stable GUI has included:

- League Table
- Fixture Explorer
- Season Comparison

## Backend capabilities

- League tables
- Team summaries
- Multi-season team comparison
- Fixture queries
- Head-to-head queries
- Player queries
- Persistent club identity resolution

## Data-quality principles

Season-local team IDs are not treated as globally stable.

Persistent club identity is used to follow a club across seasons.

Explicit fixture corrections are retained with provenance.

## Tests

The current research baseline is documented in `CURRENT_WORK.md` and `PROJECT_ORIENTATION.md`.

The latest validated research gate on the active development branch is **26/26**:

- Query Lab: 14/14
- Player Research V0.1: 6/6
- Player Research V0.2: 6/6

The older 13/13 figure in historical documentation refers to an earlier checkpoint.

## Project health

Run:

    .\project-health.ps1

The health gate checks source coverage, the canonical fixture master, season integrity, duplicate IDs, required fields, score/completion semantics, team integrity, dates and a modern player↔fixture relationship.

The current known warning concerns the rescheduled 2019–20 Manchester City v Arsenal fixture; see `CURRENT_WORK.md` for details.

## Local development

    python -m streamlit run .\gui\app.py

The local application normally appears at:

    http://localhost:8501

For the current UI redesign preview on `agent/fixture-landing-page`:

    streamlit run .\gui\app_redesign.py

## Recovery

Repository:

    dallum96-gif/football-research-lab

Fresh clone:

    git clone https://github.com/dallum96-gif/football-research-lab.git

Then:

    cd football-research-lab
    python .\tests\test-query-lab.py
    python -m streamlit run .\gui\app.py

## Git safety

Do not use `git add .` casually in the full local research workspace.

Stage only the files intended for the deployable repository.

Do not use destructive cleanup commands to resolve ordinary local research-workspace clutter without first preserving anything potentially valuable.
