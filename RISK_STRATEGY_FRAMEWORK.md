# Risk Strategy Framework — Football Research Laboratory

**Last reviewed:** 30 August 2026

## Status

This is the durable quality architecture for the Football Research Laboratory.

Current milestone state belongs in `CURRENT_WORK.md`; repository-memory governance belongs in `FRL_DOCUMENTATION_SYNC_CONTRACT.md`.

## Governing principle

> **No result is allowed to become research knowledge unless the system can show where the data came from, which representation was used, what information was available at the time, what transformation produced the result, what population it describes, and how the claim was evaluated.**

## 1. Layered quality architecture

FRL should be understood as a chain of evidence and governed transformations rather than a single application:

```text
PRESERVED SOURCE EVIDENCE
        ↓
VALIDATED / RECONCILED EVIDENCE
        ↓
IDENTITY / RELATIONSHIPS
        ↓
SOURCE REPRESENTATION / ROUTE
        ↓
GOVERNED VARIABLE
        ↓
METRIC + COVERAGE / MISSINGNESS
        ↓
POPULATION / COMPARABILITY
        ↓
HISTORICAL STATE / ANALYSIS
        ↓
RESEARCH / MODELS
        ↓
EVALUATION
        ↓
DECISION / MARKET (explicit)
        ↓
PRODUCT / GUI
```

The GUI is the least authoritative layer.

Market information remains quarantined from ordinary football research/model inputs unless the research question explicitly requires market information.

## 2. Raw evidence versus canonical and derived data

Raw/source data is evidence and should not be casually mutated into working truth.

Conceptually:

```text
SOURCE
  ↓
RAW / PRESERVED
  ↓
VALIDATED
  ↓
RECONCILED / CANONICAL WHERE JUSTIFIED
  ↓
DERIVED VARIABLES / FEATURES
  ↓
ANALYSIS / MODELS
```

Every important result should be traceable backwards through these stages.

A derived value inherits the limitations, rights dependencies, missingness and temporal semantics of its inputs.

## 3. Data contracts

Every ingestion/adapter boundary should validate explicit schema and semantic contracts where applicable:

- grain;
- identifiers;
- season / competition;
- timestamps;
- completion semantics;
- required fields;
- units;
- missing-value behaviour;
- uniqueness;
- relational integrity;
- source/version identity.

Unknown or contradictory schema conditions should fail closed rather than silently produce nonsense.

## 4. Source diversity and source routing

Different source families can expose apparently similar football concepts with different:

- names;
- grains;
- definitions;
- versions;
- units;
- missingness semantics;
- historical coverage;
- correction behaviour.

Follow `FRL_SOURCE_NORMALISATION_CONTRACT.md` and `FRL_SOURCE_ROUTE_AUDIT_2026-08-30.md`.

A source field-name match is not evidence of equivalence.

A source route should be chosen for a declared:

```text
football concept
+ requested grain
+ competition / period / as-of state
+ analytical purpose
```

Do not implement “first non-null source wins”.

Where representations cannot be harmonised defensibly:

1. preserve both;
2. keep provenance/version identity;
3. expose the semantic limitation;
4. leave canonical comparability unavailable until established.

## 5. Whole-ecosystem discovery

When a requested metric, classification, identity mapping or retrieval capability is not clearly established, the default is **discovery before implementation or acquisition**.

Follow `FRL_DATA_ECOSYSTEM_DISCOVERY_CONTRACT.md`.

Failure to find a capability in one repository path or resolver is not proof that it is absent.

Inspect, where relevant:

- current implementation;
- archived/backup implementations;
- GitHub-tracked datasets;
- local upstream/source workspaces;
- source-family variants;
- preserved raw snapshots;
- partitioned datasets;
- identity bridges;
- merged/derived datasets;
- neighbouring fields / alternate grains;
- existing consumers;
- source documentation / provenance.

The audit should establish:

```text
source family
    ↓
representation / dataset
    ↓
grain
    ↓
identifiers
    ↓
coverage
    ↓
missingness semantics
    ↓
transformation / derivation
    ↓
consumer
    ↓
FRL suitability
```

## 6. Identity and relationship integrity

Source identifiers are evidence, not universal IDs.

Season-local team identity is distinct from persistent club identity.

Player, fixture, event, competition and source-family identities require explicit bridges where they cross boundaries.

Never join bare numeric IDs across source families merely because they look compatible.

Fail closed when the relationship cannot be verified.

## 7. Provenance and versioning

Important transformations must retain source lineage.

A user/researcher should eventually be able to ask:

> Where did this number come from?

and receive an inspectable answer including, where relevant:

- source family;
- source/version/snapshot;
- native field;
- identity route;
- transformation / aggregation;
- observed and eligible population;
- temporal cutoff;
- limitations.

Later snapshots or corrected source values must not silently overwrite evidence history.

## 8. Missingness and coverage

Missing evidence is not zero.

Every aggregate metric must distinguish, where relevant:

- eligible observations;
- observed observations;
- missing observations;
- structural zeros;
- observed total / numerator;
- denominator;
- coverage status.

A partial metric must not be presented as a complete-season/population statistic without explicit qualification.

Derived comparisons must use compatible populations.

Example: full-season goals must not be compared with partial-season xG to create an apparently full-season over/underperformance statistic.

## 9. Aggregation semantics

Aggregation is part of the metric contract.

Do not assume all numeric fields can be averaged or summed.

Typical distinctions:

- counts may be summable when source completeness/identity is established;
- percentages normally require numerator/denominator reconstruction;
- rates require an explicit denominator;
- per-90 requires governed minutes/eligibility;
- player → team aggregation requires concept-specific proof;
- provider-specific expected metrics remain source/version-specific unless equivalence is established.

## 10. Population, ranking and percentile risk

A rank/percentile is only meaningful relative to an explicit population.

A governed ranking should declare:

- competition / season / as-of state;
- eligible entities;
- exclusions;
- minimum coverage/minutes where relevant;
- metric representation/version;
- tie policy;
- percentile method;
- directionality;
- whether the percentile is raw distributional position or performance-oriented.

Do not rank incomplete observations alongside complete observations as though they were directly comparable.

Player populations require particular care around position, role, minutes and team context.

## 11. Three kinds of time

FRL distinguishes:

### Event time
When the football event occurred.

### Availability time
When the information became knowable to a hypothetical historical analyst.

### Ingestion time
When FRL happened to retrieve/capture the information.

For historical simulation and leakage control, availability time is the critical constraint.

A final historical record does not prove the information was available at the historical cutoff.

## 12. Temporal integrity / leakage

A derived research feature or model input must not use information unavailable at the prediction/evaluation timestamp.

Conceptually:

```text
latest allowed input availability < prediction/evaluation cutoff
```

A violation is a leakage failure, not a minor warning.

## 13. Research versus market

The research engine should answer:

> What do the football evidence and model imply?

The market layer should answer:

> What price is available at a declared observation time?

Then a separate decision layer can compare:

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

Kelly staking is strategy configuration, not part of the football model.

## 14. Model evaluation

Time-respecting evaluation is the default.

Preferred structures include:

- walk-forward evaluation;
- season-based holdouts;
- discovery vs unseen test periods;
- prospective validation where practical.

Random train/test splits are not the primary historical evaluation method for time-dependent football data.

## 15. Baseline discipline

Complexity must earn its place.

Candidate models should be compared with deliberate simple baselines such as:

- historical league frequencies;
- Elo-style baselines;
- simple goals-for/goals-against models;
- simple Poisson.

If a more complex model cannot show credible out-of-sample improvement, complexity is not automatically justified.

## 16. Robustness and false discovery

Exploratory research can find interesting patterns without validating them.

FRL must distinguish:

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

Large variable/hypothesis spaces increase false-discovery and p-hacking risk.

Future experiment/result tracking should preserve failed and inconclusive tests as well as attractive findings.

## 17. Test classes

### Unit tests
Does a function produce the expected result for controlled inputs?

### Integration tests
Do components and source/identity/analysis seams work together?

### Data-quality tests
Is the evidence structurally trustworthy and correctly linked?

### Analytical-contract tests
Are aggregation, coverage, missingness, populations and ranking semantics correct?

### Statistical evaluation
Does research/model performance generalise, calibrate and survive robustness/baseline testing?

Passing one class does not imply passing another.

## 18. Validation-state rule

Do **not** hard-code an old test count into this durable risk contract as though it were the eternal current baseline.

Dated closeout/audit documents preserve historical validated checkpoints.

For current work:

- run the applicable current gates;
- report actual command output;
- record material validation state in `CURRENT_WORK.md` when useful;
- do not claim a gate passed unless it was run for the relevant state.

## 19. Documentation drift as a quality risk

FRL uses repository documentation as operational memory.

Stale standing documents can cause new sessions to implement against obsolete architecture even when the code/data are correct.

Therefore material milestones must follow `FRL_DOCUMENTATION_SYNC_CONTRACT.md`.

Documentation drift is a project-quality defect when it changes the assumptions future work is instructed to trust.

## 20. Research release principle

A model or analytical claim should graduate from exploratory work only after surviving the controls appropriate to its purpose, such as:

```text
DATA / SOURCE VALIDATION
      ↓
IDENTITY / RELATIONSHIP VALIDATION
      ↓
METRIC / POPULATION VALIDATION
      ↓
TEMPORAL / LEAKAGE VALIDATION
      ↓
OUT-OF-SAMPLE TESTING
      ↓
CALIBRATION
      ↓
ROBUSTNESS
      ↓
BASELINE COMPARISON
      ↓
UNSEEN / PROSPECTIVE DATA
```

The objective is not certainty. It is to make uncertainty, assumptions and failure modes visible and bounded.

## Final principle

> **Preserve the evidence, govern the representation, make the population explicit, keep time honest, and do not let presentation outrun what the system can defend.**
