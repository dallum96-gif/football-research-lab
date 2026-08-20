# Football Research Lab — GUI Design Contract

The Overview page is the visual benchmark for the entire application.

The GUI contract applies to the current site and to the future React + Next.js frontend. Frontend technology may change; the FRL visual identity and analytical semantics do not change unless a future design-system decision explicitly approves it.

## Current visual identity

The current FRL site uses a **warm light analytical interface**, not the older dark charcoal / blue-black application background.

The authoritative colour implementation is `gui/theme.py` and its FRL theme variables. The GUI must preserve those variables and their semantic roles rather than introduce page-specific palettes.

Current authoritative palette roles are:

- warm off-white application background: `--frl-bg`;
- warm white primary surface: `--frl-surface`;
- slightly darker warm raised surface: `--frl-surface-raised`;
- restrained charcoal borders: `--frl-border` and `--frl-border-strong`;
- near-black primary text: `--frl-text`;
- muted warm-grey secondary text: `--frl-muted` and `--frl-muted-soft`;
- FRL orange-red primary accent: `--frl-accent` and `--frl-accent-bright`;
- restrained olive/green secondary accent: `--frl-secondary`;
- semantic negative/warning colours through the existing theme variables;
- dark sidebar as a deliberate navigation surface, rather than a dark application canvas.

The current `gui/theme.py` definitions are authoritative. Do not revert the application to dark charcoal / blue-black merely because an older design document used that language.

The visual goal remains: **professional, elegant, analytical, restrained, information-rich and easy to interrogate.**

## Typography

Preserve:

- the FRL/global font family;
- typography hierarchy;
- spacing rhythm;
- small uppercase context/eyebrow labels;
- page/entity titles;
- concise context/subtitles;
- primary analytical data;
- supporting metadata.

The same approved font family and typography system must be used across every workspace and component. A Next.js migration must not substitute a framework-default font merely for convenience.

## Functional/UI principles

- Useful football data appears before advanced configuration.
- Advanced filters belong in collapsed expanders or progressive-disclosure controls.
- Tables are first-class analytical components.
- Visualisations are first-class analytical components.
- Never replace an approved table or visualisation design merely to add functionality.
- Never introduce native widgets where an existing shared FRL component already establishes the visual language, unless explicitly requested.
- A behavioural change must not alter font, size, colour, spacing, background, alignment or border styling unless requested.
- Prefer shared components and theme variables over page-specific styling.
- Fix classes of UI problems, not individual symptoms.
- Never duplicate navigation headers, section labels or workspace identities.
- Every page must have a clear primary purpose visible immediately.
- Entity interaction should prefer subtle text/link behaviour over large rectangular buttons.
- The GUI must present research results; it must not define source precedence, identity mappings, metric formulas, temporal rules, leakage rules or fallback semantics.

## Selector pattern

Selectors are part of the FRL visual hierarchy, not generic form widgets placed on top of a page.

The current Next.js Fixture Explorer establishes the selector precedent for future work:

### Context selectors

Selectors that define the identity/context of the current page should be integrated directly into the heading hierarchy.

Pattern:

```text
FIXTURES

Arsenal  ⌄                         Season  2025–26 ⌄
Premier League · fixture history
```

Rules:

- the primary entity name remains the dominant visual element;
- the team selector should be expressed through a discrete chevron/action attached to the title rather than a duplicate visible team input;
- the season selector remains a small, transparent, typographic control in the heading context area;
- no surrounding card, pill, dark background or raised box around context selectors;
- use quiet underline/border treatment only where necessary to communicate interactivity;
- use the FRL muted text and orange-red accent sparingly for focus/active states;
- preserve the existing FRL typography and spacing hierarchy.

### Exploration selectors

Selectors that refine a research population should sit inside a clearly purposeful analytical section below the page context.

Pattern:

```text
EXPLORE
Fixture view

Opponent     All opponents  ⌄
Venue        Home + Away    ⌄
Result       All results    ⌄
```

Rules:

- the section must communicate why the controls exist;
- selectors should reuse the same transparent, typographic treatment established by the heading/Season control;
- avoid generic bordered input boxes and dashboard-style control cards;
- controls should feel like part of the text/layout hierarchy rather than standalone UI objects;
- the section is the appropriate place to add progressive disclosure such as single-season vs multi-season viewing and compact time-range/comparison controls;
- changing exploration controls must not change canonical entity identity semantics.

### General rule

When a new page needs a selector, first ask whether it is:

```text
context
or
exploration
```

Then use the corresponding FRL selector pattern rather than inventing a new control style.

The final test is:

> **Does the selector look like something the FRL naturally says, or like a generic browser widget that has been stuck onto the page?**

If the latter, simplify it.

## Change protocol

Before modifying an existing page:

1. Identify the current approved state.
2. Read the active theme and shared component implementation.
3. Identify exactly what is changing.
4. Preserve everything else.
5. Check whether the requested behaviour can be implemented using an existing shared component or architectural seam.
6. Confirm the change does not alter canonical identifiers, query semantics or provenance.
7. Do not redesign surrounding UI unless the design-system decision requires it.

After modifying:

- Verify syntax/build.
- Verify route still exists.
- Verify existing data still renders.
- Verify controls still work.
- Verify no deprecated APIs were introduced.
- Verify the visual contract has not changed unintentionally.
- Verify canonical entity references remain unchanged.
- Verify navigation remains same-tab unless an explicit product decision changes that behaviour.

## Research Result presentation

The FRL should progressively standardise around a reusable **Research Result** concept.

A Research Result is a presentation-ready representation of a trusted analytical/query result. It should be capable of driving multiple views without changing analytical meaning.

Where applicable, a Research Result should expose:

- result data;
- population definition;
- filters and exclusions;
- season/competition scope;
- temporal/as-of semantics;
- provenance/source lineage;
- metric or feature version;
- sample size;
- uncertainty and limitations;
- missing-data semantics;
- canonical entities/relationships represented by the result;
- optional methodology and reproducibility metadata.

The same Research Result should be able to feed, where useful:

```text
Table
Chart
Comparison
Timeline
Distribution
Summary
Export
Provenance / methodology
```

The frontend must not silently recalculate an analytical quantity differently from the trusted query/research layer.

## Analytical visualisation principles

Data visualisation is part of the research product, not decorative UI.

Use the best presentation for the research question:

- Plotly/React Plotly for mature analytical chart primitives where appropriate;
- bespoke React visual components where interaction itself is part of the research experience;
- analytical tables for inspectable exact values;
- coordinated chart/table/comparison views where shared selection improves reasoning.

Plotly is a tool, not the FRL visual identity.

Prefer visualisations that reveal:

- relationships;
- change over time;
- distributions;
- uncertainty;
- meaningful contrasts;
- historical state;
- model behaviour;
- research-population differences.

Avoid decorative visualisations that do not help answer a football question.

## Identity and route safety

The frontend must preserve the canonical FRL identity model exactly.

### Fixture

Canonical fixture identity:

```text
(season, fixture_id)
```

A source-specific match ID is evidence attached to the canonical fixture, not a competing canonical identity.

### Team

Season-local source team identities must remain distinct from persistent longitudinal club identities.

```text
season-local source team identity
        ↓
verified identity mapping
        ↓
persistent team identity
```

### Player

Player identities are season-aware and fail-closed.

```text
season context + source player identifier
        ↓
verified identity mapping
        ↓
canonical player identity
```

Unknown, ambiguous or conflicting mappings must not be guessed by the frontend.

### Player–Fixture

Canonical grain:

```text
(season, fixture_id, player_id)
```

### Team–Fixture

Canonical grain:

```text
(season, fixture_id, verified team identity/context)
```

Season and competition are contextual dimensions, not substitutes for canonical entity identity.

Routes, API payloads, client state and cached results must retain whatever combination of canonical identity and temporal/context dimensions is required to resolve the underlying research object unambiguously.

Display names must never become identity keys merely because they are convenient for UI code.

## Tables

Tables are core research components, not generic dataframes.

Rules:

- names left aligned;
- numbers aligned consistently;
- quiet borders;
- compact rows;
- minimal or no zebra striping unless it adds genuine readability;
- no unnecessary icons;
- clear hierarchy between primary and supporting columns;
- subtle hover states;
- do not make every cell look like a widget;
- preserve exact values and research semantics represented by the underlying result.

## Entity navigation

Football entities are part of the information architecture.

Whenever sensible:

- player names should lead to Player Profile;
- fixture/opponent names should lead to Fixture Landing;
- team names should lead to Team Research contexts;
- result views should preserve navigability back to the canonical research object.

The user should learn that football entities are navigable without being surrounded by button-heavy UI.

## Metrics

Avoid the AI-dashboard pattern of many decorated cards.

Metrics should feel editorial and information-dense.

Use cards only when they materially improve comprehension.

## Fixture Explorer

The Fixture Explorer should feel like a football record, not a control panel.

The fixture rows should dominate the viewport. Controls should be compact, clear and easy to change.

Recommended hierarchy:

```text
FIXTURES

Manchester City  ⌄
Premier League · fixture history                         Season  2025–26 ⌄

──────────────────────────────────────────────────────────────────

EXPLORE
Fixture view

Opponent     All opponents  ⌄
Venue        Home + Away    ⌄
Result       All results    ⌄

38 fixtures shown

DATE         OPPONENT                 VENUE   SCORE   RESULT
16 Aug       Wolverhampton            Away    0–4     W
```

The heading's Team/Season controls establish page context. The Explore section is deliberately separate so additional analytical controls can be added without damaging the identity hierarchy.

The initial Explore controls are:

- opponent selection;
- venue filter;
- result filter.

The intended next capabilities are:

- single-season vs multi-season viewing;
- compact time-range/comparison control;
- comparison of a team against selected opponents across multiple seasons where the underlying Research Result supports it.

These are progressive additions to Fixture Explorer, not reasons to overload the page header.

Inside each row:

- opponent = strongest text/entity;
- score = strong and scannable;
- date = quiet metadata;
- venue = quiet metadata;
- result = clear but restrained.

Avoid raw dataframe appearance and avoid oversized control blocks.

## Progressive disclosure

The first screen should tell the story quickly. Deeper evidence can live one click away.

Do not expose 40 metrics merely because they exist.

Use deeper views for:

```text
Overview
  ↓
History / Matches / Comparisons
  ↓
Advanced analysis / Methodology / Provenance
```

## Evidence and provenance

Exploration should feel fluid.

Evidence should feel calmer and more deliberate.

A provenance section should make source lineage easy to inspect without dominating normal exploration.

When a Research Result is formal or model-derived, the UI should make methodology, coverage, uncertainty and provenance inspectable.

## Incomplete data

Incomplete evidence is a valid state.

The UI should communicate:

> No data is currently available for this period.

rather than:

> The application is broken.

Do not fabricate missing history, convert missing values to false zeros without semantic justification, or imply that known coverage is complete.

## Model-result presentation

Model outputs should be presented as research objects, not merely headline predictions.

Where applicable, expose:

- prediction;
- probability/distribution;
- model name/version;
- training window/population;
- evaluation period;
- evaluation metrics;
- calibration;
- uncertainty;
- baseline comparison;
- provenance and reproducibility metadata.

Visual polish must never be allowed to imply model validity.

## Final visual test

Before accepting a design change, ask:

> **Would this look normal in a serious football analytics product, or does it look like an AI made a dashboard?**

If the latter, simplify it.
