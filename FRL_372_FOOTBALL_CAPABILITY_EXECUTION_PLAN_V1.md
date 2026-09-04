# FRL 372 Football Capability Execution Plan V1

**Status:** Active capability-industrialisation plan  
**Date:** 2026-09-04  
**Parent product direction:** `FRL_PRODUCT_NORTH_STAR_AND_EXPERIENCE_ARCHITECTURE_V1.md`

---

## Objective

Turn the preserved PulseLive football evidence universe into a coherent, governed FRL capability layer without reducing the ambition to the easiest source family.

The preserved raw audit established:

- **553** distinct scalar raw paths;
- **181** capture/provenance paths;
- **372** football/match paths;
- **249** team-match statistical paths;
- **123** additional football paths covering events, lineups, managers and match/team context.

The active capability North Star is therefore:

> **372 football/match raw paths remain in scope for semantic understanding, governed research access or explicit context/evidence roles.**

This does not mean 372 canonical metrics or 372 GUI elements.

Raw paths can represent statistics, events, identities, relationships, lineups, context or metadata carried at different grains.

---

## Why the 249 comes first

The 249 team-match statistical paths are Phase 1 because they are the largest coherent block with:

- one primary source family;
- one natural analytical grain;
- strong historical depth;
- direct relevance to Team Scouting, Opposition Report, Matchday and Research Explorer;
- substantial overlap with FRL's already packaged historical team-match source fields.

The September reconciliation established:

- **26** `EXISTING_EXPOSED`;
- **164** `EXISTING_SOURCE_FIELD_UNCATALOGUED`;
- **59** `RAW_SNAPSHOT_ONLY`.

This means Phase 1 is primarily a semantic/governance and route-discovery problem, not a requirement to write 249 bespoke extractors.

The 249 must never be mistaken for the final capability boundary.

---

# Workstream architecture

## Phase 1 — Team-match statistics

**Scope:** 249 paths.

Objectives:

1. verify generic research access for already exposed fields;
2. classify the 164 packaged-but-uncatalogued fields by football meaning;
3. establish aggregation and transformation semantics;
4. establish sparse-zero/missingness semantics;
5. establish historical season coverage and comparability;
6. promote defensible batches to reusable governed access;
7. investigate packaged equivalents or routes for the 59 raw-snapshot-only fields;
8. keep GUI exposure separate from research capability.

Primary product beneficiaries:

- Team Scouting;
- Opposition Report;
- Matchday / Fixture Intelligence;
- Team Stats / Rankings;
- Research Explorer.

## Phase 2 — Events

**Scope:** event-level raw paths.

Potential capabilities include:

- goal chronology;
- assist relationships;
- cards;
- substitutions;
- event timing;
- game-state reconstruction;
- state-dependent analysis;
- event-derived fixture/team/player features where semantics permit.

Primary product beneficiaries:

- Opposition Report;
- Matchday;
- Team/Player Scouting;
- future game-state modelling.

Events remain evidence at Event grain until an explicit derivation promotes them to another grain.

## Phase 3 — Lineups, formations and roles

**Scope:** player-lineup and team-lineup paths.

Potential capabilities include:

- starting XI;
- substitute status;
- position/role evidence;
- formation;
- personnel continuity;
- lineup change;
- player participation context.

Primary product beneficiaries:

- Player Scouting;
- Opposition Report;
- Matchday;
- temporal role/profile analysis.

No player identity should be inferred merely from display names or source numeric coincidence.

## Phase 4 — Match, team and manager context

**Scope:** remaining football context paths.

Potential capabilities include:

- match timing/context;
- venue;
- score/result state;
- team relationships;
- manager context;
- competition/fixture descriptors.

These variables often provide essential context rather than leaderboard metrics.

Primary product beneficiaries:

- all product surfaces;
- historical reconstruction;
- filtering and segmentation;
- research provenance.

---

# Capability layers

Every workstream must preserve this separation:

```text
RAW SOURCE PATH
      ↓
SOURCE-NATIVE EVIDENCE
      ↓
SEMANTIC / IDENTITY / COVERAGE REVIEW
      ↓
GOVERNED FRL VARIABLE OR CONTEXT CAPABILITY
      ↓
GENERIC TRANSFORMATION / ANALYTICAL SERVICE
      ↓
OPTIONAL PRODUCT EXPOSURE
```

A field may be research-visible as source evidence without being consumer-exposed as a governed variable.

Discovery must not silently imply promotion.

---

# Product doctrine

The capability layer should be broad.

The first product view should be curated.

The full governed depth should remain logically discoverable through progressive disclosure.

The product rule remains:

> **Curate presentation, not away the underlying research capability.**

Therefore:

- a scouting page can select a small set of high-information variables;
- an Opposition Report can select variables around tactical questions;
- Matchday can select variables relevant to the fixture;
- Research Explorer can expose the much broader governed universe;
- all of those surfaces should resolve the same variable definition rather than owning separate metric logic.

---

# Current execution order

1. **Protect the discovery → promotion governance boundary.**
2. **Triage the 249 team-match statistics into promotion and route-discovery batches.**
3. **Promote the highest-value, lowest-risk team-match batches through generic resolver access.**
4. **Prove generic transformations and population/ranking semantics over the expanded team universe.**
5. **Prototype Team Scouting / Opposition Report using governed capability only.**
6. **Industrialise the remaining 123 football paths by workstream: Events → Lineups/Roles → Match/Manager Context.**
7. **Score genuine unresolved capability gaps against Player Scouting, Team Scouting, Opposition Report, Matchday and Research needs.**
8. **Only then begin requirement-led current/future source acquisition.**

---

# Definition of success

The industrialisation programme succeeds when adding an understood source variable increasingly requires:

- a semantic definition;
- grain;
- provenance route;
- missingness/coverage rules;
- transformation rules where legitimate;
- product-family metadata where useful;

rather than a new bespoke extractor, API route and UI implementation for every field.

The long-term desired property is:

> **FRL can safely answer questions across essentially the full legitimate football evidence universe it possesses, while each product experience remains simple, visual and coherent.**
