# Project Status

## Stable checkpoint

The `main` branch is the stable project base.

The last verified test state before the unfinished Form & Streaks work was:

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

## Stable GUI

- League Table
- Fixture Explorer
- Season Comparison

## Known state

Head-to-head exists in the backend and has passed invariant testing, but its GUI integration should be reintroduced carefully.

Form & Streaks was experimented with locally but is NOT considered stable and should not be treated as part of the production application until rebuilt and tested.

## Engineering principles

1. Fix classes of problems, not individual failing assertions.
2. Persistent club identity is separate from season-local IDs.
3. Preserve provenance.
4. Prefer invariant tests over single example tests.
5. Keep unfinished experiments out of `main`.
6. Keep query logic separate from Streamlit presentation.

## Immediate roadmap

1. Reintroduce the Head-to-Head GUI cleanly.
2. Build Form & Streaks from the stable base.
3. Add richer opponent and streak analysis.
4. Decide how player data should be packaged for deployment.
5. Continue expanding the GUI only after backend tests pass.

## Recovery

Repository:

    dallum96-gif/football-research-lab

Fresh clone:

    git clone https://github.com/dallum96-gif/football-research-lab.git

Then:

    cd football-research-lab
    python .\tests\test-query-lab.py
    python -m streamlit run .\gui\app.py
