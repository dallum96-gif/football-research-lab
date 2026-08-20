# Football Research Laboratory — UI Design System

## Purpose

This is the visual and interaction brief for the Football Research Laboratory GUI and future React/Next.js frontend.

The goal is to make the Laboratory feel like a coherent, professional football research product. The design system is technology-independent: Streamlit and React are implementation layers, not sources of visual identity.

## Design objective

The desired qualities are:

- professional;
- elegant;
- pretty;
- intuitive;
- natural;
- restrained;
- analytical;
- information-rich;
- fast to scan and easy to interrogate.

Reference in spirit:

**StatsBomb analytical clarity + Football Manager information depth + modern web-app usability.**

Do not copy either product literally.

## Avoid the AI-dashboard aesthetic

Do not drift towards:

- excessive rounded cards;
- gradients;
- glowing or neon effects;
- oversized hero blocks;
- giant navigation buttons;
- decorative badges everywhere;
- rainbow status colours;
- repetitive metric cards with icons;
- excessive whitespace that separates related information;
- generic SaaS marketing copy;
- visual decoration that competes with the football data.

The interface should look like a thoughtful human-designed analytics product.

## Current colour system

The current FRL site uses a **warm light analytical theme**. This replaces the older dark charcoal / blue-black application-canvas description that existed in earlier iterations of this document.

The authoritative implementation is `gui/theme.py`. Its semantic variables are the design-system source of truth:

- `--frl-bg`: warm off-white application background;
- `--frl-surface`: warm white primary surface;
- `--frl-surface-raised`: slightly darker warm raised surface;
- `--frl-border`: quiet structural border;
- `--frl-border-strong`: stronger structural divider;
- `--frl-text`: near-black primary text;
- `--frl-muted`: muted warm-grey secondary text;
- `--frl-muted-soft`: quieter metadata text;
- `--frl-accent`: FRL orange-red primary interaction accent;
- `--frl-accent-bright`: brighter accent state;
- `--frl-secondary`: restrained olive/green secondary/positive accent;
- `--frl-negative`: semantic negative state;
- `--frl-warning`: semantic warning state;
- `--frl-sidebar`: dark navigation surface.

The dark sidebar remains deliberate. The **main analytical canvas is light and warm**.

Colour communicates hierarchy, interaction and semantic state. It should not be used merely to decorate the page.

Do not reintroduce a dark application background merely because it appeared in older design documentation.

Do not introduce a generic React/SaaS palette, gradients, neon effects or framework-default colours during the Next.js migration.

## Typography

Use typography to establish hierarchy.

Preferred hierarchy:

1. small uppercase metadata / eyebrow;
2. page/entity name;
3. concise descriptive subtitle;
4. primary data;
5. supporting metadata.

The existing FRL font family and typography system remain authoritative across all workspaces and components.

Do not use giant marketing-style titles for normal research screens.

Do not allow a frontend framework to silently substitute its own default typography.

## Navigation

Navigation should be text-led, compact and left aligned.

The information architecture is defined separately by the FRL navigation contract. The visual system governs its presentation rather than redefining which workspaces exist.

Rules:

- all text shares the same left alignment;
- section headings are quiet and small;
- navigation items sit close together;
- no giant blocks around each navigation item;
- selected state should be subtle;
- icons should be small, monochrome line icons;
- icons should clarify meaning, not act as decoration;
- entity navigation should generally be subtle text/link interaction rather than large buttons;
- navigation should preserve the FRL's same-tab behaviour unless an explicit product decision changes it.

Avoid emoji and colourful app-style icons.

## Sidebar

The sidebar is navigation, not a marketing panel.

It should feel quiet enough to fade into the background while remaining easy to scan.

The dark sidebar is an intentional contrast against the current light analytical canvas.

The laboratory identity can be present, but the sidebar should not consume large vertical space with descriptive copy.

## Main page structure

Each research workspace should answer almost immediately:

1. Where am I?
2. What am I looking at?
3. What can I do here?

Preferred structure:

```text
SMALL CONTEXT LABEL

SUBJECT / PAGE TITLE

Concise context

Primary controls

────────────────────────────────

Primary data / evidence
```

Primary controls should be compact, visually integrated and easy to use.

## Horizontal rhythm

Prefer strong horizontal alignment to excessive vertical stacking.

Related controls should share a row when the screen width allows it.

Example:

```text
Season [▼]                         Team [▼]
```

rather than two large vertically stacked controls.

Controls should not dominate the page; the research output should.

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
- hover states should be subtle;
- do not make every cell look like a widget;
- exact values shown by a table must come from the same trusted Research Result that can feed associated charts or comparisons.

## Research Results and visualisation

Data visualisation is a first-class research capability.

The FRL should progressively standardise around a **Research Result** object that can drive multiple presentations without changing analytical meaning.

A Research Result may support:

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

It should carry, where applicable:

- result data;
- population definition;
- filters/exclusions;
- season/competition scope;
- temporal/as-of semantics;
- provenance/source lineage;
- metric or feature version;
- sample size;
- uncertainty and limitations;
- missing-data semantics;
- canonical entity/relationship references.

The visualisation should never silently recalculate the statistic using different filters or populations.

## Analytical visual vocabulary

The FRL should support a broad visual vocabulary, including:

- analytical tables;
- time-series and rolling-window charts;
- team/player comparisons;
- scatter and relationship views;
- distributions;
- ranking visualisations;
- H2H/matchup views;
- event timelines;
- league-position trajectories;
- home/away splits;
- player-role and performance profiles;
- model calibration/performance charts;
- probability/distribution displays;
- historical-state visualisations;
- research-population summaries;
- bespoke interactive views where the interaction itself aids research.

Use Plotly/React Plotly where mature analytical chart primitives are appropriate. Use bespoke React components when the visual interaction, entity linkage or research workflow requires finer control.

Plotly is an implementation tool, not the FRL visual identity.

Prefer visualisations that reveal relationships, changes over time, distributions, uncertainty or meaningful contrasts over decorative summaries.

## Entity navigation

Football entities are part of the information architecture.

Whenever sensible:

- player names should lead to Player Profile;
- fixture/opponent names should lead to Fixture Landing;
- team names should lead to Team Research contexts;
- charts and tables should preserve a route back to the underlying research object.

The interface should teach the user that football entities are navigable without surrounding every entity with a button.

## Identity-safe presentation

The GUI may display canonical identities and source identities for provenance or research inspection, but it must not invent identity mappings.

Important canonical semantics include:

```text
Fixture        = (season, fixture_id)
Player–Fixture = (season, fixture_id, canonical player identity)
Team identity  = season-local source identity -> verified persistent club identity
Player identity = season-aware source identity -> verified canonical player identity
```

Display names are labels, not canonical identity keys.

Unknown or ambiguous identity should remain visibly unresolved rather than being guessed.

## Metrics

Avoid the AI-dashboard pattern of many decorated cards.

Metrics should feel editorial and information-dense.

Use cards only when they materially improve comprehension.

## Fixture Explorer

The Fixture Explorer should feel like a football record, not a control panel.

Recommended hierarchy:

```text
FIXTURES

Manchester City
Premier League · 2025–26

[Season] [Team]

38 matches

DATE         OPPONENT                 VENUE   SCORE   RESULT
16 Aug       Wolverhampton            Away    0–4     W
```

The fixture rows should dominate the viewport.

Inside each row:

- opponent = strongest text/entity;
- score = strong and scannable;
- date = quiet metadata;
- venue = quiet metadata;
- result = clear but restrained.

Avoid a raw dataframe appearance and avoid oversized control blocks.

## Progressive disclosure

The first screen should tell the story quickly. Deeper evidence can live one click away.

Do not expose 40 metrics merely because they exist.

This applies especially to future Player Profiles:

```text
Overview
  ↓
Seasons / History / Matches
  ↓
Advanced / Comparisons / Career
```

The same principle should apply to statistical models and Research Results: show the key finding first, then expose diagnostics, methodology, uncertainty and evidence progressively.

## Evidence and provenance

Exploration should feel fluid.

Evidence should feel calmer and more deliberate.

A provenance section should make source lineage easy to inspect without dominating normal exploration.

For formal research and model outputs, provenance and methodology are part of the result and should remain accessible from the presentation layer.

## Statistical model presentation

The GUI should present model outputs as research objects rather than single numbers.

Where applicable, expose:

- prediction;
- probability/distribution;
- model/version;
- training population/window;
- evaluation period;
- evaluation metrics;
- calibration;
- uncertainty;
- baseline comparison;
- provenance/reproducibility.

Visual polish must never imply model validity.

## Incomplete data

Incomplete evidence is a valid state.

The UI should communicate:

> No data is currently available for this period.

rather than:

> The application is broken.

Do not fabricate missing history, convert missing values to false zeros without semantic justification, or imply that known coverage is a complete career.

## Final visual test

Before accepting a design change, ask:

> **Would this look normal in a serious football analytics product, or does it look like an AI made a dashboard?**

If the latter, simplify it.
