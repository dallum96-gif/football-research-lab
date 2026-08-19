# Football Research Laboratory — Complete Player-Match Evidence Build Contract

**Status:** Active implementation contract  
**Date:** 19 August 2026

## Purpose

Build a backend player-match evidence layer from the approved `Premier-League-Stats`
source without changing the canonical fixture identity layer or prematurely shaping
the data for the GUI.

## Canonical grain

The retained evidence is one source-player row attached to:

```text
(season, fixture_id, source player-match matchId, source player ID)
```

The FRL canonical Player–Fixture relationship remains:

```text
(season, fixture_id, canonical player identity)
```

A source player ID must not be silently promoted to a longitudinal FRL player identity.
Where a verified player identity is not yet established, retain the source player
ID and source name/position as evidence and leave canonical identity unresolved.

## Source selection

Use only the direct seasonal files:

```text
pl_stats/<club>/players_match_stats/<season>_players_match_stats.csv
```

Do **not** recursively ingest:

```text
players_match_stats/by_position/...
```

Those are partitioned/organisational copies of the player-match evidence and can
duplicate the underlying rows.

## Fixture resolution

Reuse the established:

```text
match_stats.fixture_source_match()
```

mechanism and the verified team identity registry.

The player-match source `matchId` is a separate namespace from the `events_stats`
`matchId`. The fixture is therefore resolved through verified home/away source-team
identity rather than numeric ID coincidence.

Gameweek is metadata, not the final fixture identity.

## Retention rule

The backend evidence layer retains **every source-native player-match field** present
in the source file for the relevant season. It must not be reduced to today's preferred
metrics.

FRL-added columns are limited to relationship/provenance/interpretation fields such as:

- canonical season and fixture ID;
- resolved player-match source ID;
- source player ID;
- source team ID;
- participation classification;
- source-file provenance.

## Participation classification

Where source semantics support it:

```text
substitute=False + minutesPlayed > 0  -> starting
substitute=True  + minutesPlayed > 0  -> sub_in
substitute=True  + minutesPlayed = 0  -> bench
```

Any other state is `unknown` rather than inferred.

This provides the backend required for future fixture views of:

- starting XI;
- used substitutes;
- unused substitutes.

It does **not** infer injury, suspension or another absence reason from non-participation.

## Known fixture exception

The documented 2019-20 Manchester City v Arsenal fixture (`fixture_id=275`) remains a
known provenance-aware correction case. The batch builder records it as
`KNOWN_EXCEPTION` and never fabricates a player-match mapping.

All other unresolved, ambiguous, empty or duplicate states are failures of the batch
quality gate.

## Output

The batch builder writes:

```text
data/player_match_evidence.csv
data/player_match_evidence_build_audit.csv
```

The evidence file is written through a temporary file and atomically promoted with
`os.replace()` so an incomplete batch does not overwrite the last good output.

## Validation requirement

Before promotion, validate:

- canonical fixture coverage;
- source fixture uniqueness;
- one source player row per `(fixture, source player, source match)`;
- absence of partition duplicates;
- participation classification;
- preservation of source-native columns;
- known exception state;
- no unexplained unresolved fixtures.

The existing 26/26 research baseline and project-health gate remain separate mandatory
controls.
