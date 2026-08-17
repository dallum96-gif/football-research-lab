# Current Work — Football Research Laboratory

**Last updated:** 17 August 2026

This file is intentionally short and volatile. Update it whenever the active task, branch, checkpoint or next step changes.

## Active branch

`design/player-filter-tiles`

This is the active GUI/application-architecture branch for the current redesign work.

The branch is based on the current redesign PR and must be compared with `main` before substantive changes.

## Stable / validated baseline

Current research gate:

**26/26 tests passing**

Breakdown:

- Query Lab: 14/14
- Player Research V0.1: 6/6
- Player Research V0.2: 6/6

Additional player-match evidence-layer tests currently validated locally:

- Player-Match Source: 6/6
- Player-Match Research: 3/3
- Player Research Passing Integration: 3/3
- Player Research Player-Match: 2/2

The project-health gate remains a separate required control for relevant data-layer changes.

## Governing architecture contract

`FRL_DATA_HIERARCHY_RELATIONSHIP_CONTRACT.md` is now a required architectural-memory document for fresh sessions.

It is governed by:

- `RISK_STRATEGY_FRAMEWORK.md`
- `NON_DESTRUCTION_ASSURANCE.md`
- `DATA_CONSTRUCTION.md`

The contract establishes the FRL as a connected football evidence graph rather than a collection of isolated pages.

Core principle:

> **Deep evidence underneath. Simple research experience on top.**

The FRL should preserve as much useful, provenance-aware football evidence as practical, including event-level source evidence, even when the project does not yet know how the information will be used. Retention does not imply trust: retained evidence must still be validated, reconciled, temporally safe and evaluated before promotion into trusted research or modelling features.

Canonical entities are:

- Player
- Team
- Fixture

Canonical relationships include:

- Player–Fixture: `(season, fixture_id, player_id)`
- Team–Fixture: `(season, fixture_id, team_id)`
- Fixture Events, attached through validated fixture/team/player identities where known

The GUI is downstream from identity, canonical data, evidence, analytical state and modelling layers.

## Product navigation contract

The primary sidebar is now fixed as:

- Home
- Fixtures & Results
- League Table
- Teams
- Players
- Analysis

These are primary workspaces, not a list of every entity or analytical capability.

Contextual/detail views do not become sidebar clutter. In particular:

- Player–Fixture Detail is reached through a player/fixture relationship.
- Form and Streaks are shared analytical services, not a sidebar workspace.
- Matchday Centre, Query, Combined Metrics, Records and future mathematical/statistical models sit under Analysis.

## Current product architecture direction

The intended graph is:

```text
Player ←→ Player–Fixture ←→ Fixture ←→ Team–Fixture ←→ Team
                              ↓
                  shared historical/analytical state
                              ↓
             Research / Query / Models / Matchday
                              ↓
                             GUI
```

Team and Player each have separate profile and statistics/research responsibilities.

### Teams

Two primary views are planned:

**Team Profile** — identity, history, current context, concise form, recent fixtures and connected navigation.

**Team Stats** — season/multi-season statistics, filtering, comparisons, home/away analysis and deeper historical research.

The existing canonical query mechanisms are the safe starting seam: `team_summary`, `team_compare`, `team_form`, `fixtures` and the verified team identity registry.

### Players

Three complementary views:

**Player Profile** — who is this player?

**Player Stats / Research** — what has this player done and how does it compare?

**Player–Fixture Detail** — what did this player do in this specific match?

### Fixtures & Results

Fixture Explorer remains the entry point into the canonical fixture object, with Fixture Landing Page branching into match detail, player performance, player-fixture detail, team context, research and modelling.

### League Table

The League Table is an analytical competition view and should eventually support historical point-in-season views, ranges, home/away splits and navigation into Team Profile/Team Stats.

### Analysis

Analysis is the umbrella for:

- Matchday Centre;
- Prediction Lab;
- Head-to-Head as an existing contextual analytical capability;
- future Query/research tooling;
- comparable-match discovery;
- Combined Metrics;
- Records;
- future mathematical/statistical modelling;
- research consensus / ensembles where justified;
- explicit future market/decision layers.

## Player-match source and identity architecture

For work involving player-match source data, read:

`PLAYER_MATCH_SOURCE_BRIDGE.md`

The established audited principle is that canonical fixture identity remains `season + fixture_id`, and upstream source namespaces must be resolved through existing verified mechanisms rather than compared directly.

The verified player-match enrichment layer is represented by:

- `player_match_stats.py`
- `player_match_research.py`
- `player_research_player_match.py`
- `player_identity_registry.py`
- `player_identity_registry.csv`

The evidence layer is fail-closed. Verified specialist values may override displayed metrics where identity and source evidence are proven; otherwise documented canonical fallback values remain visible and provenance records the absence of specialist verification.

## GUI design contract

`GUI_DESIGN_CONTRACT.md` and `UI_DESIGN_SYSTEM.md` remain governing visual references.

The current redesign direction is compact, editorial and playful without becoming decorative or form-heavy. The primary navigation is deliberately smaller than the application graph.

Players filter work uses the approved light, transparent tile presentation with no dark selector/query surfaces.

## Non-destruction rule for current work

UI redesign changes should not modify:

- query semantics;
- canonical fixture identity;
- persistent club identity;
- provenance rules;
- research calculations;
- historical data;
- validated evidence-layer contracts.

A UI change is successful only when the new presentation works and trusted existing behaviour remains intact.

## Verification discipline

Before declaring a substantive change complete:

1. Inspect the relevant current implementation and existing consumer.
2. Identify the narrowest safe change surface.
3. Add targeted regression coverage for new behaviour.
4. Validate Python syntax/structure.
5. Verify the route still exists.
6. Verify existing data still renders.
7. Verify requested controls work.
8. Run the applicable research gate.
9. Run the project-health gate where relevant.
10. Inspect the GitHub Actions result before calling the branch safe.

Do not claim tests or project-health success unless they have actually been executed and passed.

## Fresh-session architecture sequence

The normal fresh-session Master Prompt should now be interpreted as requiring:

```text
read orientation
→ read current work
→ read data construction
→ read risk strategy
→ read non-destruction assurance
→ read UI design system
→ read FRL data hierarchy & organisation contract
→ establish branch/repository state
→ inspect relevant working/archived/local mechanisms
→ run 26/26
→ run project health
→ only then start substantive work
```

The hierarchy contract is part of project memory and must not be treated as optional background.

## Immediate next step

Continue implementing the architecture contract in the application without creating duplicate data mechanisms.

The next bounded feature is Team Profile + Team Stats, using the established canonical team identity and query seams rather than introducing new source joins.

From there, continue toward the connected research graph while preserving the deep-evidence retention principle, provenance, temporal safety and non-destruction guarantees.
