# FRL Source Rights Register

**Status:** Provisional working register — not legal advice
**Purpose:** Record where FRL data comes from, how it is acquired, what reuse signal exists, and which sources require further rights/terms review before public or commercial redistribution.

## Operating rule

A public endpoint or a public GitHub repository is not, by itself, proof that unrestricted bulk reuse or redistribution is permitted. FRL should prefer sources with explicit, source-appropriate reuse terms and should preserve provenance for every source family.

Recommended acquisition preference:

1. Explicitly open/licensed downloadable dataset
2. Official API with clearly permitted automated/research use
3. Reputable provider with explicit research/reuse terms
4. Public but ambiguous endpoint/repository only after terms review

## Current / important sources

| Source | FRL use | Origin stated by source | Acquisition mode | Reuse signal | Current FRL rights status | Notes |
|---|---|---|---|---|---|---|
| `imadeddine-belkat/Premier-League-Stats` — FPL gameweek data | Player/gameweek statistics, fixtures, identity support | Official FPL API | Downloaded from public GitHub CSVs / local clone | README states MIT; referenced `LICENSE` file is currently absent/404 | **REVIEW REQUIRED** | Public GitHub availability reduces operational dependency on the API, but upstream FPL terms may still matter for underlying data. |
| `imadeddine-belkat/Premier-League-Stats` — historical `pl_stats` | Team-match metrics, player-match metrics, player-season totals, squads/bios | README states Premier League / PulseLive feeds | Downloaded from public GitHub CSVs / local clone | README states MIT; referenced `LICENSE` file is currently absent/404 | **REVIEW REQUIRED** | Repository author can license their own code/collection work, but that does not necessarily grant rights they do not own in underlying PL/Opta/PulseLive-origin data. |
| Premier League / PulseLive SDP live endpoints | Rich fixture snapshots: match metadata, event timeline, lineups, formations, managers, team stats, commentary | Premier League / PulseLive | Direct API acquisition into local immutable snapshots | Public unauthenticated endpoints; no explicit bulk-reuse licence verified by FRL | **REVIEW REQUIRED / DO NOT ASSUME REDISTRIBUTION RIGHTS** | Historical backfill is preserved locally. Do not make public/commercial redistribution decisions until terms are reviewed. |
| FRL canonical/derived datasets | Canonical fixtures, identity mappings, derived historical state, features, models | Built from FRL source evidence | Internal FRL processing | Depends on upstream source lineage | **INHERITS SOURCE DEPENDENCIES** | Derived status does not automatically remove upstream rights obligations. Preserve lineage. |

## What the GitHub-hosted Imadeddine source already provides

### FPL gameweek layer

- per-player / per-gameweek statistics;
- points, minutes, goals, assists;
- xG/xA and FPL-specific indicators where supplied;
- prices, transfers, selection and related FPL state;
- fixture lists and difficulty ratings;
- player/team indexes and join keys.

### Historical Premier League layer

The `pl_stats` archive provides:

- **team-match aggregate metrics** (`events_stats`) — roughly 180 fields per team/match, including possession, passing, zones, duels, chances, set pieces, defensive actions, touches, cards and related match statistics;
- **player-match metrics** (`players_match_stats`) — minutes, starter/substitute status, goals, assists, passing, shots, tackles, duels, carries/contests and other player-performance fields where supplied;
- **player-season totals** (`players_stats`) — season aggregate player statistics;
- **squad/bio data** — position, nationality, DOB, physical/profile fields where supplied.

Important semantic note: `events_stats` is primarily a team-match aggregate-statistics table despite its name. It is not equivalent to a chronological match event timeline.

## What the direct PulseLive historical snapshot adds

The direct fixture snapshot layer is primarily valuable for **rich match-centre evidence**, including:

- chronological goals;
- cards;
- substitutions;
- starting XI and substitutes;
- source formation;
- managers;
- match metadata such as ground/attendance where supplied;
- rich match-centre team statistics;
- commentary;
- retrieval-time source provenance.

There is substantial overlap between PulseLive `stats` and the GitHub-hosted historical team-match metrics. The strongest incremental value of the direct snapshot is therefore the timeline/lineup/formation/manager/match-centre context rather than ordinary analytical team statistics.

## Current practical distinction

### Lower operational dependency

Using an already-hosted GitHub dataset means FRL does not need to repeatedly call the upstream Premier League/FPL service to reconstruct historical analytical metrics.

### Not automatically lower rights risk

If a GitHub repository itself derived its data from Premier League / PulseLive / Opta feeds, moving the bytes through GitHub does not automatically change the underlying rights position.

Therefore FRL must distinguish:

- **distribution/acquisition channel** — GitHub, API, file download;
- **original data source** — PL/PulseLive, FPL, StatsBomb, OpenFootball, etc.;
- **licence/terms for the repository or code**;
- **licence/terms for the underlying data**.

These are separate questions.

## Future preferred sources

Where practical, future league expansion should favour sources with clear data reuse terms, for example:

- OpenFootball / explicitly public-domain or CC0 fixture-result data;
- StatsBomb Open Data under its stated open-data/attribution conditions;
- other downloadable datasets with explicit licences that clearly cover the data itself.

Before adopting any source, record:

- source name and URL;
- original provider;
- acquisition method;
- licence/terms URL;
- permitted use as understood;
- attribution requirement;
- redistribution restriction;
- commercial-use status;
- data families/variables supplied;
- seasons/competitions covered;
- acquisition date/version/checksum where appropriate.

## Immediate follow-up

1. Complete a source-by-source terms review before FRL is publicly released or commercialised.
2. Verify the intended licence status of `imadeddine-belkat/Premier-League-Stats`, including the discrepancy between the README's MIT statement and the missing `LICENSE` file.
3. Avoid new recurring direct PulseLive acquisition until the relevant terms are understood; prefer preserved historical evidence and clearly licensed sources where possible.
4. Build the forthcoming FRL Variable Capability Inventory so each variable family can be linked to both its technical provenance and its source-rights classification.
