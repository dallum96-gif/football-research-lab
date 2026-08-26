# FRL Unrouted Variable Disposition V1

## Purpose

Record the authoritative disposition of canonical variables that do not currently have an explicit reusable source-grain route.

This is a disposition record, not a second canonical variable catalogue.

## Current accounting

The current canonical universe contains **1,414** variables.

The explicit route registry contains **956 unique routes**.

Therefore:

```text
1,414 canonical variables
- 956 explicit routes
= 458 variables without an explicit reusable route
```

The 458 are fully classified as:

```text
458 unrouted
├── 452 FPL source variables
│   ├── 241 research-facing FPL variables
│   └── 211 FPL rules / configuration variables
└── 6 local_json / raw_upstream variables
```

## FPL disposition

The 452 FPL variables belong to the separate first-class `fpl` research domain.

The **241 research-facing variables** are exposed through the FPL domain registry and evidence access layer.

The **211 rules/configuration variables** are preserved as source evidence but are not exposed as reusable research variables. Their retention is deliberate: source coverage and research accessibility are distinct states.

FPL variables are not inserted into the core `team_match`, `player_match`, `player_season` or `squad` source-family pathways merely to satisfy route coverage.

## Local JSON disposition

The remaining **6 local_json / raw_upstream variables** remain preserved and explicitly unresolved for reusable research access.

They are not converted into inferred canonical relationships, and no synthetic route is created merely to eliminate the unresolved count.

## Completion rule

A variable is not considered unresolved merely because it lacks a route. Each variable must have an explicit disposition:

- routed through an established source/query seam;
- exposed through the separate FPL domain;
- preserved as configuration/provenance-only evidence; or
- preserved as explicitly unresolved pending an evidenced future seam.

This document should remain consistent with the executable disposition tests and the authoritative canonical/route registries.
