# FRL Universal Variable Access — Status / Handoff

**Date:** 25 August 2026  
**Purpose:** Durable record of the universal-variable-access decision and implementation state.

## Decision

The FRL should make every **validated / defensible source variable** directly reachable by authorised consumers, including the GUI, through one standard resolution seam.

The GUI must not need to know:

- the underlying source file;
- source-specific joins;
- source-local schemas;
- identity-reconciliation mechanics;
- how a derived metric is calculated.

The GUI should be able to ask, conceptually:

```python
resolve_variable(
    "successfulDribbles",
    season="2024-25",
    fixture_id="..."
)
```

and the FRL should determine the correct source family, grain, identity path and retrieval mechanism.

## Canonical graph rule

Variables are attached to their **natural analytical grain**, not duplicated onto every entity for convenience.

Examples:

```text
fixture metadata        -> Fixture
possession              -> Team–Fixture
successfulDribbles      -> Player–Fixture
player season goals     -> Player–Season
match event             -> Event
```

The GUI can nevertheless reach relevant values by traversing the football graph:

```text
Fixture
  -> Team–Fixture
  -> Player–Fixture
  -> variables
```

This preserves the FRL analytical grain and avoids redundant mega-tables.

## Variable lifecycle

A variable should be distinguishable across these states:

```text
DISCOVERED
  -> CATALOGUED
  -> VALIDATED
  -> RESOLVABLE
  -> GUI_ACCESSIBLE
```

Not every source field has to be UI-visible by default. **Accessibility and presentation are separate decisions.**

## Runtime architecture

The intended flow is:

```text
validated/canonical variable name
        ↓
Universal Variable Resolver
        ↓
source-field / semantic registry
        ↓
existing generic research-field query layer
        ↓
verified source-family / identity bridge
        ↓
structured value + provenance + coverage context
        ↓
GUI / research consumer
```

The resolver must reuse existing audited source-family handlers. It must not create duplicate CSV extraction or identity joins merely to expose a variable.

## Existing generic source-query seam

The broad research layer already exposes generic retrieval for:

- `team_match`
- `player_match`
- `player_season`
- `squad`

through `research_field_query.py`, built on the audited source-family adapter layer.

The searchable-variable contract requires season-aware retrieval, fail-closed behaviour for fields absent in the requested season, and preservation of source/provenance fields where applicable.

## Current player-fixture display variables

The current proposed universal fixture-page set is:

| Display statistic | Canonical/runtime variable | Grain | Source fields |
|---|---|---|---|
| Tackle won % | `wonTacklePct` | Player–Fixture | `wonTackle`, `totalTackle` |
| Interceptions won | `interceptionWon` | Player–Fixture | `interceptionWon` |
| Pass completion % | `passCompletionPct` | Player–Fixture | `accuratePass`, `totalPass` |
| Key passes | `keyPass` | Player–Fixture | `keyPass` |
| Successful dribbles | `successfulDribbles` | Player–Fixture | `successfulDribbles` |
| Shots on target | `onTargetScoringAttempt` | Player–Fixture | `onTargetScoringAttempt` |

`wonTacklePct` and `passCompletionPct` are derived values and must expose their underlying inputs in provenance.

`progressiveBallCarriesCount` was intentionally **not** selected for the universal result page because its historical coverage is intermittent rather than decade-wide.

## Important discovery from the Arsenal–Liverpool issue

The GUI previously reported that it could not confirm `successfulDribbles`. That did **not** mean the source variable was unavailable.

The problem was that the existing fixture-detail consumer path did not expose the Player–Fixture evidence layer. This revealed the architectural gap between:

```text
source capability
research/query capability
GUI capability
```

The universal resolver is intended to remove that gap.

## Current implementation work

Development branches / PRs created during this work:

- **PR #27** — Universal Variable Access contract and initial resolver seam.
- **PR #28** — Canonical-context wiring foundation for fixture/team/player/season/event relationships.
- **PR #29** — Runtime binding to the existing generic research-field handlers.

PR #29 is the current implementation line for the runtime wiring. It intentionally delegates to the existing `research_field_query` / source-family adapter seam.

## Runtime direction

The resolver should not require a hand-written handler for every source column.

For native variables, the requested season/context should be able to establish whether the field is empirically present and then dispatch through the appropriate existing family handler.

For canonical aliases / derived variables, explicit metadata should define:

- natural grain;
- family;
- source field(s);
- transformation;
- human-facing label;
- definition;
- coverage/semantic status.

## Safety rules

1. Missing historical fields fail closed.
2. Never synthesize zero because a field is absent.
3. Never silently backfill a historical field from a later season.
4. Never infer a source-local player/team identity from an unrelated numeric ID.
5. Reuse verified fixture → source-match relationships.
6. Preserve source field, source family and source-local IDs in provenance where relevant.
7. Do not turn source-native evidence into a canonical concept merely because the GUI wants to display it.
8. Historical retrieval does not by itself establish historical information-availability time; temporal reconstruction must remain separate.
9. GUI components consume resolved analytical values; they should not recreate data transformations independently.

## Verification state

The GitHub-side implementation has been written to development branches and PRs.

The local Windows-only FRL environment required for the project's full `26/26` baseline and PowerShell project-health gate is not mounted in this execution environment, so those checks have **not** been claimed as executed here.

Before merge/integration, run the repository-mandated sequence locally:

```text
26/26 baseline
project health
relevant resolver tests
relevant GUI/fixture smoke tests
```

## Next logical work

1. Complete catalogue-driven registration/mapping for the full validated variable universe rather than maintaining manual per-variable GUI handlers.
2. Verify the resolver against representative Fixture, Team–Fixture, Player–Fixture and Player–Season contexts.
3. Verify historical coverage and fail-closed behaviour across the decade.
4. Only then wire the GUI result-page component to the resolver for the six selected player statistics.
5. Treat the universal variable resolver as the standard consumer seam for future GUI and natural-language query work.

## North-star interpretation

The long-term goal is:

> **Every validated FRL variable is attached to the correct canonical relationship, has a machine-readable definition and provenance path, and is reachable by authorised consumers through the standard resolver without those consumers needing to know where the data lives.**

That is an architectural capability. It should outlive the current result page and the current six displayed statistics.
