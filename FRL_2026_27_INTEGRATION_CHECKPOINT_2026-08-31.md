# Football Research Laboratory — 2026/27 Integration Checkpoint

**Checkpoint date:** 31 August 2026  
**Checkpoint ID:** `LIVING_2026_27_INITIAL_INTEGRATION_V1`  
**Integrated main commits:**

- `10ff03f8` — `data: integrate governed 2026/27 season release`
- `9d0b06ee` — `fix: make expected-metric artifact hashes newline portable`

This checkpoint records the first completed governed 2026/27 integration increment. It does **not** close the living-season programme.

For standing documentation-governance rules see `FRL_DOCUMENTATION_SYNC_CONTRACT.md` and `data/frl_documentation_state_v1.json`.

## North-star objective

The active objective remains:

> **Keep FRL current and increasingly automated, integrate all defensible 2026/27 evidence already available through the known preserved ecosystem, measure capability and missingness honestly, and let demonstrated gaps determine what supplementary evidence or provider work is justified next.**

The intended sequence remains:

```text
new/preserved upstream release
        ↓
immutable pin + source manifest
        ↓
schema / identity / relationship validation
        ↓
affected 2026/27 rebuild
        ↓
consumer + regression validation
        ↓
capability / gap delta
        ↓
only then: supplementary-source decision
```

This means the current integration is a reusable release loop, not a one-off import.

## What is now integrated

The pinned upstream source release is the `imadeddine-belkat/Premier-League-Stats` ecosystem at commit:

`1ec7f0dc79055902251cd938650f622b0e79f3cc`

The integrated checkpoint contains:

- 380 canonical 2026/27 fixtures;
- 10 completed fixtures and 370 scheduled fixtures at the pinned release boundary;
- 610 preserved FPL player × fixture rows;
- 300 retained zero-minute/non-participation rows;
- 0 duplicate player-fixture rows;
- 0 unresolved fixture relationships;
- 20 team-season relationships;
- player identity statuses split between canonical `VERIFIED` and explicit `SOURCE_NATIVE_VERIFIED` routes rather than falsely promoting every source row into canonical identity;
- source-native fixture/player evidence and immutable release manifests under `data/season_releases/2026-27/`;
- current capability/gap state under `data/season_releases/2026-27/capability_gap_register.json`;
- canonical fixture coverage extended from ten seasons / 3,800 fixtures to eleven seasons / 4,180 fixtures;
- capability inventory coverage regenerated to reflect the living 2026/27 season;
- Next.js Team Stats surfaces changed to present unavailable current-season metrics explicitly rather than silently omitting them.

The current release pointer and immutable release record preserve the as-of/source boundary. Later releases must supersede through the governed release lifecycle rather than overwrite historical evidence of what FRL knew at an earlier release.

## Important identity and missingness position

The integration preserves the existing contracts:

- canonical fixture, team and player identity remain separate namespaces and relationships;
- FPL `element`, `player_code`, `team_code` and `fixture_code` remain source identifiers;
- `SOURCE_NATIVE_VERIFIED` is not equivalent to canonical `VERIFIED`;
- zero-minute source rows are retained as non-participation evidence;
- scheduled fixtures with blank scores are not converted to zero-score completed fixtures;
- source blanks remain missing by default unless an explicit field/source rule establishes structural zero;
- current-season incompleteness is represented explicitly;
- no live Premier League/PulseLive acquisition was introduced by this increment;
- no supplementary provider was introduced by this increment.

## Validation record

Validation performed on the integrated Windows development environment included:

- `tests/test_incremental_fpl_materialization.py` — **4 passed**;
- `tests/test_variable_capability_inventory.py` + incremental materialisation gate — **8 passed**;
- regenerated capability inventory followed by deterministic `--check` — **passed**;
- affected expected-metric / Team Stats cluster after portability repair — **24 passed**;
- Next.js `npm --prefix web run typecheck` — **passed**;
- Next.js `npm --prefix web run build` — **passed**;
- `project-health.ps1` — **passed with the existing 2019/20 uncompleted-fixture warning**;
- `python scripts/check_documentation_sync.py` before checkpoint refresh — **passed**;
- `git diff --check` — **passed** (line-ending notices only).

The full Python suite after the current-season fixes finished at:

- **133 passed**;
- **13 failed**;
- **17 warnings**.

The 13 remaining failures were isolated from this milestone:

- 12 legacy Streamlit/UI contract tests whose expectations have drifted from the active Next.js product architecture;
- 1 Altair v6 compatibility failure in the legacy visualisation layer (`config` on a layered sub-spec).

They remain repository debt and must not be misreported as 2026/27 integration failures.

A separate Windows portability defect was discovered during validation: expected-metric artifact integrity originally hashed raw checkout bytes, so Git-normalised LF content failed on a clean CRLF Windows checkout. Commit `9d0b06ee` changed verification to hash newline-normalised UTF-8 text while leaving the governed artifact and recorded canonical hash unchanged.

## What this milestone does not mean

This checkpoint does **not** mean:

- 2026/27 data acquisition is finished;
- FRL has all desired current-season variables;
- the first pinned release is the final truth for the season;
- FPL evidence is semantically interchangeable with historical Opta-derived evidence;
- low coverage through one route means the wider preserved ecosystem lacks the variable;
- a new provider should now be selected by convenience rather than by demonstrated gaps;
- legacy Streamlit cleanup has become the product priority;
- temporal/as-of reconstruction can be weakened for convenience.

## Immediate continuation objective

The next current-season work package is:

1. **Operationalise repeatable release detection/integration.**
   - identify a new upstream release/commit;
   - pin it immutably;
   - compare it with the previously integrated release;
   - rebuild only affected 2026/27 outputs;
   - preserve correction/supersession history.
2. **Interrogate the generated capability-gap register empirically.**
   - separate genuine source absence from disconnected evidence, identity gaps, semantic uncertainty, coverage gaps, comparability limits and rights/operational restrictions;
   - prioritise gaps according to FRL research, modelling and product value rather than raw variable count.
3. **Connect additional preserved evidence where it already exists and contracts permit.**
   - do this before acquiring a new provider;
   - retain each source family, grain, identity route and missingness semantics explicitly.
4. **Assess supplementary providers only against demonstrated requirements.**
   - compare missing variables/grains, coverage, identity reliability, semantic comparability, reproducibility and rights;
   - do not silently coalesce a supplementary source into FPL or historical source identities.
5. **Continue product/research development without allowing it to fork metric definitions or temporal state.**
   - Next.js remains the active frontend;
   - FastAPI/shared governed analytical services remain authoritative;
   - historical reconstruction and evidence provenance remain first-class constraints.

## Standing non-goals

Unless explicitly authorised by a later work package, this checkpoint does not authorise:

- live PulseLive scraping/acquisition;
- destructive canonical replacement;
- fuzzy identity promotion;
- cross-provider first-non-null fallback;
- fabricated current-season observations;
- a second canonical fixture/team/player system;
- unrelated legacy Streamlit repair as a blocker to current-season progress.

> **The first release is integrated. The job now is to keep the season current, make the release loop repeatable, and let measured capability gaps drive the next source decision.**
