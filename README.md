# Football Research Lab

A provenance-aware research application for historical Premier League and FPL data.

## Stable architecture

- `query_lab.py` — core research/query layer
- `query_api.py` — API wrapper used by the GUI
- `gui/app.py` — Streamlit interface
- `identity/team_seasons.csv` — season-local identities and persistent club mapping
- `fixtures_master_corrected.csv` — corrected fixture master
- `identity/data_quality/fixture_corrections.csv` — fixture correction provenance

## Current stable GUI

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

Run:

    python .\tests\test-query-lab.py

The last verified stable checkpoint passed 13/13 tests.

## Local development

    python -m streamlit run .\gui\app.py

The local application normally appears at:

    http://localhost:8501

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
