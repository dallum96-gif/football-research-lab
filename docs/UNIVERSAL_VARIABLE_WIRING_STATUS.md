# Universal Variable Wiring — Status

## Current state

The universal-access contract and canonical context/resolver façade are now implemented on `feature/universal-variable-wiring`.

The resolver is intentionally fail-closed until an existing, audited source/query handler is registered for a variable's canonical relationship. This prevents the FRL from claiming that a variable is GUI-accessible merely because the variable is catalogued.

## Required next integration

Attach the existing verified source/query handlers for:

- Fixture
- Team–Fixture
- Player–Fixture
- Team–Season
- Player–Season
- Event

Then promote each variable from `VALIDATED`/catalogued state to `RESOLVABLE` only when the handler and identity/temporal tests pass.

## Acceptance example

A request such as:

```python
resolve_variable(
    "successfulDribbles",
    fixture=("2024-25", fixture_id),
    team=persistent_team_code,
)
```

must return player–fixture values by following the verified player/fixture relationship. It must not inspect source paths or construct a provider-specific join inside the GUI.
