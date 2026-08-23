# FRL Discovery Closure — 2026-08-22

## Scope
This closes the current open-ended upstream discovery phase. Discovery has been taken as far as the currently traceable FRL lineage and adjacent documented source surfaces allow. The remaining items are explicitly classified rather than silently assumed absent.

## Source ladder traversed
1. FRL local preserved CSV universe.
2. `imadeddine-belkat/Premier-League-Stats` published extraction layer.
3. Official FPL API surface beyond the three endpoints used by that scraper.
4. Current Premier League / PulseLive SDP football-data surface.
5. Premier League content / broadcasting / static resource surfaces.
6. Legacy PulseLive resources and historical endpoint documentation.
7. Adjacent independent upstream documentation / data products used only to test whether a capability exists elsewhere; not treated as proof of Premier League-source availability.

## Confirmed resource families
- competitions, seasons, structures, phases, matchweeks and awards
- clubs / teams / season teams
- stadium / ground / venue
- squads and biographical player metadata
- season player directories
- player career / club-season history
- player season and career statistics
- player-match statistics
- team form and aggregate statistics
- overall/home/away standings
- fixtures/results, kickoff/timezone, attendance and scores
- lineups, formations and substitutions
- match events including goals/cards/substitutions and timestamps
- match officials
- match commentary / textstream
- large granular team-match statistical surfaces
- season/team staff resource
- broadcasting schedules / events
- editorial/content/media/static resources
- FPL manager profiles, histories, transfers, picks and league/H2H resources
- FPL live gameweek status, dream-team and set-piece resources
- FPL bootstrap player/team fields beyond the downstream CSV selection
- FPL fixture nested `stats` object, which is explicitly dropped by the upstream CSV scraper

## Club manager requirement
FRL specifically wants **club manager/head-coach history**, not merely generic staff.

The historical PulseLive team-season `staff` resource is established. Preserve the staff resource broadly, then derive a canonical manager/head-coach relationship where role/title and tenure evidence support it.

Target relationship:
`club -> date/season -> manager/head coach -> tenure interval`

## Field-universe findings
- Current retained FRL source-field universe: **447 distinct fields** across the established principal families.
- Current retained-universe review: **325 uncatalogued fields** reviewed and assigned preliminary taxonomy/disposition without automatic semantic promotion.
- FPL upstream bootstrap: **109 element fields**, **22 team fields** observed.
- Upstream FPL fields not retained by Imadeddine scraper: **77 element fields**, **18 team fields**.
- FPL fixture fields explicitly dropped by scraper: `stats`, `pulse_id`.
- Legacy/current Premier League player-stat vocabularies are broader than the current 447-field CSV universe; historical documentation exposes 150+ player stat attributes and granular location buckets.

## Terminal statuses for difficult branches
### Shot-level / shot-map data
**STATUS: NOT CONFIRMED AT PUBLIC PL/PULSELIVE ENDPOINT BOUNDARY.**

External Opta-derived products prove that shot-level XY coordinates, xG, xGOT, outcome, body part and situation exist in football-data products, but this is not sufficient to claim a public Premier League/PulseLive shot-event endpoint. Historical PulseLive player statistics do expose granular shot-location buckets. FRL should preserve those confirmed location metrics and keep true XY shot maps as an upstream discovery candidate until a direct source path is proven.

### Direct Premier League injury-history feed
**STATUS: NOT ESTABLISHED.**

No reliable direct PL/PulseLive historical injury ledger was established. Availability can be derived from lineups, appearances, squad state, chronology and (on FPL side) explicit availability/status fields. Injury classification must remain evidence-backed and fail-closed.

### Direct Premier League transfer-history feed
**STATUS: NOT ESTABLISHED.**

Player club/season history is established and can support transfer/club-spell reconstruction. FPL manager transfer history is established but is a different domain. Do not infer a dedicated PL transfer endpoint without direct evidence.

### Club manager/head-coach history
**STATUS: ESTABLISHED VIA TEAM-SEASON STAFF RESOURCE; CANONICAL MANAGER RELATIONSHIP STILL TO BE MODELED.**

### Commentary
**STATUS: ESTABLISHED.**

Legacy/current match textstream/commentary resources expose timestamped event/commentary content. Preserve commentary as a source/event family even if some fields never become canonical statistical variables.

## Preservation rule
Anything FRL deliberately retains from upstream gets a local, versioned copy.

- Tabular data: CSV where practical.
- Nested/raw resources: raw JSON or equivalent source payload plus flattened analytical representations where useful.
- The finished FRL application should query the local preserved layer/database, not depend on live API requests on every refresh.

## Taxonomy rule
Classify the entire discovered universe, not just the current 325 uncatalogued fields. Taxonomy is separate from semantic approval and separate from commercial rights.

Design references:
- Football Manager: breadth, conditions, filters and searchability.
- FBref: statistical groupings and taxonomy.
- FotMob: player/team/match profile presentation and UX.

## Rights / commercial status
Technical availability is not commercial permission.

At this closure checkpoint, **0% of the third-party Premier League / FPL / Opta-derived universe has been verified as commercially cleared for FRL redistribution/use**.

Use the rights categories:
- commercially cleared now
- licence / permission required
- rights unclear / legal review
- FRL-original / independently derived

## What is closed and what is not
The discovery *process* is now closed for the currently traceable ladder. This does NOT mean every unknown field or endpoint in the internet is impossible to find. It means every discovered branch has a terminal status and any remaining uncertainty is named explicitly.

The project can now move from open-ended discovery into:
1. master endpoint/field inventory,
2. retain/exclude decisions,
3. local preservation implementation,
4. semantic registry and taxonomy completion,
5. database design and relationship integration,
6. FM/FBref/FotMob-style UI navigation.

## Governing principle
> Discover as far upstream and as wide as reasonably possible; preserve practical source data locally; classify every discovered capability; and never convert uncertainty into a false 'does not exist' claim.
