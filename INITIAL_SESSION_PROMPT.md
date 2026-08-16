# Football Research Laboratory — Initial Session Prompt

**Before any substantive response to the user, validate the repository.**

A fresh ChatGPT/coding session must not begin substantive project discussion, implementation, debugging, refactoring or UI work until the following validation has been completed.

## Mandatory first response procedure

1. Read `PROJECT_ORIENTATION.md`.
2. Read `CURRENT_WORK.md`.
3. Establish the current branch and repository state.
4. Run the complete **26/26 research baseline**.
5. Run `project-health.ps1`.
6. Understand and record any warnings.
7. Only then begin substantive interaction with the user.

If validation cannot be run, explicitly tell the user that the project has not been validated. Never imply that the baseline is passing when it has not been run.

## 26/26 research baseline

The current research regression baseline is:

- Query Lab — **14/14** — `tests/test-query-lab.py`
- Player Research V0.1 — **6/6** — `tests/test-player-research.py`
- Player Research V0.2 — **6/6** — `tests/test-player-research-v02.py`

**Total: 26/26.**

Run exactly:

```powershell
python .\tests\test-query-lab.py
if ($LASTEXITCODE -ne 0) { throw "Query Lab baseline failed" }

python .\tests\test-player-research.py
if ($LASTEXITCODE -ne 0) { throw "Player Research V0.1 baseline failed" }

python .\tests\test-player-research-v02.py
if ($LASTEXITCODE -ne 0) { throw "Player Research V0.2 baseline failed" }
```

Do not substitute pytest, a partial subset, or an invented test runner.

## Project health gate

Then run:

```powershell
.\project-health.ps1
```

Acceptable outcomes:

- `GREEN LIGHT - PROJECT HEALTH CHECK PASSED`
- `GREEN LIGHT - PASSED WITH WARNINGS`

A green result with warnings is still a pass only when the warnings are understood and are known/accepted project conditions.

`RED LIGHT - PROJECT HEALTH CHECK FAILED` means stop and investigate before treating the project as safe.

## Development principle

After the gate passes, inspect the working code and existing mechanisms before changing anything. Reuse established query, identity, provenance and data contracts. For GUI changes, keep trusted backend/query behaviour unchanged wherever possible.
