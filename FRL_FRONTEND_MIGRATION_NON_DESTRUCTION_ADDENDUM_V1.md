# FRL Frontend Migration — Non-Destruction Addendum V1

## 1. Migration is additive first

The move from Streamlit to React/Next.js is a presentation-layer migration, not permission to rewrite trusted data or research infrastructure.

Until validated parity is established:

- preserve the Streamlit implementation as historical/reference material;
- avoid deleting working GUI components merely because React replacements exist;
- keep rollback paths available;
- introduce new API/result contracts alongside existing query paths where possible.

## 2. Preserve canonical semantics

A frontend migration must not change:

- fixture identity `(season, fixture_id)`;
- season-local versus persistent team identity;
- season-aware player identity resolution;
- Player–Fixture grain;
- Team–Fixture semantics;
- canonical joins and relationship integrity;
- provenance meaning;
- historical/as-of definitions.

A change is not equivalent merely because row counts, labels or screenshots look correct.

## 3. Preserve visual identity while changing technology

Next.js provides a new implementation medium, not permission to invent a new FRL visual identity.

The current light theme, typography, spacing rhythm, navigation character, compact layouts and restrained accent system remain authoritative through `gui/theme.py`, `GUI_DESIGN_CONTRACT.md` and `UI_DESIGN_SYSTEM.md`.

## 4. Research-result equivalence

When replacing a Streamlit view, compare the underlying Research Result or trusted query output before comparing pixels.

The replacement should preserve:

- population;
- filters;
- temporal scope;
- values;
- missing-data state;
- provenance;
- methodology.

## 5. Regression discipline

For each migration stage:

1. establish the current working baseline;
2. define the exact change surface;
3. preserve unrelated behaviour;
4. validate the new frontend path;
5. compare canonical/query results;
6. run the existing research and project-health gates;
7. review the result before deprecating the old implementation.

Broad destructive cleanup is prohibited merely to make a migration appear tidy.

## 6. Navigation safety

Canonical routes should remain same-tab and identity-safe unless an explicit product decision changes that behaviour.

Navigation parameters must preserve the identity/context required to resolve the canonical research object.

## 7. Rollback

Every meaningful frontend migration step should be reversible through version control and should retain the previous working implementation until the replacement is validated.
