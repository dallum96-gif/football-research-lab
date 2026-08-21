# FRL Searchable Variables Contract V1

**Status:** Additive research-layer contract
**Date:** 21 August 2026

## Purpose

The FRL should make as many defensible source variables searchable as practical without requiring a bespoke query function for every metric and without collapsing source-native evidence into canonical concepts prematurely.

## Search architecture

```text
source family
    ↓
verified relationship bridge
    ↓
source-native field registry
    ↓
empirical season coverage
    ↓
generic research-field query
    ↓
query API / future natural-language interface
```

## Searchable does not mean canonical

A field may be searchable while remaining:

- source-specific;
- retained-only;
- historically intermittent;
- semantically unreviewed;
- unavailable for some seasons;
- unsuitable for modelling until its meaning is validated.

The query result must expose the source family and source field rather than silently relabelling the variable as an FRL canonical concept.

## Identity requirements

Source IDs remain source-local unless the existing FRL identity bridge explicitly reconciles them.

Fixture-scoped team-match and player-match queries must resolve through the established canonical fixture → verified source match pathway.

Player-season and squad queries may return source-native player IDs until player identity reconciliation is verified.

## Coverage requirements

Every field query is season-aware.

A field absent from a requested season fails closed rather than returning zero, null-filled synthetic observations, or an implied historical backfill.

The decade inventory distinguishes:

- `CORE_DECADE`
- `LONG_RUN`
- `INTERMITTENT`
- `SINGLE_SEASON`

## Provenance requirements

A result should retain, where applicable:

- FRL season;
- FRL fixture ID;
- source match ID;
- source team ID;
- source player ID;
- source field name;
- source family;
- registry status.

## Temporal requirements

Source retrieval time is not treated as historical availability time.

The current generic field query layer therefore makes no claim that a result was knowable at a historical prediction timestamp. Availability-time semantics will be added through the temporal reconstruction layer before historical predictive features can consume these results.

## Current implementation

- `source_field_registry.py` — semantic catalogue;
- `audit_source_field_coverage.py` — empirical season coverage;
- `build_source_field_inventory.py` — decade-wide field inventory;
- `research_field_query.py` — generic source-field retrieval;
- `research_query_extensions.py` — query-facing dispatch for the new research layer.

The legacy Query Lab remains authoritative for existing production query behaviour until the new layer passes the full assurance gates.
