# Football Research Laboratory — Data Ecosystem Discovery Contract

**Status:** Foundational discovery / source-governance contract  
**Date:** 17 August 2026  
**Branch:** `design/player-filter-tiles`

## Purpose

The FRL deliberately preserves a richer football evidence ecosystem than the current GUI exposes. Data may exist in multiple repositories, source families, grains, partitions, derived files and historical implementations.

Therefore:

> **Failure to find a field, metric, classification or capability in one place is never sufficient evidence that the FRL does not have it.**

## Required discovery rule

Before concluding that information is absent, unavailable, or requires a new external source, audit the relevant whole ecosystem.

At minimum, where applicable, inspect:

- current application/query code;
- archived and backup implementations;
- all relevant tracked datasets and directory trees;
- local upstream/source workspaces;
- source-family variants and parallel products;
- partitioned datasets such as `by_position`;
- merged/derived datasets;
- identity registries and crosswalks;
- neighbouring fields and alternative field names;
- source documentation and provenance notes.

Do not search only for the expected column name.

## What the audit must establish

```text
source family
      ↓
dataset / file / endpoint
      ↓
grain
      ↓
relevant fields
      ↓
source identifiers
      ↓
coverage
      ↓
transformation / derivation
      ↓
existing consumer
      ↓
FRL suitability
```

A capability may exist:

- at a different grain;
- under another field name;
- in a partitioned dataset;
- in an upstream source rather than the canonical layer;
- as a documented derived quantity;
- in an archived implementation.

## Source diversity

The FRL must also assume that future leagues and source providers may use different schemas, field names, identifier systems, grains, units and metric definitions.

The canonical FRL layer should therefore normalise **meaning**, not pretend source schemas are identical.

Each source adapter should retain:

- native field name;
- native definition;
- source grain;
- source identifier;
- mapped FRL concept;
- transformation/aggregation;
- units/scaling;
- missing-value semantics;
- coverage;
- source/version/provenance.

Where two sources cannot be harmonised without an unsupported assumption, retain both source representations and leave the canonical concept unavailable rather than inventing equivalence.

## Completion rule

A conclusion such as:

> “We do not have this data.”

should only be made after a documented ecosystem audit has established that no defensible source or derivation exists.

If a new external source is then considered, record why existing FRL sources were insufficient.

## North Star alignment

This contract protects the FRL's principle of preserving rich source evidence for future research, scouting, intelligence and modelling. It prevents premature data acquisition, duplicate infrastructure and false conclusions about what the Laboratory already knows.

> **Search the whole evidence ecosystem before declaring the evidence absent.**
