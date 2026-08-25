# FRL Universal Variable Runtime Wiring V1

**Status:** Implementation contract / runtime wiring

## Purpose

The FRL already has a broad source-field research layer. This contract defines the runtime seam that makes those variables directly requestable from Fixture, Team–Fixture, Player–Fixture and Player–Season contexts without requiring GUI consumers to know source-specific retrieval functions.

## Runtime flow

```text
canonical/source variable name
        ↓
variable resolver
        ↓
source-family registry / semantic mapping
        ↓
existing generic research-field query
        ↓
verified fixture/source relationship
        ↓
structured result + provenance
        ↓
GUI / research consumer
```

## Context rules

A resolver request should identify the natural context where necessary:

- Fixture: `season`, `fixture_id`;
- Team–Fixture: `season`, `fixture_id`, optional source `team_id`;
- Player–Fixture: `season`, `fixture_id`, optional source `player_id`;
- Player–Season: `season`, optional source `player_id`.

The resolver must not infer a source-local player or team identity from an unrelated numeric ID. Existing verified fixture/source relationships remain authoritative.

## Source-family dispatch

The runtime may use the existing generic research-field query functions for:

- `team_match`;
- `player_match`;
- `player_season`;
- `squad`.

No new CSV extraction path is permitted merely to expose another variable.

## Canonical aliases and derived variables

Canonical display variables may map to source fields or documented transformations. Examples:

```text
Tackle won %
    = wonTackle / totalTackle

Pass completion %
    = accuratePass / totalPass
```

The resolver owns the transformation metadata and returns the underlying inputs in provenance where appropriate.

## Availability

A variable is only returned when its source field is actually present in the requested season/context. Missing historical fields fail closed. No synthetic zeros or retrospective backfills are allowed.

## Objective

> Make the broad, validated FRL variable universe directly reachable from the football graph while preserving the existing source-family, identity, provenance and temporal contracts.
