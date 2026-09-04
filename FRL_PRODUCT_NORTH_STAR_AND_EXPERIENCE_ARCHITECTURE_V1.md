# FRL Product North Star & Experience Architecture V1

**Status:** Active product architecture decision  
**Date:** 2026-09-04  
**Scope:** Product intent, information architecture, interaction philosophy, capability-led data acquisition

For repository-memory governance see `FRL_DOCUMENTATION_SYNC_CONTRACT.md`.

---

## 1. Objective

Turn FRL's broad research/data ambition into a coherent product system that makes deep football evidence feel effortless to explore.

The product objective is:

> **FRL should make enormous statistical depth feel simple, visual and fluid — whether the user is scouting a player, studying a team, preparing for an opponent, researching a population, or forming an independent view of a fixture.**

This does **not** replace the durable research North Star in `FRL_MASTER_PROMPT.md`.

It defines the product experience through which that research environment becomes useful.

---

## 2. Definition of done for this milestone

This milestone is complete when FRL has a durable answer to:

1. what major user experiences the product is trying to support;
2. what question each experience answers;
3. what information should appear immediately versus progressively;
4. how deep data remains discoverable without becoming overwhelming;
5. how scouting, rankings, research and fixture analysis share one governed variable architecture rather than becoming separate statistical systems;
6. how product requirements determine future data-acquisition priorities.

This milestone does **not** require every final screen to be designed or built.

---

# 3. Product promise

The interface should feel:

- sleek;
- visually appealing;
- smooth;
- professional;
- analytical;
- playful in restrained ways;
- recognisably FRL.

The interaction principle is:

> **Playful interaction, serious information.**

The comprehension principle is:

> **FRL should feel simple before it feels powerful.**

The depth principle is:

> **Curate the first view; preserve the full evidence underneath.**

FRL should never solve information overload by deleting research capability.

It should solve it through hierarchy, navigation and progressive disclosure.

---

# 4. Shared product architecture

FRL should deliberately provide different **lenses over one governed football-variable universe**.

```text
GOVERNED FOOTBALL EVIDENCE / VARIABLES
               ↓
       SHARED ANALYTICAL LAYER
               ↓
 ┌─────────────┼──────────────┬───────────────┬──────────────┐
 │             │              │               │              │
SCOUTING   OPPOSITION      MATCHDAY       STATS /       RESEARCH
           REPORT          / FIXTURE      RANKINGS
                           INTELLIGENCE
```

These are presentation and investigation lenses, not separate data systems.

A metric must not acquire a different definition merely because it appears in scouting, Matchday or rankings.

---

# 5. Product experiences

## 5.1 Player Scouting

Primary question:

> **What sort of player is this, how are they performing, and what should an analyst care about?**

A strong first view should communicate within roughly ten seconds:

- player identity and role;
- positional / role profile;
- major strengths;
- major weaknesses or comparatively low areas;
- current performance / form context;
- league/cohort context;
- important output.

### Presentation direction

Visual summaries first.

Potential primitives include:

- percentile profile;
- positional profile graphic;
- selected trend visual;
- compact trait summaries;
- contribution / involvement distributions;
- pitch/spatial visuals where governed evidence permits;
- a small curated set of headline numbers.

The user can then move into families such as:

`Shooting · Creation · Passing · Possession/Progression · Defending · Discipline · Goalkeeping · FPL where relevant`

The full underlying metric universe should remain logically navigable below the curated summary.

### Interpretation

FRL may eventually generate concise analyst-style interpretations such as:

> High-volume progressive passer with strong opposition-half involvement.

But interpretive language must be:

- based on governed definitions;
- reproducible;
- cohort-aware;
- threshold/version controlled;
- consistent across players.

Until that standard exists, the visual evidence should stand on its own.

---

## 5.2 Team Scouting

Primary question:

> **What kind of team is this, what are they good at, how do they behave, and what is unusual about them?**

This should be analytical rather than simply duplicating Team Profile.

A quick summary should communicate:

- broad style / tendencies;
- attacking profile;
- possession / progression profile;
- defensive profile;
- major strengths / vulnerabilities;
- recent change / stability where meaningful;
- league context.

Team Profile remains identity/story/navigation.

Team Scouting / Team Stats remains measurement and understanding.

---

## 5.3 Opposition Report

This is a distinct product mode rather than merely another Team Profile section.

Primary question:

> **If I were preparing to face this team, what would I need to understand?**

The report should eventually organise evidence around football preparation rather than source fields.

Candidate sections:

1. **At a glance** — style, strengths, weaknesses, recent state;
2. **Build-up & progression** — pass direction, progression, territory, long/short tendencies;
3. **Chance creation** — shots, big chances, crosses, through balls, final-third behaviour, creators;
4. **Threat profile** — where/how attacks become dangerous;
5. **Defensive behaviour** — tackles, recoveries, interceptions, pressures/duels where available, shot suppression;
6. **Transitions & possession loss** — regain/loss tendencies and game-state behaviour where governed;
7. **Set pieces** — corners and other set-piece capabilities where evidence permits;
8. **Personnel dependencies** — key players / role concentration where player evidence permits;
9. **Recent tactical change** — only where sufficient temporal evidence supports it;
10. **Deep evidence** — all relevant source/governed metrics, coverage and provenance.

This surface should become one of FRL's clearest demonstrations that statistics can help explain football rather than merely rank it.

---

## 5.4 Matchday / Fixture Intelligence

Primary question:

> **What does the evidence tell us about this fixture?**

The fixture is the entry point.

FRL should **not** organise the initial experience around bookmaker markets.

At this stage FRL is forming an independent football opinion without bookmaker odds.

Potential evidence groups include:

- team matchup / stylistic interaction;
- expected scoring environment;
- shooting volume / shot-on-target tendencies;
- likely player involvement;
- chance creation / assists;
- saves / goalkeeper workload;
- tackles / defensive activity;
- fouls / cards;
- corners / crossing;
- form and recent state;
- home/away context;
- model output where properly validated;
- sample and uncertainty context.

### Betting-support principle

The product may help users construct bet-builder ideas by surfacing football phenomena that correspond to common markets.

But FRL should first answer:

> **What do we independently think is likely or interesting?**

A later market/odds layer would answer the separate question:

> **Is the available price attractive?**

These should not be conflated.

---

## 5.5 Stats / Rankings / Compare

The existing rule remains:

> **Profiles describe entities. Stats analyse entities. Rankings analyse populations. Compare analyses selected entities together. Research tests the questions these surfaces reveal.**

Stats and rankings provide systematic access to the governed metric universe.

They are not expected to make all metrics equally prominent.

The signature vertical-list tile grammar can remain a recognisable FRL pattern for fast metric exploration.

Compare remains a later lens over the same governed result architecture.

---

## 5.6 Research Explorer

Primary question:

> **What evidence do we actually possess, how can I interrogate it, and what new football question can I test?**

This is where FRL's breadth should be least curated and most discoverable.

The objective is not a raw database browser.

It should progressively allow users to navigate:

- entity/grain;
- variable family;
- metric definition;
- season/period;
- population;
- splits;
- distributions;
- trends;
- derived variables;
- provenance / coverage / missingness;
- future natural-language questioning.

---

# 6. Progressive disclosure: the anti-overwhelm system

FRL should use a four-layer information hierarchy.

## Layer 1 — Glance

Purpose:

> Understand the story in seconds.

Characteristics:

- visual-first;
- very small number of high-information signals;
- clear entity / period / comparison context;
- no wall of metrics.

## Layer 2 — Explore

Purpose:

> Understand the major components of performance/style.

Characteristics:

- logical football families;
- strong visualisations;
- selected supporting numbers;
- easy transitions to related entities/metrics.

## Layer 3 — Analyse

Purpose:

> Investigate the underlying statistical evidence.

Characteristics:

- broader metric universe;
- ranks / distributions;
- time windows;
- splits;
- comparisons;
- full ledgers/tables;
- filtering / cohorts.

## Layer 4 — Research

Purpose:

> Inspect definitions, source routes and limitations or begin deeper analysis.

Characteristics:

- provenance;
- coverage / missingness;
- transformation;
- population eligibility;
- source representation/version;
- temporal/as-of semantics;
- export/query/research pathways where supported.

Important limitations must still surface earlier when they materially affect interpretation.

---

# 7. Navigation and interaction rules

The product should feel **super smooth** to move through.

Navigation should preserve football context wherever possible.

Examples:

```text
Fixture
  → Team
  → Opposition Report
  → Player
  → Player Scouting
  → Metric ranking
  → Full metric detail
```

and:

```text
Player Scouting
  → team context
  → upcoming fixture
  → Matchday
  → relevant opposing player/team tendency
```

Rules:

- preserve season/context while navigating unless the user changes it;
- entity names should be links where useful rather than dead labels;
- metric visuals should drill into the relevant metric detail/ranking;
- rankings should drill back to entity analysis;
- deeper evidence should be one deliberate interaction away rather than hidden in unrelated pages;
- browser back/forward and deep links should remain meaningful;
- transitions/animation should clarify state, not delay navigation.

---

# 8. Visual direction

The existing FRL warm editorial system remains authoritative.

External inspiration may be taken from products such as Football Manager or FotMob for:

- information hierarchy;
- scouting mental models;
- fluid navigation;
- football-first interaction patterns.

FRL should **not** imitate their visual identity.

The desired result remains uniquely FRL:

> **sleek + sexy + analytical + a little fun + professional**

Avoid sportsbook/neon aesthetics for Matchday/betting-support work.

Avoid turning scouting into videogame decoration.

Animations, traits, badges and colour are welcome only when they improve comprehension and remain restrained.

---

# 9. Capability philosophy

The product should not be curated at the **data capability** layer.

The interface should be curated at the **presentation** layer.

Therefore:

> **FRL itself should aim to make every legitimate governed football variable research-accessible; individual product surfaces should select only the variables that answer their question well.**

This is especially important given the broad preserved PulseLive snapshot inventory.

The September 2026 raw snapshot audit established:

- 3,800 preserved fixture snapshots;
- 553 distinct scalar raw paths;
- 372 football/match paths after capture/provenance metadata is separated;
- 249 team-match statistical paths.

Those numbers describe source capability, not 553 independently governed product metrics.

The immediate architectural opportunity is to industrialise the common team-match-statistic grain so adding a new governed team metric increasingly becomes catalogue/governance work rather than bespoke product code.

---

# 10. Capability-led acquisition framework

Future data acquisition must begin with product/research requirements, not provider catalogues.

The sequence is:

```text
PRODUCT / RESEARCH QUESTION
        ↓
REQUIRED FOOTBALL CAPABILITY
        ↓
CURRENT FRL CAPABILITY CHECK
        ↓
GAP CLASSIFICATION
        ↓
CONNECT / DERIVE / GOVERN IF ALREADY PRESENT
        ↓
ONLY THEN: EVALUATE SUPPLEMENTARY SOURCE
```

Every apparent gap should first be classified as one of:

- `SOURCE_PRESENT_NOT_CONNECTED`;
- `CONNECTED_NOT_GOVERNED`;
- `SEMANTICS_UNRESOLVED`;
- `IDENTITY_UNRESOLVED`;
- `DERIVATION_NOT_APPROVED`;
- `COVERAGE_INSUFFICIENT`;
- `CURRENT_SEASON_ABSENT`;
- `HISTORICAL_ABSENT`;
- `COMPARABILITY_UNRESOLVED`;
- `RIGHTS_OR_OPERATIONAL_BLOCK`.

Only genuine unresolved requirements should trigger provider evaluation.

---

# 11. Capability requirements by experience

## Player Scouting — high-value capability families

Priority capabilities include:

- minutes / role / position;
- shooting and shot quality;
- chance creation / xA / key-pass style evidence;
- passing volume and accuracy;
- progressive / territorial passing;
- carrying / dribbling / progression;
- touches / involvement;
- defensive actions / recoveries / duels;
- aerial contribution;
- discipline;
- goalkeeper-specific evidence;
- temporal trends and role changes;
- reliable player identity across seasons and source families.

A demonstrated current-season weakness is rich individual-player passing/progression detail: FPL evidence should not be relabelled as a substitute for genuine passing metrics.

## Team Scouting / Opposition Report — high-value capability families

Priority capabilities include:

- shooting / shot quality;
- chance creation;
- passing direction / volume / accuracy;
- final-third / opposition-half activity;
- long-ball / crossing / through-ball tendencies;
- possession / territory / progression;
- ball recoveries / possession loss;
- tackles / interceptions / clearances / duels;
- shot suppression / goalkeeper workload;
- set pieces;
- events and game-state chronology;
- formations / lineups / substitutions;
- player contribution concentration.

Historical PulseLive team-match evidence is particularly strong here; current-season rich team-match coverage remains a major requirement.

## Matchday / Fixture Intelligence — high-value capability families

Priority capabilities include:

- temporally safe recent team/player evidence;
- home/away and opponent-context splits;
- shots / shots on target;
- goals / xG / scoring-state models;
- assists / chance creation;
- saves;
- tackles / recoveries;
- fouls / cards;
- corners / crosses;
- starting/availability/role evidence where trustworthy;
- model probabilities and calibrated evaluation where available.

This surface places particularly high value on **current, time-safe, player-level evidence**.

## Research Explorer

Priority is breadth:

- all governed football variables;
- natural grain;
- season/coverage metadata;
- source/version/provenance;
- transformation/derivation;
- population/comparability;
- flexible retrieval and filtering.

---

# 12. Immediate execution plan

## Phase A — Product architecture lock

**Status: this milestone.**

- record this product North Star;
- update living product/design documentation;
- create a machine-readable capability-requirements map;
- make product requirements the decision boundary for future source acquisition.

## Phase B — Universal capability industrialisation

- audit the 249 team-match-statistic paths against existing canonical variable/source-field systems;
- identify what can flow through one generic team-match retrieval/aggregation seam;
- classify each field's aggregation/missingness/coverage semantics;
- increase research accessibility without forcing every field into the GUI.

## Phase C — Experience prototypes

Build low-risk visual prototypes over already-governed evidence for:

1. Player Scouting summary;
2. Team Scouting summary;
3. Opposition Report skeleton;
4. Fixture Intelligence / Matchday evidence hierarchy.

These prototypes should test information hierarchy and navigation, not invent unavailable football evidence.

## Phase D — Capability-gap scoring

For every experience, classify required capabilities as:

```text
STRONG_NOW
PARTIAL_NOW
HISTORICAL_ONLY
CURRENT_ONLY
SOURCE_PRESENT_NOT_CONNECTED
DEMONSTRATED_GAP
NOT_YET_REQUIRED
```

Score unresolved capabilities by:

- number of product experiences unlocked;
- research/model value;
- player vs team grain importance;
- current-season importance;
- historical depth required;
- identity/semantic complexity;
- acquisition/rights/operational cost.

## Phase E — Data acquisition

Only after Phase D:

- define exact missing capability bundles;
- inspect existing preserved routes again;
- evaluate candidate sources/providers against those bundles;
- prefer sources that close several high-value gaps coherently;
- preserve source truth and provider differences;
- avoid provider lock-in at the product layer.

---

# 13. Review questions for future design work

Every new product surface should answer:

1. What question is the user trying to answer?
2. What should be understood in ten seconds?
3. What visual representation communicates that best?
4. What detail should be one interaction deeper?
5. What full evidence should remain reachable?
6. What coverage/provenance limitation changes interpretation?
7. Does this surface reuse governed variables/results rather than inventing definitions?
8. Can the user move naturally to the next football question?

---

# 14. Final product principle

> **FRL is an analytical football environment that makes enormous statistical depth feel effortless to explore — whether scouting a player, preparing for an opponent, researching the league, or forming an independent view of a fixture.**

The data layer should remain ambitious.

The first view should remain disciplined.

The navigation between them should feel effortless.
