# Current Work — Football Research Laboratory

**Last updated:** 15 August 2026

This file is intentionally short and volatile. Update it whenever the active task, branch, checkpoint or next step changes.

## Active branch

`agent/fixture-landing-page`

This is the active development branch for the current GUI redesign and Fixture Landing Page work.

Do not assume `main` contains these changes. Establish branch state before changing code.

## Stable / validated baseline

Current research gate:

**26/26 tests passing**

Breakdown:

- Query Lab: 14/14
- Player Research V0.1: 6/6
- Player Research V0.2: 6/6

Project health gate:

**GREEN LIGHT - PASSED WITH WARNINGS**

Known warning:

- 2019–20 fixture ID 275, Manchester City v Arsenal, has no score in the current fixture-master source state because of the rescheduled fixture representation. The health script warns rather than fabricates a result. This is known and accepted.

## Non-destruction rule for current work

The 26/26 baseline is the pre-change research contract.

UI redesign changes should not modify:

- query semantics;
- canonical fixture identity;
- persistent club identity;
- provenance rules;
- research calculations;
- test expectations;
- historical data.

A UI change is successful only when the new presentation works **and** trusted existing behaviour remains intact.

## Current product task

Redesign the user interface so the Football Research Laboratory feels like a professional football research product rather than a conventional Streamlit dashboard.

Target qualities:

- professional
- elegant
- pretty
- intuitive
- natural
- restrained
- data-led
- not AI-generated-looking

Design reference in spirit:

**StatsBomb analytical clarity + Football Manager information depth + modern application usability.**

Do not copy either product literally.

## Current UI decisions

### Navigation

- Use compact, left-aligned text-first navigation.
- Small monochrome line icons may sit beside navigation labels.
- Avoid large filled button blocks.
- Avoid excessive spacing between navigation items.
- Keep section headings quiet.
- Active state should be subtle, preferably a muted accent rather than a large coloured button.

Current conceptual navigation:

- Explore: League Table, Fixtures
- Research: Players
- Analysis: Head-to-Head, Form & Streaks
- Modelling: Prediction Lab
- Evidence: Data Quality, Provenance

### Global visual system

- near-black charcoal / very dark navy background
- slightly lighter surfaces
- off-white primary text
- muted grey secondary text
- one desaturated green accent
- subtle borders
- minimal cards
- compact controls
- restrained use of colour
- no gradients, glow effects or decorative AI-style widgets

### Fixture Explorer

Current explicit design requirements:

- Season + Team must be on the same row.
- Fixture rows should dominate the page.
- Filters should be compact and secondary.
- Opponent is the dominant entity in each row.
- Date/metadata quieter.
- Score prominent and scannable.
- Result clear but restrained.
- Do not present it as an unstyled dataframe.
- Avoid large rectangular opponent buttons where a navigable text/entity treatment can be used.
- Clicking a fixture must continue to resolve through the canonical fixture ID and existing fixture-detail query contract.

Current extracted presentation module:

`gui/fixture_explorer.py`

### Player Profile / History

Future feature, not current data-acquisition work.

Plan for:

- Overview
- Seasons
- History
- Matches
- Advanced
- Comparisons
- Career

Player chronology can be incomplete. Incomplete chronology is a valid data state, not an application failure.

The future profile must not:

- invent missing seasons;
- infer that missing data means the player was inactive;
- claim that known coverage is a complete career;
- crash when chronology has gaps.

Do not source additional historical player data yet.

## Current UI implementation state

The redesign is intentionally being developed as a preview rather than replacing the production entry point immediately.

Important files:

- `gui/theme.py` — current visual system
- `gui/navigation.py` — navigation metadata
- `gui/ui_shell.py` — navigation shell
- `gui/fixture_explorer.py` — Fixture Explorer presentation layer
- `gui/app_redesign.py` — preview entry point
- `gui/app.py` — production app; leave untouched until the redesigned workspaces are sufficiently mature

The trusted backend boundary remains:

`query_lab.py` → `query_api.py` → GUI

## What not to do

- Do not run `git clean` in the full local research workspace.
- Do not run `git reset --hard` to resolve local clutter.
- Do not casually delete untracked research/data files.
- Do not use `git add .` for deployable commits.
- Do not modify the query/data layer for purely visual problems.
- Do not source additional player history merely to make the future profile look complete.
- Do not treat an exploratory UI mock-up as stable production behaviour.

## Immediate next step

Before further implementation, refine the **sidebar and Fixture Explorer visual design** against the agreed design principles. The current preview is structurally useful but is not yet considered visually final.

The next implementation should be a deliberate design pass, not another small CSS patch.
