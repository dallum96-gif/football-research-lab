# Football Research Laboratory — Project Vision

This document preserves the original project vision that sits behind the Football Research Laboratory. It is intentionally broader than the current application. The current code is only the beginning of this idea.

## The central idea

We are not really building a betting model. We are building a **football research laboratory**.

It should sound more complicated than it needs to be because it can be built in layers.

The core principle is:

> **Give us the data and let us ask whatever football question we can think of.**

The laboratory should be an environment in which historical football data can be interrogated, hypotheses can be tested, models can be compared, and interesting patterns can be investigated without having to redesign the underlying database every time a new question occurs to us.

## The eventual research interface

The long-term interface should allow a user to construct questions from football conditions rather than choosing from a fixed set of canned reports.

For example:

```text
CUSTOM QUERY

Home team
  Elo: 1650–1750

Away team
  Elo: 1450–1550

Home team's last 5
  >= 10 points

Away team's last 5
  <= 4 points

Home xG difference
  > +0.5

Away xG difference
  < -0.2

Home advantage
  Yes

Historical period
  2016–2026
```

The system should be able to return something such as:

```text
147 comparable matches found.

OUTCOMES

Home win: 62.6%
Draw: 21.1%
Away win: 16.3%
Over 2.5: 58.5%
BTTS: 54.4%
```

The important feature is not the exact example above. It is the ability to drill down and rerun the same historical query with one condition changed.

For example:

> What happened historically when a team with an Elo rating 150+ higher than its opponent had won at least 4 of its previous 5 matches, while the opponent had lost at least 3 of its previous 5?

Then:

> How does that change if the stronger team is at home?

Then:

> What if the stronger team has scored 2+ goals in each of its last three?

Then:

> What if we exclude matches involving the top six?

That is a **query engine sitting on top of the football database**, not one monolithic model.

## Independent analytical approaches

The laboratory should eventually allow several analytical approaches to coexist rather than forcing everything into one model.

### 1. Historical precedent

> What happened in comparable situations?

### 2. Elo

> How strong are these teams relative to each other?

### 3. Poisson

> Given expected attacking and defensive strengths, what is the likely goal distribution?

### 4. Monte Carlo

> If we simulate this match many times, what happens?

### 5. Player model

> How does the expected XI change those strengths?

### 6. Market

> What does the bookmaker think?

The eventual architecture can combine these into something like:

```text
                  MATCH
                    |
       +------------+------------+
       |            |            |
       v            v            v
 HISTORICAL       ELO        POISSON
 PRECEDENT                     |
       |            |           v
       |            |       MONTE CARLO
       |            |           |
       +------------+-----------+
                    |
                    v
              MODEL ENSEMBLE
                    |
                    v
              FAIR PROBABILITY
                    |
             +------+------+
             |             |
             v             v
         BOOKMAKER      HISTORICAL
           ODDS         CALIBRATION
             |             |
             +------+------+
                    |
                    v
                 ANALYSIS
```

The point is not to assume that every eventual feature must be built. The architecture should make them possible.

## The database principle

One of the most important design decisions is that we should **not design the database around the questions we currently think we will ask**.

We should design it around the underlying football entities and events.

Then derive variables from those foundations.

For example, we should not make `last_5_form` a permanent primitive data field. We should store the underlying matches and derive:

- last 3
- last 5
- last 8
- last 10
- home last 5
- away last 5
- rolling xG
- rolling xGA
- rolling goal difference
- strength-adjusted form
- and other derived variables

This gives the research engine enormous flexibility and reduces duplication.

## The Question box

Eventually the laboratory should support a natural-language or structured **Question** interface.

A user might ask:

> Historically, how often does a team win when it has a 200+ Elo advantage, has scored at least 8 goals in its last five games, and its opponent has conceded at least 8?

The software should translate the question into database conditions, identify the comparable matches, and return the historical evidence.

For example:

```text
QUERY RESULT

126 comparable matches
79 wins
27 draws
20 losses

Win rate: 62.7%

Compare with league baseline: 44.8%
```

The answer should remain auditable: the system should be able to show which matches were included and why.

## Protection against false discoveries

This is a core scientific requirement.

If a system searches thousands of historical combinations, some patterns will look spectacular purely by chance. The laboratory must protect itself against false discoveries, overfitting and p-hacking-style behaviour.

The system should eventually be able to warn the user when:

> The result is based on only 17 historical matches.

and, where appropriate:

> You have tested 4,821 similar hypotheses; this is one of the strongest results.

The research workflow should also support discovery and testing periods. For example:

```text
2016–2023
    |
    v
DISCOVER PATTERN
    |
    v
2024–2026
    |
    v
TEST PATTERN
```

This separation between discovering a pattern and testing whether it generalises is fundamental to the laboratory's eventual credibility.

## The development philosophy

The visible GUI is only the fun part. The underlying research engine matters more.

We should build incrementally:

1. **Repository** — What data do we have?
2. **Database** — How do clubs, players and fixtures relate?
3. **Analytics** — What happened?
4. **Modelling** — What is likely to happen?
5. **Research** — When have situations like this happened before?
6. **Market** — Does the market price this correctly?
7. **Interactive tool** — Let the user ask almost any football question.

The project should not rush into the final interface at the expense of the foundations.

The current work on identity resolution, fixture corrections, provenance and invariant-based testing is deliberately the boring-but-critical stage that makes the later research environment trustworthy.

## The dream project

The project is not fundamentally an FPL app and not fundamentally a betting model.

Those are possible applications of the broader system.

The actual dream is a **little football research environment** in which the user can say:

> **Give me the data and let me ask questions.**

The computer should gradually become capable of answering increasingly sophisticated questions while exposing the evidence underneath the answer.

And eventually, we should be able to ask something deliberately ridiculous, such as:

> Find Premier League matches since 2016 where the home team's Elo was between 1550 and 1650, they had scored at least 2 goals in four of their previous five, the away team had an xG difference below -0.3 over its previous eight, and both teams had started the previous match with at least three players under 23. What happened?

The system should be able to go and find them.

That is the laboratory.
