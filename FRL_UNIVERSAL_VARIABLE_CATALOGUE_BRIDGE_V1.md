# FRL Universal Variable Catalogue Bridge V1

**Date:** 25 August 2026  
**Status:** Development implementation

## Purpose

The universal variable resolver must not depend on a hand-written Python handler for every source field. The existing FRL source-family research layer already provides generic field retrieval; this bridge makes the requestable universe discoverable by context.

## Runtime behaviour

`variable_universe.py` provides:

- `list_variables(...)` — discover variables empirically available for a requested season and football context;
- `variable_catalogue(...)` — serialisable metadata for GUI/query consumers;
- `resolve_all(...)` — resolve a selected subset or the complete discovered context set through the universal resolver.

## Context selection

The facade chooses the natural source family from the supplied context when possible:

```text
fixture + player -> player_match
fixture + team   -> team_match
fixture only     -> team_match + player_match
player only      -> player_season + squad
explicit family  -> requested family
```

This is a consumer-routing convenience only. It does not create new identities or cross-source joins.

## Discovery rule

Native fields are discovered from the requested season using the existing `available_fields()` mechanisms. A field therefore does not need a bespoke handler to become requestable.

Canonical derived variables are added only when all required underlying source fields are empirically present for that season.

## Important distinction

The repository currently documents an older 477-variable canonical baseline in `FRL_MATCH_VARIABLE_UNIVERSE_EXPANSION_STRATEGY_V1.md`. The 1,414-variable mapping discussed during local FRL work is not currently present in the public tracked repository as a machine-readable manifest visible to this runtime environment.

This bridge therefore does **not** claim that the public repository already contains 1,414 fully catalogued runtime variables. Instead, it provides the runtime mechanism needed to consume the authoritative manifest when that canonical mapping is brought into the tracked repository.

## Safety

- Missing fields fail closed.
- No synthetic zero values are generated for absent fields.
- No historical backfill is inferred.
- Source-family ambiguity requires context.
- Existing audited source/query mechanisms remain authoritative.
- Variables remain at their natural analytical grain.

## End state

When the full validated canonical mapping is available as machine-readable metadata, it should feed this bridge so that the GUI can request any validated variable through one standard seam rather than requiring per-variable UI code.
