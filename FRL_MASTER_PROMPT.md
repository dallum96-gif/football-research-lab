# Football Research Laboratory — Master Prompt

We are working on the Football Research Laboratory (FRL).

For current project state, always read `CURRENT_WORK.md` and `data/frl_documentation_state_v1.json`. For documentation-governance rules read `FRL_DOCUMENTATION_SYNC_CONTRACT.md`.

## North Star

The Football Research Laboratory is intended to become a serious, extensible football research and modelling platform, not merely a football statistics website or a single betting model.

Its purpose is to allow a researcher to start with a football question or hypothesis and progressively:

**interrogate governed football evidence → identify patterns → understand what is happening → construct derived metrics → build and evaluate models → apply useful models where appropriate.**

The system should ultimately allow the user to query almost anything that can reasonably be answered from available football data, including through a future natural-language interface whose answers retain evidence and provenance.

## Core principles

### 1. Data is infrastructure

Build a rich, well-understood historical evidence foundation. Preserve useful source variables even when their future analytical application is unknown.

### 2. Source truth is plural

The preserved ecosystem may contain several legitimate representations of the same football concept.

Do not collapse them because names look similar or because one is non-null.

Preserve:

- source family;
- source/version identity;
- grain;
- native meaning;
- missing-value semantics;
- coverage;
- transformation / derivation;
- rights/provenance status.

Select a governed source representation for the requested concept, grain, period and analytical purpose.

### 3. The architecture must support discovery

Do not design the system around today's hypotheses or preferred metrics. The underlying evidence and architecture should outlive any individual metric, question or model.

### 4. Derived metrics and models are experiments

Metrics, features and predictive models should be straightforward to construct, compare, revise and replace.

Derived status never removes source limitations, missingness, provenance or temporal constraints.

### 5. Research comes before betting

Betting is an eventual downstream application of predictive research, not the purpose of the underlying platform.

### 6. Explanation matters as well as prediction

FRL should help explain football phenomena, not merely produce predictions.

### 7. Data quality and provenance come before presentation

Interfaces and analytical outputs must not outrun the reliability, coverage, provenance or understanding of the underlying evidence.

### 8. The user should not need to know the database schema

Backend complexity should be accessible through structured exploration and eventually natural-language querying.

### 9. Historical state is first-class

FRL must support reconstruction of moments in time and must distinguish:

- event time;
- information-availability time;
- ingestion/retrieval time.

Do not use future information when reconstructing historical state or evaluating a model.

### 10. Missingness is part of the meaning

Missing evidence is not zero.

Every aggregate, rate, comparison and ranking must use an explicit observed/eligible population and must expose limitations where coverage is partial.

## Governing idea

> **We are not building one football model. We are building the research environment in which we can discover which models, metrics and explanations are worth building.**

## Architectural direction

The current analytical direction is:

```text
PRESERVED SOURCE EVIDENCE
        ↓
IDENTITY / RELATIONSHIPS
        ↓
SOURCE REPRESENTATION
        ↓
GOVERNED SOURCE ROUTE
        ↓
GOVERNED VARIABLE
        ↓
METRIC + COVERAGE / MISSINGNESS
        ↓
POPULATION / COMPARABILITY
        ↓
ANALYSIS RESULT
        ↓
FASTAPI
        ↓
NEXT.JS PRODUCT / RESEARCH CONSUMERS
```

This is a target analytical spine. Existing code may remain transitional while it is migrated safely.

## Source and capability discovery

A field not being found in one resolver or repository path is not proof that FRL lacks the capability.

Before declaring data absent or acquiring another source, inspect the relevant preserved ecosystem according to `FRL_DATA_ECOSYSTEM_DISCOVERY_CONTRACT.md`.

A useful future capability distinction is:

```text
SOURCE_PRESENT
CONNECTED
DERIVABLE
GOVERNED
COMPARABLE
PRODUCT_READY
```

These are not interchangeable states.

## Product architecture

The durable product rule is:

> **Profiles describe entities. Stats analyse entities. Rankings analyse populations. Compare analyses selected entities together. Research tests the questions these surfaces reveal.**

Team / Player analytical information architecture is documented in `FRL_TEAM_PLAYER_STATS_VISUALISATION_PROTOTYPE.md` and may evolve through evidence.

The active frontend is **Next.js + React** with **FastAPI** as the frontend-facing Python boundary. Streamlit remains legacy/reference implementation unless a task explicitly concerns it.

The exact immediate product milestone belongs in `CURRENT_WORK.md`, not in this durable master prompt.

## Research workflow

Preferred research progression:

```text
Observation
    ↓
Hypothesis
    ↓
Formalisation
    ↓
Historical / empirical test
    ↓
Challenge and alternative explanations
    ↓
Out-of-sample / prospective evaluation where appropriate
    ↓
Research conclusion
```

Exploratory patterns must not automatically become trusted evidence.

## Probabilistic and modelling discipline

Distinguish clearly between:

- plausible explanation;
- historical association;
- predictive improvement over a baseline;
- out-of-sample predictive performance;
- calibrated probability;
- economic value after realistic market costs.

Backtests alone are insufficient. Temporal leakage, selection bias, multiple testing, calibration and robustness must be considered.

## Commercial objective

Revenue generation is legitimate, but FRL should not be forced to become the revenue vehicle if another opportunity has materially stronger evidence of demand and fit.

Commercial discovery should follow the same evidence-led philosophy as research.

## Learning objective

FRL is also a vehicle for developing the researcher's quantitative, software and analytical understanding.

Do not outsource understanding merely because implementation can be outsourced.

Use important real FRL problems to teach the relevant statistical, modelling, software and research concepts where practical.

## Working method

For substantial workstreams establish:

- objective;
- definition of done;
- necessary steps;
- current step;
- review point.

Separate research/audit mode from build mode.

When new evidence changes the plan, update the plan deliberately rather than allowing interesting side work to displace the objective invisibly.

## Repository recovery

Treat `dallum96-gif/football-research-lab` as the source of truth for tracked code and durable documentation.

For a fresh substantive session:

1. read `FRL_MASTER_PROMPT.md`;
2. read `PROJECT_ORIENTATION.md`;
3. read `CURRENT_WORK.md`;
4. inspect `data/frl_documentation_state_v1.json`;
5. establish branch / working tree / upstream state;
6. inspect task-relevant contracts, implementation and preserved source routes;
7. run validation appropriate to the change;
8. reconcile standing documentation when the milestone materially changes project state.

Do not ask the user to re-explain information recoverable from the repository.

## Documentation sync rule

Repository memory is part of the architecture.

> **Whenever a milestone materially changes current architecture, product phase, validation interpretation, source-routing understanding, frontend status or design language, the milestone is not complete until standing repository memory has been checked for drift.**

See `FRL_DOCUMENTATION_SYNC_CONTRACT.md`.

## Final principle

> **Build the foundations. Preserve source truth. Govern the meaning. Keep time honest. Test the ideas. Follow the evidence.**
