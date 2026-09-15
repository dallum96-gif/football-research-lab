# Player Profile Universal Foundation V1 — 15 September 2026

**Milestone:** `PLAYER_PROFILE_UNIVERSAL_FOUNDATION_V1`  
**Status:** validated feature-branch integration candidate; not merged to the active reference branch or stable `main`  
**Feature branch:** `feat/player-profile-universal-foundation-v1`  
**Target branch:** `design/bet-builder-reference-v1`  
**Fork point:** `11a42f68cf7c4c0eab2b1ea0286cddf3337cbda3`

This is a dated checkpoint record. Current state after this date belongs in `CURRENT_WORK.md` and `data/frl_documentation_state_v1.json`.

## Objective

Turn the successful Martin Ødegaard Player Profile prototype into a reproducible, identity-safe and provenance-safe foundation that can support Premier League players without silently misidentifying players, seasons, clubs, portraits or analytical denominators.

The product decision is deliberately split into two layers:

1. **universal Player Profile composition** — identity, portrait, biography, participation, club context, season navigation and an analytical-profile slot;
2. **position-specific analytical templates** — MID V1 is governed; DEF/FWD/GKP must be researched separately rather than inheriting Ødegaard's midfielder axes.

The milestone did not redesign or modify the global shell, primary/secondary navigation, shared header system or global visual tokens.

## Definition of done

The milestone required:

1. one explicit Profile-level relationship seam connecting seasonal route identity to the appropriate source/research identities without declaring a source ID globally canonical;
2. correct cross-season navigation even when route identifiers change;
3. one compatible source representation for Profile per-90 numerators and denominator;
4. biography evidence packaged into FRL rather than requiring Daniel's local upstream checkout at runtime;
5. explicit transfer/multi-club context rather than `clubs[0]` inference;
6. portrait identity separated from route identity;
7. the universal shell preserved while MID V1 remains position-specific;
8. representative acceptance and frontend/backend validation proving the result.

A final convergence requirement was added when the audit found that the tracked FPL participation aggregate was stale relative to the pinned Player-Season source: Profile participation had to become internally consistent with the same governed Player-Season checkpoint when complete evidence exists.

## What changed

### 1. Player identity became an explicit relationship

`player_profile_identity.py` resolves Profile identity without treating numeric equality across source families as a canonical join.

The key acceptance case is Ødegaard:

- 2026/27 route: `184029`;
- 2024/25 route: `13`;
- both resolve to research identity: `player_match:547410`;
- portrait/Player-Season source identity: `184029`.

Season navigation now uses the route identifier belonging to the selected season rather than reusing the current URL's code.

### 2. Player Profile received a dedicated source representation

`scripts/materialize_player_profile_source_stats.py` materialises `data/player_profile_source_stats_v1.csv` from pinned upstream Player-Season evidence.

Pinned upstream release:

`imadeddine-belkat/Premier-League-Stats@115d889df4e2efab5e7c1d8ca0f3ca86ecfd2ae6`

The representation preserves:

- `gamesPlayed` → `source_appearances`;
- `starts` → `source_starts`;
- `timePlayed` → `source_minutes`;
- `expectedGoals`;
- `expectedAssists`;
- `successfulPassesOppositionHalf`;
- `forwardPasses`;
- `recoveries`;
- `tacklesWon`.

Source blanks remain unavailable rather than zero.

### 3. Numerator/denominator provenance was repaired

MID V1 no longer takes a Player-Season numerator and divides it by FPL participation minutes.

All six Profile axes are calculated from one Player-Season row and divide by that row's `timePlayed`:

- Goal threat — xG / 90;
- Chance creation — xA / 90;
- Advanced passing — accurate opposition-half passes / 90;
- Forward passing — forward passes / 90;
- Recoveries / 90;
- Tackles won / 90.

For the pinned 2026/27 Ødegaard row:

- 45 forward passes;
- 224 `timePlayed` minutes;
- `45 / 224 × 90 = 18.080357...`, displayed/documented as **18.0804 per 90**.

This supersedes the earlier Profile checkpoint that divided 45 forward passes by 221 minutes.

The broader Player Stats/rich Player-Match denominator question is intentionally outside this milestone and remains a separate audit surface.

### 4. Descriptive participation became representation-consistent

The tracked FPL fixture aggregate on the reference branch still produced 145 minutes for current Ødegaard, while the pinned Player-Season source records 3 appearances, 3 starts and 224 minutes.

Profile now uses `gamesPlayed`, `starts` and `timePlayed` from `PLAYER_PROFILE_SOURCE_STATS_V1` **as one complete block** when all three are observed.

If any of those fields is missing, the Profile falls back **as one block** to the established FPL player-fixture aggregate. It never creates a hybrid participation row from two representations.

Current acceptance expectation:

**Ødegaard 2026/27 = 3 appearances / 3 starts / 224 minutes.**

This is the governed pinned snapshot for this milestone, not a claim that 224 is necessarily the live real-world total on 15 September.

### 5. Biography became packaged runtime evidence

`scripts/materialize_player_profile_biography.py` creates:

- `data/player_profile_biography_v1.csv`;
- `data/player_profile_biography_v1.metadata.json`.

Runtime Profile requests read that packaged projection only. Daniel's local `C:\Users\...` upstream source checkout is no longer a runtime requirement for biography.

The verified Profile source-player identity is authoritative for biography lookup. Display names are corroborating evidence, not an identity join key. No fuzzy join was added. Conflicting stable biographical facts for the same verified source identity are withheld.

### 6. Club context became transfer-aware

`player_profile_context.py` now distinguishes:

- a verified single-club season;
- a multi-club season where the latest unique canonical fixture observation resolves the primary/current club;
- an unresolved multi-club season, where primary club is withheld.

Tests explicitly cover transfer chronology and the fail-closed unresolved case.

### 7. Portrait identity was separated from the route

The frontend receives a verified `portrait_player_code` rather than assuming the current seasonal route code is also the Premier League/source portrait ID.

This is required for cases such as historical Ødegaard, whose 2024/25 route is `13` while his portrait/Player-Season identity resolves to `184029`.

### 8. Universal shell and position-specific analysis were separated

The Ødegaard page remains the visual/compositional basis for Player Profile.

MID V1 is the only governed comparative template in this milestone. DEF/FWD/GKP profiles still resolve identity, biography, portrait, participation, club context and history, but comparative analysis deliberately returns unavailable pending separate positional research/governance.

## Acceptance matrix

The validated acceptance matrix includes:

| Case | Purpose |
| --- | --- |
| Current Ødegaard (`2026-27/184029`) | complete MID path, source participation and six-axis comparison |
| Historical Ødegaard (`2024-25/13`) | changing route ID with stable research/portrait relationships |
| Gabriel (`2026-27/226597`) | defender universal profile + withheld MID comparison |
| Eberechi Eze (`2026-27/232413`) | low-minute MID threshold and participation fallback |
| David Raya (`2026-27/154561`) | goalkeeper universal profile + packaged biography |
| Kai Havertz (`2026-27/219847`) | forward universal profile + withheld MID comparison |

The matrix also asserts Ødegaard cross-season research identity continuity and requires every plotted MID axis to declare `timePlayed` as its denominator.

## Validation

GitHub Actions run `35018232558` on implementation commit `ba11bb1fcfc1242f130e2d32bd91dc20320d0438` passed all feature gates and then materialised the governed evidence in bot commit `11b27f726d8869f8da7c5da58fd3d0e05e2a4cc7`.

Observed gates:

- pinned upstream checkout — PASS;
- Player Profile source materialisation — PASS;
- biography materialisation — PASS;
- changed Python compile — PASS;
- focused Profile regression suite — **26 passed in 6.34s**;
- acceptance matrix — PASS;
- TypeScript `npm run typecheck` — PASS;
- Next.js 16.3.1 production `npm run build` — PASS.

The build produced the dynamic `/players/[season]/[playerCode]` route successfully.

## Important non-Profile findings

### Existing API import blocker

The target/reference branch currently has `api/frl_api.py` importing `team_records_materialization` while the tracked module is absent. A clean full `api.player_stats` package collection therefore remains blocked by target-branch state.

This milestone records that condition and does not fabricate an unrelated Team module merely to obtain a green Profile gate.

### Frontend dependency audit

The clean `npm install --no-package-lock` used for validation reported **three critical-severity vulnerabilities** in the existing dependency graph. Typecheck and production build passed. Dependency-security remediation was not silently broadened into this Player Profile milestone and remains separate technical debt.

## Non-goals / parked work

This milestone does not:

- merge into stable `main`;
- claim visibility into Daniel's uncommitted Windows work;
- redesign the global shell or shared header/navigation;
- create DEF/FWD/GKP radar templates;
- claim that FPL MID is the final role ontology for midfielder comparison;
- convert missing Carrying into take-ons or another proxy;
- rewrite the whole Player Stats or rich Player-Match denominator architecture;
- fix the unrelated target-branch Team API import defect;
- resolve existing npm dependency vulnerabilities.

## Convergence result

The original objective is satisfied at feature-branch level:

> **Ødegaard's first-draft page can now act as the universal Player Profile composition without requiring the product to pretend Ødegaard's seasonal route ID, portrait ID, Player-Season ID, research identity, club membership and analytical denominator are the same thing.**

The milestone is an **integration candidate**, not integrated truth. Before merge into `design/bet-builder-reference-v1`, reconcile it with Daniel's live local Windows state and review the known target-branch blockers. Stable `main` remains unchanged until a later explicit integration decision.
