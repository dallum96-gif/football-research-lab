# Football Research Laboratory — Canonical Variable Mapping Architecture V1

**Status:** Architectural contract / mapping blueprint  
**Declared:** 23 August 2026

## 1. Purpose

This document defines how the FRL canonical variable universe is mapped into the shared football research graph and subsequently exposed to Fixture, Team/Club, Player and Manager research views.

The purpose is **not** to create four separate data systems. The purpose is to ensure that the canonical evidence universe is represented once at the correct entity/relationship grain and can then be reused across all FRL research surfaces.

This document extends the existing hierarchy, identity and analytical-data contracts. It does not replace them.

## 2. Current canonical baseline

The current working canonical variable universe is:

**1,414 canonical variables**

The recent source-universe audit found that a much larger discovered source inventory does not imply a correspondingly larger canonical analytical universe. Source aliases, home/away dimensional variants, derived measures and structural containers must not be counted as independent canonical concepts merely because they appear as separate source fields.

The canonical universe remains the working baseline until an individual source field is proven to represent a genuinely distinct concept.

## 3. Governing principle

> **Map every structurally valid atomic source facet into the football graph at its correct grain; do not duplicate analytical concepts across presentation surfaces.**

Mapping and exposure are separate decisions.

A variable can be:

1. discovered;
2. mapped;
3. validated;
4. available to the canonical/evidence layer;
5. used by a shared research service;
6. exposed in one or more GUI views.

GUI exposure must never determine whether a source variable is preserved.

## 4. Canonical research graph

```text
                              SEASON / COMPETITION
                                      │
                 ┌────────────────────┼────────────────────┐
                 │                    │                    │
               TEAM                 PLAYER              MANAGER
                 │                    │                    │
                 │                    │                    │
             TEAM-SEASON          PLAYER-SEASON      MANAGER-TEAM TENURE
                 │                    │                    │
                 └────────────┬───────┴────────────┬───────┘
                              │                    │
                         TEAM-FIXTURE        PLAYER-FIXTURE
                              │                    │
                              └─────────┬──────────┘
                                        │
                                     FIXTURE
                                        │
                                      EVENT
```

The graph is the analytical foundation. GUI pages are lenses over this graph.

## 5. Canonical grains

Every mapped variable must have one explicit primary analytical grain.

### Fixture

```text
(season, fixture_id)
```

Use for match identity, chronology, competition context, final result, match-level state and other attributes that describe the fixture itself.

### Team–Fixture

```text
(season, fixture_id, persistent_team_code)
```

Use for team-specific match observations, including home/away-normalised team statistics, team result state and team performance measures.

### Player–Fixture

```text
(season, fixture_id, canonical_player_id)
```

Use for player participation and player-specific match observations.

### Team–Season

```text
(season, persistent_team_code)
```

Use for season aggregates and season-scoped team context.

### Player–Season

```text
(season, canonical_player_id)
```

Use for season aggregates, roster/profile state and season-level player evidence.

### Event

```text
(season, fixture_id, source_event_identity)
```

Use for event-level evidence where the source provides a distinct event record. Event evidence must retain a stable route back to the canonical fixture and, where applicable, player/team identity.

### Manager

```text
(canonical_manager_id)
```

Use for longitudinal manager identity/profile attributes.

### Manager–Team Tenure

```text
(canonical_manager_id, persistent_team_code, tenure_start, tenure_end)
```

Use for historical managerial employment and team-tenure state.

### Manager–Fixture

```text
(season, fixture_id, canonical_manager_id, persistent_team_code)
```

Use when a manager is attributable to a team's participation in a fixture under the relevant historical/availability semantics.

## 6. Variable destination policy

Every canonical variable must map to the entity or relationship that naturally owns the observation.

### 6.1 Fixture-owned variables

Examples:

- fixture identity;
- season / competition;
- kickoff and chronology;
- stadium/venue;
- officials;
- match status;
- final score/result;
- match-level temporal state;
- fixture-level event container references.

Do not copy team-specific observations into the Fixture row merely because they are displayed on a fixture page.

### 6.2 Team–Fixture variables

This is the primary home for team match evidence.

Examples include:

- team shooting;
- team xG/xGA where source grain is team-match;
- possession;
- territorial measures;
- passing/distribution;
- chance creation;
- defending;
- goalkeeping;
- set-piece activity;
- discipline;
- team-level attacking mechanisms;
- team-level ball-security measures;
- team-level advanced event aggregates.

Fixture presentation may display these values, and Team Stats may aggregate them, but the underlying values remain Team–Fixture evidence.

### 6.3 Player–Fixture variables

Primary home for player-specific match evidence.

Examples include:

- participation;
- minutes;
- starter/substitute state;
- goals/assists;
- shooting;
- passing;
- chance creation;
- dribbling/carrying;
- duels/aerials;
- defensive actions;
- goalkeeper actions;
- discipline;
- player event statistics.

Player Profile and Player Stats consume these observations through research services rather than owning duplicate copies.

### 6.4 Team–Season variables

Use for season-level team observations that are directly supplied or reproducibly aggregated from Team–Fixture evidence.

Examples include:

- season totals;
- season rates;
- season shooting profile;
- passing profile;
- defensive profile;
- possession profile;
- set-piece profile;
- home/away splits.

### 6.5 Player–Season variables

Use for season-level player evidence, including:

- season totals;
- season rates where the underlying canonical basis is clear;
- profile/roster context;
- position/role context;
- club-season membership;
- season-level specialist measures.

### 6.6 Event variables

Event-level variables must not be flattened into arbitrary Fixture or Player rows merely for convenience.

Examples may include:

- goal events;
- card events;
- substitutions;
- shot events;
- event timestamps;
- event player/team identity;
- event coordinates where actually available;
- event-specific contextual attributes.

Event data should be retained at source/native grain or a documented canonical event grain.

## 7. Home/away and other dimensional variants

Home/away source variants are not separate canonical concepts merely because they are separate columns.

Example:

```text
source:
expectedGoals_h
expectedGoals_a

canonical concept:
expected_goals

canonical dimension:
venue_role = home | away
```

The source-level fields remain preserved for provenance and exact reconstruction. The analytical model should avoid needless duplication of the conceptual variable.

Other source dimensions should be handled the same way where the distinction is genuinely dimensional rather than semantically distinct.

## 8. Atomic facet preservation

Distinct source facets should remain independently mapped even when they later feed the same derived research measure.

Examples:

```text
attempted passes
successful passes
unsuccessful passes
final-third passes
forward passes
through balls
crosses
key passes
assists
shots
shots in box
shots outside box
shots on target
blocked shots
xG
```

Higher-level metrics may be derived later, but the atomic evidence must not be discarded merely because the GUI currently needs only one aggregate.

This preserves future research capability and provenance.

## 9. Derived-variable policy

A measure such as a per-90 rate, percentage or composite should normally be treated as a derived analytical product when the underlying canonical observations exist.

Examples:

```text
xG per 90
pass completion percentage
xG per shot
shots per 90
points per game
```

Derived variables should record:

- source canonical inputs;
- transformation formula;
- population/filter;
- temporal/as-of semantics;
- transformation/version metadata.

A source-supplied derived value may still be retained as source evidence, but FRL must not silently confuse it with an independently observed atomic fact.

## 10. Manager architecture

Manager should be a first-class canonical entity.

The minimum model is:

```text
MANAGER
   │
   └── MANAGER–TEAM TENURE
            │
            └── MANAGER–FIXTURE
```

A manager must not be represented solely as a mutable `manager_name` field on Team.

Tenure must preserve historical state, including start and end boundaries and the relevant team identity.

This allows FRL to support questions such as:

- manager record at a club;
- team performance under a manager;
- before/after managerial change analysis;
- player performance under a manager;
- tactical/statistical profile under a manager;
- manager tenure comparisons across clubs.

Manager attribution must follow the project's historical/availability semantics and may not be backfilled from today's manager identity into earlier fixtures.

## 11. Presentation mapping

The canonical graph should feed four major entity-facing experiences without duplicating the underlying data model.

### Fixture

Consumes:

- Fixture;
- Team–Fixture;
- Player–Fixture;
- Event;
- shared historical analytical state.

### Club / Team

User-facing language may call the entity a Club or Team, but the canonical identity remains Team.

Consumes:

- Team;
- Team–Season;
- Team–Fixture;
- Manager–Team tenure;
- shared analytical state.

### Player

Consumes:

- Player;
- Player–Season;
- Player–Fixture;
- club history;
- manager context where validated;
- shared analytical state.

### Manager

Consumes:

- Manager;
- Manager–Team tenure;
- Manager–Fixture;
- Team–Fixture under the relevant tenure;
- Player–Fixture under the relevant tenure;
- shared historical state.

## 12. Research-facing layers

A mapped variable does not automatically become a GUI field.

Recommended status progression:

```text
DISCOVERED
   ↓
MAPPED
   ↓
VALIDATED
   ↓
AVAILABLE TO RESEARCH
   ↓
RESEARCH-FACING
   ↓
GUI-EXPOSED
```

A variable may remain fully preserved and queryable without being placed on a profile page.

## 13. Variable registry requirements

The canonical variable registry should eventually contain, at minimum:

```text
canonical_variable
source_field
source_family
source_resource
source_grain
canonical_grain
entity
relationship
source_type
raw_or_derived
identity_requirement
temporal_semantics
transformation
null_semantics
provenance
validation_status
research_status
ui_status
```

This registry is the authority for variable mapping. Individual GUI components must not create independent field-to-source mappings.

## 14. Minimum mapping workflow

```text
1. INVENTORY
      ↓
2. RECONCILE
      ↓
3. IDENTIFY SOURCE GRAIN
      ↓
4. ASSIGN CANONICAL GRAIN
      ↓
5. VERIFY IDENTITY BRIDGE
      ↓
6. DEFINE TEMPORAL SEMANTICS
      ↓
7. PRESERVE ATOMIC FACET
      ↓
8. MAP / VALIDATE
      ↓
9. REGISTER DERIVATION IF NEEDED
      ↓
10. EXPOSE THROUGH SHARED RESEARCH SERVICES
      ↓
11. EXPOSE TO GUI ONLY WHEN JUSTIFIED
```

## 15. Safety and integrity rules

1. Do not create separate copies of the same canonical concept for different GUI pages.
2. Do not flatten relationship-level evidence into entity rows merely because it is convenient for presentation.
3. Do not silently treat provider IDs as canonical IDs.
4. Do not backfill current identities into historical states.
5. Do not discard atomic source facets because they are not currently displayed.
6. Do not treat source-derived rates as equivalent to atomic observations without recording the derivation.
7. Do not expose an unmapped or unvalidated value as trusted research.
8. Preserve provenance for every mapped value.
9. Keep source acquisition, source evidence, canonical representation and GUI exposure as separate layers.
10. Reuse the established identity and relationship bridges before creating new seams.

## 16. Completion condition

The canonical variable mapping phase is complete when every variable in the approved 1,414-variable universe has a documented answer to:

1. What source evidence supports it?
2. What observation grain owns it?
3. What canonical entity/relationship owns it?
4. What identity bridge is required?
5. What temporal/as-of semantics apply?
6. Is it atomic or derived?
7. How is provenance retained?
8. Is it validated?
9. Is it research-facing?
10. Is it exposed in the GUI, and if so, where?

The goal is not maximum GUI field count. The goal is a complete, reusable, provenance-aware football evidence graph.
