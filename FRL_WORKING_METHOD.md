# Football Research Laboratory — Working Method

## Purpose

This document records durable principles for how the Football Research Laboratory should be built, researched and used. It is deliberately separate from personal biography or chat history.

## 1. Build the system and the researcher together

The FRL is both a software platform and a vehicle for developing research capability.

Implementation should not require the researcher to understand every technical detail, but important analytical decisions should be understandable and challengeable. When a statistical, modelling or research concept becomes important to the project, teach the concept through the real FRL problem where practical.

The preferred learning loop is:

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

Do not outsource understanding merely because implementation can be outsourced.

## 2. Plans should create structure without suppressing discovery

The project benefits from explicit plans, but the blueprint is expected to evolve as the data and research problems become better understood.

For each substantial workstream, establish:

- objective;
- definition of done;
- necessary steps;
- current step;
- review point.

When an interesting discovery appears, distinguish between:

- something required to complete the current objective;
- something that changes the long-term architecture;
- something worth recording but parking for later.

Do not confuse changing the plan because new evidence warrants it with abandoning the plan because something interesting appeared.

## 3. Research mode and build mode are distinct

**Research mode** is for understanding questions, inspecting evidence, exploring alternatives and deciding what is worth doing.

**Build mode** is for implementing an established decision with the smallest appropriate change surface.

Moving between the modes is expected. Neither should silently replace the other.

## 4. Exploration must remain falsifiable

The FRL should make it cheap to generate and investigate hypotheses, but an interesting pattern is not automatically a finding.

The preferred progression is:

```text
Observation
    ↓
Hypothesis
    ↓
Formal test
    ↓
Challenge / alternative explanation
    ↓
Out-of-sample or prospective evaluation where appropriate
    ↓
Research conclusion
```

The system should make it possible to record failed or inconclusive investigations rather than only preserving attractive results.

## 5. Commercial research should be evidence-led

Revenue is a legitimate short-term objective, but the FRL should not be forced to become the revenue vehicle if another opportunity has materially stronger evidence of demand and fit.

When investigating commercial opportunities, prioritise:

- identifiable customer and problem;
- evidence of willingness to pay;
- competitive alternatives;
- acquisition difficulty;
- technical difficulty;
- time to first testable revenue;
- realistic upside;
- major risks and invalidating evidence.

Prefer the opportunity with the strongest evidence-adjusted probability of success, not merely the most exciting or technically impressive idea.

A commercial hypothesis should be tested with the smallest experiment capable of producing meaningful evidence before substantial resources are committed.

## 6. Probability and prediction require intellectual discipline

The eventual betting and prediction work should use probabilistic reasoning rather than narrative confidence.

The project should distinguish clearly between:

- a plausible story;
- a historical association;
- predictive improvement over a baseline;
- out-of-sample predictive performance;
- calibrated probability estimates;
- economic value after realistic market costs.

A model should earn confidence through evidence rather than through complexity or backtest performance alone.

## 7. The working relationship with AI

The AI should act as a research and technical partner rather than an unquestioned authority.

It should:

- generate hypotheses;
- explain technical and statistical concepts;
- implement and test analyses;
- challenge assumptions;
- identify uncertainty;
- distinguish evidence from inference;
- preserve reproducibility;
- defer to the FRL's validated data for claims about FRL data.

When an assumption materially affects a conclusion, surface it rather than silently choosing one.

## 8. Progress is not measured by code volume

The highest-value next action may be:

- writing code;
- understanding an architectural constraint;
- validating a data assumption;
- testing a research hypothesis;
- improving the user workflow;
- talking to a prospective user/customer;
- or deciding not to build something.

The team should periodically ask:

> **What is the highest-value thing we can accomplish with the next block of time?**

This is especially important when commercial progress becomes a short-term priority.

## 9. Preserve optionality, but avoid premature implementation

The long-term Laboratory should remain capable of supporting future questions, variables, derived metrics, research methods and models.

That does not mean implementing every future capability now.

The desired pattern is:

**design for future capability → preserve the necessary foundations → implement when justified.**

## 10. The practical objective

The short-term objective is not to know in advance which research model, product or revenue stream will succeed.

It is to build a system and working process that allow promising hypotheses to be identified cheaply, tested rigorously, rejected when they fail, and developed when the evidence supports them.

> **Build the foundations. Learn the machinery. Test the ideas. Follow the evidence.**
