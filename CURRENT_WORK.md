# Current Work — Football Research Laboratory

**Last updated:** 31 August 2026  
**Checkpoint:** `LIVING_2026_27_INITIAL_INTEGRATION_V1`

For documentation-governance rules see `FRL_DOCUMENTATION_SYNC_CONTRACT.md` and `data/frl_documentation_state_v1.json`.

The completed initial 2026/27 increment is recorded in `FRL_2026_27_INTEGRATION_CHECKPOINT_2026-08-31.md`. The governing source, identity, temporal, missingness and supplementary-source rules remain those established in `FRL_2026_27_INCREMENTAL_SEASON_INTEGRATION_PLAN.md` and the stronger durable contracts it references.

## Current platform state

FRL is a governed football research platform whose active product frontend is **Next.js + React**, with **FastAPI** as the frontend-facing API. Streamlit remains legacy/reference only.

The standing architecture remains centred on:

- canonical fixture, team and player identity rather than source-id coincidence;
- preserved source-native evidence with explicit provenance;
- temporal/as-of reconstruction so FRL can distinguish what is true now from what was knowable at an earlier point;
- explicit missing, partial, unresolved and unavailable states rather than silent zero/fallback behaviour;
- governed source routing and explicit derivations;
- reproducible materialisation from pinned evidence;
- shared analytical services so product surfaces do not invent separate metric definitions, populations, ranks or percentiles.

The current integrated product state includes:

- Homepage V1, standalone Fixtures V1 and Team Profile V1 frozen for now;
- Team Stats Team View and League Rankings as paired analytical surfaces over one shared season analysis result;
- six curated Team View Overview metrics;
- additional family-level League Rankings metrics without automatically promoting them to Overview;
- Possession grouped under Passing;
- corners per match as the first family-only rankable metric;
- governed expected-metric routing and player-derived xG for 2022-23 through 2025-26;
- automated repository-memory synchronisation and targeted analytical/frontend regression gates.

## 2026/27 living-season checkpoint

The first governed 2026/27 release is now integrated on `main`.

Integrated commits:

- `10ff03f8` — `data: integrate governed 2026/27 season release`;
- `9d0b06ee` — `fix: make expected-metric artifact hashes newline portable`.

Pinned upstream release:

`imadeddine-belkat/Premier-League-Stats@1ec7f0dc79055902251cd938650f622b0e79f3cc`

Current materialised state at that release boundary:

- 380 2026/27 canonical fixtures;
- 10 completed and 370 scheduled fixtures;
- 610 FPL player × fixture rows;
- 300 zero-minute/non-participation rows retained;
- 0 duplicate player-fixture rows;
- 0 unresolved fixture relationships;
- 20 team-season relationships;
- canonical fixture coverage extended to eleven seasons / 4,180 fixtures;
- current release/source manifests and preserved source bytes under `data/season_releases/2026-27/`;
- a reproducible capability-gap register at `data/season_releases/2026-27/capability_gap_register.json`.

Player identity remains deliberately split between canonical `VERIFIED` and explicit `SOURCE_NATIVE_VERIFIED` routes. Source-native verification must not be rewritten as canonical resolution merely to increase a coverage number.

## Immediate objective

The immediate objective is no longer “start 2026/27 integration.” The first release is integrated.

The active objective is:

> **Keep FRL current and increasingly automated, integrate every defensible 2026/27 capability already available through the known preserved ecosystem, measure capability and missingness honestly, and let demonstrated gaps decide what supplementary evidence or provider work is justified next.**

The living-season loop is therefore:

```text
upstream release / correction
        ↓
immutable source pin + manifest
        ↓
release delta
        ↓
schema / identity / relationship validation
        ↓
affected 2026/27 rebuild
        ↓
regression + consumer validation
        ↓
capability / gap delta
        ↓
source decision only where a demonstrated gap remains
```

This is a continuing release process, not a one-off import.

## Current 2026/27 source position

The initial release connected the fixture and FPL player-fixture evidence that could be promoted safely through existing contracts.

Standing rules remain:

- canonical fixtures/results are the trusted fixture spine;
- FPL is a distinct source family and its player-fixture evidence is not historical Opta-derived `players_match_stats`;
- FPL `element`, `player_code`, `team_code` and `fixture_code` remain source identifiers;
- fixture, team and player relationships are separate;
- source blanks mean missing by default;
- zero-minute registered-player rows are retained as non-participation evidence;
- missing scores are not zero scores;
- current-season outputs must expose incomplete/as-of populations;
- a later source release must supersede through a preserved release history rather than erase the earlier state;
- low coverage through one connected route is not proof that the wider preserved ecosystem lacks the concept;
- direct, FPL-derived, player-derived and any future supplementary representations must not be first-non-null coalesced.

No live Premier League/PulseLive acquisition and no new supplementary provider were introduced by the initial increment.

## Capability and supplementary-source objective

The generated gap register is now an active decision instrument rather than a future deliverable.

The next source work must distinguish whether a desired capability is limited by:

- genuine source absence;
- preserved evidence that is not yet connected;
- unresolved identity;
- unresolved football meaning or aggregation semantics;
- invalid/unapproved derivation;
- insufficient current coverage;
- cross-period/provider incomparability;
- rights or operational restrictions.

Only after that classification should FRL evaluate a supplementary provider for the unresolved requirement. Any candidate must be assessed against the actual missing variables/grains, coverage, identity reliability, semantic comparability, preservation/reproducibility requirements and rights position.

The objective is **not** to maximise provider count or raw variable count. It is to maximise trustworthy research capability.

## Team Stats analytical checkpoint

The living-season objective does not discard the shared Team Stats architecture already established.

`team_analysis_kernel.py` remains the shared governed analytical seam for Team View and League Rankings. The standing product rule remains:

> **Profiles describe entities. Stats analyse entities. Rankings analyse populations. Compare analyses selected entities together. Research tests the questions these surfaces reveal.**

Team View and League Rankings must not drift into independent definitions of the same metric, population, rank or percentile.

The six current Overview metrics remain:

1. points per match;
2. goals per match;
3. goals against per match;
4. shots per match;
5. shots on target per match;
6. possession.

Corners per match remains an additional family-only Attack ranking metric.

The 2026/27 frontend now represents governed unavailability explicitly rather than silently omitting current-season metrics that do not have approved observations.

Selective Team Stats family expansion can continue, but it must not distract from or fork the current-season source/temporal architecture.

## Expected-metric standing position

Single-season xG route policy remains governed by `FRL_EXPECTED_METRIC_ROUTING_CONTRACT.md` and the current route implementation.

The player-derived expected-goals artifact remains pinned to upstream commit `1ec7f0dc79055902251cd938650f622b0e79f3cc` for its declared historical seasons. During 2026/27 validation, a Windows checkout portability defect was found in artifact integrity verification: raw working-tree bytes differed under CRLF conversion even though the Git blob was correct. Commit `9d0b06ee` now hashes newline-normalised UTF-8 text, preserving the canonical recorded hashes without rewriting the governed artifact.

This portability fix is not a change to football meaning, expected-goals values or provenance.

## Validation state

The 2026/27 milestone validation recorded:

- incremental FPL materialisation: **4 passed**;
- combined capability-inventory + incremental materialisation gate: **8 passed**;
- capability inventory deterministic `--check`: **passed**;
- affected expected-metric / Team Stats cluster after portability repair: **24 passed**;
- Next.js typecheck: **passed**;
- Next.js production build: **passed**;
- `project-health.ps1`: **passed with the existing 2019/20 uncompleted-fixture warning**;
- `git diff --check`: **passed** apart from line-ending notices.

The full Python suite after the milestone was:

- **133 passed**;
- **13 failed**;
- **17 warnings**.

The 13 remaining failures are not 2026/27 integration failures:

- 12 stale legacy Streamlit/UI contract expectations;
- 1 Altair v6 compatibility failure in the legacy visualisation layer.

Do not turn those legacy failures into a blocker for the living-season objective unless the affected legacy surface becomes an active product dependency.

## Immediate development sequence

1. **Make the 2026/27 release loop repeatable.**
   - detect/identify the next upstream release or correction;
   - pin it immutably;
   - compare with the current integrated release;
   - rebuild only affected outputs;
   - preserve supersession and as-of evidence.
2. **Interrogate the current capability-gap register.**
   - prioritise gaps according to research, modelling and product value;
   - distinguish route gaps from genuine source gaps.
3. **Connect additional preserved evidence where it already exists and contracts permit.**
4. **Evaluate supplementary sources only against demonstrated unresolved requirements.**
5. **Continue selective Team Stats/product expansion through the shared governed analytical architecture.**
6. **Resume wider modelling work only on evidence that is temporally safe, reproducible and semantically governed.**

## Validation discipline

Do not use a historical fixed test count as a universal baseline.

For current work:

- validate immutable release identity, hashes, schemas and deterministic regeneration;
- validate fixture/team/player relationships and fail-closed identity behaviour;
- validate scheduled/completed/missing states and zero-minute semantics;
- preserve release, retrieval and as-of metadata;
- run affected FPL/URA/query/API/regression gates;
- run Next.js `typecheck` and `build` when frontend behaviour changes;
- run `project-health.ps1` when canonical/query/data behaviour changes;
- run `python scripts/check_documentation_sync.py` for standing repository-memory changes;
- use `--base-ref` where milestone-sensitive branch changes are being validated;
- run `git diff --check` before integration;
- report actual results and explicitly isolate unrelated failures.

## Repository discipline

Treat stable `main` / `origin/main` as the authoritative integrated line, while recognising that a developer working tree may contain unrelated local modifications or untracked files.

Before staging or integrating any work:

- compare local and remote ancestry;
- preserve unrelated tracked/untracked work;
- stage explicit intended paths only;
- do not use destructive reset/clean commands to manufacture a clean tree;
- do not treat a dirty local working tree as equivalent to GitHub divergence;
- re-establish local/remote synchronization explicitly after remote or local integration work.

## Standing repository memory

Fresh sessions should use this order:

1. `FRL_MASTER_PROMPT.md`
2. `PROJECT_ORIENTATION.md`
3. `CURRENT_WORK.md`
4. `data/frl_documentation_state_v1.json`
5. `FRL_2026_27_INTEGRATION_CHECKPOINT_2026-08-31.md`
6. task-relevant durable contracts / dated audits
7. current implementation

The documentation-sync rule remains mandatory:

> **A milestone that changes current architecture, product phase, source-routing understanding, validation interpretation or frontend/design status is not complete until standing repository memory has been checked for drift.**
