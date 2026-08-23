# FRL Coding Rules

These rules are part of the Football Research Laboratory engineering contract. They are intended to guide both human contributors and coding agents working in this repository.

## 1. Repository is the source of truth

Before modifying code:

- Read the relevant project contracts and `CURRENT_WORK.md`.
- Inspect the existing implementation and tests.
- Do not invent filenames, functions, modules, commands, or data relationships.
- Prefer existing repository seams over parallel implementations.

## 2. Evidence before inference

Never promote:

- source-local IDs to FRL identity;
- name matches to verified identity;
- missing data to zero;
- an inferred relationship to a canonical relationship

without an explicit contract permitting it.

Unresolved states must remain unresolved.

## 3. Source boundaries

Use only approved source families and their documented adapters.

Do not silently introduce another provider or alternate source path to close a gap.

Preserve source-native fields and provenance.

## 4. Temporal correctness

All timestamps represent instants, not strings.

When comparing timestamps across systems:

- Parse them as timezone-aware datetimes.
- Compare canonical instants.
- Never compare raw timestamp strings when timezone representations may differ.
- Never strip timezone information.
- Never convert a local timestamp to UTC by changing clock fields manually.
- Treat naive timestamps as an explicit error unless the relevant contract defines their timezone.

## 5. Tests

Run tests through the repository's established test runner.

Do not assume `python tests/foo.py` is equivalent to pytest.

A test passing silently is not evidence of success unless the runner reports it.

When a test fails:

1. Classify the failure.
2. Determine whether it is code, test, environment, or fixture data.
3. Inspect the smallest relevant seam.
4. Fix the underlying contract rather than weakening the assertion.

## 6. No speculative API usage

Before calling a function:

- Verify that it exists.
- Inspect its signature.
- Use the repository's established API.

Never invent helper names.

## 7. Additive and non-destructive changes

Do not overwrite canonical evidence.

Analytical materialisations are derived artifacts and must remain reproducible from canonical inputs.

Prefer additive changes unless an explicit migration contract requires replacement.

## 8. Research result semantics

A result object must preserve:

- population;
- filters and parameters;
- temporal/as-of context;
- provenance;
- limitations;
- version information.

Presentation code must not recompute research metrics independently.

## 9. Failure handling

Never solve a failing reconciliation by lowering standards.

Prefer:

`unresolved + reason`

over:

`unsupported match`.

## 10. Completion discipline

Before declaring a task complete:

- Run the directly affected tests.
- Run the relevant broader regression tests.
- Run project health checks where required by `CURRENT_WORK.md` or the applicable project protocol.
- Record the exact commands and results when the task changes a contract, data layer, or verification gate.

## 11. Do not confuse namespaces

The following are distinct unless an explicit verified relationship exists:

- source player ID;
- Player-Season player ID / `pl_code`;
- FPL element ID;
- FRL persistent player identity.

Likewise:

- source team ID;
- season-local team ID;
- persistent team code.

Never join these namespaces solely because their values appear compatible.

## 12. Prefer the smallest valid seam

When a problem is unresolved, investigate the narrowest existing source, adapter, registry, or query seam capable of answering it.

Do not redesign a working layer to solve a downstream edge case.

## 13. Preserve reproducibility

A research result must be reconstructable from the same declared inputs and code contract.

Do not make results depend on hidden state, undocumented local files, current wall-clock time, or accidental filesystem ordering unless the contract explicitly calls for it.

## 14. Distinguish source coverage from reconciliation failure

If an approved source family genuinely lacks a corresponding record, record that as a source-coverage limitation rather than manufacturing an identity or weakening a match rule.

A complete reconciliation is not allowed to mean an unsupported reconciliation.
