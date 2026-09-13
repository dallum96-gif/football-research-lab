# Football Research Laboratory — UI Design System

**Last reviewed:** 13 September 2026  
**Applies to:** Active Next.js + React product and current reference-design work

For repository-memory governance see `FRL_DOCUMENTATION_SYNC_CONTRACT.md`.

## Purpose

This document defines FRL's current visual and interaction direction.

FRL should feel like a distinctive football research product: analytical, premium, editorial, deliberate, information-rich and human-designed. It should not resemble a generic SaaS dashboard, AI template, sportsbook HUD or game interface.

`FRL_LUXURY_DESIGN_CONSTITUTION.md` defines the higher-level design discipline. This file translates that discipline into current product rules.

## Authority and migration rule

The product is mid-migration.

For live design work, use this precedence:

1. current implemented reference surface / accepted current visual direction;
2. `FRL_LUXURY_DESIGN_CONSTITUTION.md`;
3. this document;
4. older screenshots, CSS tokens and historical design notes.

Do **not** resurrect an old visual treatment simply because its token remains in `globals.css` or an older page still uses it.

The root variables in `web/src/app/globals.css` still contain the earlier warm parchment/coral/olive token set. Those values describe legacy/migration-era implementation state; they are not the governing colour brief for new FRL work.

## Current design character

Desired qualities:

- dark;
- premium;
- editorial;
- analytical;
- calm;
- restrained;
- football-first;
- information-rich;
- digitally precise;
- playful only where it improves comprehension;
- composed rather than assembled from UI components.

A useful test remains:

> **FRL should look expensive even in black and white.**

## Current colour direction

The current intended product language is a **dark editorial system**.

Use the following semantic direction rather than treating this document as a frozen token file:

- near-black / charcoal for primary structural surfaces;
- slightly differentiated dark material surfaces where hierarchy genuinely requires them;
- warm ivory / cream for primary text;
- muted grey / stone for secondary text and metadata;
- restrained coral / orange for the principal FRL brand/action emphasis;
- olive / green for positive, confirmed or football-result semantics where appropriate;
- subtle blue/grey support tones only where they improve hierarchy;
- red only for meaningful negative/result/risk semantics;
- thin low-contrast borders and rules rather than heavy containers.

Avoid lime green as a brand or decorative accent. Green should not become FRL's default visual identity.

Do not convert the palette into a rainbow metric system.

Exact token consolidation remains migration work. Until it is completed, inspect the target surface before changing colours and avoid assuming legacy root variables represent the intended final theme.

## Typography

Typography should carry status and hierarchy.

Primary interface/data typography should remain clean, highly legible and digitally precise.

Editorial serif or italic-serif treatments may be used sparingly for high-value identity, headline or editorial moments where they strengthen the reference design. They must not reduce data legibility or turn every page into a magazine cover.

Typical hierarchy:

1. quiet context / eyebrow;
2. entity, fixture or page identity;
3. concise context/subtitle;
4. primary football information;
5. analytical evidence;
6. provenance / limitations / secondary metadata.

Do not use giant marketing-style headings in normal research workspaces merely for spectacle.

## FRL wordmark

The compact **`FRL.`** wordmark is the primary brand mark.

- the full stop is part of the mark;
- the mark remains compact and typographic;
- the full phrase **Football Research Laboratory** is supporting descriptor copy;
- do not embellish the wordmark with gradients, icons, crests or decorative symbols.

## Navigation

The active reference direction uses a **two-level top navigation system**, replacing the older assumption that a permanent dark sidebar is the primary shell.

The current shell language is:

- simple global navigation;
- contextual second-row navigation;
- shared content rails between shell and page body;
- restrained active-state treatment;
- controls appear where relevant instead of remaining permanently visible;
- football entity/deep-link context must survive navigation.

Do not add large floating navigation cards or an icon to every navigation item.

## Layout and composition

Compose pages before reaching for containers.

Prefer:

- strong shared alignment rails;
- deliberate whitespace;
- thin rules;
- typographic hierarchy;
- compact contextual controls;
- natural football reading order;
- progressive disclosure.

Avoid stacking independent cards simply because a component exists.

Rounded containers are permitted where the current reference design genuinely uses them, but they must not become the default structure for every fact or metric.

## Football identity

Football identity should be visible and navigable.

Current reference work supports richer identity through:

- club crests;
- stadium imagery;
- team names and season context;
- fixture/result identity;
- kits where analytically/productively useful.

Visual assets must not replace governed identity relationships. Team names, season-local identity and persistent club identity still come from the analytical/data architecture.

## Fixtures and results

Fixtures is an active reference surface, not a frozen V1 page.

The desired language is a premium football archive / sporting ledger:

- fixture rows read naturally as matches rather than admin records;
- opponent, score/result, date and competition context carry hierarchy;
- month/round grouping should create rhythm without dashboard chrome;
- upcoming fixtures remain quieter than completed results;
- controls are integrated into the composition;
- provenance/coverage remains available but visually secondary;
- result pages may be richer and more cinematic while retaining analytical clarity.

## Matchday / Fixture Intelligence

Matchday is an analytical workspace, not a sportsbook imitation.

The interface may expose governed betting-relevant football evidence, but it must keep clear visual/conceptual separation between:

- descriptive evidence;
- model probabilities;
- market price;
- edge/value interpretation;
- staking/strategy.

Do not make descriptive hit rates or `evidence_index` look like calibrated probabilities.

Dense evidence should feel typeset and deliberate rather than gamified.

## Profiles

Profiles describe entities rather than attempting to expose every available statistic.

Team Profile / Team Overview is active design work and may use richer visual identity, including crest/stadium context, but should still prioritise:

- identity;
- current/season context;
- record and fixture history;
- football narrative/context;
- navigation into deeper analytical surfaces.

Do not turn profiles into giant metric walls.

## Stats and rankings

Stats surfaces analyse entities and populations.

The durable product distinction remains:

> **Profiles describe entities. Stats analyse entities. Rankings analyse populations. Compare analyses selected entities together. Research tests the questions these surfaces reveal.**

The signature tiled vertical-list language remains valid for Team and Player analytical browsing where it improves scanability.

For leaderboard/tile surfaces:

- normally show no more than four metric tiles at once;
- selecting a fifth requires removing one of the active four;
- reset selection when analytical family/cohort changes;
- preserve governed rank/tie values rather than renumbering visually;
- keep full ranking/detail ledgers available through progressive disclosure;
- player ranking controls must not silently redefine the governed cohort.

Colour accents in statistical tiles are categorical rhythm, not universal metric semantics.

## Tables and ledgers

Tables/ledgers remain core research components.

Rules:

- primary names left aligned;
- numbers aligned consistently;
- compact but readable rows;
- thin/quiet separators;
- strong scan hierarchy;
- restrained hover/selection treatment;
- no dataframe-default appearance;
- no turning every cell into a widget.

## Charts

Charts should answer one clear visual question.

- labels and axes remain quiet;
- preserve inner padding and legibility;
- avoid unnecessary series/legends;
- colour must not carry meaning alone;
- do not add a chart because a page looks empty.

## Missing, partial and uncertain evidence

Incomplete evidence is a legitimate analytical state.

Do not:

- fabricate history;
- convert unknown to zero;
- present partial-source rates as complete-season evidence;
- rank incomparable observations without qualification;
- hide important limitations merely because they are technical.

Prefer calm specific language such as:

`17 / 38 matches observed`

rather than a generic error state.

## Provenance

Normal exploration should remain fluid, but methodology and evidence quality must remain inspectable.

Where interpretation depends on it, the user should be able to reach:

- source representation;
- metric definition;
- observed/eligible population;
- limitations;
- temporal/as-of context;
- provenance/correction history.

## Hard rejection rules

Avoid as a primary visual language:

- neon/glowing chrome;
- gratuitous gradients;
- glassmorphism;
- huge KPI walls;
- floating card grids everywhere;
- excessive pills/badges;
- icon-heavy navigation;
- gamified HUD styling;
- generic rounded SaaS controls;
- decorative motion;
- rainbow metrics;
- empty hero space without product purpose;
- filler metrics added only to occupy layout.

A dark theme does not make these patterns acceptable.

## Accessibility and responsiveness

Desktop remains the current priority, but design decisions should preserve:

- keyboard-accessible interaction;
- meaningful focus states;
- sufficient contrast;
- semantic labels;
- responsive degradation;
- readable tables/ledgers;
- non-colour-only state communication.

## Active/open surfaces

As of this checkpoint, the following are explicitly open to product/design iteration:

- global shell/navigation;
- Fixtures;
- fixture result workspace;
- Matchday / Bet Builder reference work;
- Team Profile / Team Overview;
- Team and Player Stats/Rankings;
- Homepage/Overview where required to bring it into the same product language.

Do not treat older 'frozen V1' wording as current authority unless a new task explicitly refreezes a surface.

## Validation

Visual/product acceptance should include:

- target-route rendering;
- deep-link/navigation checks;
- responsive sanity checks;
- Next.js typecheck/build;
- regression review for shared shell changes;
- confirmation that analytical definitions remain backend-governed;
- current documentation reconciliation when the visual language materially changes.

## Final visual test

Before accepting a design change, ask:

> **Does this feel like FRL — dark, premium, analytical, football-first and intentional — or like a generic generated dashboard?**

If the latter, simplify and return emphasis to football identity, evidence, typography and composition.
