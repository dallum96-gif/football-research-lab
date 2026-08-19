# Site Functionality Phase 1 — Fixture Research Experience

The backend evidence foundation is now sufficiently rich to begin application functionality without repeatedly expanding the data plumbing.

Phase 1 starts with the existing Fixture Explorer → Fixture Landing Page flow.

The landing page is a presentation/query layer over the canonical fixture and validated evidence layers. It must not create a second fixture store.

## First user journey

Fixture Explorer → canonical fixture → Fixture Landing Page → match context → team evidence → player participation and match evidence → provenance/data-quality context.

## Rules

- Preserve canonical `(season, fixture_id)` identity.
- Use the existing query layer rather than duplicating business logic in the GUI.
- Use progressive disclosure; do not dump every raw source field onto the first screen.
- Keep complete evidence accessible through structured deeper sections.
- Preserve provenance and known limitations.
- Represent missing evidence as unavailable, not fabricated zero.
- Make team/player entities navigable where routes exist.
- Keep existing curated fixture statistics compatible while richer evidence is introduced incrementally.

## Phase 1 target

Build a professional Fixture Landing Page using the existing canonical fixture route, then expose the complete team/player evidence through structured sections.

## Deliberately not in Phase 1

Natural-language querying, new predictive models, manager ingestion, new external sources, and a wholesale application-shell rewrite.