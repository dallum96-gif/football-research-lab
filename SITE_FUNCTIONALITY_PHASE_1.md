# Site Functionality Phase 1 — Fixture Research Experience

## Scope

The backend evidence foundation is now sufficiently rich to begin application functionality without repeatedly expanding the data plumbing.

Phase 1 starts with the existing Fixture Explorer → Fixture Landing Page flow.

The fixture landing page should be a presentation/query layer over the canonical fixture and validated evidence layers. It must not create a second fixture store.

## First user journey

Fixture Explorer
→ select canonical fixture
→ Fixture Landing Page
→ match context
→ team evidence
→ player participation and match evidence
→ provenance / data-quality context

## Design rules

- Preserve the canonical `(season, fixture_id)` fixture identity.
- Use the existing query layer rather than duplicating business logic in the GUI.
- Prefer progressive disclosure over dumping all 194 team fields and 72 player fields onto the first screen.
- Keep complete evidence accessible through deeper sections/research controls.
- Preserve source provenance and known limitations.
- Missing evidence must be represented as unavailable, not fabricated as zero.
- Player names and team names should become entity navigation targets where routes exist.
- The existing curated fixture statistics display remains compatible while richer evidence is introduced incrementally.

## Phase 1 target

Build a professional Fixture Landing Page using the existing canonical fixture route, then expose the new complete team/player evidence through structured sections rather than raw source dumps.

## Deliberately not in Phase 1

- natural-language query interface;
- new predictive models;
- manager data ingestion;
- injury-reason classification beyond currently supported source evidence;
- alternate external data sources;
- redesign of the entire application shell in one change.
