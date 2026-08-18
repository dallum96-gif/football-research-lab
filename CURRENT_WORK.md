# Current Work — Football Research Laboratory

**Last updated:** 17 August 2026

## Active branch

`design/player-filter-tiles`

This remains the development line. `main` is the stable integration line.

## Current platform checkpoint

The FRL data-platform work is deliberately additive and local-first.

Validated:

- canonical relationship-integrity proof: green;
- temporary Parquet/DuckDB analytical materialisation for `fixtures` and `team_fixtures`: green;
- analytical/query-equivalence proof: prototype corrected after two test-environment issues; latest corrected CI run is being validated.

The previous query-equivalence attempt failed in the prototype only: DuckDB attempted to import `pytz` while ordering an inferred timezone-aware timestamp. No canonical data, relationship mapping or GUI behaviour failed. The proof was corrected to order the stored timestamp representation directly.

## Foundational visualisation principle

**Data visualisation is a first-class FRL research output.**

Charts, tables, comparisons, timelines and other visualisations must be generated from validated analytical/research outputs rather than maintaining separate presentation-specific truth.

Visualisations must inherit:

- the same population and filters;
- the same temporal/as-of semantics;
- the same provenance and source lineage;
- the same uncertainty/limitations;
- the same identity and relationship semantics;
- the same reproducibility/version information where practical.

The GUI remains governed by `GUI_DESIGN_CONTRACT.md` and `UI_DESIGN_SYSTEM.md`. Rich analytical visualisation must remain within that visual language rather than becoming generic dashboard clutter.

The durable visualisation rule is recorded in `FRL_VISUALISATION_DATA_CONTRACT.md`.

## Immediate next steps

1. Confirm the corrected CSV-vs-DuckDB query-equivalence gate is green.
2. Build the small reusable analytical query seam over the local Parquet representation without switching production consumers.
3. Prove that the same research result object can feed both a table and at least one chart.
4. Validate visualisation outputs against the GUI contract before any interface rollout.
5. Only then consider expanding Parquet materialisation to more datasets or considering object storage.
