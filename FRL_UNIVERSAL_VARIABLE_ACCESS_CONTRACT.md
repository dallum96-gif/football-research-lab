# FRL Universal Variable Access Contract

**Status:** Foundational architecture contract — v1.0

## Purpose

Every validated FRL variable should be discoverable and retrievable through one standard programmatic interface without requiring downstream consumers, including the GUI, to know the variable's source schema, storage location or source-family-specific retrieval mechanism.

The FRL should therefore distinguish:

```text
VARIABLE CATALOGUE
    ↓
What is this variable?
    ↓
VARIABLE RESOLVER
    ↓
Give me its values for this context
    ↓
QUERY / RESEARCH SERVICES
    ↓
GUI / OTHER CONSUMERS
```

## 1. Five lifecycle states

A source-backed variable moves through explicit states where applicable:

1. `DISCOVERED` — the source field/capability has been found.
2. `CATALOGUED` — the variable's meaning, grain and source are recorded.
3. `VALIDATED` — identity, semantics, coverage and provenance are sufficiently established for reusable FRL access.
4. `RESOLVABLE` — a tested resolver can retrieve the variable for its supported context.
5. `GUI_ACCESSIBLE` — the GUI can request the variable through the standard resolver contract.

These states must not be collapsed. A source field existing does not prove that a safe GUI retrieval pathway exists.

## 2. Variable metadata contract

A variable definition should expose, where applicable:

- canonical FRL variable name;
- human-readable label;
- definition;
- entity/grain;
- source family;
- native source field(s);
- transformation/derivation;
- units / value type;
- historical coverage;
- identity requirements;
- missing-value semantics;
- provenance metadata;
- resolution service/path;
- lifecycle status.

## 3. Resolver contract

Consumers should request variables through a standard operation conceptually equivalent to:

```python
resolve_variable(
    variable="successfulDribbles",
    fixture=(season, fixture_id),
)
```

The resolver is responsible for determining the appropriate source family and retrieval pathway from the variable definition.

Consumers must not independently:

- inspect source CSV paths;
- guess source field names;
- construct provider-specific joins;
- duplicate identity reconciliation;
- reimplement documented metric transformations;
- silently substitute a different variable.

## 4. Grain-aware resolution

The resolver must respect the canonical FRL grains:

```text
Fixture        = (season, fixture_id)
Team–Fixture   = (season, fixture_id, persistent_team_code)
Player–Fixture = (season, fixture_id, canonical player identity)
```

A request for a player-fixture variable must therefore resolve through the verified player-fixture relationship rather than attempting to infer a player identity from display names or unrelated numeric IDs.

## 5. Derived variables

Derived display/research variables should have explicit definitions in the same catalogue/resolution framework.

For example:

```text
Tackle won %
    = wonTackle / totalTackle

Pass completion %
    = accuratePass / totalPass
```

The calculation belongs to the analytical/resolution layer, not to the GUI component.

Division-by-zero and missing-data semantics must be explicit.

## 6. GUI rule

The GUI should be variable-agnostic.

A presentation component may request a list of canonical FRL variables and receive structured, provenance-aware values. The component should not need to know whether the values originate from team-match, player-match, player-season, FPL, PulseLive, another validated source family, or a documented derived calculation.

The GUI may decide which variables to expose prominently, but it must not become a second variable registry or second analytical engine.

## 7. Research/data safety

Universal accessibility does **not** mean every discovered field is automatically promoted.

The FRL retains the distinction:

```text
retain broadly
    ↓
validate rigorously
    ↓
resolve safely
    ↓
expose progressively
    ↓
promote empirically
```

Variables with unresolved semantics, identity ambiguity, insufficient coverage or provenance problems remain unavailable to consumers that require validated evidence.

## 8. Failure behaviour

Resolution must fail closed when the requested variable cannot be supported safely.

A resolver should distinguish at least:

- variable unknown;
- variable known but not validated;
- variable validated but not resolvable for this context;
- value unavailable for this fixture/player/season;
- value successfully resolved.

It must not turn unavailable values into false zeros or silently select a different metric.

## 9. Provenance

A successful resolution should retain enough metadata for the consumer to understand:

```text
variable
source
status
context
transformation
coverage
```

The user should ultimately be able to ask where a displayed value came from and trace it through the existing FRL provenance architecture.

## 10. Architectural objective

The durable objective is simple:

> **If a variable is validated by the FRL, an authorised consumer should be able to request it without needing to know where it lives.**

This contract exists to make that property systematic rather than dependent on one-off GUI integrations.
