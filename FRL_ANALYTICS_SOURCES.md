# Football Research Laboratory — Analytics Sources & Discovery

## Status

**Living research-source map and discovery brief.**

This document complements `ANALYTICAL_VISUAL_MOODBOARD.md`. The moodboard records analytical and visual ideas that FRL may want to exploit; this file records **where to keep looking for new ideas, methods, tools and evidence**.

It is not a whitelist and it is not an instruction to reproduce another product. Future FRL iterations should use it to discover useful work, understand the analytical question being solved, and trace promising ideas back to technical or methodological sources where possible.

---

## 1. Purpose

FRL should not rely only on accidental discovery of interesting football-analysis posts.

A deliberate source-investigation process should periodically search for work that could improve FRL's:

- analytical concepts
- derived metrics
- modelling ideas
- spatial analysis
- visualisation grammar
- interaction design
- tactical tooling
- recruitment analysis
- player and team profiling
- match analysis
- provenance and research methods

The objective is not to collect attractive graphics. The objective is to discover **useful football questions and credible ways of answering them**.

---

## 2. Discovery method

Future source investigations should work outward from known-good references rather than treating social-media search as a random feed.

### A. Network discovery

Start with established useful accounts and inspect:

- people they cite
- collaborators
- researchers they reply to
- accounts they repost
- tools or datasets they mention
- papers they reference
- repositories they maintain
- companies or academic groups they work with

This allows FRL to explore the football-analytics network around sources already shown to be relevant.

### B. Concept-led discovery

Search directly for analytical areas that FRL wants to develop, including:

- passing networks
- pass maps
- shot maps
- field tilt
- territorial dominance
- expected possession value
- expected threat
- pressing models
- turnover sequences
- defensive-action height
- progression
- possession chains
- player similarity
- role clustering
- recruitment models
- residual / expected-vs-actual analysis
- tactical visualisation
- formation analysis
- lineup optimisation
- squad construction
- spatial football modelling

### C. Wider-source investigation

Do not restrict discovery to X/Twitter.

Where useful, follow promising work into:

- GitHub repositories
- personal websites
- blogs
- Substacks/newsletters
- conference talks
- academic papers
- technical documentation
- analytics-company research
- public notebooks
- open datasets
- podcasts/interviews where methodology is discussed

The wider source is often more valuable than the social post because it may reveal **how the analysis was constructed**.

### D. Account-level reading

Do not judge an account from one viral chart.

When a source looks promising, inspect enough of its wider output to understand:

- recurring football questions
- analytical philosophy
- visual language
- methods used
- data requirements
- whether the work is descriptive, explanatory, predictive or product-oriented
- which ideas are genuinely transferable to FRL

---

## 3. What qualifies as a useful source

A source is especially valuable when it contributes one or more of the following:

1. A football question FRL should be able to investigate.
2. A metric or model that suggests a useful derived concept.
3. A visual form that reveals a pattern better than a table.
4. A spatial/event-data application.
5. A comparison or benchmarking method.
6. A tactical or recruitment workflow.
7. An interactive football-native interface.
8. A methodology FRL can study or reproduce independently.
9. A public dataset or upstream source worth auditing.
10. A useful critique of common analytical practice.

Visual attractiveness alone is insufficient.

---

## 4. Initial source network

The initial network comes from Daniel's first FRL analytical moodboard exercise.

### FC_Mossman / Spencer Mossman — `@fc_mossman`

Particularly useful for player profiling, peer populations, role-specific templates, pressing analysis, multidimensional scatterplots and joint interpretation of volume/efficiency.

### Ben Griffis — `@BeGriffis`

Particularly useful for passing networks, average positions, progression, style fingerprints, scatterplot analysis, tactical structures and interpretable model outputs.

### Ted Knutson / mixedknuts — `@mixedknuts`

Useful for role-specific recruitment profiles, radar grammar, player evaluation and football-oriented metric selection.

### SkillCorner — `@SkillCorner`

Useful for spatial/off-ball analytics, expected possession value, passing risk/reward, player archetypes and richer event/tracking-derived concepts.

### Soccermatics / David Sumpter — `@Soccermatics`

Useful for connecting football modelling to usable analytical products, tactical tools and researcher-driven workflows.

### Earpiece

Useful for shadow-team concepts, shortlist-to-XI workflows and football-native interactive squad manipulation.

### Markstats / Markstatsbot — `@markstatsbot`, `@markrstats`

Particularly relevant for passing networks, average positions, field tilt, defensive-action height, progression, xG/xThreat and compact match-analysis outputs.

### Gradient Sports — `@Gradient_Sports`

Useful for clear player identity, benchmarked bar profiles, deltas from positional norms and accessible analytical presentation.

### Sofascore — `@Sofascore`

Useful for reusable pitch canvases, pass maps, shot maps, dribble maps and defensive-action layers.

### Opta Analyst

Useful for zonal and spatial comparison, difference maps, temporal change and accessible communication of advanced football analysis.

### Daniel Evans — `@DEvansData`

Useful for Football Manager-style information systems, tactics-board concepts and interactive environments connecting players, squads and analysis.

### liverpxxl9 — `@liverpxxl9`

Useful as a reference for communicating passing-network and tactical interpretation in ordinary football language.

This list should expand when new sources materially broaden FRL's analytical vocabulary.

---

## 5. How discoveries should be recorded

When a new source is worth keeping, record:

- **Source / creator**
- **Where found**
- **Football question** being addressed
- **Method / metric / model** being used
- **Visual or interaction principle** worth retaining
- **Potential FRL application**
- **Implied data requirements**
- **Methodology link or repository**, where available
- **Caveats**, especially when the method is proprietary or insufficiently documented

Where the discovery materially changes the visual/analytical vocabulary, also update `ANALYTICAL_VISUAL_MOODBOARD.md`.

---

## 6. Source-quality discipline

FRL should distinguish inspiration from evidence.

A social-media graphic may be useful inspiration without establishing that its metric is valid or reproducible.

Before FRL implements a concept as governed analysis, investigate where possible:

- metric definition
- data source
- population
- exclusions
- sample requirements
- units
- transformations
- model assumptions
- known limitations

Do not silently reproduce proprietary metrics whose definitions are unavailable.

Where a proprietary concept is valuable, FRL may study the general analytical question and construct its own documented implementation from available evidence.

---

## 7. Relationship to upstream data investigation

Source discovery should help identify **which upstream data capabilities matter**.

For example, repeated inspiration around:

- pass maps
- shot maps
- passing networks
- field tilt
- possession value
- pressing sequences

creates a concrete reason to audit PulseLive/Opta-derived upstream material for:

- event coordinates
- pass end coordinates
- event order
- timestamps
- possession IDs
- recipients
- qualifiers
- tactical state
- substitutions
- turnovers
- defensive actions

Thus the moodboard and source map should help prioritise data archaeology rather than remain isolated design documents.

---

## 8. Ongoing FRL inspiration watch

A useful future workflow is a periodic FRL source investigation.

The investigation should:

1. Search recent public work around the known source network.
2. Search concept areas relevant to FRL's current roadmap.
3. Investigate promising creators beyond individual posts.
4. Prefer genuinely novel ideas over repetitions of concepts already captured.
5. Trace interesting social posts to deeper methodological sources where possible.
6. Surface only discoveries that could materially improve FRL.
7. Record durable discoveries in this file and/or the analytical visual moodboard.

The output should be curated rather than exhaustive.

---

## 9. Standing principle

> **FRL should continuously learn from the best public football analytics work without becoming an imitation of any one analytics product.**

The aim is to understand the questions, methods and product ideas that already exist, combine them with FRL's governed data architecture, and develop an increasingly distinctive research environment of its own.
