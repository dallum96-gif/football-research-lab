# Football Research Laboratory — Data Hierarchy & Organisation Contract

## Status

**Architectural contract — v1.0**

This document defines how the Football Research Laboratory (FRL) organises evidence, canonical entities, relationships, shared analytical services, research tools, modelling and presentation.

It is governed by:

- `RISK_STRATEGY_FRAMEWORK.md`
- `NON_DESTRUCTION_ASSURANCE.md`
- `DATA_CONSTRUCTION.md`

It incorporates the current FRL product vision: the application is one connected football research system, not a set of isolated pages.

This is an architectural contract. It fixes boundaries, identity rules, navigation responsibilities and safety invariants while leaving future metric formulas, composite metrics and model methodologies open until they are properly designed and validated.

---

## 1. Governing principle

> **Every FRL result must be a view of a canonical entity, a canonical relationship, or a documented derived analytical service whose source hierarchy, identity basis, temporal semantics and provenance are understood before presentation.**

The GUI is the least authoritative layer.

It must not become the place where the project invents:

- source precedence;
- identity mappings;
- historical-state definitions;
- metric formulas;
- leakage rules;
- fallback semantics.

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
RESEARCH SERVICES / MODELS
        ↓
PRESENTATION VIEWS
        ↓
GUI / NAVIGATION
```

This directly implements the layered approach in the Risk Strategy Framework and the minimal-change, regression-first discipline in the Non-Destruction Assurance Agreement.

---

## 2. The FRL is a graph, not a collection of pages

The long-term product vision is a connected evidence graph.

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
          │       comparable       Projection /
          │       matches          Elo / Poisson /
          │                        Monte Carlo /
          │                        Player model
          └──────────────┬──────────────┘
                         │
                      GUI views
```

A page is a **lens** over that graph. It is not a separate data system.

A new page must therefore reuse existing canonical entities, relationships and analytical services wherever possible.

---

## 3. Canonical entities

### 3.1 Fixture

Fixture is the central match-level research object.

Canonical identity:

```text
(season, fixture_id)
```

The canonical fixture master remains the trusted fixture identity.

A source-specific match ID is evidence attached to a canonical fixture through a verified source mapping. It must never create a competing fixture identity.

A fixture can expose, through the relevant services:

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
- model outputs.

### 3.2 Team

Team is a longitudinal club entity.

The project must preserve the distinction:

```text
season-local source team identity
        ↓
verified identity mapping
        ↓
persistent team identity
```

Persistent team identity is used for longitudinal research. Source-local IDs are used only when a source query specifically requires them.

The established team identity registry remains authoritative unless deliberately replaced through a controlled architecture change.

### 3.3 Player

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

### 3.4 Season / competition context

Season and competition are contextual dimensions used to scope entities, relationships, statistics and historical state.

They must not be confused with source IDs.

---

## 4. Canonical relationships

### 4.1 Player–Fixture

This is a first-class relationship, not a convenience join.

Canonical grain:

```text
(season, fixture_id, player_id)
```

It answers:

> **What did Player X do in Fixture Y?**

It is the foundation for:

- fixture player tables;
- player-fixture detail;
- player match histories;
- player role analysis;
- player influence research;
- specialist player-match evidence.

Player-fixture detail is a **contextual detail view**, not a primary sidebar workspace.

### 4.2 Team–Fixture

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

### 4.3 Source identity relationships

Every external source is joined into the canonical model through an explicit identity mapping.

The preferred pattern is:

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

## 5. Canonical data versus specialist evidence

The FRL must distinguish between **canonical representation** and **preferred specialist evidence**.

### Canonical

The authoritative representation of the entity or relationship within the FRL.

Examples:

- canonical fixture master;
- persistent team identity;
- canonical player identity;
- canonical player-fixture relationship.

### Specialist evidence

A source that provides richer or more specific measurements for a particular metric or analytical purpose.

A specialist source may override a displayed metric when:

1. the source field is understood;
2. the source record is structurally valid;
3. the identity bridge is verified;
4. the evidence is available under the relevant temporal rules;
5. the transformation is documented.

A specialist source does **not** become the canonical entity model merely because it provides a richer statistic.

---

## 6. Metric hierarchy and fallback policy

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

The rule is:

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

## 7. Provenance follows the value

Important analytical values must be traceable to:

```text
value
source
status
reason
```

Conceptually:

```text
attempted_passes = 1842
source = PLAYER_MATCH
status = VERIFIED
reason = VERIFIED_FPL_ELEMENT_TO_SOURCE_PLAYER_ID
```

or:

```text
attempted_passes = 1624
source = FPL_CANONICAL
status = CANONICAL_FALLBACK
reason = NO_VERIFIED_SOURCE_ID
```

The GUI does not need to expose all provenance at all times, but the analytical layer must preserve it where practical.

For fixture corrections, source history and verified correction records must remain inspectable rather than being silently overwritten.

---

## 8. Shared analytical state

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

These are **services**, not page-specific calculations.

```text
canonical fixtures + validated history
                  ↓
        shared analytical state
                  ↓
      ┌───────────┼───────────┐
      │           │           │
     form       streaks     trends
      │           │           │
      └───────────┼───────────┘
                  ↓
     team / fixture / matchday / model
```

### Temporal rule

For a historical fixture, derived state must use only information that was available before that fixture under the project's availability-time and leakage rules.

The invariant is:

```text
prior completed fixtures
        ↓
construct current fixture state
        ↓
only then add current fixture
```

### Navigation rule

Form and streaks are **not top-level sidebar workspaces**.

They are contextual analytical capabilities presented through Team Profile, Team Stats, Matchday Centre and future research tools as appropriate.

No page may maintain an independent definition of "last five", "unbeaten streak" or equivalent shared state.

---

## 9. Product navigation contract

The primary sidebar contains exactly six headings:

```text
Home
Fixtures & Results
League Table
Teams
Players
Analysis
```

These are **primary workspaces**, not a list of every entity view in the system.

### 9.1 Home

Home is the front door to the Laboratory.

Its job is to answer:

> **What can I investigate here?**

It should provide a research dashboard and entry points into:

- clubs;
- players;
- fixtures;
- seasons;
- comparisons;
- research questions;
- notable analytical findings where methodology and provenance are visible.

Home should not become the canonical owner of statistics that belong elsewhere.

### 9.2 Fixtures & Results

This is the match explorer and result history.

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

### 9.3 League Table

The League Table is an analytical competition view.

It should eventually support:

- current standings;
- historical point-in-season standings;
- range / multi-season views;
- overall / home / away splits;
- position / points / GD / xG / xGA / xGD / relevant shared features;
- direct navigation into Team Profile and Team Stats.

It must derive from canonical fixture/result and team identity layers rather than maintain a separate results system.

### 9.4 Teams

Teams have two primary user-facing views.

**Team Profile** answers:

> **Who are this club, and what is their current context?**

It may include:

- identity;
- historical Premier League presence;
- club history;
- current snapshot;
- concise current form;
- recent fixtures;
- current team context;
- navigation into Team Stats and Fixtures.

**Team Stats** answers:

> **What has this team done historically and analytically?**

It should be the team analogue of the current Player Stats / Research workspace and support:

- season / multi-season statistics;
- filtering;
- comparisons;
- home/away splits;
- deeper form/streak/trend analysis;
- club history;
- future research extensions.

Team Profile and Team Stats are separate presentation responsibilities over the same canonical Team entity and shared analytical services.

### 9.5 Players

Players have three complementary perspectives.

**Player Profile** answers:

> **Who is this player?**

**Player Stats / Research** answers:

> **What has this player done, and how does it compare?**

**Player-fixture detail** answers:

> **What did this player do in this specific fixture?**

Player-fixture detail is reached contextually from Fixtures and Players; it is not a sidebar workspace.

### 9.6 Analysis

Analysis is the home for research and modelling tools.

It currently includes or is intended to include:

- Matchday Centre;
- Prediction Lab;
- future modelling tabs;
- future Research / Query tools;
- future comparable-match analysis;
- future combined metrics / metric laboratory;
- future Records where a meaningful analytical use case is established.

Analysis tools must consume shared analytical services and canonical relationships rather than recreate their own definitions.

---

## 10. Matchday Centre architecture

Matchday Centre is a contextual analytical surface for a fixture.

It combines:

```text
fixture context
       ↓
shared historical state
       ↓
Stat Pack
       ↓
model outputs
```

The **Stat Pack** may present:

- relevant recent form;
- relevant streaks;
- trends;
- rest/context variables;
- league positions;
- H2H context;
- descriptive likelihoods where methodology is documented;
- relevant player/team context.

The **Prediction Lab** presents model outputs separately from raw descriptive statistics.

Market information remains quarantined from research by default and enters only an explicit decision layer when required.

---

## 11. Research and Query architecture

The long-term destination is not a collection of isolated analytical pages. It is a research environment where users can formulate questions across the graph.

Examples include:

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

A Query tool must:

- consume canonical entities;
- consume documented metric definitions;
- consume shared analytical services;
- retain the exact filters and assumptions;
- expose the fixtures that produced the result;
- report sample size;
- distinguish exploratory findings from validated research.

Failure to find a metric or retrieval path in the repository is not evidence that the mechanism is absent. Existing working consumers, archived implementations and known upstream/local sources must be inspected first, as required by the Risk Strategy and RDAA.

---

## 12. Combined metrics

Combined Metrics are a research capability, not a new canonical data layer.

Every combined metric must eventually define:

```text
component metrics
source policy for each component
normalisation
formula
interpretation
validation status
```

A composite statistic is not automatically trustworthy merely because its components are individually valid.

The project must distinguish:

```text
exploratory composite
        ≠
validated research metric
```

No composite metric should quietly enter trusted research or model features without documentation and appropriate evaluation.

---

## 13. Records

Records may become a future analytical surface.

They should be derived from canonical data and shared analytical services rather than stored as a second record database wherever practical.

Potential uses include:

- all-time player records;
- season records;
- team streak records;
- fixture records;
- club records.

A record result should remain traceable to the rows and calculation that produced it.

Records are intentionally a future surface until the exact scope and methodology are defined.

---

## 14. Modelling environment

Projection Lab is one model in a broader modelling environment.

The architecture must support independent approaches such as:

```text
Historical precedent
Elo
Poisson
Monte Carlo
Player model
Market / decision layer
```

A model consumes established analytical services and selects features explicitly.

```text
canonical entities
        ↓
historical state
        ↓
shared research features
        ↓
model-specific feature selection
        ↓
model
        ↓
evaluation
        ↓
GUI
```

Models must preserve temporal and availability semantics and remain separately evaluable.

No complex model receives privileged status merely because it is newer. Appropriate simple baselines remain mandatory under the Risk Strategy.

---

## 15. Relationship and integrity rules

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

### Source identity mapping

A verified source mapping must be unique and unambiguous.

Ambiguity produces:

```text
NO VERIFIED JOIN
```

not a heuristic best match.

### Navigation identity

Every GUI route to an entity or relationship must carry its canonical identity, not a display-name-only identity.

---

## 16. Non-destruction requirements

Consistent with `NON_DESTRUCTION_ASSURANCE.md`:

- UI changes must not rewrite canonical data;
- presentation components should sit behind established seams;
- specialist metric bridges must not replace canonical identity models;
- source fallbacks must be explicit;
- historical-state definitions remain shared;
- fixture IDs remain stable;
- player IDs remain stable;
- team identity mappings remain stable;
- provenance and corrections remain inspectable;
- incomplete evidence must not be invented into complete-looking values;
- context views must resolve the same underlying entities rather than maintaining duplicate data copies;
- broad destructive Git operations are prohibited as convenience measures;
- unrelated UI, data and research changes should not be mixed in one release unit without explicit justification.

The assurance question remains:

> **What evidence do we have that this change did not destroy something we already trusted?**

---

## 17. Validation obligations

Architectural changes must be validated at the layer they affect.

### Entity / identity changes

Require identity, conflict and cross-season audits.

### Fixture changes

Require fixture-master and project-health validation.

### Player-fixture evidence changes

Require source schema, identity bridge and metric coverage tests.

### Historical analytical state changes

Require temporal/leakage safeguards and state-construction tests.

### Research / Query changes

Require deterministic fixture traceability, sample-size reporting and appropriate evaluation where claims are promoted beyond exploration.

### Model changes

Require time-respecting evaluation, baselines, calibration and robustness where applicable.

### GUI changes

Require:

- route/render validation;
- canonical data resolution;
- unchanged fixture identity;
- unchanged player/team identity;
- unchanged trusted query behaviour;
- provenance remains accessible;
- incomplete states do not crash the interface;
- the established research baseline remains green when the change is intended to be presentation-only.

---

## 18. Future expansion points

The contract intentionally reserves space for:

- Query / Research;
- Combined Metrics;
- Records;
- broader player influence modelling;
- additional team research;
- additional fixture research;
- similarity / comparable-match systems;
- additional prediction models;
- explicit market / decision tooling.

Their detailed methodology must be defined when implemented. The contract does not allow them to bypass the canonical model, identity layer, shared analytical state, provenance rules or validation framework.

---

## 19. Re-entry rule for future sessions

A future session working on the FRL architecture should treat this document as the starting point for organisation questions, together with:

1. `RISK_STRATEGY_FRAMEWORK.md`
2. `NON_DESTRUCTION_ASSURANCE.md`
3. `DATA_CONSTRUCTION.md`
4. current working application behaviour;
5. relevant archived / backup implementations;
6. known upstream/local source mechanisms.

The user should not have to re-teach the application hierarchy when the repository already contains the contract.

The default assumption is:

```text
DISCOVER EXISTING MECHANISM
        ↓
UNDERSTAND ITS LINEAGE
        ↓
REUSE THE SAFEST ARCHITECTURAL SEAM
        ↓
MAKE THE MINIMUM CHANGE
        ↓
VALIDATE
```

The goal is not simply to make the application work. The goal is to make it difficult for a future change to produce a plausible-looking but incorrectly sourced, historically unsafe or disconnected result.
