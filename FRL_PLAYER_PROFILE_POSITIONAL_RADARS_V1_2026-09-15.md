# FRL Player Profile Positional Radars V1

**Date:** 15 September 2026  
**Checkpoint:** `PLAYER_PROFILE_POSITIONAL_RADARS_V1`  
**Status:** Active feature-branch milestone; not stable `main`

## Objective

Every current Player Profile should expose an analytical six-axis comparison appropriate to the player's broad position class: **GKP, DEF, MID or FWD**. The approved Player Profile composition remains unchanged; the analytical rail becomes position-aware.

Player Profile is a **current-state surface**. Career/previous-season exploration remains available through the separate History view, but the hero rail does not expose a season selector.

## Position templates

### Goalkeeper

- Shot stopping — `(expectedGoalsOnTargetConceded - goalsConceded) / timePlayed * 90`
- Save rate — `savesMade / (savesMade + goalsConceded)`
- Save volume — `savesMade / timePlayed * 90`
- Claiming — `(catches + punches) / timePlayed * 90`
- Smothering — `goalkeeperSmother / timePlayed * 90`
- Distribution — `gkSuccessfulDistribution / (gkSuccessfulDistribution + gkUnsuccessfulDistribution)`

### Defender

- Aerial duels — `aerialDuelsWon / aerialDuels`
- Tackling — `totalTackles / timePlayed * 90`
- Interceptions — `interceptions / timePlayed * 90`
- Clearances — `totalClearances / timePlayed * 90`
- Recoveries — `recoveries / timePlayed * 90`
- Progression — `forwardPasses / timePlayed * 90`

The defender Tackling axis deliberately uses **total tackles / 90**, not tackle-success percentage. This gives a semantically direct tackling-volume dimension and avoids creating an unavailable axis merely because `tacklesWon` is blank while `totalTackles` is observed.

### Midfielder

- Goal threat — `expectedGoals / timePlayed * 90`
- Chance creation — `expectedAssists / timePlayed * 90`
- Advanced passing — `successfulPassesOppositionHalf / timePlayed * 90`
- Forward passing — `forwardPasses / timePlayed * 90`
- Recoveries — `recoveries / timePlayed * 90`
- Ball winning — `tacklesWon / timePlayed * 90`

### Forward

- Goal threat — `expectedGoals / timePlayed * 90`
- Scoring — `goals / timePlayed * 90`
- Chance creation — `expectedAssists / timePlayed * 90`
- Shot volume — `totalShots / timePlayed * 90`
- Box presence — `totalTouchesInOppositionBox / timePlayed * 90`
- Shot accuracy — `shotsOnTargetIncGoals / totalShots`

Shot accuracy replaces the earlier `successfulDribbles / 90` **1v1 threat** proposal. A combined FWD population contains central strikers as well as wide forwards; shot accuracy is more broadly applicable to the position class and is derived only from same-row Player-Season shot evidence.

## Source and denominator rules

All axes use `PLAYER_PROFILE_SOURCE_STATS_V1`, materialised from the pinned Player-Season release `imadeddine-belkat/Premier-League-Stats@115d889df4e2efab5e7c1d8ca0f3ca86ecfd2ae6`.

- Per-90 axes use the same row's `timePlayed`.
- Ratios use numerator and denominator from the same Player-Season row.
- Source blanks remain unavailable rather than becoming zero.
- Qualification remains 33% of currently available league minutes for the selected living-season state.
- Comparisons remain within the same broad FPL position classification.

## Product rule

The Profile hero is about **now**. It no longer offers a season selector. The History tab remains the deliberate route for captured prior seasons and preserves season-specific route IDs where they differ.

## Definition of Done

V1 is complete only when:

1. representative qualified GKP, DEF, MID and FWD players each return a six-axis position-specific comparison;
2. current Ødegaard remains 3 appearances / 3 starts / 224 Player-Season minutes at the pinned checkpoint;
3. no source blank is coerced to zero;
4. the approved Player Profile CSS/portrait composition is unchanged;
5. the hero season selector is absent while History remains available;
6. Python regressions, acceptance matrix, TypeScript, production build and documentation-sync gates pass.

## Integration posture

This remains a draft integration candidate into `design/bet-builder-reference-v1`. Stable `main` is unchanged. Daniel's protected Windows working state remains separate from tracked GitHub until deliberately reconciled.