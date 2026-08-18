# Non-Destruction Assurance — Football Research Laboratory

## Purpose

This document defines how changes are made safely in a research system where preserving trusted behaviour is more important than making a feature appear to work quickly.

## Core rule

> **A change is not safe merely because the new feature works. It is safe only when the new feature works and trusted existing behaviour remains demonstrably intact.**

## Development cycle

```text
ESTABLISH BASELINE
      ↓
UNDERSTAND CURRENT BEHAVIOUR
      ↓
DEFINE CHANGE SURFACE
      ↓
IDENTIFY FAILURE MODES
      ↓
MAKE MINIMAL CHANGE
      ↓
TARGETED VALIDATION
      ↓
REGRESSION / FULL GATE
      ↓
REVIEW RESULT
      ↓
RELEASE / NEXT ITERATION
```

## 1. Establish the baseline first

Before code changes:

- identify the active branch;
- compare against `main` where relevant;
- inspect the current implementation;
- record the current test/health state;
- distinguish committed work from local/untracked experiments.

The current research baseline is 26/26 passing.

## 2. Define the change surface

Every task should answer:

- Which layer is actually changing?
- Which contracts must remain untouched?
- What existing outputs could be affected?
- What failure modes are plausible?

For UI work, the default assumption is that the research/query contract should not change.

## 3. Existing working behaviour safeguard

When a requested capability already appears to exist somewhere in the working system, inspect the **current working application first**, followed by relevant **archived, backup or pre-change implementations**.

Do not begin by designing a replacement mechanism merely because the current GitHub repository does not expose the expected function, field or filename.

Archived implementations are evidence for understanding established behaviour. They may be inspected to recover retrieval paths, source classifications, identity handling, aggregation rules and interface contracts. They are not permission to restore unrelated or obsolete code wholesale.

## 4. Local-source discovery safeguard

The Football Research Laboratory repository is the source of truth for its committed architecture, contracts and deployable code. However, upstream source data and retrieval mechanisms may live in a separate local workspace.

When GitHub does not clearly establish how a requested metric, classification, identity mapping or retrieval capability works, inspect the known upstream/local source tree before inferring that the capability is absent.

The discovery process should work from structure and lineage rather than relying only on an intuitive keyword:

```text
WORKING CONSUMER
      ↓
RELEVANT RETRIEVAL / TRANSFORMATION
      ↓
LOCAL UPSTREAM SOURCE TREE
      ↓
RAW / SOURCE FILE SCHEMA
```

Search for representative data families, neighbouring metrics, source identifiers, file structures and existing consumers. Trace the mechanism from raw source to the working result.

**Non-Inference from Absence:** failure to locate a function, field, file or mechanism in the Laboratory repository is not evidence that the underlying capability does not exist. Where a working application, archived implementation or known upstream source exists, those must be inspected before inventing a substitute.

Before implementing a new mechanism, establish where possible:

- source of the information;
- source field(s);
- identity key(s);
- classification rules;
- existing retrieval path;
- aggregation/transformation rules;
- existing consumer proving the capability works;
- safest reuse point.

The preferred outcome is reuse of the established mechanism through an existing architectural seam.

## 5. Prefer architectural seams

Safe refactoring often means extracting a presentation component behind an existing API rather than rewriting the API itself.

For the current GUI redesign:

```text
trusted query/data layer
        ↓
thin presentation component
        ↓
new UI shell
```

This keeps the change surface understandable and reversible.

## 6. Preserve data and provenance

Do not modify canonical data merely to make a UI state look cleaner.

Do not replace missing historical evidence with invented defaults.

Do not hide corrections or source limitations.

## 7. Validate classes of behaviour

Tests should protect invariants and contracts rather than only the exact example that triggered a bug.

A fix for a specific player, club, fixture or season should be evaluated for the broader class of problem it represents.

## 8. GUI-specific assurance

For GUI changes, validate at least:

- the new page/workspace renders;
- navigation works;
- canonical data still resolves correctly;
- fixture IDs remain unchanged;
- player/team identities remain unchanged;
- query results remain unchanged;
- provenance remains accessible;
- incomplete data states do not crash the UI;
- the 26/26 research gate remains green when the change is expected to be presentation-only.

## 9. Local workspace safety

The local research workspace may contain untracked or generated material that is not part of the deployable repository.

Never use broad destructive cleanup merely to obtain a clean Git status.

Avoid:

- `git clean` without an explicit, reviewed cleanup plan;
- `git reset --hard` as a convenience;
- broad staging such as `git add .`;
- deleting unknown local research files.

When a local file conflicts with a branch checkout, preserve it first, then establish the intended branch state.

## 10. Release thinking

A commit should have a clear purpose and a bounded change surface.

Good examples:

- `gui: extract fixture explorer presentation`
- `ui: refine navigation styling`
- `tests: add invariant for player chronology gaps`

Avoid commits that mix unrelated UI, data and research changes.

## 11. Reversibility

Prefer changes that can be reverted without reconstructing lost information.

Feature branches are the normal place for experiments. `main` should represent trusted, reviewed behaviour rather than a dumping ground for unfinished work.

## 12. Final standard

The assurance question is:

> **What evidence do we have that this change did not destroy something we already trusted?**

The answer should identify actual tests, invariants, inspection or other evidence rather than relying on intuition.
