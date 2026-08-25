# FRL Next-Session Handoff — 25 August 2026

## Current objective

The FRL is transitioning from variable-universe construction into deliberate data presentation. The immediate architectural blocker found during result-page work was that GUI consumers could not reliably retrieve player-match variables even where the underlying source field was known to exist.

## Decision made

Adopt a **Universal Variable Access** architecture:

```text
Variable universe
      ↓
Canonical variable / source-field catalogue
      ↓
Universal resolver
      ↓
Natural analytical grain + verified identity bridge
      ↓
Existing generic source/query mechanism
      ↓
Structured result + provenance
      ↓
GUI / research / future NL interface
```

The GUI should be able to request a variable in football context without knowing its storage location, source schema, joins or derivation logic.

## Canonical graph principle

Do not duplicate every variable onto Fixture, Team and Player rows.

Attach each variable at its **natural grain**:

- Fixture
- Team–Fixture
- Player–Fixture
- Team–Season
- Player–Season
- Event
- other validated grains as the universe expands

The fixture/team/player graph makes the correct observations reachable without redundant data structures.

## Source/query seam already available

The existing broad research layer already provides generic field retrieval through the audited source-family adapters for:

- `team_match`
- `player_match`
- `player_season`
- `squad`

Relevant modules include:

- `research_field_query.py`
- `research_query_extensions.py`
- `source_family_adapters.py`
- `source_field_registry.py`
- `player_match_stats.py`

Do not create bespoke CSV extraction paths for GUI fields.

## Immediate result-page variables

The six selected player-match display statistics are:

1. `wonTacklePct` — Tackle won % = `wonTackle / totalTackle`
2. `interceptionWon` — Interceptions won
3. `passCompletionPct` — Pass completion % = `accuratePass / totalPass`
4. `keyPass` — Key passes
5. `successfulDribbles` — Successful dribbles
6. `onTargetScoringAttempt` — Shots on target

These were selected because the required underlying player-match data was established as decade-wide. `progressiveBallCarriesCount` was rejected for the universal result page because its coverage is intermittent.

## Arsenal–Liverpool lesson

The GUI saying it "cannot confirm successful dribbles" was a **consumer-path failure**, not evidence that `successfulDribbles` is absent from FRL source data.

The fixture-detail query returned team-match statistics but did not expose the Player–Fixture evidence layer. The resolver exists to bridge that gap.

## Development work

Current relevant development PRs:

- PR #27 — Universal Variable Access contract / initial seam.
- PR #28 — canonical-context wiring foundation.
- PR #29 — runtime binding to audited research-field handlers.

The current runtime implementation branch is:

`feature/universal-variable-runtime`

A durable status record is also stored in:

`FRL_UNIVERSAL_VARIABLE_ACCESS_STATUS_2026-08-25.md`

## What has been implemented

The runtime resolver can:

- resolve explicit canonical aliases;
- resolve registered native source fields;
- use empirical season field availability rather than requiring one handwritten handler per native field;
- dispatch to existing generic family handlers;
- calculate the two approved derived player-match percentages;
- fail closed for unknown variables;
- fail closed when a native field is ambiguous across families without context;
- preserve source-field/provenance context.

## What remains

The broad architectural goal is **not yet equivalent to all 1,414 canonical variables being fully GUI-ready**.

The next implementation phase is to make the resolver **fully catalogue-driven across the validated FRL universe**, including:

- machine-readable natural grain;
- source family;
- source field(s);
- canonical alias where needed;
- derivation metadata where needed;
- semantic/validation status;
- empirical coverage;
- appropriate resolver dispatch.

Then test representative variables at every major grain.

## Required verification before integration

The project requires the fresh-session sequence and local assurance gates. Because the local Windows FRL workspace is not mounted in this environment, do not claim the following have passed until run in the project environment:

- 26/26 baseline;
- project health;
- universal resolver tests;
- relevant fixture/player GUI smoke tests.

## Suggested next task

Take the existing 1,414-variable canonical mapping as the source of truth and build a **catalogue-to-runtime bridge** so the resolver can automatically determine:

```text
variable
→ natural grain
→ source family
→ source field(s)
→ season coverage
→ identity requirements
→ retrieval handler
→ provenance
```

The end-state requirement is:

> **Every validated FRL variable is directly reachable by authorised consumers from the correct football context, without the GUI needing to know where the data lives.**
