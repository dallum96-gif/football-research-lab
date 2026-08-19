# Football Research Laboratory — Local Checkout and Execution SOP

## Purpose

Whenever work involves the user's local Football Research Laboratory checkout, treat the local repository state as an explicit dependency. Never assume that a remote commit, branch, script, file, or data artifact exists locally.

## Standard procedure

Before giving the user any command that executes, modifies, imports, validates, or deletes anything:

1. **Identify the operating context**
   - Confirm the repository and intended branch.
   - Confirm the relevant local working directory when known.

2. **Verify local synchronisation**
   - Determine the current local branch.
   - Establish whether the required remote commit/branch is actually present locally.
   - Do not assume that a successful remote write means the user's checkout contains it.
   - If `git pull` is required, establish that network/DNS connectivity is available before relying on it.

3. **Verify file and path existence**
   - For every script, module, CSV, directory, or other path required by the command, verify that it exists in the local checkout.
   - Never provide an execution command for a newly created script until its presence on the user's active local branch has been established.
   - Distinguish clearly between:
     - exists remotely
     - exists on the intended branch
     - exists in the user's local checkout

4. **Establish a baseline**
   - Inspect the relevant existing files, data, schema, identity registries, and current outputs before making changes.
   - Preserve a clear before-state for any meaningful change.

5. **Define the change surface**
   - Explicitly identify which files and data are permitted to change.
   - Treat all unrelated files and canonical datasets as protected unless the task explicitly requires otherwise.

6. **Protect trusted data**
   - Follow the Risk Strategy Framework and Non-Destruction Assurance Assessment.
   - Separate raw evidence, staged evidence, validated/proof data, and canonical data.
   - Never use canonical files as scratch space.
   - Prefer atomic writes and reversible changes.
   - Never perform broad cleanup, destructive regeneration, or opportunistic refactoring during a targeted data task.

7. **Validate before promotion**
   - Validate syntax, schema, row counts, uniqueness, provenance, identity resolution, fixture identity, team identity, and player identity as applicable.
   - Fail closed when an identity, source bridge, provenance field, or expected reconciliation cannot be verified.
   - Never infer that missing evidence is equivalent to evidence of absence.

8. **Promote only after validation**
   - Do not replace or update canonical data until the staged/proof dataset has passed its defined validation gates.
   - Compare proposed canonical output with the existing canonical state before promotion.
   - Preserve rollback/recovery capability.

9. **Run regression gates**
   - After promotion, run the relevant project health, integrity, coverage, schema, identity, and regression checks.
   - A targeted task is not complete merely because the immediate script succeeds.

10. **Report exact state**
    - State what changed.
    - State what did not change.
    - State which files/data remain protected.
    - State which checks passed.
    - State which cases remain blocked or unresolved.
    - Do not claim a task is complete when only a partial or staged result exists.

## Hard execution rules

- **Never assume remote state equals local state.**
- **Never give a command for a file that has not been verified to exist locally.**
- **Never repeatedly ask the user to pull when connectivity may be the actual blocker; diagnose connectivity first.**
- **Never modify canonical data while still discovering or classifying source/identity problems.**
- **Never bypass an existing FRL identity reconstruction mechanism with ad-hoc string matching merely to make a batch pass.**
- **Always prefer the smallest reversible change that preserves existing trusted behaviour.**

This document is authoritative for local execution and repository-state checks. The Master Prompt contains the governing rule and points to this SOP rather than duplicating every detail.