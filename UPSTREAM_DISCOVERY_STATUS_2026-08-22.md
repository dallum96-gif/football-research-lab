# FRL Upstream Discovery Status — 2026-08-22

This document records the latest discovery wave and prevents unproven capabilities from being mistaken for confirmed source resources.

## Confirmed source resources

### Historical / legacy Premier League-PulseLive
- competitions
- competition seasons
- season/team structure
- team-season staff (`/football/teams/{team_id}/compseasons/{season_id}/staff`)
- player history (`/football/players/{player_id}/history`)
- broadcasting schedule for fixtures
- historical match/team/player datasets represented in the Imadeddine archive

### Current Premier League SDP / website surfaces
- standings
- matches / fixtures / results
- matchweek and phase context
- venue / ground
- attendance
- lineups
- formations
- substitutions
- match events
- officials
- commentary
- granular match statistics
- player directories / profiles
- player season and career statistics
- team metadata / squads / form / aggregate statistics
- awards and season structure
- content / broadcast / static resource families

### FPL API surfaces
- bootstrap-static
- fixtures
- element-summary
- live gameweek data
- gameweek status
- manager profile
- manager history
- manager transfers
- manager gameweek picks
- classic league standings
- H2H league matches
- dream team
- set-piece notes
- most-valuable-team statistics
- league cup status

## Confirmed richer but not fully retained by current FRL CSV layer

- FPL bootstrap player fields not retained by upstream CSV export: 77 fields observed in the audit
- FPL bootstrap team fields not retained by upstream CSV export: 18 fields observed in the audit
- FPL fixture `stats` object is explicitly dropped by the upstream scraper
- FPL fixture `pulse_id` is explicitly dropped by the upstream scraper

## Availability / injury discovery

Confirmed FPL player availability signals exist in the bootstrap player universe, including:
- `status`
- `chance_of_playing_this_round`
- `chance_of_playing_next_round`
- `news`
- related availability/context fields

These provide a genuine availability signal but do not constitute a complete historical Premier League injury ledger.

Historical Premier League squad/match chronology also supports a derivable player-availability / games-missed model from:
- squad participation
- lineups
- appearances/minutes
- substitutions
- match chronology
- career / club spells

Injury classification must remain evidence-backed rather than inferred from every absence.

## Shot-level / shot-map status

Third-party Opta-derived products expose shot-level coordinates, xG/xGOT, outcome, player and situation data.

However, no direct public Premier League/PulseLive shot-map endpoint has yet been conclusively established from the audited Premier League API surfaces.

Status: `NOT_YET_ESTABLISHED_SOURCE_PATH`

Do not promote shot maps into the Premier League/PulseLive source registry merely because Opta-derived products contain them.

## Transfer-history status

FPL manager transfer history is confirmed.

A direct Premier League/PulseLive player transfer-history endpoint has not yet been conclusively established in the current discovery ladder.

Status: `NOT_YET_ESTABLISHED_SOURCE_PATH`

Player club/season history is established and can support transfer-like chronology, but transfer semantics must not be inferred where explicit transfer evidence is absent.

## Manager status

Historical team-season staff is confirmed through the legacy PulseLive staff resource.

A complete current Premier League manager-history endpoint separate from staff has not yet been conclusively established.

Status: `ESTABLISHED_STAFF_RESOURCE; MANAGER_HISTORY_ENDPOINT_NOT_YET_PROVEN`

## Commentary status

Match commentary is confirmed as a first-class match resource in the current Premier League ecosystem.

Commentary/event objects can contain timestamps, event types, text descriptions and player references. This should be treated as an event-level dataset rather than a simple match field.

## Important discovery rule

The existence of a metric or resource in:
- an Opta-derived third-party product,
- another football API,
- historical documentation, or
- a downstream CSV

does not by itself prove that the current Premier League/PulseLive API exposes that resource directly.

The ladder therefore records source provenance and confidence separately.

## Commercial status

Technical availability remains separate from commercial rights. No third-party Premier League/FPL/Opta-derived dataset has yet been verified as commercially cleared for FRL redistribution/use at this checkpoint.

## Current terminal categories

Every discovery branch should eventually terminate in one of:
- `ESTABLISHED_AND_LOCALLY_CAPTURABLE`
- `ESTABLISHED_UPSTREAM_NOT_YET_CAPTURED`
- `DERIVABLE_FROM_ESTABLISHED_EVIDENCE`
- `NOT_YET_ESTABLISHED_SOURCE_PATH`
- `KNOWN_BUT_ACCESS_RESTRICTED`
- `RIGHTS_UNRESOLVED`

This status layer is intentionally conservative and is the basis for the next discovery waves.
