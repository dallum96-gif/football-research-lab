# Football Research Laboratory — Documentation Sync Contract

**Status:** Active repository-memory contract  
**Date:** 30 August 2026

## 1. Purpose

FRL deliberately uses repository documentation as durable project memory for new ChatGPT/Codex sessions, returning contributors and future collaborators.

That makes documentation freshness an architectural requirement rather than optional housekeeping.

The failure mode this contract prevents is:

```text
implementation changes materially
        ↓
standing repository memory remains stale
        ↓
new session trusts obsolete architecture / roadmap / validation state
        ↓
work begins from the wrong assumptions
```

## 2. Governing rule

> **Whenever a milestone materially changes FRL's current architecture, active product phase, validation baseline, source-routing understanding, frontend status or design language, the milestone is not complete until the standing repository memory has been checked for drift.**

This does not require every code edit to rewrite documentation.

It does require every **material project-state change** to reconcile the documents that future sessions are instructed to trust.

## 3. Documentation classes

### A. Durable contracts

These describe principles and invariants that should change rarely.

Examples:

- `FRL_MASTER_PROMPT.md`
- `RISK_STRATEGY_FRAMEWORK.md`
- `NON_DESTRUCTION_ASSURANCE.md`
- `FRL_SOURCE_NORMALISATION_CONTRACT.md`
- identity / relationship / temporal contracts
- research-result and data-architecture contracts

Durable contracts should avoid embedding volatile claims such as:

- the current branch;
- the exact current test count;
- the immediate feature being built;
- temporary UI implementation details.

Where current state matters, point to a living-state document instead.

### B. Living-state documents

These are expected to move with the project.

Current living-state set:

- `CURRENT_WORK.md`
- `FRL_SHORT_TERM_PRODUCT_ROADMAP.md`
- `UI_DESIGN_SYSTEM.md`
- `README.md`

These documents may contain current product state, active sequencing and current implementation choices.

### C. Orientation / gateway documents

`PROJECT_ORIENTATION.md` is the fast-start gateway.

It should contain enough stable architecture to orient a new session, but it must delegate volatile details to `CURRENT_WORK.md` and the current state manifest rather than hard-coding temporary branch or milestone information.

### D. Historical records

Closeouts, audits and dated status documents preserve what was true at a particular checkpoint.

They should normally remain immutable historical evidence even after their state is superseded.

Examples:

- `FRL_BACKEND_CLOSEOUT_2026-08-26.md`
- dated branch health audits
- dated source-route audits

Historical records should be labelled as historical/checkpoint evidence and should not be treated as current state merely because they remain in the repository.

## 4. What counts as a material change

A documentation reconciliation is mandatory when work changes any of the following:

1. active frontend architecture or legacy status;
2. current product phase or near-term sequence;
3. authoritative data/query/analysis boundary;
4. source-routing or capability interpretation;
5. canonical identity or relationship architecture;
6. temporal/as-of semantics;
7. active validation/gate interpretation;
8. current visual/design system;
9. a major product information-architecture decision;
10. the status of a major milestone from future → active → complete;
11. a previously trusted architectural claim being invalidated by new evidence.

Routine implementation work that does not alter project-level state need not trigger broad documentation rewrites.

## 5. Required reconciliation method

For each standing document affected by a material milestone, classify each relevant statement as:

```text
STILL_TRUE
TRUE_BUT_STALE_EXAMPLE
CURRENT_STATE_IN_WRONG_DOCUMENT
SUPERSEDED
CONTRADICTORY
```

Then:

- retain `STILL_TRUE` principles;
- refresh stale examples;
- move volatile state into living documents;
- mark or remove superseded current-state claims;
- reconcile contradictions explicitly rather than choosing silently.

Do not rewrite durable contracts merely to make them sound newer.

## 6. Current source of truth for current state

The machine-readable current-state checkpoint is:

`data/frl_documentation_state_v1.json`

It records:

- checkpoint date;
- active frontend;
- legacy frontend;
- active product phase;
- required standing documents;
- known stale claims that should not reappear in current-state documents.

It is metadata, not a substitute for the explanatory documents.

## 7. Automated documentation gate

The repository includes:

`scripts/check_documentation_sync.py`

The gate verifies at minimum:

- required standing documents exist;
- current-state documents do not contain known obsolete claims;
- the current manifest references the expected documentation set;
- living/orientation documents contain a documentation-sync marker;
- when run against a Git base ref, architecture-sensitive changes are surfaced if the current-state checkpoint has not been updated.

The GitHub workflow:

`.github/workflows/documentation-sync.yml`

runs the gate automatically.

Automation cannot decide whether every human statement is semantically current. It exists to make drift harder to miss, not to replace review.

## 8. Validation counts

Durable documents must not present a historical test count as the eternal current baseline.

Preferred wording:

> Run the current applicable gates and use their actual output. Dated closeouts preserve historical validated checkpoints.

Exact counts may appear in dated closeout records or in `CURRENT_WORK.md` when they are useful for the current checkpoint.

## 9. Architecture diagrams

When the architectural spine changes materially, reconcile all standing diagrams that claim to describe the current system.

A stale diagram is a stale contract.

The current analytical direction is:

```text
preserved evidence
    ↓
identity / relationships
    ↓
source representation + governed source route
    ↓
governed variable
    ↓
metric + coverage / missingness
    ↓
population / comparability
    ↓
analysis result
    ↓
FastAPI
    ↓
Next.js product / Research consumers
```

Existing code may remain transitional while migration occurs. Documentation should distinguish **current implementation reality** from **target architecture**.

## 10. Completion rule

A material milestone is documentation-complete only when:

1. the implementation/research decision is validated;
2. relevant living documents are reconciled;
3. affected durable contracts are checked for contradiction;
4. `data/frl_documentation_state_v1.json` is updated when the checkpoint changes;
5. `python scripts/check_documentation_sync.py` passes;
6. historical records that should remain immutable are left intact.

## 11. Final principle

> **Repository memory is part of the product architecture. Keep the code, evidence, decisions and documentation describing them in the same reality.**