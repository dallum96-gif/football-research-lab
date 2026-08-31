# FRL 2026/27 Integration Handoff — 2026-08-31

This file is a review handoff, not an approval, commit, or replacement for the
governing FRL contracts. Read `AGENTS.md`, the master prompt, and
`FRL_2026_27_INCREMENTAL_SEASON_INTEGRATION_PLAN.md` before continuing.

## Repository state at handoff

- Repository: `C:\Users\dlall\football_database\football-research-lab`
- Branch: `integration/2026-27-governed`
- Local HEAD: `6f17005993535c0eb12e383ea3c2ef1812cd69fa`
- `origin/main`: `6f17005993535c0eb12e383ea3c2ef1812cd69fa`
- Ahead/behind relative to `origin/main`: `0/0`
- The branch has no configured upstream.
- No commit or push was performed for the compatibility work described below.

The trusted HEAD already contains the separately committed initial integration:

- `10ff03f8 data: integrate governed 2026/27 season release`
- `9d0b06ee fix: make expected-metric artifact hashes newline portable`
- `6f170059 docs: record initial 2026/27 integration checkpoint`

## Pinned source

- Repository: `https://github.com/imadeddine-belkat/Premier-League-Stats.git`
- Commit: `1ec7f0dc79055902251cd938650f622b0e79f3cc`
- Commit date: `2026-08-25T12:56:53Z`
- Commit message: `Auto-update FPL data for 2026-08-25`
- Rights classification: `REVIEW_REQUIRED`

Consumed Git-object hashes:

- fixtures: `cc868ce4066b5a7de27f1feeafd945e0738833b65b4680afc9e404c93bbc57bf`
- merged player-fixture evidence: `a1c7a4a79f9505c517dfb17db8dd7d6aed653bde289d3d6587b17c0bc5c25de8`
- player index: `9aed59759b1586022e94fd5067be6b2319cc012804e8ee40b1fcc70284a37670`
- team index: `f47e407a06fb239586864712919ecf4ee244a9e8ccc6bf1220f456fcc7052078`

## Materialised state already in HEAD

- 380 canonical fixtures: 10 completed and 370 scheduled.
- 20/20 team identities resolved.
- 610 FPL player x fixture observations.
- 300 zero-minute registered-player observations.
- 388 `VERIFIED` player identities.
- 222 `SOURCE_NATIVE_VERIFIED` player identities.
- 0 unresolved or ambiguous fixture/player observations in the pinned materialisation.
- No 2026/27 Opta-derived `players_match_stats`, team-match `events_stats`, rich
  events, lineups/formations, or odds were present in the pinned release.

## Uncommitted implementation produced by the compatibility pass

Review these files as the bounded task diff:

- `api/frl_api.py`
- `api/player_performance.py`
- `fpl_variable_access.py`
- `research_access.py`
- `source_family_adapters.py`
- `team_analysis_kernel.py`
- `team_research_stats.py`
- `variable_resolver.py`
- `tests/test-query-lab.py`
- `tests/test_2026_27_vertical_compatibility.py` (new)

Semantics established:

- `history[].*` routes only to `FPL_PLAYER_FIXTURE`.
- `fixtures[].*` routes only to `FPL_FIXTURE`.
- Other FPL registry surfaces fail closed rather than coalescing.
- URA returns source release/path/hash, FPL IDs, canonical fixture relationship,
  player identity state/route, participation state, and an explicit declaration
  that historical Opta equivalence is not asserted.
- Canonical completed results support the current table and result-derived Team
  Stats even when optional team-match evidence is absent.
- Missing shots, possession and similar metrics remain unavailable, not zero.
- 2026/27 team xG reports `NO_GOVERNED_SEASON_ROUTE`; FPL player-fixture xG is
  deliberately not promoted into historical Team Stats xG.
- Fixture detail remains HTTP 200 when historical Player-Match evidence is absent.
- Fixture player-performance can display source-native FPL goals, assists, xG,
  xA, defensive contribution and saves with explicit provenance.

## Confirmed vertical canaries

- Fixture `2026-27/1`: Arsenal 3–0 Coventry City, canonical detail HTTP 200.
- Fixture `2026-27/11`: scheduled, both scores remain null, HTTP 200.
- Fixture `2026-27/6`: Nottingham Forest 0–1 Leeds United.
- No production 1–0 or 0–0 existed in the pinned release; synthetic regression
  coverage preserves those zero-score semantics.
- Bukayo Saka: starter/goal/FPL xG canary.
- Riccardo Calafiori: assist canary.
- Piero Hincapié: substitute-appearance canary.
- Kepa: registered zero-minute and observed-zero canary.
- David Raya: goalkeeper/save canary.
- Gabriel: discipline canary.

HTTP canaries passed for seasons, completed/scheduled/nonexistent fixture detail,
fixture player-performance, Team Stats overview and League Rankings. The rich
fixture-evidence endpoint correctly returns 404 because no verified rich source
match exists; the fixture page treats that enrichment as optional.

## Validation evidence

- Deterministic incremental materialiser `--check`: passed.
- New vertical suite: 7 passed.
- Broad affected suite: 103 passed; three direct stale `test-query-lab.py`
  expectations exposed and corrected.
- Final query/incremental/vertical rerun: 25 passed, 17 FastAPI deprecation warnings.
- `npm run typecheck`: passed.
- `npm run build`: passed.
- Temporal-integrity PowerShell gate: passed.
- Temporal-provenance PowerShell gate: passed.
- `git diff --check`: passed.

The trusted integration checkpoint recorded a full Python result of 133 passed
and 13 unrelated legacy failures (12 obsolete Streamlit GUI contracts and one
Altair v6 compatibility failure). Do not change those merely to obtain green.

## Pre-existing/unrelated working-tree state to preserve

Do not stage, discard, clean, restore, or absorb these without separate review:

- `FRL_SHORT_TERM_PRODUCT_ROADMAP.md`
- tracked generated `__pycache__` files
- `data/frl_variable_capability_summary_v1.json`
- `web/next-env.d.ts`
- `web/tsconfig.json`
- backup/damaged frontend files
- `audit_fixture_evidence_coverage.py`
- `data/raw/pulselive.zip`
- `web/package-lock.json`

The Premier-League-Stats workspace is also dirty with extensive untracked files.
Its local `main` is `ca7b54ee1924d368303a22433cf6775831ac80fa`, three commits
behind `origin/main`; it was not modified.

## Safe next action

Before doing anything, fetch and re-check both repositories. Review only the
bounded implementation files listed above against the governing contracts and
current diff. Do not commit until the user explicitly authorises it. If commit
is authorised, stage only the reviewed bounded implementation/test files and
leave all pre-existing files untouched.
