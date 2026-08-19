# Football Research Laboratory — Backend Data Layers V1

## Purpose

Complete the approved-source backend before further GUI work. The GUI may expose only a subset of these layers; the backend preserves the richer evidence universe.

## Approved source boundary

Until the Laboratory expands beyond 2008-09 or adds another league/competition, football evidence may originate only from `imadeddine-belkat/Premier-League-Stats` and the upstream feeds used by that repository. FRL-created artefacts may transform, canonicalise, reconcile or document that evidence but may not add an independent provider.

## Evidence layers

### Canonical fixture
`(season, fixture_id)` remains the FRL fixture identity.

### Complete fixture-team evidence
`data/fixture_team_evidence.csv`

Grain: `(season, fixture_id, venue)`.
Preserves every source-native `events_stats` field available for the resolved home/away team rows. Existing `data/fixture_match_stats.csv` remains as a compatibility/curated layer.

### Complete player-match evidence
`data/player_match_evidence.csv`

Grain: one source player-match row attached to `(season, fixture_id)`.
Preserves every source-native `players_match_stats` field plus FRL relationship/provenance fields. Participation classification distinguishes `starting`, `sub_in`, and `bench`.

### Player-season evidence
`data/player_season_evidence.csv`

Grain: upstream player-season row. Preserves all source-native `players_stats` fields. Source player IDs remain source-local until a verified longitudinal player identity exists.

### Squad / registration evidence
`data/squad_evidence.csv`

Grain: source squad player membership for a club-season. Preserves all source-native squad fields including position, shirt number, nationality, birth data, join date and loan status where supplied.

### FPL player-gameweek evidence
`data/fpl_player_gw_evidence.csv`

Grain: upstream FPL player/gameweek row. Preserves the complete upstream FPL CSV schema. FPL identifiers remain a separate namespace from PL/PulseLive player IDs.

### FPL fixture evidence
`data/fpl_fixture_evidence.csv`

Grain: upstream FPL fixture record. Preserves complete FPL fixture fields. FPL fixture IDs are source-local evidence, not FRL fixture identity.

### Existing event/goal evidence
Existing canonical/event layers remain authoritative for their established contracts and are not replaced by the new evidence layers.

## Research/navigation graph

```text
FIXTURE
├── canonical identity / result
├── complete team evidence
├── player-match evidence
├── goal/event evidence
└── future additive manager / availability evidence

PLAYER
├── longitudinal identity when verified
├── squad / registration evidence
├── player-season evidence
├── fixture participation + player-match evidence
└── separate FPL player-gameweek evidence

TEAM
├── longitudinal / season identity
├── season context derived from evidence
└── fixture-team evidence
```

## Deliberately absent / parked

Manager data is reserved for a future additive layer because the approved source currently does not provide a defensible historical fixture-level manager dataset.

Historical injury/suspension/absence reasons are also not fabricated from non-selection. The player-match layer can establish observed participation states; absence reasons remain unavailable unless supplied by the approved source ecosystem.

## Completion standard before GUI-focused work

The backend should have reusable build/access seams for every evidence layer above, with explicit source provenance, fail-closed identity handling, no duplicate upstream materialisations, and season-level validation. After that point, GUI work should consume the backend rather than add new source-specific data plumbing.
