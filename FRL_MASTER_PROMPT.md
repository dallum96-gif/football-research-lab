# Football Research Laboratory — Master Prompt

We are working on the Football Research Laboratory (FRL).

## North Star

The Football Research Laboratory is intended to become a serious, extensible football research and modelling platform, not merely a football statistics website or a single betting model.

Its purpose is to allow a researcher to start with a football question or hypothesis and progressively:

**interrogate the underlying data → identify patterns → understand what is happening → construct derived metrics → build and evaluate predictive models → apply useful models where appropriate, including betting.**

The system should ultimately allow the user to query almost anything that can reasonably be answered from the available football data, including through a future natural-language interface in which questions can be asked in plain English and answered with evidence and links back to the relevant underlying data and research objects.

The initial implementation may be relatively small in scope, but the architecture should remain deliberately extensible toward much larger league, team, fixture and player datasets.

## Core principles

### 1. Data is infrastructure

Build a rich, well-understood and historically useful data foundation. Preserve useful source variables even when their eventual analytical application is not yet known.

### 2. The architecture must support discovery

Do not design the system around today's hypotheses or today's preferred metrics. The underlying data and architecture should outlive any individual metric, research question or predictive model.

### 3. Derived metrics and models are experiments

Metrics, features and predictive models should be straightforward to construct, compare, revise and replace. There is no assumption that one permanent model is the correct model.

### 4. Research comes before betting

Betting is an eventual application of predictive research, not the purpose of the underlying platform. Predictive claims must be challenged and evaluated appropriately before money is risked.

### 5. Explanation matters as well as prediction

The Laboratory should help us understand football phenomena, not merely produce predictions. A useful relationship or historical precedent can be as valuable as a predictive model.

### 6. Data quality and provenance come before presentation

Interfaces, visualisations and analytical outputs must not outrun the reliability, coverage, provenance or understanding of the underlying data.

### 7. The user should not need to know the database schema

Backend complexity should be accessible through structured exploration and eventually natural-language querying. The backend may be considerably richer than what is directly exposed in the UI.

### 8. Historical state is first-class

The Laboratory must support reconstruction of moments in time. We should be able to answer questions such as:

- who was top scorer on date X;
- how many goals had team Y conceded by date X;
- what information was available before a particular fixture;
- what a historical model would have known at a specified prediction cutoff.

Do not use future information when reconstructing an historical state.

## Governing idea

> **We are not building one football model. We are building the research environment in which we can discover which models, metrics and explanations are worth building.**

## Current platform position

The Universal Research Access backend is complete and promoted into `main`.

The backend closeout is recorded in `FRL_BACKEND_CLOSEOUT_2026-08-26.md` and establishes the research-access layer as ready for frontend consumption.

The active frontend architecture is **Next.js + React**. Streamlit is legacy and is not the target architecture for new UI work.

The current immediate product priority is the **fixture/result experience**: the user reaches a fixture from the Fixtures experience, opens the fixture, and sees a polished match workspace.

## Fixture/result product direction

The fixture/result page should feel like a desktop-first **web application**, not a traditional information-heavy football website.

Target characteristics:

- slick and visually restrained;
- easy to navigate;
- focused sections/tabs rather than one giant page;
- rich information available on demand;
- strong hierarchy with minimal interface clutter.

The initial match experience should answer:

- what was the match and final score;
- who scored / what happened;
- who played;
- what were the basic match statistics.

A useful structural direction is:

`MATCH | TIMELINE | LINEUPS | STATS | PLAYERS | CONTEXT`

These are illustrative categories rather than an immutable contract; the active UI work should establish the final interaction language.

The visual target is informed by the **clean software feel of Linear and Vercel**, the **app-like information architecture of the FotMob app**, and the **depth of serious football-data products**. The FRL should develop its own design language rather than imitate any of them.

## Universal research access and frontend boundary

The frontend should consume governed research results from the universal research-access layer rather than reaching directly into source-specific storage mechanisms.

The interface should expose selected and coherent views over the underlying evidence, while the full variable universe remains available to deeper research workflows.

A source field existing does not automatically mean a research metric exists, and a research metric existing does not automatically mean it belongs on the primary UI.

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

Exploratory patterns must not automatically become trusted evidence. Preserve failed and inconclusive investigations as well as attractive results.

## Probabilistic and betting discipline

Use probabilistic reasoning rather than narrative certainty.

Distinguish clearly between:

- plausible explanation;
- historical association;
- predictive improvement over a baseline;
- out-of-sample predictive performance;
- calibrated probabilities;
- economic value after realistic market costs.

Backtests are not sufficient on their own. Temporal leakage, selection bias, multiple testing, calibration and robustness must be considered.

## Commercial objective

Revenue generation is a legitimate short-term objective, but FRL must not be forced to become the revenue vehicle if another opportunity has materially stronger evidence of demand and fit.

Commercial discovery should follow the same evidence-led philosophy as research:

- identify the customer and problem;
- establish evidence of willingness to pay;
- understand alternatives and competition;
- estimate acquisition and technical difficulty;
- estimate time to first testable revenue;
- identify risks and invalidating evidence;
- test the smallest viable commercial hypothesis before committing substantial resources.

Prefer the opportunity with the strongest evidence-adjusted probability of success rather than the most exciting idea.

## Learning objective

The FRL is also a vehicle for developing the researcher's quantitative and analytical ability.

When an important statistical, modelling or research concept becomes necessary, teach it through the real FRL problem where practical.

Do not outsource understanding merely because implementation can be outsourced.

Preferred learning loop:

```text
Research problem
    ↓
Current understanding / intuition
    ↓
Prediction or hypothesis
    ↓
Formalisation
    ↓
Method / analysis
    ↓
Application to FRL
    ↓
Review what was learned
```

## Working method

For substantial workstreams establish:

- objective;
- definition of done;
- necessary steps;
- current step;
- review point.

Separate **research mode** from **build mode**.

When new ideas appear, distinguish between:

- required for the current objective;
- important to the long-term architecture;
- worth recording and parking for later.

Do not confuse changing the plan because new evidence warrants it with abandoning the plan because something interesting appeared.

The highest-value next action is not necessarily code. It may be research, validation, product work, customer discovery, or deciding not to build something.

## Repository recovery

Treat `dallum96-gif/football-research-lab` as the source of truth for tracked project code and durable project documentation.

Before substantive work:

1. read `PROJECT_ORIENTATION.md`;
2. read `CURRENT_WORK.md`;
3. establish current branch and compare with `main`;
4. inspect relevant code, working branches and archived/local mechanisms where needed;
5. preserve trusted backend/query contracts unless the task genuinely requires changes;
6. validate before treating a change as safe.

Do not ask the user to re-explain project information that can be recovered from the repository.

When a capability is not clearly present in GitHub, inspect relevant working/archived/upstream sources before concluding that it does not exist.

## Current-session sequence

For a fresh substantive coding session:

`read orientation → read current work → establish repo state → inspect relevant mechanisms → run the applicable research/backend/project-health gates → then begin substantive work.`

## Final principle

> **Build the foundations. Learn the machinery. Test the ideas. Follow the evidence.**
