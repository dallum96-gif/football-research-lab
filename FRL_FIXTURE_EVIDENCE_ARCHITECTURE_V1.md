# Football Research Laboratory — Fixture Evidence Architecture V1

**Status:** Core backend seam / additive architecture
**Date:** 27 August 2026

## Purpose

Provide a universal fixture-level evidence composition path for the Next.js/React
fixture experience without moving source knowledge or fixture-specific data into
the frontend.

## Canonical request

```text
season + fixture_id
```

Canonical fixture identity remains the existing `(season, fixture_id)` pair.
Source match IDs are attached evidence, not competing identities.

## Evidence grains

### Event

Events remain event-grain observations:

```text
fixture → event → event
```

The currently validated reusable event materialisation is the FRL goal-event
evidence produced by the existing `build_fixture_goal_evidence_v5.py` pathway.
No cards, substitutions, assists or other event types are fabricated when
structured evidence is not independently validated.

### Player-fixture

Lineup/participation remains player-fixture grain. Existing Player-Match source
rows and the established `player_identity_to_player_match_observations`
relationship are reused. Participation is classified only from the existing
`substitute` and `minutesPlayed` fields.

```text
not substitute + minutes > 0  → starting
substitute + minutes > 0      → sub_in
substitute + minutes = 0      → bench
otherwise                     → unknown
```

No tactical placement is inferred.

## Universal consumer path

```text
validated source evidence
        ↓
existing canonical fixture/source-match relationship
        ↓
source-family adapter / event evidence adapter
        ↓
Universal Research Access for reusable player-match variables
        ↓
fixture_research_access.fixture_research_result()
        ↓
structured Research Result envelope
        ↓
API / frontend
```

## Explicit unavailable evidence

The seam currently returns `UNAVAILABLE` for:

- historical formation;
- tactical pitch coordinates/lineup placement;
- historical managers;
- structured assists when independently structured assist evidence is absent;
- event families not currently backed by validated event-level data.

## Coverage validation

`validate_fixture_evidence_coverage.py` iterates the ten canonical seasons
2016-17 through 2025-26 and validates every canonical fixture exposed by the
existing fixture master. It records source-match coverage, event coverage,
lineup coverage, formation/manager coverage, identity failures, duplicate
observations and fail-closed exceptions.

The validator is intentionally read-only.

## Non-destruction

This architecture is additive. It does not rewrite the Universal Research
Access layer, variable resolver, identity registries, relationship contracts,
Player-Match adapters, Match Statistics, or the frontend fixture route.
