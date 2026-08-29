# FRL Fixture Evidence Architecture V1

**Status:** additive backend seam
**Date:** 27 August 2026

## Purpose

Provide one governed access path for fixture-level evidence required by the Next.js fixture/result experience without embedding source-specific extraction or fixture-specific presentation data in the GUI.

## Source boundary

The FRL source mapping already records PulseLive match-centre resources at fixture grain, including `resources.events.payload`, `resources.lineups.payload`, goals, cards, substitutions, formations, lineup players and managers. These resources are preserved as source evidence and attached through the verified `canonical_fixture_to_source_match` relationship.

## Runtime pathway

```text
canonical (season, fixture_id)
        ↓
verified fixture → PulseLive source-match relationship
        ↓
preserved PulseLive snapshot
        ↓
source normalisation
        ↓
fixture_evidence.py
        ↓
fixture_research_access.py
        ↓
existing Universal Research Access for player-match participation
        ↓
query_api.fixture_evidence()
        ↓
frontend
```

## Analytical grain

Events remain Event-level observations. Lineup/player participation remains Player–Fixture grain. Formation and managers are fixture/team contextual evidence. There is no fixture × player × event Cartesian expansion.

## Events

Supported mapped event families are normalised independently:

- goals;
- cards;
- substitutions.

A source event ID is retained when present; the adapter never fabricates a provider event ID. Goal `assistPlayerId` is retained as a source-player relationship. Event player names are only enriched from the same fixture's lineup source-player namespace and therefore do not form a canonical identity join.

## Lineups

Lineup players retain source player ID, source name, position, shirt number and source team ID. Participation classification comes from the existing Player–Match evidence through Universal Research Access (`minutesPlayed`, `substitute`, `venue`). Missing participation observations remain `unknown`.

Source player IDs are separately checked through the existing season-aware player identity bridge. Ambiguous/unresolved relationships remain fail-closed.

## Formation and placement

Formation is exposed when the preserved PulseLive lineup payload contains a formation value. Explicit tactical placement remains source evidence only when the preserved formation lineup contains numeric x/y coordinates.

The frontend-facing fixture research result may additionally expose presentation-only placement with status `DERIVED_FORMATION_LAYOUT`. That layout is permitted only when all of the following agree deterministically:

- the verified Player-Match participation identifies exactly eleven starters for the side;
- the source formation string describes exactly ten outfield positions;
- the preserved PulseLive formation lineup supplies one goalkeeper line followed by line sizes matching that formation;
- the source formation order contains exactly the same eleven source-native players as the verified starting XI.

Derived x/y values are diagram geometry, not football/source evidence. Their provenance must identify the source formation and ordering fields, state that explicit source coordinates were absent, and classify the output as `PRESENTATION_ONLY`. If these checks do not close, placement remains unavailable; player positions or names must not be used to guess a layout.

## Managers

Manager records are retained from the mapped PulseLive lineup payload with source manager ID, first name, last name and type. They remain source-native evidence unless a separate canonical manager identity contract is established.

## Missing data

The result distinguishes:

- `AVAILABLE` — validated source evidence is present;
- `UNAVAILABLE` — no preserved evidence is available;
- `KNOWN_EXCEPTION` — evidence exists but a known relationship/data-quality condition prevents full promotion.

No missing event, participation, formation or manager value is converted to a fabricated zero or guessed value.

## Provenance

The result retains season, canonical fixture ID, source match ID, source path, resource endpoint/retrieval metadata where present, relationship contract/status and source-player IDs.

## Historical integrity

The canonical fixture remains `(season, fixture_id)`. PulseLive source match IDs are attached evidence only. Source snapshots are read locally; the runtime seam does not fetch current live upstream data during frontend rendering.

## Validation requirement

`validate_fixture_evidence_coverage.py` traverses the canonical fixture master and records event, lineup, formation, manager and identity coverage. The full 3,800-fixture run must be executed in the FRL local source workspace before the seam is declared universally covered.
