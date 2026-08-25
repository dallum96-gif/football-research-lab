# FRL Match Variable Universe Expansion Strategy — V1

**Status:** Active execution strategy  
**Declared:** 23 August 2026, 22:21 BST

## Objective

Build the richest possible FRL match evidence layer from every usable facet present in the available source universe.

The goal is not to collect a shortlist of attractive metrics. The goal is to establish a complete, auditable inventory of source variables and map every usable field into the FRL evidence architecture.

Current baseline:

- **477 variables mapped**
- approximately **900 additional source variables/fields** identified earlier as an unmapped expansion frontier

The 477 are the existing mapped baseline. The ~900 are not assumed to be new metrics; they must first be re-inventoried and reconciled against the authoritative source universe.

## Governing principle

> **Map the source universe first; decide what becomes research-facing second.**

A field should not be discarded merely because it is not currently exposed in the GUI, not currently queried, or not obviously useful today.

A variable may be:

- source-native and directly retained;
- a canonical representation of source evidence;
- a derived analytical variable;
- a duplicate/alias of an already mapped field;
- unavailable under the required temporal/source contract;
- structurally invalid;
- or genuinely new and therefore requiring a new mapping contract.

## Execution phases

### Phase A — Recover the source universe

Inventory all relevant source files and source families before modifying mappings.

For each source family capture:

- source file/path;
- source family/provider;
- field name;
- field type;
- example values where useful;
- season/date coverage;
- observation grain;
- entity implied by the field;
- whether the field is raw or derived;
- existing FRL mapping, if any.

### Phase B — Reconcile against the 477 baseline

Join the complete source-variable inventory against the current mapped-variable registry.

Produce:

1. already mapped variables;
2. unmapped variables;
3. duplicate/alias variables;
4. ambiguous variables requiring interpretation;
5. variables that exist only in sources outside the current canonical data boundary.

Do not count aliases as new variables merely because their source spelling differs.

### Phase C — Classify every unmapped field

Every unmapped field receives a structured classification:

```text
source field
→ source family
→ observation grain
→ entity / relationship
→ identity contract
→ temporal semantics
→ raw meaning
→ transformation / aggregation
→ provenance
→ mapping status
```

The default identity contract is `FRL_DEFAULT_IDENTITY_SCHEMA_V1.md`.

The player/team/fixture relationship contract is `FRL_IDENTITY_RELATIONSHIP_CONTRACT_V1.md`.

### Phase D — Map the usable universe

Every field that can be safely represented is mapped, even when it is not immediately research-facing.

A mapping must specify:

- source field;
- FRL variable name;
- source family;
- grain;
- entity/relationship;
- identity requirements;
- temporal/as-of behaviour;
- transformation or aggregation, if any;
- null/availability semantics;
- provenance/evidence basis;
- validation status.

### Phase E — Preserve facets rather than prematurely collapsing them

Do not compress multiple source fields into a single concept merely because they are related.

If a source provides distinct facets such as:

- attempted passes;
- completed passes;
- key passes;
- progressive actions;
- crosses;
- dribbles;
- defensive actions;
- pressures;
- interceptions;
- clearances;
- recoveries;
- tackles;
- cards;
- substitutions;
- player minutes;
- shots and shot locations;
- possession/territory measures;
- event-level actions;

then each distinct source facet should be retained and mapped independently where structurally valid.

Higher-level concepts can be derived later from the preserved atomic evidence.

### Phase F — Match evidence completeness audit

After mapping, produce a match-data completeness matrix covering at minimum:

- fixture identity;
- team identity;
- player identity;
- participation;
- line-ups/substitutions;
- score/result;
- event evidence;
- team performance statistics;
- player performance statistics;
- disciplinary data;
- possession/territory;
- passing/creation;
- defensive actions;
- shooting;
- goalkeeper actions;
- contextual metadata;
- temporal availability/provenance.

The matrix should distinguish:

- source exists + mapped;
- source exists + unmapped;
- source absent;
- source present but identity unresolved;
- source present but temporally unsafe;
- derived only.

## Research-facing boundary

Mapping is not the same as exposure.

A variable can be completely mapped and validated while remaining unavailable to the GUI or public query layer until its research semantics have been designed.

The correct order is:

```text
source discovery
→ mapping
→ validation
→ canonical/evidence availability
→ research service
→ GUI exposure
```

## Safety rules

1. Do not silently mutate raw source data.
2. Do not invent a missing source field from a related statistic.
3. Do not treat source identifiers from different families as interchangeable.
4. Do not create a cross-source identity merely to make a variable join.
5. Preserve event-time, availability-time and ingestion-time distinctions.
6. Preserve provenance for every mapped field.
7. Preserve atomic source facets even when they are not immediately useful.
8. Do not delete or overwrite existing mappings until the replacement has been validated.
9. Keep source inventory, mapping and research exposure as separate layers.
10. Reuse the established player/team/fixture identity bridges before creating new ones.

## Execution target

The immediate target is:

**477 mapped → full source-variable census → complete unmapped frontier → systematic mapping → richest validated match evidence layer.**

The ~900 figure is an initial working estimate, not an immutable count. The authoritative count must come from the new complete census.

## Completion condition

The phase is complete when the FRL can answer, for every source variable in the approved match-data universe:

1. what the field is;
2. where it comes from;
3. what observation it belongs to;
4. how its identity is established;
5. what its temporal semantics are;
6. how it is transformed, if at all;
7. whether it is mapped and validated;
8. why it is or is not research-facing.

Only after that should the project decide which variables deserve GUI/query exposure.
