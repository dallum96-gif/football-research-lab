# Football Research Laboratory — Governed Source Routing Contract

**Status:** Foundational analytical-source contract  
**Date:** 30 August 2026

## 1. Purpose

FRL can preserve multiple legitimate representations of the same football concept across source families, source versions and grains.

This contract defines how FRL selects a representation for analytical use without destroying source meaning or inventing equivalence.

Read together with:

- `FRL_SOURCE_NORMALISATION_CONTRACT.md`;
- `FRL_DATA_ECOSYSTEM_DISCOVERY_CONTRACT.md`;
- `FRL_SOURCE_ROUTE_AUDIT_2026-08-30.md`;
- `FRL_SOURCE_RIGHTS_REGISTER.md`;
- `RISK_STRATEGY_FRAMEWORK.md`.

## 2. Core rule

> **Choose a source representation by meaning, grain, period and analytical purpose — never by field name or first non-null value.**

The strongest preserved route may vary by:

- football concept;
- requested grain;
- competition;
- season/as-of period;
- source/version;
- required completeness;
- analytical purpose.

There is no universal rule that one source family always outranks another.

## 3. Three distinct objects

### Source representation

A source-native or explicitly derived representation with known:

- source family;
- source/version/snapshot identity;
- native field(s);
- grain;
- identifiers;
- units;
- missingness semantics;
- coverage;
- provenance;
- rights status where known.

Examples:

- `events_stats.expectedGoals` at team-match grain;
- PulseLive snapshot `stats.expectedGoals` at team-match grain;
- `players_match_stats.expectedGoals` at player-match grain.

### Source route decision

An explicit decision selecting one representation for a declared analytical request.

A route decision must explain why that representation is suitable for the requested concept/grain/period/purpose.

### Governed variable

An FRL football concept with stable meaning whose current observation is supplied by an approved representation/route.

A governed variable is not merely a renamed source column.

## 4. Requested route context

Source routing should receive enough context to make the decision inspectable:

```text
football concept
+ requested grain
+ competition
+ season / as-of period
+ analytical purpose
+ required comparability / completeness
        ↓
source route decision
```

Examples of purpose may include:

- source-specific research;
- Team Stats display;
- league ranking;
- player cohort comparison;
- model feature construction;
- historical as-of reconstruction.

A representation acceptable for descriptive display may still be unsuitable for ranking or model training.

## 5. Route classifications

Every material route decision should use one of the following statuses.

### `KEEP_CURRENT_ROUTE`

The existing connected representation is already the strongest suitable preserved route.

### `BETTER_EXISTING_ROUTE`

A stronger direct preserved representation exists and should replace/supplement the currently connected route.

### `DERIVED_ROUTE_PREFERRED`

The strongest defensible observation should be constructed from another governed grain through an explicit derivation.

### `MULTIPLE_SOURCE_REPRESENTATIONS`

Several legitimate source-specific representations exist and should remain distinct.

### `SEMANTIC_REVIEW_REQUIRED`

Candidate representations exist but definition, grain, aggregation or equivalence is not sufficiently established.

### `COVERAGE_GAP`

The preserved ecosystem cannot honestly provide the requested concept/grain/period.

## 6. No silent fallback/coalescing

Forbidden pattern:

```text
if source_A is not null:
    use source_A
else if source_B is not null:
    use source_B
else:
    use source_C
```

unless a prior semantic contract has proved those representations interchangeable for the requested use.

A later/richer representation is not automatic historical truth.

When equivalence is unproven, preserve separate variable/representation identities.

## 7. Grain transformation

Changing grain creates a derivation and must be explicit.

Example:

```text
player-match observations
        ↓
governed player + fixture + team relationships
        ↓
concept-specific aggregation
        ↓
derived team-match observation
```

Before approval establish:

- that aggregation is meaningful for the football concept;
- required contributor completeness;
- structural zero vs missing rules;
- identity completeness;
- denominator/numerator rules where relevant;
- comparison against any independent direct representation.

Do not sum or average merely because values are numeric.

## 8. Aggregation families

Common patterns include:

### Additive count
Potentially summable when source completeness and identity are established.

Examples may include some goals, shots, passes or defensive counts.

### Ratio / percentage
Normally reconstruct from governed numerator and denominator rather than averaging source percentages.

### Rate
Requires an explicit denominator and eligible population.

### Per-90
Requires governed minutes and eligibility rules.

### Provider/model metric
Expected metrics such as xG/xA/xGOT remain provider/version-specific unless equivalence is established.

### Non-additive team state
Possession or other team-level shares must not be reconstructed through naive player summation.

## 9. Missingness and coverage

A source route must preserve the representation's missing-value semantics.

Every route used for aggregate/comparison work should be able to expose, where relevant:

- eligible observations;
- observed observations;
- missing observations;
- structural zeros;
- coverage status;
- known exceptions.

A route can be technically available but analytically unsuitable because coverage is not comparable.

## 10. Source/version and time

Representations may differ because of later snapshots, provider revisions or corrected source surfaces.

Preserve:

- retrieval/snapshot identity;
- event/fixture period;
- information-availability status where known;
- version/correction lineage.

A later snapshot may improve final historical descriptive evidence without proving that the value was available to a historical analyst at the earlier time.

## 11. Capability states

Source routing and capability inventory should ultimately distinguish:

### `SOURCE_PRESENT`
Evidence exists in the preserved ecosystem.

### `CONNECTED`
FRL can currently retrieve the representation through a registered adapter/resolver.

### `DERIVABLE`
FRL possesses governed inputs/relationships needed to construct the concept at the requested grain.

### `GOVERNED`
Meaning, route, aggregation, missingness and provenance have an approved contract.

### `COMPARABLE`
The observation is safe to compare across the requested population/period.

### `PRODUCT_READY`
Coverage and methodological clarity are sufficient for ordinary product exposure.

These states are intentionally separate.

## 12. Ranking/model restrictions

A metric route used for ranking must establish a comparable eligible population.

A metric route used for modelling must additionally establish temporal/as-of validity for the model's prediction cutoff.

A representation acceptable for season-end description may therefore remain invalid for historical model training.

## 13. Rights and operational independence

Route selection must not treat acquisition convenience as rights clearance.

Preserve the distinction between:

- distribution/acquisition channel;
- original provider;
- source/version;
- intended use;
- rights/terms status.

Using an already-preserved GitHub/local copy can reduce live API dependency without changing underlying data-rights uncertainty.

## 14. Current reference example: expected goals

The 30 August audit establishes multiple xG representations:

- direct team-match `events_stats.expectedGoals`;
- later preserved PulseLive snapshot team-match xG;
- player-match `players_match_stats.expectedGoals`;
- an explicit future player-match → team-match derived sum.

The player-derived route materially improves recent coverage but differs numerically from the direct team-match representation on overlap.

Therefore:

- do not silently use it as a fallback under the same source identity;
- version/name the derived representation explicitly;
- use exact-population coverage for derived comparisons;
- keep older-season coverage gaps visible.

See `FRL_SOURCE_ROUTE_AUDIT_2026-08-30.md`.

## 15. Initial routing families

The first families to receive explicit route policy should be:

1. fixture/result;
2. team-match shooting;
3. team-match expected metrics;
4. possession;
5. team-match passing;
6. defensive actions;
7. discipline;
8. goalkeeper actions;
9. chance creation / big chances;
10. player-match attacking;
11. player-match passing/possession;
12. player-match defending;
13. player-season context;
14. FPL-specific variables;
15. derived temporal/team-state variables.

A family rule is a default, not permission to ignore field-specific evidence.

## 16. Promotion workflow

Before a new route becomes governed:

```text
ecosystem discovery
    ↓
identify candidate representations
    ↓
verify grain / identity / semantics
    ↓
measure coverage
    ↓
compare overlapping values where possible
    ↓
define missingness / aggregation
    ↓
record provenance / version / rights status
    ↓
classify route
    ↓
add tests
    ↓
promote to governed route
```

## 17. Testing requirements

A governed route should have tests appropriate to its type, including where relevant:

- source schema recognition;
- identity resolution;
- grain preservation;
- missing-value mapping;
- coverage counts;
- structural zero handling;
- aggregation behaviour;
- known source-version exceptions;
- overlap/equivalence evidence;
- fail-closed behaviour;
- population/comparability restrictions.

## 18. Relationship to the analytical kernel

Source routing sits **below** metric construction.

Preferred flow:

```text
SourceRepresentation
    ↓
SourceRouteDecision
    ↓
GovernedVariable
    ↓
MetricDefinition / MetricObservation
    ↓
PopulationContext
    ↓
AnalysisResult
```

A metric should not need to know how to hunt through unrelated source files. It should request governed variables/representations through the routing contract.

## 19. Final principle

> **Preserve every legitimate representation, select one deliberately for the question being asked, and never hide semantic uncertainty behind convenient fallback logic.**
