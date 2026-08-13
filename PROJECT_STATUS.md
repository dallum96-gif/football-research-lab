# Project Status — 13 August 2026

## Stable checkpoint

The `main` branch remains the stable project base.

The last verified stable test state before the current GUI feature work was:

    13/13 tests passing

## Working data layer

- Corrected fixture master
- Season-local team identity registry
- Persistent club identity mapping
- Fixture correction/provenance registry

## Working query layer

- League table
- Team summary
- Multi-season team comparison
- Fixture queries
- Head-to-head queries
- Player query functions

## Current development branch

`agent/head-to-head-gui`

This branch adds the Head-to-Head GUI on top of the tested H2H backend.

The feature has been tested locally and is working.

The branch currently provides:

- League Table
- Fixture Explorer
- Season Comparison
- Head-to-Head

The underlying H2H test suite has passed 14/14 when run on the feature branch.

## Stable GUI

The production `main` interface remains:

- League Table
- Fixture Explorer
- Season Comparison

The Head-to-Head interface is currently a feature-branch change awaiting review and merge.

## Known state

Head-to-head exists in the backend and has passed invariant testing. Its GUI is now working on `agent/head-to-head-gui`.

A Form & Streaks experiment exists only in local Git stash and is NOT considered stable or part of production. It must be rebuilt from a clean base and tested before being introduced again.

The earlier `tab5` Streamlit error was caused by unfinished local GUI changes on `main`, not by the stable repository state. Those changes have been isolated rather than committed.

## Engineering principles

1. Fix classes of problems, not individual failing assertions.
2. Persistent club identity is separate from season-local IDs.
3. Preserve provenance.
4. Prefer invariant tests over single example tests.
5. Keep unfinished experiments out of `main`.
6. Keep query logic separate from Streamlit presentation.
7. Develop feature work on branches and review it before merging to `main`.
8. Establish repository state before modifying code.

## Immediate roadmap

1. Review and merge the Head-to-Head GUI branch.
2. Rebuild Form & Streaks cleanly from the stable base.
3. Add richer opponent and streak analysis.
4. Decide how player data should be packaged for deployment.
5. Continue expanding the GUI only after backend invariants pass.

## Recovery

Repository:

    dallum96-gif/football-research-lab

Fresh clone:

    git clone https://github.com/dallum96-gif/football-research-lab.git

Then:

    cd football-research-lab
    python .\tests\test-query-lab.py
    python -m streamlit run .\gui\app.py
