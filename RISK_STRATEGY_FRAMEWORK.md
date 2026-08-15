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

## 4. Identity

Season-local team IDs are not globally stable.

Persistent club identity is a separate concern from season-local identity.

Historical changes such as renames, promotions, relegations and source-ID changes must be handled through identity registries rather than ad hoc string matching.

## 5. Provenance

Important transformations must retain source lineage.

For corrected fixtures, preserve both the canonical analytical state and the evidence describing the correction.

A user should eventually be able to ask:

> Where did this number come from?

and receive an inspectable answer.

## 6. Three kinds of time

The system distinguishes:

### Event time
When the football event occurred.

### Availability time
When the information became knowable to a hypothetical historical analyst.

### Ingestion time
When our tooling happened to retrieve the information.

For historical simulation and leakage control, availability time is the critical constraint.

## 7. Temporal integrity / leakage

A derived research feature must not use information unavailable at the prediction/evaluation timestamp.

Conceptually:

```text
source availability time < prediction time
```

If a feature violates this, it is a leakage failure, not a minor warning.

Historical state is intended eventually to answer:

> What did the laboratory know immediately before this fixture?

## 8. Research versus market

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

## 9. Model evaluation

Time-respecting evaluation is the default.

Random train/test splits are not the primary historical evaluation method for time-dependent football data.

Preferred structures include:

- walk-forward evaluation;
- season-based holdouts;
- discovery versus unseen test periods.

## 10. What good means

Evaluation should be defined before optimisation.

Probability models should be assessed using measures such as:

- log loss
- Brier score
- calibration
- discrimination/resolution
- domain-appropriate distributional/scoring measures

Goal models may also use Poisson/deviance, MAE, RMSE and distributional scoring measures as appropriate.

Results should be compared with simple baselines.

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
