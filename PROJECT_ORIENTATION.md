# Football Research Laboratory — Project Orientation

## Purpose of this document

This is the fast-start guide for a new contributor, a new ChatGPT session, or anyone returning after a long interruption.

Read this document first, then `CURRENT_WORK.md`. After that, inspect the repository files named in the relevant sections before changing code.

The goal is to become familiar with the project quickly without relying on chat history.

---

## 1. The project in one sentence

> **Give us the data and let us ask whatever football question we can think of.**

The Football Research Laboratory is not fundamentally an FPL dashboard or a betting model. It is intended to become a provenance-aware historical football research environment in which users can explore football evidence, test hypotheses, compare analytical approaches, and eventually construct increasingly arbitrary questions against the underlying football database.

See `PROJECT_VISION.md` for the complete seven-stage progression:

1. Repository
2. Database
3. Analytics
4. Modelling
5. Research
6. Market
7. Interactive tool

The current code is still in the foundation stages. The GUI is important, but it sits above the trusted research/data layer rather than defining it.

---

## 2. Source of truth and branch discipline

Repository:

`dallum96-gif/football-research-lab`

GitHub is the project's source of truth for tracked code and documentation.

Before changing code:

1. establish the current branch and repository state;
2. identify the stable `main` state;
3. distinguish committed branch work from local/untracked experiments;
4. preserve unfinished experiments rather than deleting them;
5. make the smallest sensible change;
6. validate before treating the change as safe.

Do not casually run destructive commands such as `git clean`, `git reset --hard`, or broad staging (`git add .`) in the full local research workspace.

The local workspace may contain useful research artefacts, generated data, inspection scripts, backups and experiments that are intentionally outside the deployable repository.

---

## 3. Core architectural principle

The laboratory separates football evidence from presentation and future decision/market layers.

Conceptually:

```text
RAW / SOURCE
    ↓
VALIDATED / CANONICAL
    ↓
HISTORICAL STATE
    ↓
RESEARCH / FEATURES / MODELS
    ↓
EVALUATION
    ↓
MARKET / DECISION (explicit future layer)
    ↓
GUI
```

The research layer should not accidentally inherit market information. Any future model using bookmaker/exchange information must make that dependency explicit.

The database should represent underlying football entities and events rather than being designed around today's favourite questions. Derived concepts such as last-5 form, rolling xG, strength-adjusted form and similar-match conditions should be calculable from the underlying evidence.

---

## 4. Quality architecture

The project's governing quality principle is:

> **No result is allowed to become research knowledge unless the system can show where the data came from, what information was available at the time, what transformation produced it, and how the result was tested out-of-sample.**

Quality is therefore not a single test script. It is an architecture containing:

- schema validation
- data integrity
- identity integrity
- chronology and temporal integrity
- provenance / lineage
- leakage prevention
- unit tests
- integration tests
- statistical evaluation
- walk-forward / out-of-sample testing
- calibration and robustness checks
- baseline comparison

These are distinct concerns. Passing a code test does not prove the dataset is correct; passing a data-quality gate does not prove a model is valid; and model validity does not imply betting profitability.

See `RISK_STRATEGY_FRAMEWORK.md` for the full project-level quality philosophy.

---

## 5. Non-Destruction Assurance

The project uses a non-destruction mindset for development work.

A successful change must demonstrate not only that the new behaviour works, but that trusted existing behaviour has not been damaged.

Default development pattern:

```text
Understand existing behaviour
        ↓
Identify the change surface
        ↓
Predict failure modes
        ↓
Make minimal change
        ↓
Run targeted validation
        ↓
Run regression / full gate as appropriate
        ↓
Inspect the result
        ↓
Only then treat the change as safe
```

For GUI work, the safest approach is normally to keep the trusted query/data contracts unchanged and migrate the presentation layer incrementally.

See `NON_DESTRUCTION_ASSURANCE.md`.

---

## 6. Trusted data foundation

The core football data model deliberately distinguishes season-local identity from persistent club identity.

Important files include:

- `fixtures_master_corrected.csv` — canonical corrected fixture master
- `identity/team_seasons.csv` — season-local identities and persistent club mapping
- `identity/data_quality/fixture_corrections.csv` — explicit fixture correction provenance
- `_merged/players/*_all_players_gw.csv` — historical player/gameweek source data
- `data/fixture_match_stats.csv` — packaged historical fixture statistics used by the match-statistics layer

The project treats raw/source data as evidence rather than as something to silently mutate into the working truth.

A fixture should remain resolvable through its canonical identity even when historical corrections are required. The corrected analytical view must preserve provenance for the correction rather than hiding the fact that a change occurred.

---

## 7. Trusted query architecture

The principal research boundary is:

`query_lab.py`

↓

`query_api.py`

↓

GUI presentation

`query_lab.py` contains the research/query logic and data-resolution rules.

`query_api.py` is the interface used by the GUI and should remain comparatively thin.

The GUI should not duplicate business logic that belongs in the query layer.

Important current query capabilities include:

- league tables
- team summaries
- multi-season team comparison
- fixture queries
- fixture detail
- head-to-head
- form/streak queries
- player research/query functions

---

## 8. Fixture architecture and current feature

The active development area is the Fixture Landing Page on branch:

`agent/fixture-landing-page`

The intended flow is:

```text
Fixture Explorer
      ↓
canonical season + fixture ID
      ↓
query_api.fixture_detail()
      ↓
query_lab fixture resolution
      ↓
match statistics + provenance
      ↓
Fixture Landing Page
```

This does **not** create a separate fixture database. The landing page is a richer presentation of the existing canonical fixture record.

The match-statistics layer supports core statistics and optional statistics. Missing optional statistics must be represented safely rather than causing the fixture page to fail.

A known fixture-data warning exists for the rescheduled 2019–20 Manchester City v Arsenal match (`season=2019-20`, fixture ID `275`). The project-health gate intentionally warns about its missing score rather than inventing one. This is a known data-state condition, not a reason to rewrite the health logic during UI work.

---

## 9. Current research validation contract

The current development baseline uses **26/26 research tests passing**.

The current breakdown is:

- Core Query Lab: 14/14
- Player Research V0.1: 6/6
- Player Research V0.2: 6/6
- Total: 26/26

Older documentation contains a historical 13/13 checkpoint. That is a past state and must not be mistaken for the current research baseline.

The project-health PowerShell gate is a separate control. It currently checks source-file coverage, the 3,800-fixture canonical master, season integrity, duplicate fixture IDs, required fields, score/completion semantics, team integrity, date integrity, and the 2025–26 player↔fixture relationship.

A current health result of `GREEN LIGHT - PASSED WITH WARNINGS` is acceptable when the known 2019–20 fixture warning is the only issue.

---

## 10. GUI redesign philosophy

The current GUI is being redesigned without rewriting the trusted research layer.

The intended feel is:

> **StatsBomb's analytical clarity + Football Manager's information depth + modern web-app smoothness.**

But the visual target is explicitly **not** a generic AI-generated dashboard.

Desired qualities:

- professional
- elegant
- pretty but restrained
- natural
- intuitive
- data-led
- information dense without feeling cramped
- editorial rather than decorative

Avoid:

- excessive rounded cards
- gradients
- glowing effects
- rainbow accents
- giant widget buttons
- repetitive icon cards
- unnecessary badges
- oversized hero sections
- decorative copy
- UI where the component chrome overwhelms the data

The data should be interesting; the interface should help the user understand it.

---

## 11. Current GUI design system

The visual language should be:

- near-black charcoal / very dark blue background
- slightly lighter charcoal surfaces
- off-white primary text
- muted grey secondary text
- one restrained, desaturated green accent
- subtle borders
- compact controls
- left-aligned navigation
- small monochrome line icons used as navigation cues
- few cards
- quiet tables

The sidebar should behave like professional application navigation, not a stack of large Streamlit buttons.

Preferred navigation pattern:

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

All navigation text should share a deliberate left alignment. Icons should be small, monochrome and subordinate to the text. Active state should be subtle rather than a large filled button.

The main content should establish context immediately and favour strong horizontal alignment over excessive vertical stacking.

---

## 12. Fixture Explorer UI rules

The Fixture Explorer is currently being redesigned.

Important decisions:

- Season and Team selectors should sit on the same row.
- The fixture list should occupy the majority of the page.
- Filters should be compact and secondary.
- The opponent should be the visually dominant entity in each row.
- Date and metadata should be quieter.
- Score should be strong and easy to scan.
- Result should be visually clear but restrained.
- The interface should not look like a raw dataframe.
- Opponent navigation should eventually feel like text/entity navigation rather than a large rectangular button.
- Clicking an opponent/fixture should lead into the existing canonical fixture-detail route.

The test for success is not merely "it fits on the page". It should feel sleek, calm, editorial and easy to scan.

---

## 13. Player Research and future Player Profile

`player_research.py` and `gui/player_research_ui.py` form the current Player Research feature.

Future architecture should distinguish:

```text
Players
   ↓
Player Research
   ↓
find / filter / compare
   ↓
Player Profile
   ├── Overview
   ├── Seasons
   ├── History
   ├── Matches
   ├── Advanced
   ├── Comparisons
   └── Career
```

The Player Profile / History feature is a future capability, not a reason to source more data now.

The historical player dataset is incomplete for some players. This is a valid data state.

The future profile must:

- render safely when chronology is partial;
- never fabricate missing seasons or clubs;
- distinguish "no data available" from "the player was not playing";
- avoid counting known coverage as proof of a complete career;
- expose uncertainty/provenance calmly rather than presenting missing data as an application failure.

For now, improve robustness to incomplete chronology rather than expanding data acquisition.

---

## 14. Future research laboratory direction

The eventual laboratory should support independent analytical approaches rather than one monolithic model:

- historical precedent / comparable matches
- Elo
- Poisson
- Monte Carlo
- player-state modelling
- explicit market analysis

The research engine should support arbitrary derived conditions from underlying football evidence. Examples include multiple form windows, rolling xG/xGA, home/away splits, strength-adjusted form and custom historical filters.

False-discovery protection is a first-class requirement. Exploratory findings must not automatically become trusted evidence. Eventually, discovery periods, unseen test periods, experiment tracking, calibration and robustness analysis should be part of the research workflow.

---

## 15. Key files to inspect when re-entering the project

Start here:

1. `PROJECT_ORIENTATION.md` — this file
2. `CURRENT_WORK.md` — current branch/task/checkpoint
3. `PROJECT_VISION.md` — full long-term vision and seven-stage progression
4. `README.md` — repository-level summary and recovery instructions
5. `PROJECT_STATUS.md` — historical project status; useful context but may be dated
6. `query_lab.py` — trusted research engine
7. `query_api.py` — GUI-facing query contract
8. `match_stats.py` — fixture statistics abstraction
9. `gui/app.py` — current production Streamlit entry point
10. `gui/theme.py` — current visual system
11. `gui/navigation.py` — navigation metadata
12. `gui/ui_shell.py` — presentation shell
13. `gui/fixture_explorer.py` — extracted Fixture Explorer presentation
14. `project-health.ps1` — project health gate
15. `tests/` — research/data validation suite

For current redesign work, inspect `CURRENT_WORK.md` before assuming a feature is complete.

---

## 16. How a fresh session should behave

A fresh coding session should **not** ask the user to re-explain the project if these documents are available.

Instead:

1. Read `PROJECT_ORIENTATION.md`.
2. Read `CURRENT_WORK.md`.
3. Establish current branch and compare it with `main`.
4. Inspect the relevant files for the task.
5. Preserve the 26/26 research baseline unless a change explicitly concerns a research contract.
6. Keep UI work isolated from the data/query layer wherever possible.
7. Preserve local/untracked experiments unless the user explicitly asks for cleanup.
8. State uncertainty when the repository does not contain enough evidence rather than inventing historical context.

This document is intended to make a new session familiar with the architecture and project culture quickly, while still requiring code inspection before substantive changes.
