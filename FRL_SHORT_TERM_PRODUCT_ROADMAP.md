# Football Research Laboratory — Short-Term Product Roadmap

**Status:** Active near-term planning document  
**Last updated:** 4 September 2026

For repository-memory governance see `FRL_DOCUMENTATION_SYNC_CONTRACT.md`.

## Purpose

This roadmap turns FRL's governed research/data foundation into a coherent analytical product while preserving the principle that product needs should drive capability and source decisions.

Current-state detail belongs in `CURRENT_WORK.md`.

The active product architecture is defined in:

`FRL_PRODUCT_NORTH_STAR_AND_EXPERIENCE_ARCHITECTURE_V1.md`

The machine-readable requirements map is:

`data/frl_product_capability_requirements_v1.json`

## Governing product principles

> **The GUI should be a window into the research environment, not a collection of disconnected football pages.**

> **FRL should feel simple before it feels powerful.**

> **Curate the first view; preserve the full evidence underneath.**

The durable information-architecture rule remains:

> **Profiles describe entities. Stats analyse entities. Rankings analyse populations. Compare analyses selected entities together. Research tests the questions these surfaces reveal.**

The new experience architecture adds explicit product lenses over that shared analytical foundation:

- Player Scouting;
- Team Scouting;
- Opposition Report;
- Matchday / Fixture Intelligence;
- Stats / Rankings / Compare;
- Research Explorer.

These must share governed variables/results rather than becoming separate data systems.

---

# Completed / substantially completed foundations

## Fixture / identity / provenance foundation

Canonical fixture, team and player identity, source provenance, temporal discipline and missingness contracts are established enough to support continued analytical work.

## Team Stats analytical kernel

Team View and League Rankings have proven that multiple product projections can consume one shared governed season analysis result.

## Player analytical shell

Player Stats / Rankings / profiles have established the initial player product and cohort interaction shell, while richer player capability remains source/coverage dependent.

## League Table

League Table provides a governed competition-state surface over canonical results.

## Matchday V1

The fixture-first Matchday workspace exists and now becomes the base for a broader Fixture Intelligence experience rather than a final product endpoint.

## 2026/27 governed living-season pipeline

The release process is established and currently integrated through the second gameweek release on the active development branch.

## Raw PulseLive capability inventory

The preserved archive has been exhaustively scanned at raw-path level:

- 3,800 fixture snapshots;
- 553 scalar raw paths;
- 372 football/match paths;
- 249 team-match statistical paths.

The next task is not to put 249 values on a screen. It is to industrialise their governed accessibility.

---

# Phase 1 — Industrialise broad team-match capability

**Status: next / highest-priority backend capability task.**

## Objective

Make the broad PulseLive team-match statistics surface accessible through a generic governed research seam where semantics permit.

## Required work

1. reconcile the 249 raw team-match statistical paths with existing source-field catalogues and canonical variables;
2. distinguish duplicate/source-local representations from distinct football concepts;
3. classify each variable's natural grain;
4. classify aggregation semantics;
5. classify sparse-zero / missingness behaviour;
6. record season coverage and provider/version identity;
7. identify existing governed routes before creating new ones;
8. expose generic research access where the variable is sufficiently understood;
9. leave unresolved semantics fail-closed;
10. avoid page-specific retrieval implementations.

## Success condition

Adding the next legitimate team statistic should increasingly require:

> catalogue + semantic/governance definition

rather than:

> bespoke backend + bespoke API + bespoke frontend calculation.

---

# Phase 2 — Player Scouting information hierarchy

**Status: design/prototype after Phase 1 is underway; may proceed in parallel where it uses existing governed evidence only.**

## Objective

Create a visual-first player analytical experience that answers within seconds:

- what type of player is this?
- what are the major strengths?
- what are comparatively weak areas?
- how are they performing now?
- where do they sit within an appropriate cohort?

## Prototype constraints

- visual summaries first;
- no invented player passing metrics;
- cohort/position/minutes semantics remain governed;
- detailed metrics remain reachable through progressive disclosure;
- interpretation text is optional until it can be defended reproducibly.

## Capability implications

Rich current-season player-match technical evidence — especially passing/progression — is a demonstrated high-value requirement.

---

# Phase 3 — Team Scouting + Opposition Report

**Status: design/prototype after broad team-variable accessibility improves.**

## Team Scouting objective

Answer:

> **What kind of team is this, how do they play, and what is unusual about them?**

## Opposition Report objective

Answer:

> **If I were preparing to face this team, what would I need to understand?**

## Candidate analytical sections

- at-a-glance style profile;
- build-up / passing / progression;
- territory / possession;
- chance creation;
- threat profile;
- defensive behaviour;
- transitions / recoveries / possession loss;
- set pieces;
- personnel dependencies;
- recent tactical change;
- deep evidence / coverage / provenance.

The interface should organise information around football questions rather than provider field names.

---

# Phase 4 — Matchday → Fixture Intelligence

**Status: evolve existing Matchday V1.**

## Objective

Keep fixture-first navigation and answer:

> **What does the evidence tell us about this fixture?**

The initial product should form an independent football view without requiring bookmaker odds.

## Evidence families

Potential high-value evidence includes:

- team matchup / style interaction;
- recent time-safe form/state;
- shooting / shots on target;
- scoring / xG;
- chance creation / assists;
- likely player involvement;
- saves / goalkeeper workload;
- tackles / recoveries;
- fouls / cards;
- corners / crosses;
- home/away context;
- model probabilities where validated;
- explicit sample/uncertainty context.

Common betting markets are useful as a clue to which football phenomena matter, but they must not define the data architecture.

A future odds layer should remain separate and explicit.

---

# Phase 5 — Research Explorer / universal depth

**Status: architectural progression rather than one immediate page build.**

## Objective

Ensure the full governed capability universe remains discoverable and usable even when product summaries are deliberately curated.

Research access should progressively support:

- variable discovery;
- natural grain;
- season availability;
- definitions;
- source routes;
- coverage/missingness;
- populations/cohorts;
- ranks/distributions;
- splits/rolling windows;
- derivations;
- provenance;
- eventual natural-language investigation.

---

# Phase 6 — Capability-gap scoring

**Status: mandatory before broad supplementary-provider search.**

For each product experience, classify capabilities as:

```text
STRONG_NOW
PARTIAL_NOW
HISTORICAL_ONLY
CURRENT_ONLY
SOURCE_PRESENT_NOT_CONNECTED
DEMONSTRATED_GAP
NOT_YET_REQUIRED
```

Every gap must also be diagnosed by cause:

```text
SOURCE_PRESENT_NOT_CONNECTED
CONNECTED_NOT_GOVERNED
SEMANTICS_UNRESOLVED
IDENTITY_UNRESOLVED
DERIVATION_NOT_APPROVED
COVERAGE_INSUFFICIENT
CURRENT_SEASON_ABSENT
HISTORICAL_ABSENT
COMPARABILITY_UNRESOLVED
RIGHTS_OR_OPERATIONAL_BLOCK
```

Score unresolved requirements by:

- number of product experiences unlocked;
- research/modelling value;
- current-season importance;
- historical-depth value;
- player/team grain importance;
- identity/semantic complexity;
- rights/operational cost;
- provider-lock-in risk.

---

# Phase 7 — Requirement-led source evaluation

**Status: follows the gap-scoring milestone.**

Do not begin with:

> Which provider has the most variables?

Begin with:

> Which exact high-value capability bundles remain genuinely unresolved after the preserved FRL ecosystem has been exhausted?

Then evaluate candidate sources against:

- required variables and natural grain;
- historical/current coverage;
- update cadence;
- player/team/fixture identity reliability;
- semantic comparability;
- reproducibility / preservation;
- rights / redistribution constraints;
- operational fragility;
- provider-lock-in risk;
- cost where relevant.

Prefer sources that close several coherent high-value gaps rather than sources that merely advertise a large field count.

---

# Cross-cutting interaction direction

FRL uses progressive disclosure:

1. **Glance** — visual story in seconds;
2. **Explore** — football families / key visuals;
3. **Analyse** — broader metrics / distributions / splits / ranks;
4. **Research** — provenance / coverage / definitions / source semantics.

Navigation should preserve football context and make transitions between fixture, team, player, metric and ranking feel natural.

The signature tiled vertical-list language remains valid for statistical browsing, but it is one component pattern rather than the whole product architecture.

---

# Visual direction

The active warm editorial FRL design system remains authoritative.

External football products may inspire information hierarchy and interaction, but FRL should retain its own identity:

> **sleek + sexy + analytical + a little fun + professional**

Avoid generic SaaS dashboards and neon sportsbook aesthetics.

Use playful interaction only when it improves understanding.

---

# Validation / safety

For each implementation slice:

- inspect existing mechanisms first;
- reuse governed analytical seams;
- preserve source/identity/temporal/missingness contracts;
- validate targeted invariants;
- run relevant API/data/query regressions;
- run Next.js typecheck/build for frontend changes;
- run documentation-sync validation when project state changes;
- preserve `main` as the stable line and make development work reversible.

---

# Current next step

> **Begin Phase 1: reconcile and industrialise the 249 team-match-statistic source surface, while using the new product requirements map to determine which fields deserve first governance and which future gaps matter most.**
