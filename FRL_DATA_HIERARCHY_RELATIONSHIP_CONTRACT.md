# Football Research Laboratory — Data Hierarchy & Organisation Contract

## Status

**Architectural contract — v1.0**

This document defines how the Football Research Laboratory (FRL) organises evidence, canonical entities, relationships, shared analytical services, research tools, mathematical modelling and presentation.

It is governed by:

- `RISK_STRATEGY_FRAMEWORK.md`
- `NON_DESTRUCTION_ASSURANCE.md`
- `DATA_CONSTRUCTION.md`

It incorporates the current FRL product vision: the application is one connected football research system, not a set of isolated pages.

This is an architectural contract. It fixes boundaries, identity rules, navigation responsibilities and safety invariants while leaving future metric formulas, composite metrics, statistical methods and model methodologies open until they are properly designed and validated.

---

## 1. Vision

The FRL should be understood as **one football research environment with multiple lenses on the same evidence-backed system**.

The long-term product vision is:

> **Build a beautiful football research environment where every team, player and fixture is an entry point into increasingly sophisticated questions, with the underlying evidence always exposed.**

The current workspaces are therefore not independent applications. They are lenses over a shared football research graph.

The eventual destination is a system in which a user can move naturally from an entity to context, from context to evidence, and from evidence to research:

```text
TEAM
  ↓
Fixtures → League → Shared analytical context → Players → H2H → Models → Research

PLAYER
  ↓
Teams → Fixtures → Performance → Role / trajectory → Research

FIXTURE
  ↓
Teams → Form entering fixture → Players → Historical precedents → Models → Matchday context

RESEARCH QUERY
  ↓
exact underlying fixtures
  ↓
results / distributions / sample size / provenance
```

The system should become increasingly capable without becoming increasingly fragmented.

---

## 2. Governing principle

> **Every FRL result must be a view of a canonical entity, a canonical relationship, or a documented derived analytical service whose source hierarchy, identity basis, temporal semantics and provenance are understood before presentation.**

The GUI is the least authoritative layer.

It must not become the place where the project invents:

- source precedence;
- identity mappings;
- historical-state definitions;
- metric formulas;
- leakage rules;
- fallback semantics;
- model methodology.

The preferred architecture is:

```text
RAW / SOURCE EVIDENCE
        ↓
VALIDATION / SCHEMA CONTRACT
        ↓
IDENTITY RECONCILIATION
        ↓
CANONICAL ENTITIES + RELATIONSHIPS
        ↓
SPECIALIST EVIDENCE / ENRICHMENT
        ↓
SHARED HISTORICAL / ANALYTICAL STATE
        ↓
RESEARCH SERVICES / MATHEMATICAL MODELS
        ↓
PRESENTATION VIEWS
        ↓
GUI / NAVIGATION
```

This implements the layered approach in the Risk Strategy Framework and the minimal-change, regression-first discipline in the Non-Destruction Assurance Agreement.

---

## 3. Architectural layers

### Layer 1 — Raw / Source Evidence

Preserved source material and externally retrieved evidence.

Examples may include:

- FPL player data;
- Premier League fixture/result data;
- player-match source data;
- match-statistic source data;
- future specialist providers;
- future market inputs where explicitly quarantined to the decision layer.

Raw evidence is evidence, not automatically truth.

### Layer 2 — Validation / Identity

This layer establishes whether source material can safely enter the trusted system.

It includes:

- schema contracts;
- metric coverage audits;
- player identity registries;
- team identity registries;
- fixture/source-match identity bridges;
- conflict audits;
- cross-season identity audits;
- chronology and data-health checks.

### Layer 3 — Canonical Model

Authoritative entities and relationships used throughout the application.

Canonical model decisions must not be changed merely because another source offers richer measurements.

### Layer 4 — Shared Analytical State

Reusable historical and contextual features derived from canonical data and validated evidence.

Examples include:

- rolling form;
- streaks;
- trends;
- rest;
- season-to-date state;
- home/away state;
- opponent-strength context;
- historical precedents;
- other documented contextual features.

### Layer 5 — Research Services and Mathematical Modelling

This layer asks questions of the canonical system or produces explicit mathematical/statistical models.

It includes:

- player research;
- team research;
- H2H analysis;
- Query / comparable-match research;
- Combined Metrics;
- Records;
- Projection Lab;
- statistical and mathematical models;
- future player/team influence models;
- future simulation and ensemble approaches.

### Layer 6 — Quality / Evaluation

All research and models remain subject to:

- unit testing;
- integration testing;
- data-quality testing;
- temporal/leakage checks;
- walk-forward evaluation;
- baseline comparison;
- calibration;
- robustness;
- unseen-data evaluation.

### Layer 7 — Presentation / Decision Context

This is the GUI and explicit decision layer.

The GUI presents research; it does not define it.

Market information remains separated from football research by default and enters only an explicit decision layer when required by the research question.

---

## 4. The FRL is a graph, not a collection of pages

```text
PLAYER ←→ PLAYER–FIXTURE ←→ FIXTURE ←→ TEAM–FIXTURE ←→ TEAM
   │                                             │
   └────────────── shared research ─────────────┘
                         │
               historical analytical state
                         │
          ┌──────────────┼──────────────┐
          │              │              │
       MATCHDAY       QUERY          MODELS
        CENTRE          │              │
          │       comparable       mathematical /
          │       matches          statistical /
          │                        simulation /
          │                        ensemble
          └──────────────┬──────────────┘
                         │
                      GUI views
```

A page is a **lens** over that graph. It is not a separate data system.

A new page must therefore reuse existing canonical entities, relationships and analytical services wherever possible.

---

## 5. Canonical entities

### 5.1 Fixture

Fixture is the central match-level research object.

Canonical identity:

```text
(season, fixture_id)
```

The canonical fixture master remains the trusted fixture identity.

A source-specific match ID is evidence attached to a canonical fixture through a verified source mapping. It must never create a competing fixture identity.

A fixture can expose through the relevant services:

- teams;
- kickoff and completion state;
- result;
- match statistics;
- historical context entering the match;
- league positions entering the match;
- player participation and performance;
- corrections;
- provenance;
- historical precedents;
- mathematical/statistical model outputs.

### 5.2 Team

Team is a longitudinal club entity.

The project must preserve:

```text
season-local source team identity
        ↓
verified identity mapping
        ↓
persistent team identity
```

Persistent team identity is used for longitudinal research. Source-local IDs are used only when a source query specifically requires them.

### 5.3 Player

Player is a longitudinal research entity.

Display name alone is never sufficient canonical identity.

Source identities such as FPL `element` and external `source_player_id` must map to the canonical player through verified, season-aware identity mappings.

The player model must support:

- longitudinal identity;
- season membership;
- club history;
- source identities;
- player-fixture participation;
- profile statistics;
- research statistics;
- role and trajectory analysis;
- future player-influence modelling.

Unknown or ambiguous identity produces **no verified join**, not a best guess.

### 5.4 Season / competition context

Season and competition are contextual dimensions used to scope entities, relationships, statistics and historical state.

They must not be confused with source IDs.

---

## 6. Canonical relationships

### 6.1 Player–Fixture

Canonical grain:

```text
(season, fixture_id, player_id)
```

It answers:

> **What did Player X do in Fixture Y?**

It is the foundation for fixture player tables, player-fixture detail, player match histories, player role analysis, player influence research and specialist player-match evidence.

Player-fixture detail is a contextual detail view, not a primary sidebar workspace.

### 6.2 Team–Fixture

Canonical grain:

```text
(season, fixture_id, team_id)
```

It represents a team's participation in a fixture and supports:

- fixture history;
- home/away context;
- historical state;
- rest;
- form;
- streaks;
- season-to-date features;
- future modelling features.

### 6.3 Source identity relationships

Every external source is joined into the canonical model through an explicit identity mapping.

Preferred pattern:

```text
SOURCE A
   ↓
verified canonical identity
   ↓
CANONICAL ENTITY / RELATIONSHIP
   ↓
verified canonical identity
   ↓
SOURCE B
```

Direct provider-to-provider guessing is prohibited where a canonical identity seam exists.

---

## 7. Canonical data versus specialist evidence

The FRL must distinguish between **canonical representation** and **preferred specialist evidence**.

### Canonical

The authoritative representation of an entity or relationship within the FRL.

### Specialist evidence

A source that provides richer or more specific measurements for a particular metric or analytical purpose.

A specialist source may override a displayed metric when:

1. the source field is understood;
2. the source record is structurally valid;
3. the identity bridge is verified;
4. the evidence is available under the relevant temporal rules;
5. the transformation is documented.

A specialist source does not become the canonical entity model merely because it provides a richer statistic.

---

## 8. Metric hierarchy and fallback policy

Every important metric should eventually have a documented policy containing:

```text
metric
 ├─ preferred source
 ├─ permitted fallback
 ├─ identity requirement
 ├─ availability semantics
 ├─ transformation / aggregation
 └─ provenance status
```

Current Player Research example:

| Metric | Preferred source | Permitted fallback | Requirement |
|---|---|---|---|
| Goals | canonical FPL player data | — | canonical record |
| Assists | canonical FPL player data | — | canonical record |
| xG / xA | canonical FPL player data | — | canonical record |
| Shots | canonical FPL player data | — | canonical record |
| Attempted passes | verified player-match source | canonical FPL value | verified player identity |
| Completed passes | verified player-match source | canonical FPL value | verified player identity |
| Key passes | verified player-match source | canonical FPL value | verified player identity |
| Big chances created | verified player-match source | canonical FPL value | verified player identity |

Rule:

```text
verified specialist value exists
        ↓
use specialist value

otherwise
        ↓
use documented canonical fallback

never
        ↓
invent, coerce or silently guess
```

A canonical fallback does not weaken the fail-closed evidence layer. The system must still record that specialist verification was unavailable.

---

## 9. Provenance follows the value

Important analytical values must be traceable to:

```text
value
source
status
reason
```

The user should ultimately be able to ask:

> **Where did this number come from?**

and receive an inspectable lineage through the canonical and evidence layers.

---

## 10. Shared analytical state

Derived context must be calculated once and reused.

Shared analytical services may include:

- rolling form;
- streaks;
- trends;
- rest days;
- season-to-date state;
- home/away state;
- opponent-strength context;
- historical precedents;
- descriptive likelihood features.

These are services, not page-specific calculations.

For historical fixtures:

```text
prior completed fixtures
        ↓
construct current fixture state
        ↓
only then add current fixture
```

All historical state remains subject to event-time, availability-time and ingestion-time distinctions and the project's anti-leakage rules.

Form and streaks are **not top-level sidebar workspaces**. They are shared analytical capabilities used contextually by Team Profile, Team Stats, Matchday Centre, Query and future modelling.

No page may maintain an independent definition of "last five", "unbeaten streak" or equivalent shared state.

---

## 11. Product navigation contract

The primary sidebar contains exactly six headings:

```text
Home
Fixtures & Results
League Table
Teams
Players
Analysis
```

These are primary workspaces, not a list of every entity or relationship view.

### 11.1 Home

Home is the front door to the Laboratory.

It should answer:

> **What can I investigate here?**

It may surface entry points into:

- teams;
- players;
- fixtures;
- seasons;
- comparisons;
- research questions;
- notable findings where methodology, sample size and provenance are visible.

Home is not the canonical owner of statistics that belong to another layer.

### 11.2 Fixtures & Results

```text
Fixtures & Results
      ↓
Fixture Explorer
      ↓
Fixture Landing Page
      ├─ Match detail
      ├─ Player performance
      ├─ Player-fixture detail
      ├─ Team context
      ├─ Historical precedents
      └─ Projection / research entry points
```

### 11.3 League Table

The League Table is an analytical competition view derived from canonical fixtures/results and team identity.

Long-term capabilities may include:

- current standings;
- historical point-in-season standings;
- range / multi-season views;
- overall / home / away splits;
- position / points / GD / xG / xGA / xGD / shared analytical features;
- direct navigation into Team Profile and Team Stats.

### 11.4 Teams

Teams have two primary user-facing views.

**Team Profile** answers:

> **Who are this club, and what is their current context?**

It may include:

- canonical identity;
- historical Premier League presence;
- club history;
- current snapshot;
- concise current form;
- recent fixtures;
- current team context;
- navigation into Team Stats and Fixtures.

**Team Stats** answers:

> **What has this team done historically and analytically?**

It is the team analogue of Player Stats / Research and may support:

- season / multi-season statistics;
- filtering;
- comparisons;
- home/away splits;
- deeper form/streak/trend analysis;
- club history;
- future team research.

Team Profile and Team Stats are separate presentation responsibilities over the same Team entity.

### 11.5 Players

Players have three complementary perspectives.

**Player Profile** answers:

> **Who is this player?**

**Player Stats / Research** answers:

> **What has this player done, and how does it compare?**

**Player-fixture detail** answers:

> **What did this player do in this specific fixture?**

Player-fixture detail is reached contextually from Fixtures and Players; it is not a sidebar workspace.

### 11.6 Analysis

Analysis is the home for research and modelling tools.

It includes or is intended to include:

- Matchday Centre;
- Prediction Lab;
- future mathematical/statistical modelling tabs;
- future Research / Query tools;
- comparable-match analysis;
- Combined Metrics / metric laboratory;
- Records where a meaningful analytical use case is established;
- future simulation, ensemble and player/team influence models.

---

## 12. Matchday Centre

Matchday Centre is the contextual analytical surface for an upcoming fixture.

```text
fixture context
       ↓
shared analytical state
       ↓
Stat Pack
       ↓
model outputs
```

### Stat Pack

May present:

- relevant recent form;
- relevant streaks;
- trends;
- rest/context variables;
- league positions;
- H2H context;
- descriptive likelihoods where methodology is documented;
- relevant player/team context.

### Prediction Lab

Presents model outputs separately from descriptive statistics and keeps market information explicitly separated where appropriate.

The Stat Pack is a presentation of shared analytical services, not an independent source of truth.

---

## 13. Research / Query

The long-term destination is a research environment where users can ask cross-entity historical questions.

For example:

```text
team conditions
+ player conditions
+ historical state
+ fixture context
        ↓
comparable fixtures
        ↓
outcomes / rates / distributions
        ↓
underlying fixture list
```

A Query system must:

- consume canonical entities;
- consume documented metric definitions;
- consume shared analytical services;
- retain exact filters and assumptions;
- expose the fixtures that produced a result;
- report sample size;
- distinguish discovery from validated research.

A query result should remain reproducible from its stored conditions and underlying fixtures.

---

## 14. Combined Metrics

Combined Metrics are a research capability, not a canonical data layer.

Every combined metric must eventually define:

```text
component metrics
source policy for each component
normalisation
formula
interpretation
validation status
```

The project must distinguish:

```text
exploratory composite
        ≠
validated research metric
```

No composite should silently become a trusted feature or model input without appropriate documentation and evaluation.

---

## 15. Records

Records may become a future analytical surface.

They should be derived from canonical data and shared analytical services rather than maintained as a second records database wherever practical.

Potential uses include:

- all-time player records;
- season records;
- team records;
- streak records;
- fixture records.

Every displayed record should remain traceable to its source rows and calculation.

---

## 16. Mathematical and statistical modelling environment

Projection Lab is one model within a broader modelling environment.

The architecture must support independent approaches, for example:

```text
Historical precedent
Elo
Poisson
Monte Carlo
Player model
Other statistical / mathematical models
Ensembles / consensus
Market / decision layer
```

A model consumes established analytical services and selects its features explicitly.

```text
canonical entities
        ↓
shared historical state
        ↓
shared research features
        ↓
model-specific feature selection
        ↓
mathematical / statistical model
        ↓
evaluation
        ↓
GUI
```

Potential future capabilities may include:

- alternative probability models;
- hierarchical or multilevel models;
- time-varying team/player strength;
- simulation systems;
- player influence models;
- ensemble modelling;
- historical precedent models;
- model comparison and consensus;
- calibration diagnostics;
- uncertainty intervals;
- sensitivity analysis.

These are **potential capabilities**, not commitments to implement every method. Each model must earn its place through the Risk Strategy's validation standards and must remain distinguishable from exploratory experimentation.

Simple baselines remain mandatory where appropriate. Complexity does not receive privileged status merely because it is mathematically sophisticated.

---

## 17. Navigation and relationship graph

The intended information architecture is:

```text
HOME
  │
  ├── Fixtures & Results
  │      └── Fixture Landing
  │             ├── Match detail
  │             ├── Player-fixture detail
  │             └── Team context
  │
  ├── League Table
  │      └── Team Profile / Team Stats
  │
  ├── Teams
  │      ├── Team Profile
  │      └── Team Stats
  │
  ├── Players
  │      ├── Player Profile
  │      └── Player Stats / Research
  │
  └── Analysis
         ├── Matchday Centre
         ├── Prediction Lab
         ├── Query / Research
         ├── Combined Metrics
         ├── Records
         └── Future mathematical / statistical models
```

Entity and relationship detail remains contextual rather than being promoted into sidebar clutter.

The same entity must be reachable from multiple contexts through the same canonical identity.

Examples:

```text
Fixture → Player-fixture detail → Player Profile
Player Profile → Match appearance → Fixture Landing
Fixture → Team → Team Profile → Team Stats
Team Stats → Fixture → Fixture Landing
League Table → Team → Team Profile
Matchday Centre → Fixture / Team / Player context
Query → underlying fixtures → Fixture Landing
Records → source rows → relevant entity detail
```

---

## 18. Relationship and integrity rules

### Fixture

```text
(season, fixture_id)
```

must be unique.

### Player

Canonical player identity is persistent and distinct from season-local source IDs.

### Team

Persistent team identity is distinct from season-local source identity.

### Player–Fixture

```text
(season, fixture_id, player_id)
```

must be unique.

### Team–Fixture

```text
(season, fixture_id, team_id)
```

must be unique.

### Source mappings

Verified source mappings must be unique and unambiguous.

Ambiguity produces:

```text
NO VERIFIED JOIN
```

not a heuristic best match.

### Navigation identity

Routes must carry canonical identity, not display-name-only identity.

---

## 19. Trust, provenance and reproducibility

The FRL's defining trust requirement is that interesting answers remain inspectable.

A result should eventually be able to answer:

```text
Where did this come from?
Which fixtures produced it?
Which season?
Which identity mapping?
Which correction?
Which source?
Which transformation?
Which model?
Which assumptions?
How large is the sample?
What validation has been performed?
```

This is especially important for Query, Records, Combined Metrics, H2H and model outputs, because derived results can look authoritative even when the underlying evidence is weak.

---

## 20. Non-destruction requirements

A feature is safe only when it works **and** trusted existing behaviour remains demonstrably intact.

Therefore:

- UI changes must not rewrite canonical data;
- specialist metric bridges must not replace canonical identity models;
- source fallbacks must be explicit;
- historical-state definitions remain shared;
- fixture IDs remain stable;
- player IDs remain stable;
- team identity mappings remain stable;
- provenance and corrections remain inspectable;
- incomplete evidence must not be invented into complete-looking values;
- context views must resolve the same underlying entities instead of maintaining duplicate copies;
- existing working mechanisms must be discovered before new mechanisms are invented;
- archived / backup / local upstream mechanisms must be inspected where the committed repository is insufficient;
- broad destructive Git operations are prohibited as convenience measures;
- unrelated UI, data and research changes should not be mixed without explicit justification.

---

## 21. Validation obligations

Architectural changes must be validated at the layer they affect.

### Entity / identity changes

Identity, conflict and cross-season audits.

### Fixture changes

Fixture-master and project-health validation.

### Player-fixture evidence changes

Source schema, identity bridge and metric coverage tests.

### Historical analytical state changes

Temporal/leakage and state-construction tests.

### Query / research changes

Deterministic fixture traceability, sample-size reporting and appropriate statistical evaluation when claims move beyond exploration.

### Combined metric changes

Component-source audit, formula documentation and appropriate validation.

### Record changes

Source-row traceability and deterministic reproduction.

### Model changes

Time-respecting evaluation, suitable baselines, calibration and robustness where applicable.

### GUI changes

Require, at minimum:

- route/render validation;
- canonical data resolution;
- unchanged fixture identity;
- unchanged player/team identity;
- unchanged trusted query behaviour;
- provenance remains accessible;
- incomplete states do not crash the interface;
- the established research baseline remains green when the change is intended to be presentation-only.

---

## 22. Re-entry contract for future sessions

A future FRL session should treat this document as the starting point for organisational questions, together with:

1. `RISK_STRATEGY_FRAMEWORK.md`
2. `NON_DESTRUCTION_ASSURANCE.md`
3. `DATA_CONSTRUCTION.md`
4. `CURRENT_WORK.md`
5. current working application behaviour;
6. relevant archived / backup implementations;
7. known upstream/local source mechanisms.

The user should not need to re-teach the application's hierarchy when the repository already contains the contract.

The default sequence is:

```text
DISCOVER EXISTING MECHANISM
        ↓
UNDERSTAND ITS LINEAGE
        ↓
IDENTIFY THE CANONICAL SEAM
        ↓
MAKE THE MINIMUM SAFE CHANGE
        ↓
TARGETED VALIDATION
        ↓
FULL REGRESSION / HEALTH GATE
        ↓
REVIEW WHAT WAS PRESERVED
```

The objective is not merely a functioning application. It is a research environment where increasing analytical capability does not erode trust, provenance, reproducibility or navigational coherence.
