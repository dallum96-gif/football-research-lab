# FRL Universal Research Access Contract V1

## Purpose

`research_access.py` is the governed consumer seam for frontend, research and future natural-language consumers.

It sits above the existing canonical variable resolver and source-family evidence adapters. It must not introduce source-specific joins, identity inference, duplicated metric calculations or a competing evidence store.

## Supported operations

### Capability discovery

`discover(family=None, search=None)` returns research-facing capabilities from the authoritative canonical catalogue and FPL registry.

The result describes registry exposure only. It does not imply evidence coverage or historical information availability.

### Request validation

`validate(ResearchRequest(...))` checks:

- variable and season are present;
- family is known when supplied;
- variable resolution succeeds;
- natural-grain context requirements are respected;
- FPL resolver errors are normalised to `ResearchAccessError`.

### Evidence coverage

`coverage(variable=..., seasons=[...], family=...)` reports, per season:

- field presence;
- population;
- observed values;
- missing values;
- coverage percentage.

Coverage is evidence coverage, not proof of historical information availability.

### Research execution

`query(ResearchRequest(...))` validates the request and delegates retrieval to the existing FRL resolver. The result envelope preserves:

- resolved definition;
- results;
- population / coverage where supplied by the resolver;
- temporal semantics;
- provenance;
- limitations.

## Temporal contract

Historical state and information availability are separate concepts.

A request may carry:

- `as_of_date`: historical state reconstruction target;
- `information_available_as_of`: historical information-availability target.

The access seam must never infer one from the other.

## Provenance contract

Research results should identify, where known:

- canonical variable;
- family / natural grain;
- source field;
- authoritative registry;
- access layer.

The universal access seam performs no identity inference.

## Error contract

Invalid or unavailable requests fail closed through `ResearchAccessError` (or a subclass). Raw source-specific lookup exceptions must not leak through the public consumer boundary.

## Frontend contract

The frontend should treat this seam as the source of truth for research retrieval and capability discovery. It should not read FRL CSVs directly merely to populate a research result.

The frontend may use capability discovery to construct navigation, search, filters and variable pickers, while the research result envelope remains the canonical analytical payload.

## Validation gate

The Step 9 closeout gate must include:

- Universal Research Access unit/regression tests;
- cross-domain acceptance;
- relevant backend acceptance tests;
- Core Query Lab regression;
- Player Research gate;
- project health.

A closeout is not declared until the relevant gates have actually run and passed, with known warnings explicitly recorded.
