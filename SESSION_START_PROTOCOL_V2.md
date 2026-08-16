# Football Research Laboratory — Session Start Protocol V2

This file is mandatory for any fresh ChatGPT/coding session working on the repository.

## Non-negotiable session gate

**A fresh session must complete the session-start validation before substantive interaction with the user or any substantive code work.**

Do not begin feature discussion, implementation, debugging, refactoring or UI work from an unvalidated project state unless the user is only providing information needed to establish session context.

Required first-session sequence:

1. Read `PROJECT_ORIENTATION.md`.
2. Read `CURRENT_WORK.md`.
3. Establish the current branch and repository state.
4. Run the **26/26 research baseline**.
5. Run `project-health.ps1`.
6. Record and understand any warnings.
7. Only then proceed with substantive project interaction or implementation.

If the environment does not permit validation to run, say so explicitly and do not pretend the baseline is known to pass.

## Non-negotiable research baseline

The current development baseline is **26/26 research tests passing**.

Breakdown:

- **Query Lab: 14/14**
  - test file: `tests/test-query-lab.py`
  - the script's `__main__` test list contains 14 test functions
- **Player Research V0.1: 6/6**
  - test file: `tests/test-player-research.py`
  - the script's `TESTS` list contains 6 test functions
- **Player Research V0.2: 6/6**
  - test file: `tests/test-player-research-v02.py`
  - the script's `TESTS` list contains 6 test functions

**Total: 14 + 6 + 6 = 26 research tests.**

These are the current research regression baseline. Do not silently substitute pytest, a smaller subset, or an invented testing workflow merely because the standalone scripts are not pytest files.

## Exact command to run the 26/26 baseline

From:

`C:\Users\dlall\football_database\Premier-League-Stats\fpl_scraper\fpl_stats`

run:

```powershell
python .\tests\test-query-lab.py
if ($LASTEXITCODE -ne 0) { throw "Query Lab baseline failed" }

python .\tests\test-player-research.py
if ($LASTEXITCODE -ne 0) { throw "Player Research V0.1 baseline failed" }

python .\tests\test-player-research-v02.py
if ($LASTEXITCODE -ne 0) { throw "Player Research V0.2 baseline failed" }
```

Expected outcome:

```text
PASSED: 14 test(s)
PLAYER RESEARCH TESTS: 6/6
PLAYER RESEARCH V0.2: 6/6
```

The exact wording of the Query Lab and player scripts may differ slightly between checkpoints, but the required counts are 14, 6 and 6.

A fresh session must run this baseline before substantive interaction with the user and before substantive code changes whenever the environment permits it, and must run it again after changes that could affect the research layer or as the full regression gate for significant GUI/data work.

## Project health gate

The 26/26 research baseline is separate from the project-health gate.

Run:

```powershell
.\project-health.ps1
```

The health gate checks broader data and project integrity, including source-file coverage, the 3,800-fixture canonical master, season integrity, duplicate fixture IDs, required fixture fields, score/completion semantics, team integrity, date integrity, and the 2025-26 player-to-fixture relationship.

Acceptable success states are:

- `GREEN LIGHT - PROJECT HEALTH CHECK PASSED`
- `GREEN LIGHT - PASSED WITH WARNINGS`

`GREEN LIGHT - PASSED WITH WARNINGS` is still a pass **only when the warnings are understood and correspond to known/accepted project conditions**. The current known warning is the rescheduled 2019-20 Manchester City v Arsenal fixture representation (fixture ID 275), which must not be "fixed" by inventing data.

`RED LIGHT - PROJECT HEALTH CHECK FAILED` is a failure and must be investigated before the change is treated as safe.

## Mandatory validation sequence after changes

For any substantive change:

1. Run targeted validation for the affected feature.
2. Re-run the **26/26 research baseline** when the research/data layer may have been affected or when using the full regression gate.
3. Run `project-health.ps1`.
4. Record and understand any warnings.
5. Only then treat the change as safe.

## Discovery and non-destruction rules

Before creating a new retrieval, identity, aggregation or classification mechanism:

- inspect the current working application;
- inspect relevant archived/backup implementations when behaviour is not obvious;
- trace existing source → retrieval/query → aggregation/classification → consumer paths;
- prefer restoring or reusing an established mechanism over inventing a parallel one.

Never treat a successful new UI behaviour as proof that the change is safe. A change is safe only when the intended behaviour works **and** trusted existing behaviour, data identity, provenance and research tests remain intact.
