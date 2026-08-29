# Football Research Laboratory — Short-Term Product Roadmap

**Status:** Active near-term planning document  
**Created:** 29 August 2026

## Purpose

This document records the intended direction for the next several FRL sessions after the fixture-data operationalisation work. It is deliberately broader than a single implementation task, but narrower than the long-term North Star.

The immediate objective is to turn the governed FRL backend into a coherent research product through a sequence of reusable, data-backed interfaces.

The governing product principle is:

> The GUI should be a window into the research environment, not a collection of disconnected football pages.

The roadmap is intentionally revisable. It defines current priorities and sequencing, not immutable architecture.

---

## 1. Finish Fixture Workspace V1

The current fixture/result experience is the first operational product surface.

### V1 completion target

A user should be able to move:

```text
Fixture Explorer
    ↓
canonical fixture
    ↓
rich, governed fixture/result workspace
```

using real preserved historical evidence rather than hard-coded fixture data.

### Immediate fixture tasks

1. Complete historical PulseLive snapshot materialisation for the canonical Premier League fixture universe.
2. Resolve any genuine acquisition failures without reopening broad coverage discovery work.
3. Fix the PulseLive player identity → existing Player-Match / Universal Research Access identity bridge.
4. Preserve fail-closed behaviour where cross-source player identity cannot be verified.
5. Use source formation plus ordered lineup information for formation presentation where appropriate, while distinguishing derived display positions from source-provided coordinates.
6. Confirm events, lineups, formations, managers, current match statistics and metadata render consistently across representative fixtures.
7. Do not continue adding fixture-page statistics merely because more are available. Once V1 is operational, stabilise it and move on.

### Fixture V1 product stance

The fixture page does not need to expose every variable FRL possesses. It should communicate the match clearly and provide routes into deeper research surfaces.

---

## 2. Produce the FRL Variable Capability Inventory

Before building the main Team Stats, Player Stats, League Stats and Prediction Lab surfaces, FRL needs a structured product-facing understanding of what the backend actually knows.

The existing Universal Research Access variable universe is intentionally broad. A count such as “1,414 variables” is infrastructure information, not yet a usable product specification.

The next major analytical/documentation task should therefore create a structured capability inventory.

### Core questions for every important variable or variable family

For each variable FRL should establish:

1. **What does it mean?**
   - football concept;
   - original source definition where known;
   - whether the field is atomic, derived or model-produced.

2. **What grain is it at?**
   - fixture;
   - event;
   - team-match;
   - team-season;
   - player-match;
   - player-season;
   - league-season;
   - odds/market observation;
   - model output;
   - another explicit grain.

3. **How much historical coverage does it have?**
   - seasons;
   - fixtures;
   - teams;
   - players;
   - known gaps or exceptions.

4. **Can it legitimately be compared or aggregated?**
   - across matches;
   - across seasons;
   - across teams;
   - across positions;
   - across future leagues/sources;
   - with what caveats or transformations.

5. **What is its provenance?**
   - source family;
   - source-native field;
   - transformation path;
   - temporal/as-of semantics.

6. **Where could it be useful?**
   - Fixture workspace;
   - Team Profile;
   - Team Stats;
   - Player Profile;
   - Player Stats;
   - League Stats;
   - Head-to-Head research;
   - Prediction Lab;
   - modelling only;
   - retained research infrastructure but not currently suitable for UI exposure.

### Capability areas to catalogue

The inventory should explicitly cover at least:

| Area | Core product question |
|---|---|
| Fixture | What information can FRL know about a single match? |
| Events | What event-level evidence exists and at what depth? |
| Team-match | What can be measured for one team in one fixture? |
| Team-season | What can be aggregated reliably across a season? |
| Player-match | What can be inspected for one player in one match? |
| Player-season | What can be compared across players and seasons? |
| League-season | What league-wide context, rankings and distributions can be produced? |
| Context | What home/away, gameweek, score-state, rest, temporal and situational variables exist? |
| Odds / markets | What historical market information exists and with what time semantics? |
| Derived metrics | What FRL-created variables already exist and how are they defined? |
| Models | Which models exist, what are their inputs/outputs, and what was knowable at prediction time? |

### Desired deliverables

This should eventually produce two complementary artifacts:

#### A. Machine-readable inventory

A structured artifact generated from the governed research layer, suitable for:

- coverage checks;
- UI configuration;
- future documentation generation;
- filtering variables by grain/category/source;
- identifying candidate Team/Player/League statistics.

#### B. Human-readable FRL Data Capability Brochure

A polished, readable and visually engaging document that explains what FRL knows.

It should not read like a database schema dump.

It should walk through the system in football terms, for example:

- “What can we know about a fixture?”
- “What can we know about a team?”
- “What can we know about an individual player performance?”
- “What can we compare across a season?”
- “What market information do we preserve?”
- “Which statistics are derived by FRL?”
- “Which predictive models currently exist?”
- “What can safely be known as-of a historical date?”
- “Where are the important coverage limitations?”

The brochure should use clear categories, examples, coverage summaries and concise explanations rather than presenting hundreds of raw variable names without interpretation.

The intended audience is both the project owner and future collaborators: someone should be able to read it and understand the research capabilities of FRL without inspecting the codebase.

---

## 3. Team Research Surfaces

After Fixture V1 and the first variable capability map, build two distinct team interfaces.

### Team Profile

Purpose: identity, navigation and high-level team context.

Potential content:

- team identity;
- current/historical season selector;
- headline season record;
- recent form;
- upcoming/recent fixtures;
- key summary metrics;
- squad/player links where governed data supports them;
- routes into Team Stats and relevant research objects.

The Team Profile should not become a giant statistics table.

### Team Stats

Purpose: deep analytical exploration of team performance.

Potential dimensions include:

- totals;
- per-match rates;
- attacking metrics;
- defensive metrics;
- possession;
- passing;
- chance creation;
- discipline;
- home/away splits;
- temporal trends;
- distributions;
- rankings/percentiles against league context;
- historical season comparisons.

Exact metric groups should be selected from the Variable Capability Inventory rather than from convenience or visual familiarity.

---

## 4. Player Research Surfaces

Build two distinct player interfaces.

### Player Profile

Purpose: identity, context and navigation.

Potential content:

- canonical player identity;
- club/team history where available;
- position;
- age/season context where available;
- headline performance summaries;
- recent match history;
- fixture click-through;
- links into Player Stats and future comparisons.

### Player Stats

Purpose: detailed player research.

Potential content:

- match-level and season-level statistics;
- totals;
- per-90 metrics;
- rates and percentages;
- match distributions;
- position-aware rankings;
- league percentiles;
- historical season comparisons;
- future cross-player comparison tools.

This surface should consume the governed player identity and Universal Research Access layer rather than building source-specific shortcuts.

---

## 5. League Workspace

Create a coherent league-level surface.

### League Table

Requirements should eventually include:

- current/historical season selection;
- correct table reconstruction;
- temporal/as-of reconstruction where supported;
- links into teams and fixtures.

### League Stats

Potential content:

- team rankings;
- player leaders;
- league distributions;
- scoring trends;
- home/away trends;
- disciplinary trends;
- selected advanced metrics supported by comparable coverage;
- season-over-season context.

The league layer should provide the baseline distributions required for useful team/player percentile comparisons.

---

## 6. Prediction Lab

Reintroduce the useful conceptual parts of the original Streamlit modelling UI into the active Next.js product without restoring Streamlit as the frontend architecture.

### Initial model surface

Start with the existing Poisson model and expose more than a final probability.

Potential display:

- expected home goals;
- expected away goals;
- home/draw/away probabilities;
- correct-score probability matrix;
- model parameters;
- key input variables;
- historical calibration/performance;
- model version and provenance;
- prediction-time/as-of information.

### Product principle

FRL should expose enough evidence to answer:

> Why does the model think this?

rather than functioning as an unexplained prediction generator.

Prediction is a downstream research application, not the definition of FRL.

---

## 7. Head-to-Head / Match Research Workspace

Create a pre-match research surface intended to identify relevant trends, patterns and likely game characteristics.

This should be more sophisticated than a conventional “last five H2H results” page.

Potential inputs include:

- recent team form;
- home/away performance;
- attacking and defensive tendencies;
- scoring/conceding timing;
- shot/chance patterns;
- historical matchup evidence;
- relevant league baselines;
- model outputs;
- player availability / lineup context where available;
- derived FRL research conditions.

### Critical analytical distinction

The interface should clearly separate:

- descriptive historical pattern;
- potentially relevant contextual evidence;
- predictive evidence;
- model output.

A repeated historical pattern should not automatically be presented as predictive.

---

## 8. Add 2026/27 Data

Extend the governed data pipeline to include the 2026/27 Premier League season.

This should be treated as an extension of the existing temporal/canonical architecture rather than a separate product feature.

The intended outcome is that, once ingested correctly, the new season automatically appears across:

- fixtures;
- teams;
- players;
- league surfaces;
- variable research;
- models where inputs are available.

Avoid creating current-season-only code paths unless source reality genuinely requires them.

---

## 9. Near-Term Sequence

The current preferred sequence is:

```text
1. Finish Fixture Workspace V1
        ↓
2. Generate Variable Capability Inventory
   + FRL Data Capability Brochure
        ↓
3. Team Profile + Team Stats
        ↓
4. Player Profile + Player Stats
        ↓
5. League Table + League Stats
        ↓
6. Prediction Lab / Poisson model productisation
        ↓
7. Head-to-Head / Match Research workspace
        ↓
8. Extend governed pipeline to 2026/27
        ↓
9. Continue cross-league expansion planning
```

This is a priority spine rather than a prohibition on sensible overlap. For example, 2026/27 ingestion may need to occur earlier for operational reasons, and the variable inventory should inform all subsequent UI work.

---

## 10. Relationship to Future Cross-League Work

Cross-league expansion is recorded separately in:

`FUTURE_LEAGUE_COMBINE_PLAN.md`

The short-term Premier League product work should preserve source-agnostic abstractions so Team, Player, League and research surfaces can later accept additional competitions without being rebuilt.

Avoid allowing Premier League / PulseLive-specific assumptions to leak upward into universal FRL UI or research contracts.

---

## 11. Working Rule for the Next Several Sessions

When choosing the next task, ask:

> Does this move FRL toward an operational research product, clarify what the research environment can genuinely know, or unlock one of the agreed Team / Player / League / Prediction / Match Research surfaces?

If not, it is likely secondary work and should be recorded rather than allowed to displace the current product sequence.

The immediate priority remains completing Fixture Workspace V1 and then producing the Variable Capability Inventory.