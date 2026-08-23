# Current Work — Football Research Laboratory

**Last updated:** 23 August 2026, 22:18 BST

## Active branch

`design/player-filter-tiles`

This remains the development line. `main` is the stable integration line.

## Current platform checkpoint

The FRL data-platform work is deliberately additive and local-first.

Validated:

- canonical relationship-integrity proof: green;
- temporary Parquet/DuckDB analytical materialisation for `fixtures` and `team_fixtures`: green;
- analytical/query-equivalence proof: prototype corrected after two test-environment issues; latest corrected CI run is being validated.

## Player identity milestone — 23 August 2026

**Milestone timestamp:** 23 August 2026, 21:46 BST.

The Player-Match player-attachment reconciliation is complete:

- **145,571** Player-Match observations
- **145,571 VERIFIED** player attachments
- **0 REVIEW**
- **0 UNRESOLVED**

The final identity layer uses explicit bridges rather than assuming all source systems share the same player namespace.

The reconciliation established:

- canonical cross-source player identity through the verified player registry and relevant Player-Season / Research evidence;
- a longitudinal Player-Match `source_player_id` / `pl_code` → Player-Season bridge;
- a source-native Player-Match player bridge for identities absent from downstream Player-Season / Research namespaces.

The source-native bridge is stored in:

`data/player_source_identity_bridge.csv`

At this milestone it contains **26 source-native player identities covering 225 Player-Match observations**.

## Default identity contract

The default FRL identity schema is now formally defined in:

`FRL_DEFAULT_IDENTITY_SCHEMA_V1.md`

It is mandatory reading before identity, relationship or source-variable mapping work.

The detailed identity/relationship architecture contract remains:

`FRL_IDENTITY_RELATIONSHIP_CONTRACT_V1.md`

Fresh sessions must read both contracts before modifying player, team, fixture or source identity logic.

Historical milestone record:

`docs/IDENTITY_MILESTONE_2026-08-23.md`

Milestone commit:

`3fee450` — `milestone: complete player-match identity attachment reconciliation`

## Foundational identity rule

Source identifiers are not automatically interchangeable. In particular:

- FPL `element` is season-local;
- Player-Match `source_player_id` / `pl_code` is treated as a longitudinal source-native identity where continuity is verified;
- Player-Season `playerId` is a source-specific identity and must be bridged explicitly;
- Player Research has its own namespace and is enrichment/evidence, not the universal FRL identity key;
- team identity is season-aware and must use `identity/team_seasons.csv` rather than bare names or unscoped IDs;
- fixture identity is canonicalised as `(season, fixture_id)` and source match IDs are bridged into it.

No player attachment may silently create a cross-source identity merely to make a row resolve.

## Variable universe expansion

The identity layer is now complete enough to support the next major discovery phase: mapping the wider source-variable universe.

Current routed variable universe: **477 mapped variables**.

The wider discovered source universe contains approximately **900 additional variables/fields** awaiting systematic classification and mapping.

Variable mapping must use the default identity schema and record source family, source field, observation grain, identity contract, relationship contract, transformation/aggregation, availability semantics and provenance status before a variable is considered research-ready.

Mapping the universe is distinct from exposing variables in the GUI.

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
4. Begin systematic classification of the wider ~900-variable source universe using `FRL_DEFAULT_IDENTITY_SCHEMA_V1.md` as the identity contract.
5. Validate newly mapped variable relationships before any GUI exposure.
