# FRL Frontend Analytical Migration Addendum V1

## Purpose

This addendum records the important analytical, identity and non-destruction implications of the FRL frontend migration.

## Current theme authority

The live `gui/theme.py` implementation is authoritative for the current GUI colour system. The current site uses a warm light analytical canvas (`--frl-bg` / `--frl-surface`) with near-black primary text, muted warm-grey secondary text, orange-red primary accent, restrained olive/green secondary accent and a deliberately dark sidebar.

Older documentation describing the main application as dark charcoal / blue-black is superseded for current GUI work.

## Research Result principle

A reusable Research Result should be the frontend-facing presentation contract for trusted analytical output. One result may drive tables, charts, comparisons, timelines, distributions, summaries, exports and provenance views without changing its semantics.

A Research Result should preserve, where applicable:

- population;
- filters/exclusions;
- season/competition scope;
- temporal/as-of semantics;
- canonical entities and relationships;
- provenance;
- metric/feature version;
- sample size;
- uncertainty and limitations;
- missing-data semantics;
- methodology/reproducibility metadata.

The frontend must never silently recompute analytical quantities differently from the trusted query/research layer.

## Identity safeguards

The frontend and API boundary must preserve:

- Fixture identity = `(season, fixture_id)`;
- Player–Fixture identity = `(season, fixture_id, canonical player identity)`;
- season-local team IDs as distinct from persistent longitudinal club identity;
- season-aware source player identities as distinct from canonical player identity;
- season/competition as contextual dimensions rather than substitute entity IDs.

Display names are labels, not canonical identities.

Unknown or ambiguous mappings remain unresolved and must not be guessed in TypeScript, React state, routing or client-side data transformation.

## Historical integrity

Interactive filters, visualisations, cached results and model displays must preserve the distinction between:

1. what had happened by a historical point in time; and
2. what information would actually have been available by that time.

Frontend convenience must never reintroduce future information into a historical result.

## Visualisation priority

Data analysis and visualisation are first-class migration work. Build reusable analytical primitives early rather than treating them as late-stage presentation polish.

Use Plotly where mature analytical chart primitives are appropriate, and bespoke React components where custom interaction, entity linkage, historical exploration or research workflow demands finer control.

## Statistical model presentation

Models remain in Python. The frontend should render model results as inspectable research objects exposing, where applicable:

- prediction/probability/distribution;
- model/version;
- training window/population;
- evaluation period;
- evaluation metrics;
- calibration;
- uncertainty;
- baseline comparison;
- provenance/reproducibility.

Visual polish is never evidence of model validity.

## Architecture rule

Next.js/React is the interaction and presentation layer, not the statistical engine. FastAPI is the preferred explicit API boundary where required. Python remains the primary environment for statistical research and modelling.

The frontend must not duplicate source precedence, identity mapping, metric definitions, fallback rules, temporal rules, leakage rules or business logic that belongs in the research/query layer.

## Non-destruction rule

Any frontend migration must remain additive and reversible until validated equivalence is established.

Do not alter canonical fixture/team/player identities, relationship semantics, provenance, temporal definitions or trusted query results merely to make a screen easier to build.

Keep the existing Streamlit implementation available as reference until the replacement reaches validated parity and an explicit deprecation decision is made.
