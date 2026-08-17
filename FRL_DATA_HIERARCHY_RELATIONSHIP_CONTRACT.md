# Football Research Laboratory — Data Hierarchy & Relationship Contract

## Status

**Architectural contract — draft for review**

This document defines how the Football Research Laboratory organises canonical entities, relationships, source evidence, derived analytical state and GUI views.

It is governed by:

- `RISK_STRATEGY_FRAMEWORK.md`
- `NON_DESTRUCTION_ASSURANCE.md`
- `DATA_CONSTRUCTION.md`

The purpose is to prevent the application from becoming a collection of page-specific data joins and duplicated calculations.

---

## 1. Governing principle

> **Every GUI result must be a view of a canonical entity, canonical relationship or documented derived analytical service, with its source hierarchy and provenance understood before presentation.**

The GUI is the final presentation layer. It must not become the place where source precedence, identity resolution, historical-state semantics or metric definitions are invented.

The architectural flow is:

```text
RAW / SOURCE EVIDENCE
        ↓
VALIDATION / SCHEMA CONTRACT
        ↓
IDENTITY RECONCILIATION
        ↓
CANONICAL ENTITIES + RELATIONSHIPS
        ↓
SPECIALIST SOURCE EVIDENCE / ENRICHMENT
        ↓
DERIVED HISTORICAL STATE
        ↓
ANALYTICAL METRICS / RESEARCH SERVICES
        ↓
PRESENTATION VIEWS
        ↓
GUI
```

This is consistent with the Risk Strategy's layered architecture and the Non-Destruction Assurance requirement to preserve established mechanisms and make the minimum safe change.

---

## 2. Canonical entity model

The Laboratory's core entities are:

### 2.1 Fixture

Canonical identity:

```text
season + fixture_id
```

A fixture is the central match entity around which match detail and player-fixture relationships are organised.

Canonical fixture identity comes from `fixtures_master_corrected.csv`. Source-specific match identifiers are mapped to it through verified source identity mechanisms.

### 2.2 Team

Canonical longitudinal team identity is distinct from a season-local source team identity.

The project must preserve the distinction:

```text
season-local source team identity
        ↓
verified identity mapping
        ↓
persistent club identity
```

The application should use persistent team identity for longitudinal research and the appropriate season-local/source identity only when querying a source that requires it.

The existing `identity/team_seasons.csv` registry remains authoritative for this relationship unless a controlled architecture change explicitly replaces it.

### 2.3 Player

A player is a longitudinal research entity.

Canonical player identity must not be inferred from a display name alone.

Source-specific identifiers such as FPL `element` and external `source_player_id` are evidence-layer identities that map onto the canonical player identity through a verified season-aware identity registry.

The player identity model must support:

- longitudinal player research;
- season membership;
- source-specific identities;
- club history;
- player-fixture participation.

### 2.4 Player–Fixture relationship

This is a first-class relationship, not merely a convenience join.

Canonical grain:

```text
season + fixture_id + player_id
```

It represents:

> **Player X participated in Fixture Y**

and provides the foundation for player-fixture detail, fixture player tables and player match research.

Source-specific player-match statistics attach to this relationship through verified fixture and player identity mappings.

### 2.5 Team–Fixture relationship

A team participates in a fixture through its canonical home/away relationship.

Canonical grain:

```text
season + fixture_id + team_id
```

This relationship is the foundation for:

- team fixture history;
- home/away historical state;
- form;
- streaks;
- rest days;
- season-to-date features;
- future modelling features.

---

## 3. Canonical versus specialist source hierarchy

The Laboratory must distinguish between **canonical entity data** and **preferred specialist metric sources**.

### Canonical means

> The Laboratory's authoritative representation of the entity or relationship.

Examples:

- canonical fixture master;
- persistent team identity;
- canonical player research identity.

### Specialist source means

> A source that provides richer or more specific evidence for a particular metric or analytical purpose.

A specialist source may override a displayed metric when its identity bridge is verified and its evidence is valid. It does **not** become the canonical entity model merely because it provides a richer statistic.

Example:

```text
Canonical Player
      ↓
FPL player statistics
      ↓
Verified player-match evidence
      ↓
Specialist Passing metrics
```

The specialist layer enriches the canonical model; it does not replace the identity architecture.

---

## 4. Metric source hierarchy

Every important metric should eventually have a documented source policy:

```text
metric
  ├── primary source
  ├── permitted fallback
  ├── identity requirement
  ├── availability semantics
  └── provenance status
```

Illustrative policy for current Player Research:

| Metric family | Preferred source | Fallback | Requirement |
|---|---|---|---|
| Goals | canonical FPL player data | — | canonical record |
| Assists | canonical FPL player data | — | canonical record |
| xG / xA | canonical FPL player data | — | canonical record |
| Shots | canonical FPL player data | — | canonical record |
| Attempted passes | verified player-match source | canonical FPL value | verified player identity |
| Completed passes | verified player-match source | canonical FPL value | verified player identity |
| Key passes | verified player-match source | canonical FPL value | verified player identity |
| Big chances created | verified player-match source | canonical FPL value | verified player identity |

The distinction is critical:

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

The evidence layer remains fail-closed even where a canonical fallback is available.

---

## 5. Provenance follows the metric

Research layers should preserve enough metadata that a user or developer can answer:

> **Where did this number come from?**

Conceptually, important metrics should be traceable through:

```text
value
source
status
reason
```

For example:

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

The GUI does not have to expose all provenance metadata everywhere, but the underlying analytical layer must retain it where practical.

---

## 6. Historical analytical services

Derived capabilities such as **form, streaks, trends, rest and historical likelihood features are shared analytical services, not page-specific calculations**.

The same historical-state service should feed multiple consumers.

```text
canonical fixtures + completed history
                ↓
        historical state service
                ↓
      ┌─────────┼───────────┐
      │         │           │
    form      streaks     trends
      │         │           │
      └─────────┼───────────┘
                ↓
        analytical consumers
```

This prevents several pages from calculating competing definitions of “last five”, “unbeaten streak” or similar concepts.

### Temporal rule

For a historical fixture, derived state must use only information available before that fixture under the project's availability-time and leakage rules.

The historical-state construction must therefore preserve the invariant:

```text
prior completed fixtures
        ↓
construct current fixture state
        ↓
only then add current fixture
```

---

## 7. Form and streaks policy

Form and streaks are **not currently a required standalone top-level page**.

They are shared analytical services that can be presented in context.

A future standalone Form / Streaks Explorer may be created only if a distinct league-wide discovery use case is established, such as scanning the entire Premier League for current streaks.

Until then:

- Team Profile presents a concise current-form snapshot;
- Team Stats presents deeper historical form/streak analysis;
- Matchday Centre presents fixture-relevant form, trends and likelihood context;
- modelling services consume the same derived features;
- no page may maintain its own independent form calculation.

---

## 8. Player information architecture

The Laboratory intentionally represents the player from three complementary perspectives.

### 8.1 Player Profile

Answers:

> **Who is this player?**

Responsibilities include:

- identity;
- club history;
- seasons;
- career context;
- concise current/summary statistics;
- navigation into player research and match appearances.

### 8.2 Player Stats / Research

Answers:

> **What has this player done, and how does it compare across seasons or players?**

This is the existing analytical-style player workspace.

It should support:

- season and multi-season analysis;
- filters;
- cross-season comparison;
- per-90 metrics;
- source-enriched statistics;
- player comparison and search.

### 8.3 Player–Fixture Detail

Answers:

> **What did this player do in this specific match?**

This view is tied directly to the canonical relationship:

```text
season + fixture_id + player_id
```

It must be reachable both:

- from a Fixture Landing Page / match player table;
- from a Player Profile / Player Stats match-history context.

These views must resolve the same underlying player and fixture entities rather than maintaining parallel data copies.

---

## 9. Team information architecture

Teams receive the same three-layer thinking, with the user-facing product currently requiring two dedicated team views and fixture-context views.

### 9.1 Team Profile

Answers:

> **Who are this club and what is their current context?**

Responsibilities include:

- canonical club identity;
- historical Premier League presence;
- season/competition context;
- concise current form;
- recent fixtures;
- current snapshot metrics;
- navigation into Team Stats and Fixtures.

### 9.2 Team Stats / Research

Answers:

> **What has this team done historically and analytically?**

This should be the team analogue of the Player Stats workspace.

Responsibilities include:

- season and multi-season statistics;
- home/away splits;
- goals and expected-goals style metrics where available;
- form and streak analysis;
- trend analysis;
- filtering and comparison;
- club history.

### 9.3 Team–Fixture context

Team form, streaks, rest and historical context for a fixture should come from the shared Team–Fixture / historical-state services and be presented where the fixture context requires them.

---

## 10. Fixture information architecture

The fixture is the central hub for match-level navigation.

### 10.1 Fixture Explorer

Answers:

> **Which fixture am I interested in?**

It should provide the canonical fixture list and safe navigation into fixture detail.

### 10.2 Fixture Landing Page

Answers:

> **What happened in this match?**

Responsibilities include:

- canonical teams and kickoff;
- final result/completion state;
- core match statistics;
- advanced match statistics;
- player performance table;
- navigation to player-fixture detail;
- navigation to team pages;
- provenance where relevant.

### 10.3 Match Detail / advanced match evidence

Match statistics must attach to the canonical fixture through verified fixture/source identity. They should never become a second competing fixture identity system.

---

## 11. Matchday Centre

The Matchday Centre is the contextual analytical surface for an upcoming fixture.

It combines:

```text
fixture context
        ↓
shared historical state
        ↓
stat pack
        ↓
model outputs
```

The Matchday Centre should contain or link to:

### Prediction Lab

- model probabilities;
- fair probabilities/prices;
- model-specific research outputs;
- explicit market separation where applicable.

### Stat Pack

- recent form;
- relevant streaks;
- trends;
- historical matchup/context;
- rest/context variables;
- descriptive likelihoods where methodology is documented;
- relevant player/team context.

The Stat Pack is a **presentation of shared analytical services**, not an independent source of truth.

---

## 12. League Table

The League Table is a canonical competition view.

It should be derived from the canonical fixture/result layer and the established team identity registry.

It must not maintain a separate team identity or results history merely for presentation.

It can link naturally to:

- Team Profile;
- Team Stats;
- Fixtures;
- Matchday Centre where appropriate.

---

## 13. Modelling and future analysis tabs

Future modelling tabs should consume established analytical services rather than rebuilding their own feature definitions.

The intended pattern is:

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

Examples may include:

- Projection Lab;
- future prediction modules;
- similarity/comparable-match analysis;
- other research experiments.

Model-specific transformations belong in the modelling layer and must retain temporal/availability semantics.

Market information remains separated from football research by default and only enters an explicitly defined decision layer when required by the research question.

---

## 14. Navigation and relationship graph

The target application should behave as a graph of canonical entities and relationships:

```text
                         LEAGUE TABLE
                              │
                              │
                         TEAM PROFILE
                              │
                    ┌─────────┴─────────┐
                    │                   │
               TEAM STATS          FIXTURES
                    │                   │
                    │           FIXTURE LANDING
                    │                   │
                    │          ┌────────┼────────┐
                    │          │        │        │
                    │       MATCH     PLAYERS   TEAMS
                    │       DETAIL
                    │          │
                    │    PLAYER–FIXTURE
                    │          │
                    │     PLAYER PROFILE
                    │          │
                    │     PLAYER STATS
                    │
                    └──── shared historical state ────┐
                                                       │
                                                 MATCHDAY CENTRE
                                                       │
                                                 PREDICTION LAB
                                                       │
                                                 FUTURE MODELS
```

The same entity should be reachable from multiple contexts through the same canonical identity.

For example:

```text
Fixture → Player-fixture detail → Player Profile
Player Profile → Match appearance → Fixture Landing Page
Fixture → Team → Team Profile → Team Stats
Team Stats → relevant fixture → Fixture Landing Page
```

No route should need to manufacture a second identity merely to make this navigation possible.

---

## 15. Relationship rules

### Fixture

```text
(season, fixture_id)
```

must be unique.

### Player

Canonical player identity must be persistent and distinct from season-local source IDs.

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

### Source identity mappings

A verified mapping must never be ambiguous.

If the system cannot establish a unique verified source identity:

```text
NO VERIFIED JOIN
```

rather than a best guess.

---

## 16. Non-destruction requirements

A change to one page must not silently change another page's data semantics.

In particular:

- UI presentation changes must not rewrite canonical data;
- specialist metric bridges must not alter canonical identity models;
- source fallback rules must be explicit;
- historical-state definitions must remain shared;
- fixture IDs must remain stable;
- player IDs must remain stable;
- team identity mappings must remain stable;
- provenance and corrections must not be hidden;
- incomplete source evidence must not be invented into complete-looking research values;
- feature work must preserve the trusted baseline and be tested at the appropriate layer.

This implements the Non-Destruction Assurance principle:

> **A feature is safe only when it works and trusted existing behaviour remains demonstrably intact.**

---

## 17. Test and validation obligations

Architectural changes should be validated at the layer they affect.

### Entity / identity changes

Require identity and cross-season audits.

### Fixture relationship changes

Require fixture/master/project-health validation.

### Player-fixture source changes

Require source schema, identity bridge and metric coverage tests.

### Historical-state changes

Require temporal/leakage safeguards and state-construction tests.

### GUI changes

Require:

- route/render validation;
- canonical data still resolves;
- fixture IDs remain unchanged;
- player/team identities remain unchanged;
- query contracts remain unchanged;
- provenance remains accessible;
- incomplete states do not crash the UI;
- the trusted 26/26 research baseline remains green when the change is presentation-only.

---

## 18. Data source / consumer contract

Before a new table, card, chart or page is implemented, establish:

```text
1. What is the canonical grain?
2. What is the primary key?
3. Which source fills each metric?
4. What is the permitted fallback?
5. What identity bridge is required?
6. What is the temporal / availability rule?
7. What provenance should be retained?
8. Which existing analytical service should supply it?
9. Which GUI views consume it?
10. What invariant protects it?
```

The preferred architecture is reuse through an established seam, not page-specific retrieval.

---

## 19. Design decision: no premature Form page

The Laboratory explicitly does **not** commit to a standalone Form / Streaks page at this stage.

The current intended product model is:

```text
Team Profile
    → concise current form snapshot

Team Stats
    → deeper historical form/streak analysis

Matchday Centre
    → fixture-relevant recent form, trends and likelihood context

Future modelling
    → consumes shared form/streak features
```

A dedicated Form / Streaks discovery workspace can be introduced later only where a distinct league-wide user task is demonstrated.

---

## 20. Long-term architecture target

The long-term target is a stable, documented path from evidence to presentation:

```text
SOURCE DATA
    ↓
SCHEMA VALIDATION
    ↓
IDENTITY REGISTRIES
    ↓
CANONICAL ENTITIES
    ↓
CANONICAL RELATIONSHIPS
    ↓
SOURCE EVIDENCE ENRICHMENT
    ↓
HISTORICAL STATE
    ↓
SHARED ANALYTICAL SERVICES
    ↓
PLAYER / TEAM / FIXTURE RESEARCH VIEWS
    ↓
MATCHDAY + MODELLING
    ↓
GUI
```

The GUI should remain the least authoritative layer in this chain.

The goal is not simply to make the application work. The goal is to make it difficult for a future change to produce a plausible-looking but incorrectly sourced or historically unsafe result.
