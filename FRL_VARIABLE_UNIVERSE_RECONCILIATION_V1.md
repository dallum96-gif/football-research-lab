# FRL Variable Universe Reconciliation — V1

**Status:** Active reconciliation contract  
**Declared:** 25 August 2026

## Purpose

The FRL has used more than one count when describing its variable universe. The repository's documented mapped baseline is **477 variables**. A broader working source-universe investigation has subsequently referred to approximately **1,414 variables**.

These numbers must not be treated as competing truths or reconciled by simple arithmetic.

The authoritative FRL count must come from a complete, auditable reconciliation of source fields, canonical variables, aliases and derived variables.

## Current count semantics

### 477 — mapped baseline

The 477 figure is the documented existing mapped baseline in the FRL match-variable expansion strategy.

### 1,414 — broader working universe

The 1,414 figure is a working count from the wider source-universe investigation and is **not yet an authoritative repository census**.

It may contain:

- source-native fields;
- canonical FRL variables;
- aliases of existing variables;
- derived variables;
- repeated fields appearing in multiple grains/source families;
- fields requiring semantic review;
- fields outside the final approved canonical boundary.

Therefore the final authoritative count may be lower or higher than 1,414.

## Governing rule

> **One count, one registry, one status per variable/facet — but never collapse genuinely distinct source facets merely to reduce the count.**

The reconciliation must preserve distinct source facets when they represent different observations, grains, definitions or provenance.

## Reconciliation unit

The primary reconciliation unit is a **source-variable facet** represented by:

```text
source family
+ source field
+ natural observation grain
+ semantic meaning
```

A canonical FRL variable may represent one or more source fields where that relationship is explicitly documented.

An alias does not create a second canonical variable merely because the source spelling differs.

A derived metric does not replace its underlying atomic source fields.

## Required statuses

Every candidate must receive one of:

```text
MAPPED_VALIDATED
MAPPED_VALIDATION_PENDING
SOURCE_NATIVE_UNMAPPED
ALIAS_OF_EXISTING
DERIVED_VARIABLE
DUPLICATE_SOURCE_FACET
SEMANTICALLY_AMBIGUOUS
TEMPORALLY_UNSAFE
IDENTITY_UNRESOLVED
OUT_OF_CANONICAL_BOUNDARY
NOT_A_VARIABLE_METADATA
```

## Required metadata

Each reconciled row should contain at minimum:

```text
source_family
source_field
candidate_name
canonical_variable
natural_grain
entity_relationship
value_type
source_or_derived
coverage
identity_requirements
semantic_status
reconciliation_status
existing_mapping_reference
provenance_reference
notes
```

## Canonical graph rule

The resolved variable must be attached to its natural analytical grain:

```text
Fixture
Team–Fixture
Player–Fixture
Team–Season
Player–Season
Event
Manager–Fixture
other validated grains
```

Do not duplicate a variable onto Fixture, Team and Player simply to make it convenient for the GUI. The universal resolver should make the natural observation reachable through the football graph.

## Relationship with Universal Variable Access

After reconciliation, the authoritative registry becomes the catalogue consumed by the universal resolver:

```text
source census
    ↓
reconciliation
    ↓
authoritative variable registry
    ↓
universal resolver
    ↓
Fixture / Team / Player / Season / Event context
    ↓
GUI / research / future natural-language interface
```

The resolver must not invent a mapping for an unresolved candidate merely because a GUI requests it.

## Reconciliation procedure

1. Load the existing 477 mapped baseline.
2. Load the broad source-universe inventory used to establish the working 1,414 figure.
3. Normalise field and variable identifiers conservatively.
4. Match exact source-family + field + grain where possible.
5. Match aliases only where semantic equivalence is explicitly established.
6. Preserve source facets that differ by family, grain or meaning.
7. Identify derived variables separately from atomic fields.
8. Record coverage and temporal safety independently from semantic mapping.
9. Produce a reconciliation report showing every source/canonical candidate exactly once at its chosen reconciliation unit.
10. Calculate the authoritative counts from the reconciled rows rather than from legacy headline numbers.

## Count outputs

The reconciliation report must publish at least:

- total source-variable facets;
- canonical variables;
- mapped + validated;
- validation pending;
- unmapped source-native;
- aliases;
- derived variables;
- ambiguous / unresolved;
- out of boundary;
- GUI-accessible;
- resolver-accessible.

## Safety

- Never force the 1,414 figure to equal the final count.
- Never force the 477 figure to remain the canonical count if reconciliation proves otherwise.
- Never delete atomic source facets merely because a derived variable exists.
- Never infer semantic equivalence from similar names alone.
- Never join different source identifiers solely because values appear numerically compatible.
- Preserve temporal and provenance semantics.
- Fail closed where the evidence is insufficient.

## Completion condition

The 477/1,414 discrepancy is considered resolved when the FRL has:

1. one authoritative reconciliation dataset;
2. one documented status for every candidate;
3. one defensible explanation for every legacy 477 entry;
4. one defensible explanation for every broader-universe entry;
5. an authoritative count generated from the reconciled dataset;
6. a documented bridge from the authoritative registry into the Universal Variable Resolver.
