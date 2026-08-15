# Football Research Laboratory — Mandatory Session Start Protocol

This protocol is mandatory for any new coding/research session working on the Football Research Laboratory.

## Before changing anything

1. Treat `dallum96-gif/football-research-lab` as the GitHub source of truth for tracked project code and documentation.
2. Read `PROJECT_ORIENTATION.md`, `CURRENT_WORK.md`, `DATA_CONSTRUCTION.md`, `RISK_STRATEGY_FRAMEWORK.md`, `NON_DESTRUCTION_ASSURANCE.md`, and `UI_DESIGN_SYSTEM.md` before substantive work.
3. Establish the current branch and repository state and distinguish committed work from local/untracked experiments.
4. Inspect the current working application and relevant archived/backup implementation before replacing an established capability.
5. If a capability or classification is not obvious in GitHub, inspect the local source tree and trace the mechanism from source → retrieval/transformation → aggregation/classification → existing consumer.
6. Do not infer that a capability is absent merely because it cannot be found by an intuitive filename, metric name, or GitHub search.
7. Preserve existing retrieval, identity and classification mechanisms wherever possible. Reuse the established seam rather than creating a parallel mechanism.

## Mandatory validation gate

The project's **26/26 research tests are an imperative regression baseline**. They are not optional and must be run before a change is considered safe.

The project also has a separate PowerShell health gate:

```powershell
.\project-health.ps1
```

The health gate is distinct from the 26/26 research-test baseline. A new session must understand both.

### Interpretation of the health gate

- `GREEN LIGHT - PROJECT HEALTH CHECK PASSED` = pass.
- `GREEN LIGHT - PASSED WITH WARNINGS` = **also a pass**, provided the warnings are understood and are consistent with documented/known project states.
- `RED LIGHT - PROJECT HEALTH CHECK FAILED` = fail; do not treat the change as safe until the failure is understood and resolved or explicitly accepted as an existing baseline condition.

The current documented warning is the known 2019–20 Manchester City v Arsenal fixture with missing score data. The health gate intentionally warns about this rather than inventing a result.

### Research-test baseline

The current research validation contract is:

- Core Query Lab: 14/14
- Player Research V0.1: 6/6
- Player Research V0.2: 6/6
- Total: **26/26**

If `pytest` is unavailable, do **not** install a new testing framework merely to satisfy the session. Inspect the repository's existing test scripts and health-gate mechanism and use the project's established validation path.

## Non-destruction rule

For every change:

```text
Understand existing behaviour
        ↓
Identify exact change surface
        ↓
Inspect source + consumer + classification
        ↓
Predict failure modes
        ↓
Make the smallest change possible
        ↓
Run the mandatory validation gate
        ↓
Inspect the application/result
        ↓
Only then treat the change as safe
```

A UI-only request must not silently change the trusted query/data layer. A source-backed metric must not be reimplemented merely because its existing retrieval path is not immediately obvious.

## Design principle

The Laboratory should balance:

> **serious enough to trust, fun enough to explore.**

The current visual language treats coral/red as a first-class brand accent alongside green, not merely as an error colour. New pages should preserve the same analytical clarity and playful finishing touches rather than inventing independent palettes.
