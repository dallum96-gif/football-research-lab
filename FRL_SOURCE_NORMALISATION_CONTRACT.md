# Football Research Laboratory — Source Normalisation & Multi-League Contract V1

**Status:** Foundational data architecture contract
**Date:** 17 August 2026
**Governing documents:** `RISK_STRATEGY_FRAMEWORK.md`, `FRL_DATA_HIERARCHY_RELATIONSHIP_CONTRACT.md`, `FRL_RELATIONSHIP_INTEGRITY_CONTRACT.md`, `FRL_DATA_PLATFORM_ARCHITECTURE_V1.md`, `FRL_DATA_RESIDENCY_LINEAGE_INVENTORY_V1.md`, `NON_DESTRUCTION_ASSURANCE.md`

## 1. Purpose

The FRL must support football data from multiple leagues, competitions and source families without assuming that they share one universal schema.

Different sources may use different:

- field names;
- schemas;
- grains;
- identifiers;
- units;
- timestamp conventions;
- missing-value semantics;
- metric definitions;
- positional classifications;
- historical coverage;
- correction/versioning behaviour.

This contract defines how the FRL absorbs that diversity without flattening away source meaning or creating false equivalence.

## 2. Core rule

> **Normalise meaning, not merely column names.**

A field is not considered equivalent to an FRL concept merely because its name looks similar to another source field.

For example:

```text
shots_on_target
sot
SoT
shots_on_frame
```

may or may not represent the same concept. The source definition, grain, units and calculation must be established before promotion.

## 3. Source-native preservation

Every source should first be retained in its native representation where practical.

The raw/validated evidence layer must preserve:

- native field names;
- native identifier values;
- native units;
- native categorical labels;
- source grain;
- source/version identity;
- retrieval or snapshot metadata;
- source-specific missing-value semantics.

Source-native evidence must not be destroyed merely because it has been mapped into an FRL concept.

## 4. Source adapter boundary

Each source family should enter FRL through an explicit source adapter or normalisation contract.

Conceptually:

```text
SOURCE A
  ↓
adapter A
  ↓
                 ┐
SOURCE B → adapter B ├→ FRL canonical concept
                 │
SOURCE C → adapter C ┘
```

The adapter is responsible for making the source-to-FRL transformation inspectable and testable.

An adapter should document, where applicable:

- source field;
- source definition;
- source grain;
- source identifier;
- FRL canonical concept/field;
- transformation;
- aggregation;
- unit conversion;
- timestamp conversion;
- missing-value mapping;
- confidence/coverage limitations;
- source/version/provenance.

## 5. Canonical semantics

The FRL canonical layer defines stable meanings for concepts that are shared across sources.

Canonical fields should therefore represent the **FRL definition**, not the wording of the first source we happened to ingest.

Where multiple sources can populate the same canonical concept, each contribution retains its source lineage.

Where a concept cannot safely be harmonised, the FRL must:

1. preserve the source-specific evidence;
2. document the semantic mismatch;
3. leave the canonical concept unavailable or source-specific;
4. avoid inventing a conversion based on assumption alone.

## 6. Grain is part of the meaning

Source grain must be explicit.

Examples:

```text
player-season
player-fixture
team-fixture
fixture
event
player-career
```

A season-level classification must not be presented as fixture-level evidence.

An event-level variable must not automatically be interpreted as an aggregated match statistic.

When a transformation changes grain, the adapter/derivation must document the rule used to do so.

## 7. Identity portability

Source identifiers are source-local until verified.

The normal path is:

```text
source identifier
      ↓
source-specific identity bridge
      ↓
verified FRL identity
```

This applies to:

- leagues;
- teams/clubs;
- players;
- fixtures/matches;
- events.

Do not join across sources merely because two numeric IDs happen to be equal.

## 8. Season and competition portability

A league/source combination must not be assumed to share the FRL's existing season or competition encoding.

Adapters must explicitly establish:

- competition identity;
- season identity;
- calendar/competition boundaries;
- promotion/relegation or membership semantics;
- postponed/rescheduled fixture handling;
- competition-specific completion semantics.

The canonical FRL model may use a consistent internal representation while preserving the native source encoding in the provenance layer.

## 9. Units and definitions

Numeric equivalence requires semantic verification.

Examples that require explicit treatment include:

- metres vs kilometres;
- seconds vs minutes;
- raw counts vs per-90 rates;
- percentages vs proportions;
- expected-goal definitions from different providers;
- chances created definitions from different providers;
- tackles/duels/interceptions definitions from different providers.

The adapter must never silently change units or definitions.

## 10. Availability and historical validity

Source fields must retain temporal provenance where relevant.

A field can be:

- valid for all seasons;
- introduced in a later season;
- redefined by a provider;
- absent for some competitions;
- available only through a later historical snapshot.

These distinctions must remain visible because they affect research comparability and model training.

## 11. Cross-league comparability

A metric appearing in multiple leagues is not automatically comparable.

Before combining sources across competitions, FRL should assess:

- definition equivalence;
- recording methodology;
- league/source coverage;
- unit equivalence;
- population differences;
- provider revisions;
- historical availability.

Where the evidence does not support direct comparability, the metric should remain league/source-specific or be explicitly adjusted through a documented methodology.

## 12. Promotion states

Source data may exist in four useful states:

```text
RAW
  ↓
VALIDATED
  ↓
RECONCILED
  ↓
CANONICAL
```

A source can be valuable without reaching canonical status.

For example, a new league may initially have:

- raw match data;
- verified fixture identity;
- partial player identity;
- no defensible cross-source xG equivalence.

That source can still support source-specific research while the unresolved canonical concepts remain unavailable.

## 13. Testing requirements

Every source adapter should have tests for, where applicable:

- schema recognition;
- required-field presence;
- type and unit conversion;
- identifier uniqueness;
- identity resolution;
- grain preservation;
- missing-value semantics;
- representative metric values;
- source-to-canonical mappings;
- season/competition mapping;
- known edge cases;
- fail-closed behaviour for unresolved/ambiguous mappings.

The test suite should contain at least one representative fixture/player/team relationship test for each new source family.

## 14. Data-harmony rule

The objective is **not** to make every source look identical.

The objective is to make the FRL capable of answering cross-source questions while remaining honest about differences.

Therefore:

```text
source diversity
      ↓
explicit adapters
      ↓
shared canonical concepts where defensible
      ↓
source-specific concepts where necessary
      ↓
research/model layer chooses appropriate comparability
```

Source diversity is a feature of the evidence system, not a defect to be hidden.

## 15. North Star alignment

This contract exists to allow the FRL to expand from Premier League data to additional leagues and competitions without forcing every source to imitate the first provider's schema.

It supports the long-term goal of:

- arbitrary research queries;
- cross-league comparisons where defensible;
- scouting and football intelligence;
- combined metrics;
- mathematical/statistical modelling;
- richer visualisation;
- future natural-language research.

The governing principle is:

> **Preserve source truth, reconcile explicitly, compare only when justified.**
