# FRL Next Sessions Plan V1

**Date:** 22 August 2026
**Status:** Working roadmap

## Goal

Keep FRL development sequential and evidence-led while preserving the long-term shape: a navigable football database plus a serious research laboratory.

## Session 1 — Source-field semantic review

Review and promote source-native variables conservatively.

- Begin with the decade-wide `player_season` candidates.
- Establish exact source semantics, units, missing-value behaviour and stability across seasons.
- Promote only defensible source-native fields to the searchable catalogue.
- Keep uncatalogued fields preserved in the raw/source layer.

## Session 2 — Relationship and provenance consolidation

Complete the relationship backbone across:

```text
Fixture ↔ Team ↔ Player ↔ Player-season ↔ Player-match ↔ Source field
```

Every relationship must remain explicitly `VERIFIED`, `UNRESOLVED`, `AMBIGUOUS` or `UNAVAILABLE` as appropriate.

Confirm that source-local identifiers are never silently treated as canonical FRL identities.

## Session 3 — Raw-source archive specification

Formalise the ingestion/archive contract.

- Preserve an immutable local copy of exactly what FRL received from the approved source boundary.
- Record provenance metadata, retrieval/ingestion time and content identity where practical.
- Treat CSVs as portable source artefacts/evidence snapshots, not as a competing canonical truth.
- Keep the archive independent enough to survive source loss or source changes.

## Session 4 — Database / analytical-store design

Design the local database/analytical store around the proven relationship graph rather than around today's queries.

- Raw/source evidence remains preserved.
- Canonical entities and relationships remain explicit.
- Player-match, player-season, team-match and fixture grains remain stable.
- Storage technology remains replaceable.
- Initial implementation stays local-first.

The current Parquet/DuckDB direction remains the preferred first analytical implementation, subject to equivalence testing.

## Session 5 — Local database implementation

Build the first practical local data store and ingestion path.

```text
source archive
    ↓
ingestion
    ↓
local data store
    ↓
validated relationships
    ↓
research/query layer
```

Prove the database can be rebuilt from the preserved source archive.

## Session 6 — Move research/query workloads onto the database

Move production consumers only after equivalence has been demonstrated.

- Compare database results with existing trusted CSV-backed outputs.
- Preserve existing adapters and relationship contracts.
- Keep query semantics unchanged during storage migration.
- Add regression/equivalence gates before any old path is retired.

## Session 7 — Navigable football database UI

Build the database as a genuine product, not merely an invisible backend.

Initial exploration should support:

- seasons;
- teams;
- players;
- player-seasons;
- fixtures;
- match statistics;
- historical relationships;
- provenance/source evidence.

Navigation should follow canonical relationships rather than duplicate ad hoc joins.

## Session 8 — Research interface and visualisation

Expose the research engine through structured and eventually natural-language interfaces.

The same trusted research result should be able to drive:

- tables;
- charts;
- comparisons;
- timelines;
- distributions;
- provenance views.

## Session 9 — Modelling and advanced research

Only after the evidence/data platform is stable, expand into:

- historical precedent;
- Elo;
- Poisson;
- Monte Carlo;
- player-state modelling;
- experiment tracking;
- walk-forward/out-of-sample evaluation;
- calibration and robustness.

## Standing rule

Do not build a higher layer to compensate for an unproven lower layer.

When a result is difficult to obtain, first inspect the source, identity, relationship, temporal or storage layer before adding query complexity.

## Long-term sequence

```text
SOURCE PRESERVATION
      ↓
RELATIONSHIPS / PROVENANCE
      ↓
FIELD SEMANTICS
      ↓
DATABASE / ANALYTICAL STORE
      ↓
RESEARCH ENGINE
      ↓
NAVIGABLE DATABASE UI
      ↓
LLM / NATURAL-LANGUAGE RESEARCH
      ↓
MODELLING / EVALUATION
      ↓
MARKET / DECISION LAYER
```
