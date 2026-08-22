# FRL Master Upstream Source Universe

## Status

Discovery baseline established 2026-08-22. This document consolidates the current known source/resource universe and distinguishes direct CSV coverage from upstream capabilities.

## Source lineage

`Official FPL API` + `Premier League / PulseLive / SDP sources`
→ `imadeddine-belkat/Premier-League-Stats` published extraction
→ `FRL local preservation`
→ `FRL relationship / semantic / taxonomy layers`
→ `FRL database / research / UI`

The Imadeddine repository is an extraction layer, not the ceiling of the source universe.

## Current retained FRL field universe

447 distinct fields have been identified across the four principal retained source families:

- team_match
- player_match
- player_season
- squad

Within that retained universe, 325 fields required uncatalogued semantic review. The review and navigation taxonomy are now established as working layers; semantic/canonical promotion remains fail-closed.

## Upstream FPL universe

The upstream repository observes:

- 109 bootstrap player (`element`) fields
- 22 bootstrap team fields

The upstream scraper does not retain:

- 77 player fields
- 18 team fields
- fixture `stats`
- fixture `pulse_id`

Examples of currently identified upstream-only player candidates include form, points-per-game, per-90 metrics, availability/chance-of-playing fields, pricing/value fields, ranking fields, selection/transfer fields, status, news/scouting fields, positional/order fields and team-join metadata.

These remain candidate variables for FRL review rather than automatic promotion.

## Historical Premier League / PulseLive / SDP resource families

### Competition / season

- competitions
- competition seasons
- season structure / phases
- matchweeks
- season awards / Player of the Match-type records

### Clubs / teams

- competition teams
- season teams
- team metadata
- stadium / ground
- squads
- team form
- aggregate team statistics
- next fixture
- historical season/team staff (`/staff` resource established)

### Standings

- overall standings
- home standings
- away standings
- position
- played
- wins / draws / losses
- goals for / against
- points
- starting-position metadata where exposed

### Matches / fixtures

- fixture identity
- competition / season
- phase / matchweek
- kickoff / timezone
- ground / venue
- attendance
- result type
- half-time / full-time scores
- cards
- period / clock information

### Match centre / events

- goals
- cards
- substitutions
- penalties / other event types where exposed
- lineups
- formations
- substitutions / player state changes
- officials
- commentary
- timestamped event/commentary objects
- approximately 200 granular team-match statistics per side in the current SDP surface

### Player resources

- season player directories
- player biography/profile
- season-specific player information
- historical club / season career spells
- season statistics
- career statistics
- player-match statistics
- player metadata / external references

### Broadcast / media / content

- broadcasting schedules / broadcast events
- editorial content
- articles
- video
- photo/image references
- playlists
- audio / related media
- promotional metadata where exposed

### Static resources

- club badges / crests
- player images
- configuration / static metadata

## Confirmed source examples

Historical PL event CSVs already expose fields including attendance, venue/ground, opponent/opponent_id, result/score fields and a large event-stat surface.

Squad CSVs expose playerId, displayName, firstName, lastName, shirtNumber, position, preferredFoot, nationality, isoCode, birthDate, birthCountry, age, height_cm, weight_kg, joinDate and onLoan.

The FPL player pipeline wraps `bootstrap-static/`, `fixtures/` and `element-summary/{player_id}/`, with local disk caching for expensive player-summary payloads.

## Known gaps / unresolved capabilities

These are not treated as absent; they are simply not yet established to the required evidence standard:

- direct current manager endpoint beyond the established historical season/team `staff` resource
- direct injury-history feed
- direct transfer-history endpoint

Potentially derivable capabilities must remain distinct from direct source fields. For example, player availability / matches missed can be reconstructed from lineups, appearances, squad state and chronology, but an absence must not be labelled as an injury without supporting evidence.

## Variable-universe policy

FRL is intended to represent the widest defensible source-variable universe, not only the columns exported by a downstream scraper.

Principle:

> Discover everything. Audit everything. Preserve everything practical. Classify everything. Exclude only deliberately, with a documented reason.

A source variable can be preserved while remaining semantically unresolved, commercially restricted, or unavailable to the canonical research layer.

## Local preservation policy

Anything FRL deliberately retains from upstream gets a local, versioned copy.

- tabular data: CSV where practical
- nested/structured payloads: raw JSON/equivalent raw payload plus flattened analytical representations where useful
- research/UI layers query local data rather than live upstream APIs on every refresh
- source provenance and acquisition metadata remain attached to preserved data

## Taxonomy target

The navigation taxonomy covers the whole source universe, not merely the current 325-field review backlog.

Broad working categories:

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

UI references:

- Football Manager: breadth, conditions, filters, saved searches
- FBref: statistical grouping and taxonomy
- FotMob: profile UX and compact visual presentation

## Relationship / identity policy

Identity relationships are fail-closed:

- deterministic verified relationships may be promoted
- missing / ambiguous / unavailable relationships remain unresolved
- player-ID overlap is a namespace diagnostic
- source availability/schema differences are not identity failures

## Commercial rights policy

Commercial viability is tracked separately from technical access and semantic validity.

At this checkpoint, no third-party Premier League / FPL / Opta-derived universe has been verified as commercially cleared for FRL redistribution/use.

Rights categories:

- commercially cleared now
- licence / permission required
- rights unclear / legal review
- FRL-original / independently derived

Technical accessibility must never be treated as commercial permission.

## Next phase

1. Turn the resource families above into an explicit endpoint/field registry.
2. Identify which resources/fields are already locally preserved.
3. Identify upstream-only candidates and evaluate them.
4. Assign every retained candidate a taxonomy placement, grain, coverage and provenance record.
5. Add rights status to each candidate.
6. Implement local preservation adapters for retained upstream resources.
7. Only then move into database schema expansion and UI navigation over the complete universe.
