# Player-Match Evidence — 2016/17 Validation Baseline

**Status:** Validated reference baseline
**Date:** 19 August 2026
**Branch:** `feature/complete-player-match-evidence-2026-08-19`

## Purpose

This document records the first fully validated season for the FRL player-match evidence layer. Later seasons must satisfy the same core invariants or document an explicit source-coverage/semantic difference.

## Validated results

For 2016-17, using only the approved `Premier-League-Stats` source workspace:

- 20 canonical season player-match source files were identified.
- 72 source-native player-match fields were identified.
- 84 FRL evidence fields were produced.
- 0 source-native fields were missing from the FRL evidence output.
- 0 unexpected source fields were present in the evidence output.
- 380/380 canonical fixtures resolved to a verified player-match source match.
- 13,675 unique player-match evidence rows were written.
- 0 unresolved/error fixture states remained.
- 0 duplicate player-match evidence rows remained after excluding upstream materialisation/partition copies.
- Starting players, used substitutes and unused substitutes were successfully classified from the source `substitute` and `minutesPlayed` fields.
- The known Arsenal v Liverpool 2016-17 proof fixture reproduced the expected player population, participation states, minutes, goals and assists.

## Source handling invariant

The upstream repository contains multiple materialisations of player-match data, including merged and `by_position` copies. These are not treated as separate evidence populations. The canonical FRL source scan uses the direct seasonal player-match files under each club's `players_match_stats` directory.

## Schema invariant

The FRL evidence layer must preserve every source-native player-match field. FRL relationship, participation and provenance fields may be added, but source fields must not be silently dropped, renamed away, coerced into invented values, or replaced by derived metrics.

## Identity invariant

The canonical relationship remains:

```text
(season, fixture_id, player_id)
```

Source `matchId`, `playerId`, `pl_code` and source team IDs remain source-local identifiers until reconciled through existing FRL identity contracts.

## Participation invariant

Where source semantics permit, player-match rows are classified as:

- `starting`
- `sub_in`
- `bench`

An unavailable player who has no source player-match row is not inferred to be injured, suspended or otherwise absent from the squad.

## Promotion rule

This baseline is a validation reference, not an instruction to promote the output blindly. Before broader promotion, later seasons must be audited for:

- fixture coverage;
- player-row coverage;
- duplicate/materialisation handling;
- source schema preservation;
- player/fixture identity integrity;
- participation classification;
- known historical exceptions;
- source-specific coverage differences.

Any season that differs must record why rather than silently being normalised to the 2016-17 pattern.
