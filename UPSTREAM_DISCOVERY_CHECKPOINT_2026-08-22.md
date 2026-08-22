# FRL Upstream Discovery Checkpoint — 2026-08-22

## Purpose

Checkpoint the current state of FRL source discovery so future work can resume from a known baseline rather than relying on conversation memory.

## Source lineage established

FRL's current preserved CSV ecosystem is downstream of the public repository:

`imadeddine-belkat/Premier-League-Stats`

That repository contains two major data families:

1. **FPL Gameweek Data** from the Official FPL API (`bootstrap-static`, `fixtures`, `element-summary`).
2. **Historical Premier League archive** from Premier League / PulseLive feeds.

The Imadeddine repository is therefore a published extraction layer, not necessarily the complete upstream universe.

## FRL's current local source universe

The existing FRL source-field audit identified **447 distinct fields** across the four principal retained families:

- `team_match`
- `player_match`
- `player_season`
- `squad`

A further review found **325 uncatalogued fields** in that current retained universe. Those fields have now been reviewed for source presence, preliminary semantic disposition, and navigation taxonomy.

## What the current upstream scraper drops

The FPL bootstrap audit established:

- **109** player (`element`) fields observed in upstream bootstrap payloads.
- **22** team fields observed in upstream bootstrap payloads.
- **77** player fields not retained by the upstream CSV scraper.
- **18** team fields not retained by the upstream CSV scraper.
- Fixture fields explicitly dropped by the upstream scraper:
  - `stats`
  - `pulse_id`

Therefore the current published CSV layer is demonstrably smaller than the FPL API surface.

Examples of upstream player fields not currently retained include:

- `birth_date`
- `chance_of_playing_next_round`
- `chance_of_playing_this_round`
- `clean_sheets_per_90`
- `defensive_contribution_per_90`
- `expected_assists_per_90`
- `expected_goal_involvements_per_90`
- `expected_goals_conceded_per_90`
- `expected_goals_per_90`
- `form`
- `points_per_game`
- `selected_by_percent`
- `starts_per_90`
- `status`
- `team_join_date`
- rank/ranking fields
- pricing/value fields
- news/scouting fields
- positional/order fields

Examples of upstream team fields not currently retained include:

- `draw`
- `loss`
- `played`
- `points`
- `position`
- `strength`
- home/away attack and defence strengths
- `team_division`
- `unavailable`
- `win`

## Upstream Premier League / PulseLive / SDP resource families established

The broader source ecosystem has been shown to expose or historically expose the following resource families:

### Competition and season

- competitions
- seasons / competition seasons
- season structure / phases
- matchweeks
- awards / Player of the Match-type information

### Clubs and teams

- competition teams
- season teams
- team metadata
- stadium / ground
- squads
- team form
- aggregate team statistics
- next fixture
- season/team staff (`/staff` historical resource is established)

### Standings

- overall standings
- home standings
- away standings
- position
- played
- wins / draws / losses
- goals for / against
- points
- starting-position style metadata where exposed

### Fixtures and matches

- fixture identity
- competition / season
- phase / matchweek
- kickoff and timezone
- ground / venue
- attendance
- result type
- half-time and full-time scores
- cards
- match period / clock data

### Match centre

- goals
- cards
- substitutions
- penalties / other event types where exposed
- lineups
- formations
- substitutions and player state changes
- officials
- commentary
- match event objects
- approximately 200 granular team-match statistics per side in the current SDP surface

### Player resources

- season player directories
- player bio/profile
- season-specific player information
- career history / club and season spells
- season statistics
- career statistics
- player-match statistics
- player metadata / external references

### Broadcast and content

- broadcasting schedules / broadcasting events
- editorial content resources
- articles
- video
- photo / image references
- playlists
- audio / related media references
- promotional/content metadata where exposed

### Static resources

- club crests/badges
- player images
- configuration/static metadata

## Current confirmed examples of richer source information

### FPL side

The FPL scraper wraps:

- `bootstrap-static/`
- `fixtures/`
- `element-summary/{player_id}/`

The expensive per-player `element-summary` payload is disk-cached by the upstream repository, then shaped into CSVs. The player shaping step retains a selected subset of fields and adds join/identity fields.

### Historical PL side

The historical team-event CSVs already contain fields such as:

- `attendance`
- `venue`
- `ground`
- `opponent`
- `opponent_id`
- scores/results
- xG/xA-related fields
- large event-stat surface

Squad CSVs contain biographical fields such as:

- `playerId`
- `displayName`
- `firstName`
- `lastName`
- `shirtNumber`
- `position`
- `preferredFoot`
- `nationality`
- `isoCode`
- `birthDate`
- `birthCountry`
- `age`
- `height_cm`
- `weight_kg`
- `joinDate`
- `onLoan`

## Unresolved / not yet conclusively established

These should remain explicitly unresolved until a concrete upstream resource or evidence path is identified:

- direct current manager endpoint beyond the historical team-season `staff` resource
- direct injury-history feed
- direct transfer-history endpoint

This does **not** mean these capabilities are impossible. Injury-related availability may be derivable from lineups, appearances, squad state and chronology, but injury classification must not be inferred without supporting evidence.

## Variable-universe policy

FRL should not define its universe by whichever fields a downstream scraper happens to retain.

The target model is:

`upstream source -> discovery -> audit -> local preservation -> relationship layer -> semantic interpretation -> taxonomy -> database -> UI/research`

The intended principle is:

> **Discover everything, preserve everything practical, classify everything, and exclude only deliberately with a documented reason.**

## Local preservation rule

Anything FRL deliberately retains from an upstream source must have a local, versioned copy.

- Tabular source data: preserve as CSV where practical.
- Nested / structured source payloads: preserve raw JSON or equivalent raw payloads as well as any flattened CSV representation needed for analysis.
- Research output must not depend on hitting the upstream API on every application refresh.

The local archive is a preservation layer, not an alternative source of truth. Source provenance must remain attached to preserved data.

## Taxonomy direction

The FRL navigation taxonomy is intended to cover the **entire source universe**, not merely the currently uncatalogued 325 fields.

Current broad categories include:

- Identity & Context
- Playing Time
- Shooting & Finishing
- Chance Creation
- Passing & Distribution
- Crossing & Set Pieces
- Dribbling & Carrying
- Possession & Ball Security
- Duels & Aerials
- Defending
- Goalkeeping
- Discipline
- Team Attack
- Team Defence
- Tactical & Match Context
- Physical & Tracking
- Unclassified Review

The eventual UI target is inspired by:

- **Football Manager** for breadth, filtering, conditions and searchability.
- **FBref** for statistical taxonomy and grouped presentation.
- **FotMob** for profile/page UX and compact visual presentation.

## Relationship / identity status

All relationship work remains fail-closed.

- deterministic verified relationships may be promoted;
- missing / ambiguous / unavailable relationships remain unresolved;
- player-ID overlap is a namespace diagnostic, not an identity decision;
- source availability/schema differences are not treated as identity failures.

## Commercial-rights status

Commercial rights are tracked separately from technical availability and semantic understanding.

Current checkpoint: **0% of the third-party Premier League / FPL / Opta-derived universe has been verified as commercially cleared for FRL redistribution/use**.

This is not a statement that licensing is impossible. It means a commercial redistribution right has not yet been verified for the relevant data at this checkpoint.

The intended rights categories are:

- commercially cleared now
- licence / permission required
- rights unclear / requires legal review
- FRL-original / independently derived

Technical accessibility must never be treated as proof of commercial permission.

## What is frozen at this checkpoint

This checkpoint records the discovery state as of **2026-08-22** and should be treated as the resumption baseline for the next sessions.

Next substantive phase: complete the master upstream endpoint/field inventory, then make explicit retain/exclude decisions for the full discovered universe and implement local preservation for retained source families.
