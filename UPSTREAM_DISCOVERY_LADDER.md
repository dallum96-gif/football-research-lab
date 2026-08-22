# FRL Upstream Discovery Ladder

## Purpose

FRL must discover the widest defensible source universe before defining the limits of the database.

The discovery ladder is ordered from downstream preserved data to the highest upstream surfaces we can establish.

## Layers

### Level 1 — FRL Local Preservation

Current FRL-preserved CSV/source archive and any raw payloads already retained locally.

Status: ESTABLISHED.

### Level 2 — Imadeddine Published Extraction

`imadeddine-belkat/Premier-League-Stats`

Audit:
- retained FPL gameweek/player/team/fixture fields
- historical PL/PulseLive team-match, player-match, player-season and squad fields
- explicit fields dropped by the upstream exporter
- repository indexes and metadata

Status: ESTABLISHED.

### Level 3 — Official FPL API Surface

Discover all public endpoints and payload fields, not only the three used by the Imadeddine scraper.

Known examples:
- `bootstrap-static`
- `fixtures`
- `element-summary/{id}`
- manager/gameweek/league-related resources where publicly exposed

Status: PARTIALLY AUDITED — broader endpoint inventory required.

### Level 4 — Current Premier League SDP/PulseLive Surface

Discover all observable resources exposed by the current Premier League site, including:
- competitions / seasons / structure
- teams / squads / stadiums / form
- standings
- fixtures / matches
- lineups / formations / substitutions
- events / commentary
- officials
- player directories / season information / career history
- player and team statistics
- content / media / broadcast resources
- static resources

Status: PARTIALLY AUDITED — endpoint and payload inventory required.

### Level 5 — Premier League Content / Static APIs

Discover entity metadata and non-statistical resources:
- editorial content
- articles
- video
- images
- audio
- playlists
- broadcasts
- promotional metadata
- club/player assets
- configuration/reference resources

Status: PARTIALLY AUDITED.

### Level 6 — Legacy PulseLive Surface

Trace historical PulseLive routes separately from current SDP routes.

Known/observed examples:
- player history
- team-season staff
- broadcasting schedules
- historical competition/team/player resources

Status: PARTIALLY AUDITED.

### Level 7 — Higher-Upstream / Adjacent Sources

Only use this layer where a desired capability cannot be established within the Premier League/FPL lineage.

Candidates:
- shot-level coordinates / shot maps
- direct injury reporting
- transfer history
- other contextual or research resources

Status: DISCOVERY REQUIRED; do not silently promote third-party data into the core lineage.

## Discovery Status Rules

A capability must be classified as one of:

- ESTABLISHED: concrete source/resource and payload evidence exists.
- PARTIALLY AUDITED: source family is established but full endpoint/field coverage is not yet enumerated.
- DERIVABLE: can be reconstructed from established source evidence, with explicit provenance.
- NOT YET ESTABLISHED: requested capability has not yet been tied to a concrete source route.
- INACCESSIBLE/UNKNOWN: source may exist but cannot currently be verified through available evidence.

`NOT YET ESTABLISHED` must never be treated as `DOES NOT EXIST`.

## Inventory Contract

Every discovered resource should ultimately receive:

`source_layer -> resource/endpoint -> payload/field -> entity grain -> season coverage -> captured locally? -> preserve? -> semantic status -> taxonomy -> relationship keys -> rights status`

## Preservation Contract

Anything FRL deliberately retains from an upstream source receives a local, versioned copy.

- Structured/tabular data: CSV where practical.
- Nested source payloads: raw JSON/equivalent plus flattened analytical representations where useful.
- The finished FRL application should query local preserved data/database, not hit upstream sources on every refresh.

## Rights Contract

Technical accessibility does not imply commercial permission.

Each source/resource must separately record:
- commercial status
- licence/permission requirement
- rights uncertainty
- FRL-original/derived status

## Current Priority

1. Complete Level 3 FPL endpoint inventory.
2. Complete Level 4 current SDP endpoint inventory.
3. Complete Level 5 content/static inventory.
4. Complete Level 6 legacy PulseLive inventory.
5. Investigate Level 7 only for unresolved high-value capabilities.
6. Reconcile all discovered resources against the FRL local universe.
7. Decide explicit retain/exclude/research-only/commercial status for each item.
