# Current Work — Football Research Laboratory

**Last updated:** 23 August 2026, 22:21 BST

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

The default FRL identity schema is:

`FRL_DEFAULT_IDENTITY_SCHEMA_V1.md`

The detailed identity/relationship architecture contract is:

`FRL_IDENTITY_RELATIONSHIP_CONTRACT_V1.md`

Fresh sessions must read both contracts before modifying player, team, fixture or source-variable identity logic.

Historical milestone record:

`docs/IDENTITY_MILESTONE_2026-08-23.md`

Milestone commit:

`3fee450` — `milestone: complete player-match identity attachment reconciliation`

## Current strategy — Match Variable Universe Expansion

**Status: ACTIVE — execution phase.**

Strategy contract:

`FRL_MATCH_VARIABLE_UNIVERSE_EXPANSION_STRATEGY_V1.md`

Objective: build the richest possible validated match evidence layer from every usable facet in the approved source universe.

Baseline:

- **477 variables mapped**
- approximately **900 additional variables/fields** previously identified as an unmapped expansion frontier

The ~900 figure is a working estimate only. The authoritative frontier count must be regenerated from the source census.

### Execution order

```text
A. Recover complete source-variable universe
        ↓
B. Reconcile against the 477 mapped baseline
        ↓
C. Classify the full unmapped frontier
        ↓
D. Map every structurally valid facet
        ↓
E. Validate grain / identity / temporal semantics / provenance
        ↓
F. Build match-data completeness matrix
        ↓
G. Only then decide research-facing / GUI exposure
```

### Immediate execution task

Recover the existing source inventory and mapped-variable artefacts from the local research workspace and compute the authoritative mapped-vs-unmapped census.

Do **not** scrape new sources until the existing inventory is reconciled.

Do **not** delete or rewrite the existing 477 mappings during discovery.

All new mappings must use the default identity schema and identity/relationship contract.

## Foundational identity rule

Source identifiers are not automatically interchangeable. In particular:

- FPL `element` is season-local;
- Player-Match `source_player_id` / `pl_code` is treated as a longitudinal source-native identity where continuity is verified;
- Player-Season `playerId` is a source-specific identity and must be bridged explicitly;
- Player Research has its own namespace and is enrichment/evidence, not the universal FRL identity key;
- team identity is season-aware and must use `identity/team_seasons.csv` rather than bare names or unscoped IDs;
- fixture identity is canonicalised as `(season, fixture_id)` and source match IDs are bridged into it.

No identity attachment may silently create a cross-source identity merely to make a field resolve.

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

1. Execute the source-variable census against the existing local source universe.
2. Reconcile the authoritative universe against the 477 mapped baseline.
3. Produce the unmapped frontier inventory.
4. Begin systematic field-by-field mapping using the new identity/relationship contracts.
5. Preserve all atomic facets and defer GUI exposure decisions until mapping is complete.
6. Validate the expanded match evidence layer before changing research/query or GUI consumers.
