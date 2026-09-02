# Football Research Laboratory — UI Design System

**Last reviewed:** 2 September 2026  
**Applies to:** Active Next.js + React product

For repository-memory governance see `FRL_DOCUMENTATION_SYNC_CONTRACT.md`.

## Purpose

This is the active visual and interaction brief for the Football Research Laboratory product.

The goal is a distinctive football research application: analytical, editorial, calm, playful in small doses, and recognisably FRL rather than a generic SaaS dashboard.

## Design character

Desired qualities:

- warm;
- editorial;
- analytical;
- restrained;
- information-rich;
- app-like rather than website-like;
- playful without becoming childish;
- clear enough for ordinary football exploration but deep enough for research.

The interface should feel intentionally human-designed.

## Active colour system

Current palette:

- background: `#f5f1e8`;
- primary surface: `#fffdf8`;
- raised / secondary surface: `#ebe6da`;
- primary text: `#171714`;
- muted text: `#68645c`;
- coral accent: `#e85d3f`;
- olive accent: `#9aaa42`;
- sidebar / dark anchor: `#1b1b18`.

Primary typeface: **Inter**.

This warm-light parchment system supersedes the earlier Streamlit-era dark-charcoal/green visual direction for the active Next.js product.

Historical screenshots/legacy CSS may still contain the old system and should not be treated as current design authority.

## Colour semantics

Use colour deliberately.

### Coral

Useful for:

- primary interactive emphasis;
- selected analytical state;
- key links/actions;
- selected points/highlights;
- restrained negative/result semantics where established by the product surface.

### Olive

Useful for:

- positive/confirmed states;
- complementary analytical emphasis;
- selected supporting signals;
- restrained win/result semantics where established.

### Dark sidebar

Acts as the strong visual anchor of the application and should remain quieter than the main content.

Do not turn the palette into a rainbow metric system.

## Avoid the generic AI-dashboard aesthetic

Avoid:

- gratuitous gradients;
- glowing/neon effects;
- excessive rounded cards;
- an icon on every metric;
- giant KPI walls;
- rainbow bars;
- decorative badges everywhere;
- huge empty hero blocks on analytical pages;
- generic SaaS copy;
- filler metrics added only to occupy layout space;
- visual chrome that competes with the football evidence.

A useful heuristic remains:

> **6 strong metrics are better than 24 filler metrics.**

## Typography and hierarchy

Use typography to establish a clear reading order.

Typical hierarchy:

1. quiet context / eyebrow;
2. subject or page title;
3. concise context/subtitle;
4. primary football information;
5. analytical detail;
6. provenance / limitations / secondary metadata.

Do not use giant marketing-style headings for normal research workspaces.

## Navigation

Navigation is compact application structure, not a collection of call-to-action buttons.

Rules:

- left aligned;
- quiet section labels;
- consistent text rhythm;
- active state clear but restrained;
- no large floating navigation cards;
- icons optional and subordinate to text;
- preserve working deep links between football entities and analytical contexts.

The active navigation reflects the current Next.js product, not historical Streamlit navigation lists.

## Entity language

Football identity should be visible and navigable.

Use the FRL `TeamKit` SVG language as a signature identity treatment where appropriate.

Teams, fixtures and eventually players should feel like reusable entities rather than decorative strings.

Prefer entity/text navigation to oversized buttons.

## Page rhythm

A normal research/product page should quickly answer:

1. Where am I?
2. What entity/population am I looking at?
3. What period/context applies?
4. What can I do next?

Prefer strong horizontal alignment and compact control rows over excessive vertical stacking.

## Tables and ledgers

Tables/ledgers are core research components.

Rules:

- primary names left aligned;
- numbers aligned consistently;
- compact rows;
- quiet borders;
- strong scan hierarchy;
- hover/selected state restrained;
- no dataframe-default appearance;
- no turning every cell into a widget.

The approved Team Profile / standalone Fixture ledger language is a useful reference for compact football records.

## Profiles

Profiles describe entities rather than attempting to expose every statistic.

A profile should emphasise:

- identity;
- records/current context;
- fixtures/history/form;
- navigation into deeper analytical surfaces.

Do not turn Team Profile / future Player Profile into giant statistical dashboards.

## Stats workspaces

Stats surfaces analyse entities and populations.

Current Team Stats information architecture:

```text
Team View | League Rankings | Compare later

Overview | Attack | Passing (including possession) | Defence | Discipline
```

The UI should make the relationship between value and population context legible without overwhelming the user.

Useful analytical primitives include:

- value;
- rank;
- percentile;
- coverage/sample sufficiency;
- trend;
- distribution;
- split;
- provenance/limitation drill-down.

Do not display rank/percentile as decorative certainty when the underlying population/coverage is not comparable.

## Signature vertical-list tiles

Family-level statistical browsing now uses **tiled vertical lists** as a recognisable FRL interaction and presentation pattern across Team and Player analytical surfaces.

The visual grammar is shared, but the analytical orientation must remain correct for each surface:

- **Team View:** one team across many metrics. Tiles group coherent measures vertically; each metric row shows the team's value and league context and can drill into the equivalent population ranking.
- **Team League Rankings:** many teams within one metric. Up to four metric leaderboards may be visible at once; each tile shows the governed top ten and links to the full ranking ledger.
- **Player League Rankings:** many players within one metric and an explicit player cohort. Up to four metric leaderboards may be visible at once, with role/minutes/club controls affecting visibility without redefining the governed cohort silently.

For selectable leaderboard surfaces:

- default to no more than four visible metric tiles;
- selecting a fifth metric requires removing one of the four currently visible metrics;
- reset metric-selection state when the analytical family/cohort changes rather than allowing stale family state to leak across views;
- preserve backend/governed rank values, including tie policy, rather than renumbering rows merely by their visual list position;
- keep the full ranking/detail ledger available as progressive disclosure rather than replacing deeper analysis with the top-ten view.

The four tile accents (coral, green, gold, blue) are a restrained categorical rhythm for this component family, not a universal semantic rainbow. Colour does not redefine metric meaning or ranking direction.

This layout is intended to become recognisable FRL product language: compact, colourful enough to feel playful, fast to scan, but still subordinate to governed football evidence.

## Metric cards

Metric cards are allowed when they genuinely improve comprehension.

A strong card answers a real analytical question and should normally contain only the information required to interpret the metric.

Potential elements:

- metric label;
- value;
- rank/context;
- quiet percentile/distribution indicator;
- coverage warning where necessary;
- route into ranking/distribution detail.

Avoid icon-led KPI tiles.

## Charts

Charts should support interpretation rather than decoration.

Rules:

- keep labels/axes quiet;
- preserve enough inner padding that strokes/points do not spill outside the chart;
- prefer one clear visual question per chart;
- avoid unnecessary legends/series;
- use FRL accent colours consistently;
- ensure the textual/statistical meaning remains understandable without relying only on colour.

Known Team Stats prototype issue: the rolling PPG chart currently requires an overflow/clipping correction before it is treated as polished.

## Progressive disclosure

The first view should communicate the story quickly.

Deeper statistical detail, methodology, provenance and source limitations can be one interaction away.

Do not hide important coverage limitations merely because they are technical; present them calmly at the point where they affect interpretation.

## Missing / partial evidence

Incomplete evidence is a valid analytical state.

Do not:

- fabricate history;
- convert unknown to zero;
- present partial-source rates as though they describe a complete season;
- rank incomparable coverage without qualification.

Useful language is calm and specific, for example:

`17 / 38 matches observed`

rather than an alarming generic application error.

## Provenance

Normal exploration should remain fluid.

Evidence/provenance information should be inspectable without dominating every screen.

A future common pattern should allow the user to inspect:

- source representation;
- metric definition;
- observed/eligible population;
- limitations;
- temporal/as-of context.

## Responsive/accessibility direction

The product is currently desktop-first but should not rely on inaccessible interaction assumptions.

As surfaces mature, treat keyboard navigation, contrast, semantic labels, responsive behaviour and visual regression as product-quality concerns rather than late polish.

## Frozen/currently approved surfaces

Unless a task explicitly reopens them:

- Homepage V1 is frozen;
- standalone Fixtures V1 is frozen for now;
- Team Profile V1 is frozen for now.

Team Stats remains an active analytical/product prototype and should evolve through the governed analytical architecture rather than visual expansion alone.

See `CURRENT_WORK.md` for the current product checkpoint.

## Final visual test

Before accepting a design change, ask:

> **Does this feel like FRL — warm, analytical, clear and intentional — or like a generic generated dashboard?**

If the latter, simplify and return the emphasis to the football evidence.
