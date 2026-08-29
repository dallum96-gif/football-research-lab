# Football Research Laboratory — Interface Design Principles V2

**Status:** Active interface/product design authority  
**Created:** 29 August 2026

## Purpose

This document records the active visual and interaction principles for the FRL Next.js product.

It exists because the product direction has evolved beyond parts of the older `UI_DESIGN_SYSTEM.md`. Where this document conflicts with older visual or interaction guidance, **this V2 document takes precedence**. The older document remains useful historical context, especially for general principles such as avoiding generic dashboard aesthetics, preserving clear hierarchy, and treating football entities as navigable.

The design target is not a conventional statistics website and not a generic SaaS dashboard.

FRL should feel like one coherent, modern football research environment: **integrated, seamless, beautiful, playful, information-rich, and calm enough to use for serious analysis.**

---

## 1. Core product feeling

The interface should feel like a single application rather than a collection of separate webpages.

The desired qualities are:

- modern;
- elegant;
- beautiful;
- playful without becoming gimmicky;
- integrated;
- seamless;
- editorial where appropriate;
- analytical where appropriate;
- information-rich without being cramped;
- visually distinctive enough to feel like FRL rather than a template.

The strongest reference is the **actual successful execution of earlier FRL interfaces such as the Streamlit Overview and Prediction Lab**, not necessarily every older written styling rule.

Future design decisions should preserve what made those interfaces enjoyable while translating the experience into the active Next.js architecture.

---

## 2. One workspace, multiple views

The primary FRL interaction principle is:

> **One workspace, multiple views — not one enormous page.**

A football subject and its context should remain stable while the central workspace changes.

For example, a Team workspace may keep:

```text
ARSENAL                                      2024–25 ▾

Overview     Records     XI     Fixtures     Stats
────────

[ current view ]
```

The team, competition/season context, and workspace navigation remain visible. Selecting a view changes the content underneath rather than forcing the user through disconnected pages or a full refresh.

The same principle should apply to Player, League, Fixture, Head-to-Head and modelling workspaces where appropriate.

---

## 3. Persistent context

FRL interfaces should favour **persistent context and interchangeable views over vertically stacked information**.

The user should not have to repeatedly re-establish:

- which team/player/fixture/league they are looking at;
- which season is selected;
- which research workspace they are in.

Entity identity, season/competition context and primary workspace navigation should remain stable while moving between views.

This should make transitions such as:

```text
Team → XI → Player → Matches → Fixture
```

feel like movement through one connected research environment.

---

## 4. Viewport-first design

The important content of a normal desktop view should **ideally fit within the viewport without requiring vertical scrolling**.

This is not an absolute prohibition on scrolling. Long fixture lists, large tables and deep research outputs may legitimately scroll.

The governing rule is:

> **Do not stack multiple substantial views vertically merely because the information is available.**

Avoid pages that become:

```text
hero
↓
metrics
↓
chart
↓
chart
↓
table
↓
records
↓
XI
↓
fixtures
↓
more statistics
```

Instead, divide genuinely different tasks into fast, context-preserving views or tabs.

Where scrolling is necessary, prefer scrolling **inside the relevant content region** while retaining useful workspace context where practical.

---

## 5. Navigation depth is preferable to cramming

FRL should use progressive disclosure confidently.

> **Navigation depth is preferable to information density when the additional interaction preserves context and feels effectively instantaneous.**

A fast tab/view transition is cheap. A visually exhausting page is expensive.

Do not expose dozens of metrics or multiple analytical modes at once simply to avoid an extra click.

Primary tabs should be limited to meaningful conceptual views. Secondary tabs may be used inside deeper analytical surfaces where they reduce clutter.

Example:

```text
Team Stats

Overview    Attack    Possession    Passing    Defence    Discipline
```

---

## 6. Seamless transitions

The Next.js application should behave like an application rather than a sequence of document reloads.

Where technically appropriate:

- use client-side navigation;
- preserve team/player/season context;
- update the URL so views remain bookmarkable and browser Back/Forward remains meaningful;
- avoid full-page refreshes and visual flashes;
- reuse/carry already loaded context where safe;
- use subtle transitions between views.

Motion should be restrained. A short soft fade or slight positional movement is enough to make transitions feel polished. Avoid theatrical animation.

---

## 7. Distinct workspace archetypes

Different FRL surfaces have different jobs. They should share one design system without all becoming the same kind of dashboard.

### Profiles — identity, records and story

Team and Player Profiles are **not gritty statistics pages**.

They should feel closer to a beautifully designed football record or season story.

Appropriate content includes:

- identity;
- season context;
- league finish/record;
- headline achievements;
- key records;
- most-played XI;
- leading scorer/appearances;
- form or season trajectory;
- important/recent fixtures;
- compact routes into deeper research.

The first question is:

> **Who/what was this team or player in this period?**

not:

> How many analytical metrics can we fit here?

### Stats — analytical exploration

Stats workspaces are where FRL can become denser.

They should support:

- analytical tables;
- distributions;
- trends;
- percentiles/rankings;
- comparison;
- home/away and contextual splits;
- meaningful graphs;
- deeper variable exploration.

Even here, use tabs/subviews rather than turning the page into a long wall of charts.

### Labs — interactive research and modelling

Prediction Lab and future research laboratories should feel exploratory and interactive.

They can carry forward the enjoyable spirit of the earlier Streamlit Prediction Lab while remaining visually integrated with the rest of FRL.

Labs should expose inputs, outputs, assumptions, evidence and model/research context without becoming generic form-heavy control panels.

---

## 8. Profiles should privilege records over stats

A Team Profile might include views such as:

```text
Overview     Records     XI     Fixtures     Stats
```

A season overview might communicate, at a glance:

- league finish;
- points;
- W-D-L record;
- goals for/against or goal difference;
- a compact season-form/trajectory visual;
- leading scorer;
- most appearances;
- clean sheets or another meaningful record.

A Records view may present items such as:

- biggest win;
- biggest defeat;
- longest winning run;
- longest unbeaten run;
- top scorer;
- most appearances;
- clean sheets;
- other genuinely meaningful season records.

These should be presented editorially, not as repetitive KPI cards.

---

## 9. Most-played XI as a profile-native visual

A Most Played XI is an example of the kind of playful, football-native visual that belongs naturally on a Team Profile.

It should use a carefully designed pitch/formation presentation and existing governed player/appearance evidence.

It should not imply tactical intent unless the underlying evidence supports that claim. If the XI is derived from appearances/minutes, label it accordingly.

Player names should be navigable into Player workspaces where those routes exist.

This is representative of the broader principle:

> **Playfulness should come from football-shaped interactions and visualisations, not decorative gimmicks.**

---

## 10. Colour direction

The active Next.js warm-light identity is the current visual foundation.

Current established tokens include:

- warm parchment/off-white page backgrounds;
- creamy raised surfaces;
- near-black/charcoal typography;
- coral/orange primary accent;
- olive/green secondary accent;
- dark navigation/sidebar contrast.

Future design should evolve this palette deliberately rather than reverting automatically to older dark-interface guidance.

Colour may be richer than a one-accent analytical dashboard, but it must remain controlled and coherent.

Use colour to:

- establish identity and hierarchy;
- distinguish meaningful series/categories;
- signal interaction;
- support football/result semantics;
- give the application warmth and personality.

Avoid rainbow dashboards, arbitrary per-card colours, neon effects or decoration unrelated to meaning.

---

## 11. Typography as product identity

Typography should do substantial visual work.

Use a consistent hierarchy for:

- entity/page names;
- small uppercase editorial labels;
- large or tabular record numbers;
- navigation labels;
- chart titles/annotations;
- table headers;
- supporting explanatory copy.

Entity names may be confident and prominent without becoming marketing-style hero text.

Numerical information should be highly scannable and use tabular alignment where useful.

Charts and tables must use the same typographic system as the rest of the application so they feel native rather than embedded.

---

## 12. Charts are FRL components

Graphs must look designed as part of the website, not pasted in from a plotting library.

Default chart principles:

- warm/transparent or native-surface backgrounds;
- minimal framing;
- subtle grid lines;
- typography matching the surrounding interface;
- colour drawn from the FRL palette;
- direct labels where they improve comprehension;
- restrained legends;
- precise hover states/tooltips;
- meaningful highlighting rather than decorative colour;
- responsive sizing that respects the viewport-first layout.

Prefer a limited visual vocabulary that becomes recognisably FRL across the product.

Examples may include:

- season trajectories;
- form strips;
- rank/percentile distributions;
- compact sparklines;
- goal/shot trends;
- comparison charts;
- model probability visualisations.

Charts should support a research question, not exist simply because a metric can be plotted.

---

## 13. Tables are designed research surfaces

Tables should be deliberate application components rather than raw dataframe output.

Use:

- clear entity emphasis;
- consistent number alignment;
- restrained separators;
- native typography;
- compact but comfortable row height;
- subtle hover/selection states;
- meaningful sorting/filtering where useful;
- embedded mini-bars/sparklines only when they improve comprehension;
- restrained conditional colour.

Football entities in tables should be navigable wherever appropriate.

Tables should visually belong to the same page as surrounding charts and records.

---

## 14. Playful but serious

FRL should be enjoyable to explore.

Appropriate playfulness includes:

- pitch diagrams;
- form/result sequences;
- season arcs;
- record callouts;
- compact scoreline treatments;
- interactive player/fixture navigation;
- subtle motion and hover feedback;
- visually expressive but evidence-backed football graphics.

Avoid playfulness that undermines research credibility:

- cartoon decoration unrelated to data;
- gratuitous animation;
- novelty icons everywhere;
- decorative gradients/glows;
- game-like effects that obscure analytical meaning.

---

## 15. Integration across pages

Every new FRL page should feel like another room in the same product.

Shared concepts should have shared visual behaviour:

- entity links;
- season selectors;
- tabs;
- charts;
- tables;
- record typography;
- unavailable states;
- provenance affordances;
- navigation transitions.

Do not design Team, Player, League and Prediction pages independently and then attempt to make them match afterwards.

Reusable visual components and tokens should emerge as the pages are built.

---

## 16. Evidence, limitations and unavailable states

Beauty must never imply certainty the evidence does not support.

Missing or partial evidence should remain visible as a valid product state.

Do not fabricate records, inferred careers, tactical claims, historical availability or source completeness to make a profile look richer.

Provenance and limitations should be available without dominating normal exploration.

The interface should separate:

- source evidence;
- derived presentation;
- derived research metrics;
- model output;
- market evidence.

---

## 17. Page acceptance questions

Before accepting a new interface, ask:

1. Does the user immediately know what entity/season/context they are viewing?
2. Does the main view fit comfortably within a normal desktop viewport where practical?
3. Are we showing one coherent task/view rather than cramming several pages together?
4. Can the user move to adjacent research views without losing context?
5. Does navigation feel instantaneous and continuous?
6. Does the page feel like FRL rather than a generic dashboard/template?
7. Are typography, tables and charts visually integrated?
8. Is colour coherent and purposeful while still giving the product personality?
9. Is the page enjoyable to explore?
10. Are evidence and uncertainty represented honestly?
11. Could any section be removed or moved behind a tab without reducing the value of the current view?

If the answer to the final question is yes, prefer progressive disclosure.

---

## 18. Working design rule

The central rule for future interface work is:

> **Keep the football subject and context stable; let the research view change around it. Make each view beautiful enough to enjoy, focused enough to understand immediately, and connected enough that FRL feels like one continuous application.**
