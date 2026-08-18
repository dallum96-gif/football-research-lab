# Risk Strategy Framework — Football Research Laboratory

## Status

This is the quality architecture for the whole Football Research Laboratory.

It is not merely a testing script.

## Governing principle

> **No result is allowed to become research knowledge unless the system can show where the data came from, what information was available at the time, what transformation produced it, and how the result was tested out-of-sample.**

## 1. Layered architecture

The laboratory should be thought of as five functional quality layers around the research process:

```text
RAW / SOURCE
        ↓
CANONICAL / VALIDATED
        ↓
HISTORICAL STATE
        ↓
RESEARCH / MODELS
        ↓
QUALITY / CONTROL
        ↓
EVALUATION
        ↓
DECISION / MARKET (explicit)
        ↓
GUI
```

Market information is quarantined from the research layer by default. A model may explicitly include market information only when that is the research question.

## 2. Raw evidence versus canonical data

Raw/source data is evidence and should not be casually mutated into the working truth.

Conceptual pipeline:

```text
SOURCE
  ↓
RAW
  ↓
VALIDATED
  ↓
CANONICAL
  ↓
FEATURES
  ↓
OUTPUTS
```

Every important result should be traceable backwards through these stages.

## 3. Data contracts

Every ingestion boundary should validate an explicit schema contract.

For fixtures this includes, as appropriate:

- fixture identity
- season
- kickoff timestamp
- home team
- away team
- completion/result semantics
- recognised team identities
- uniqueness
- valid dates
- relational integrity

An unknown schema should stop the pipeline rather than silently produce nonsense.

### Source diversity and league portability

The FRL must assume that different leagues, competitions and source families may provide materially different schemas, field names, identifier systems, grains, units and definitions for apparently similar concepts.

The FRL should therefore use explicit source adapters / normalisation contracts rather than assuming that one provider schema is universal. See `FRL_SOURCE_NORMALISATION_CONTRACT.md`.

Each adapter should document, where applicable:

- source field name;
- source field definition;
- source grain;
- source identifier;
- FRL canonical concept;
- transformation or aggregation applied;
- units and scaling;
- missing-value semantics;
- coverage limitations;
- source/version/provenance.

A field-name match is not sufficient evidence that two sources measure the same thing. When concepts cannot be harmonised defensibly, preserve source-specific evidence and leave the FRL canonical concept unavailable rather than creating false equivalence.

This architecture allows the FRL to expand across leagues without forcing every new source to imitate the first provider's schema.

## 4. Identity

Season-local team IDs are not globally stable.

Persistent club identity is a separate concern from season-local identity.

Historical changes such as renames, promotions, relegations and source-ID changes must be handled through identity registries rather than ad hoc string matching.

Player, fixture and event identifiers should follow the same principle: source identifiers remain source-local until explicitly reconciled into a verified FRL identity.

## 5. Provenance

Important transformations must retain source lineage.

For corrected fixtures, preserve both the canonical analytical state and the evidence describing the correction.

A user should eventually be able to ask:

> Where did this number come from?

and receive an inspectable answer.

## 6. Existing-mechanism discovery

When a requested metric, classification, identity mapping or retrieval capability is not clearly established in the Laboratory repository, the default response is **discovery before implementation**.

The preferred discovery order is:

```text
CURRENT WORKING APPLICATION
        ↓
ARCHIVED / BACKUP IMPLEMENTATIONS
        ↓
LOCAL UPSTREAM SOURCE TREE
        ↓
GITHUB LABORATORY CONTRACTS
        ↓
NEW IMPLEMENTATION (only if genuinely necessary)
```

### Whole-data-ecosystem discovery requirement

`FRL_DATA_ECOSYSTEM_DISCOVERY_CONTRACT.md` is authoritative for discovery completeness.

**Failure to find a field, metric, classification or capability in one repository location is never sufficient evidence that it does not exist.**

Before concluding that information is absent, unavailable, or requires a new external source, audit the relevant whole ecosystem, including where applicable:

- the current working application and query layer;
- archived, backup and previous implementations;
- all relevant GitHub-tracked datasets and directory structures;
- the local upstream/source workspace;
- source-family variants and parallel data products;
- partitioned datasets such as `by_position`;
- identity registries and crosswalks;
- merged/derived datasets;
- neighbouring fields that may encode the requested concept under a different name or grain;
- source documentation and provenance notes.

Do not search only for the expected metric/column name. The same information may exist at another grain, in a partitioned dataset, in an upstream source family, or as a documented derived quantity.

The audit should establish, where applicable:

```text
SOURCE FAMILY
     ↓
FILE / ENDPOINT / DATASET
     ↓
GRAIN
     ↓
RELEVANT FIELDS
     ↓
IDENTIFIER KEYS
     ↓
COVERAGE
     ↓
TRANSFORMATION / DERIVATION
     ↓
EXISTING CONSUMER
     ↓
FRL SUITABILITY
```

If the ecosystem audit genuinely finds no defensible source, record that conclusion and the evidence supporting it before sourcing externally.

Existing working behaviour is evidence of intended behaviour. Archived implementations may reveal established retrieval paths, classifications, calculations and interface contracts.

The search must not depend only on the expected metric name. Inspect the relevant directory structure, neighbouring metrics, source identifiers, representative schemas, known consumers and existing transformations. Trace the lineage:

```text
RAW SOURCE
  ↓
STORED SOURCE DATA
  ↓
RETRIEVAL / TRANSFORMATION
  ↓
AGGREGATION / CLASSIFICATION
  ↓
EXISTING CONSUMER
```

Failure to find a mechanism in the Laboratory repository is **not evidence that the mechanism does not exist**. Where an upstream/local source or working implementation is known, those sources should be inspected before inventing a substitute.

Before modifying code, establish and record, where applicable:

- source of the information;
- source field(s);
- identity keys and classification rules;
- existing retrieval function/path;
- aggregation or transformation rules;
- existing consumer demonstrating the capability;
- proposed reuse point.

This is especially important when a capability is believed to already exist. Reuse the established mechanism rather than recreating an apparently equivalent one.

## 7. Three kinds of time

The system distinguishes:

### Event time
When the football event occurred.

### Availability time
When the information became knowable to a hypothetical historical analyst.

### Ingestion time
When our tooling happened to retrieve the information.

For historical simulation and leakage control, availability time is the critical constraint.

## 8. Temporal integrity / leakage

A derived research feature must not use information unavailable at the prediction/evaluation timestamp.

Conceptually:

```text
source availability time < prediction time
```

If a feature violates this, it is a leakage failure, not a minor warning.

Historical state is intended eventually to answer:

> What did the laboratory know immediately before this fixture?

## 9. Research versus market

The research engine should answer:

> What do the football data and model imply?

The market layer should answer:

> What price is currently available?

Then, and only then, can a separate decision layer compare:

```text
MODEL
  ↓
FAIR PROBABILITY
  ↓
FAIR PRICE
  ↓
MARKET PRICE
  ↓
EDGE / EV
  ↓
STRATEGY / STAKING
```

Kelly staking is a strategy configuration, not part of the football model itself.

## 10. Model evaluation

Time-respecting evaluation is the default.

Random train/test splits are not the primary historical evaluation method for time-dependent football data.

Preferred structures include:

- walk-forward evaluation;
- season-based holdouts;
- discovery versus unseen test periods.

## 11. Baseline discipline

Complexity must earn its place.

Candidate models should be compared with deliberately simple baselines such as:

- historical league frequencies
- Elo-only approaches
- simple goals-for/goals-against models
- simple Poisson

If a sophisticated model cannot demonstrate out-of-sample improvement over appropriate baselines, complexity is not automatically justified.

## 12. Robustness and false discovery

Exploratory research can find interesting patterns without proving them.

The laboratory must distinguish:

```text
Interesting
  ≠
Validated
  ≠
Out-of-sample validated
  ≠
Robust
  ≠
Profitable
```

Searching large numbers of historical combinations creates false-discovery and p-hacking risks. Future tooling should record experiments and distinguish discovery from confirmation.

Similarity/comparable-match engines require the same scientific treatment. Similarity must itself be validated retrospectively and stress-tested for sensitivity to reasonable parameter changes.

## 13. Four test classes

### Unit tests
Does a function produce the expected result for controlled inputs?

### Integration tests
Do components work together correctly?

### Data-quality tests
Is the underlying dataset structurally trustworthy?

### Statistical evaluation
Does the research generalise out-of-sample, remain calibrated, survive robustness checks and beat suitable baselines?

Passing one category does not imply passing another.

## 14. Current automated assurance

The current validated research baseline is **26/26**:

- Query Lab: 14/14
- Player Research V0.1: 6/6
- Player Research V0.2: 6/6

The project-health gate is a separate structural/data gate.

## 15. Research release principle

A model should graduate from exploratory work to trusted research only after surviving, where applicable:

```text
DATA VALIDATION
      ↓
LEAKAGE / TEMPORAL VALIDATION
      ↓
WALK-FORWARD / OUT-OF-SAMPLE TESTING
      ↓
CALIBRATION
      ↓
ROBUSTNESS
      ↓
BASELINE COMPARISON
      ↓
UNSEEN DATA
```

The purpose is not to prove certainty. It is to make uncertainty visible and bounded.
