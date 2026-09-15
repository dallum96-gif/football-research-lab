# FRL Player Profile Positional Radars V1

**Date:** 15 September 2026  
**Checkpoint:** `PLAYER_PROFILE_POSITIONAL_RADARS_V1`  
**Status:** Validated draft integration candidate; not stable `main`

## Objective

Every current Player Profile exposes an analytical six-axis comparison appropriate to the player's broad position class: **GKP, DEF, MID or FWD**. The approved Player Profile composition remains the visual reference; the analytical rail is position-aware.

Player Profile is a **current-state surface**. Career/previous-season exploration remains available through the separate History view, but the hero rail does not expose a season selector.

## Position templates

### Goalkeeper — `GKP_PROFILE_V1`

- Shot stopping — `(expectedGoalsOnTargetConceded - goalsConceded) / timePlayed * 90`
- Save rate — `savesMade / (savesMade + goalsConceded)`
- Save volume — `savesMade / timePlayed * 90`
- Claiming — `(catches + punches) / timePlayed * 90`
- Smothering — `goalkeeperSmother / timePlayed * 90`
- Distribution — `gkSuccessfulDistribution / (gkSuccessfulDistribution + gkUnsuccessfulDistribution)`

### Defender — `DEF_PROFILE_V1`

- Aerial duels — `aerialDuelsWon / aerialDuels`
- Tackling — `totalTackles / timePlayed * 90`
- Interceptions — `interceptions / timePlayed * 90`
- Clearances — `totalClearances / timePlayed * 90`
- Recoveries — `recoveries / timePlayed * 90`
- Progression — `forwardPasses / timePlayed * 90`

The defender Tackling axis deliberately uses **total tackles / 90**, not tackles won / 90. This is a direct tackling-volume dimension and avoids treating a blank `tacklesWon` field as either zero or proof that no tackling evidence exists when `totalTackles` is observed.

### Midfielder — `MID_PROFILE_V1`

- Goal threat — `expectedGoals / timePlayed * 90`
- Chance creation — `expectedAssists / timePlayed * 90`
- Advanced passing — `successfulPassesOppositionHalf / timePlayed * 90`
- Forward passing — `forwardPasses / timePlayed * 90`
- Recoveries — `recoveries / timePlayed * 90`
- Ball winning — `tacklesWon / timePlayed * 90`

### Forward — `FWD_PROFILE_V1`

- Goal threat — `expectedGoals / timePlayed * 90`
- Scoring — `goals / timePlayed * 90`
- Chance creation — `expectedAssists / timePlayed * 90`
- Shot volume — `totalShots / timePlayed * 90`
- Box presence — `totalTouchesInOppositionBox / timePlayed * 90`
- Shot accuracy — `shotsOnTargetIncGoals / totalShots`

Shot accuracy replaces the initial `successfulDribbles / 90` **1v1 threat** proposal. A combined FWD population contains central strikers as well as wide forwards; shot accuracy is more broadly applicable to the position class and is derived only from same-row Player-Season shot evidence.

## Source and denominator rules

All axes use `PLAYER_PROFILE_SOURCE_STATS_V1`, materialised from pinned Player-Season release:

`imadeddine-belkat/Premier-League-Stats@115d889df4e2efab5e7c1d8ca0f3ca86ecfd2ae6`

- Per-90 axes use the same row's `timePlayed`.
- Ratios use numerator and denominator from the same Player-Season row.
- Source blanks remain unavailable rather than becoming zero.
- Qualification remains 33% of currently available league minutes for the selected living-season state.
- Comparisons remain within the same broad FPL position classification.

The materialised metadata is schema `1.2.0`. The added forward shot-accuracy route is explicitly `shotsOnTargetIncGoals` → `shots_on_target`; 2026/27 contains 140 observed rows for that field and 204 observed rows for `totalShots`.

## Current-state product rule

The Profile hero is about **now**. It no longer offers a season selector. The History tab remains the deliberate route for captured prior seasons and preserves season-specific route IDs where they differ.

Cross-season identity governance remains necessary even though season switching is no longer exposed in the hero.

## Validation

The authoritative feature run from commit `31c98d6d2988a9a6a44137e0a367040b167cfe8a` passed end-to-end. GitHub Actions then materialised the refreshed governed source evidence at `a2e3ecd`.

Validated gates:

- pinned source checkout: PASS;
- source and biography materialisation: PASS;
- Python compilation: PASS;
- approved Profile CSS/portrait composition guard: PASS;
- focused Profile regression suite: **29 passed**;
- position-aware acceptance matrix: PASS;
- current Ødegaard MID: **6/6**, 3 appearances / 3 starts / 224 minutes;
- current Gabriel DEF: **6/6**;
- current David Raya GKP: **6/6**;
- current Kai Havertz FWD: **6/6**;
- low-minute Eze threshold fail-closed case: PASS;
- historical Ødegaard route continuity (`2024-25/13`): PASS;
- hero season selector absent / History retained: PASS;
- TypeScript: PASS;
- Next.js production build: PASS;
- documentation sync: PASS.

The production build is green. The screenshots from local development still show a red Next **“1 Issue”** indicator; that development-runtime issue remains a follow-up and is not silently treated as resolved by the production build.

## Integration posture

Draft PR #54 targets `design/bet-builder-reference-v1`; stable `main` is unchanged. Daniel's Windows working state has been inspected, externally safety-snapshotted and reconciled in an isolated worktree without overwriting the original local tree.

The target/reference branch still has a tracked API integration defect: `api/frl_api.py` imports `team_records_materialization` while the module is absent from tracked GitHub. Daniel's local tree contains an untracked copy, so that issue requires deliberate reconciliation outside the Player Profile milestone.

## Definition of Done

V1 is complete at feature-branch level because:

1. representative qualified GKP, DEF, MID and FWD players each return a complete six-axis position-specific comparison;
2. current Ødegaard remains 3 / 3 / 224 at the pinned checkpoint;
3. no source blank is coerced to zero;
4. the approved Player Profile CSS/portrait composition is unchanged;
5. the hero season selector is absent while History remains available;
6. regression, acceptance, TypeScript, production-build and documentation gates pass.

Final integration remains intentionally separate from feature completion.