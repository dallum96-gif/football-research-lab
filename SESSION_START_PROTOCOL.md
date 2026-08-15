# Football Research Laboratory — Session Start Protocol

This file is mandatory for any fresh ChatGPT/coding session working on the repository.

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

A fresh session must run this baseline before substantive code changes whenever the environment permits it, and must run it again after changes that could affect the research layer or as the full regression gate for significant GUI/data work.

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

## Mandatory session sequence

Before substantive work:

1. Read `PROJECT_ORIENTATION.md`.
2. Read `CURRENT_WORK.md`.
3. Establish the current branch and repository state.
4. Inspect the working application and relevant archived/backup implementation when the behaviour is not obvious.
5. Trace existing retrieval/classification mechanisms before creating new ones.
6. Run the **26/26 research baseline**.
7. Run `project-health.ps1`.
8. Record any warnings and decide whether they are known/accepted.
9. Only then make the smallest sensible change.
10. Run targeted validation and the relevant regression/full gates again.

## Non-destruction rule

Never treat a successful new UI behaviour as proof that the change is safe. A change is safe only when the intended behaviour works **and** trusted existing behaviour, data identity, provenance and research tests remain intact.
