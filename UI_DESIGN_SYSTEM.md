# Football Research Laboratory — UI Design System

## Purpose

This is the visual and interaction brief for the GUI redesign.

The goal is not to make Streamlit prettier for its own sake. The goal is to make the Laboratory feel like a coherent, professional football research product.

## Design objective

The desired qualities are:

- professional
- elegant
- pretty
- intuitive
- natural
- restrained
- analytical
- information-rich

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

## Colour

Use a restrained palette:

- very dark charcoal / blue-black background;
- slightly lighter charcoal surfaces;
- off-white primary text;
- muted grey secondary text;
- one desaturated green accent.

Colour should communicate hierarchy and interaction rather than decorate the page.

Green is for things such as:

- active navigation;
- selected states;
- subtle positive/confirmed states;
- interactive emphasis.

Do not colour every football metric green.

## Typography

Use typography to establish hierarchy.

Preferred hierarchy:

1. small uppercase metadata / eyebrow;
2. page/entity name;
3. concise descriptive subtitle;
4. primary data;
5. supporting metadata.

Do not use giant marketing-style titles for normal research screens.

## Navigation

Navigation should be text-led, compact and left aligned.

Conceptual structure:

```text
FOOTBALL RESEARCH LABORATORY

EXPLORE
  [icon] League Table
  [icon] Fixtures

RESEARCH
  [icon] Players

ANALYSIS
  [icon] Head-to-Head
  [icon] Form & Streaks

MODELLING
  [icon] Prediction Lab

EVIDENCE
  [icon] Data Quality
  [icon] Provenance
```

Rules:

- all text shares the same left alignment;
- section headings are quiet and small;
- navigation items sit close together;
- no giant blocks around each navigation item;
- selected state should be subtle;
- icons should be small, monochrome line icons;
- icons should clarify meaning, not act as decoration.

Semantic icon examples:

- League Table — table/standings
- Fixtures — calendar/pitch
- Players — person/player
- Head-to-Head — opposing arrows / two entities
- Form & Streaks — trend line
- Prediction Lab — model/chart
- Data Quality — shield/check
- Provenance — document/link/chain

Avoid emoji and colourful app-style icons.

## Sidebar

The sidebar is navigation, not a marketing panel.

It should feel quiet enough to fade into the background while remaining easy to scan.

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

## Horizontal rhythm

Prefer strong horizontal alignment to excessive vertical stacking.

Related controls should share a row when the screen width allows it.

Example:

```text
Season [▼]                         Team [▼]
```

rather than two large vertically stacked controls.

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
- do not make every cell look like a widget.

## Entity navigation

Football entities are part of the information architecture.

Whenever sensible:

- player names should lead to a future Player Profile;
- fixture/opponent names should lead to the Fixture Landing Page;
- team names should lead to team research contexts.

Prefer subtle text/link interaction to large rectangular buttons.

The user should learn that football entities are navigable.

## Metrics

Avoid the AI-dashboard pattern of many decorated cards.

Metrics should feel editorial and information-dense.

Good:

```text
POINTS       89    RECORD       28–5–5
GOALS        96–34 POSITION     1st
```

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

[Opponent] [Venue] [Result]

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

## Evidence and provenance

Exploration should feel fluid.

Evidence should feel calmer and more deliberate.

A provenance section should make source lineage easy to inspect without dominating normal exploration.

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
