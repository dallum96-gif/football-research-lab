# Football Research Laboratory — Master Frontend Migration Plan V2

**Status:** Authoritative frontend migration plan
**Date:** 20 August 2026
**Supersedes:** `FRL_MASTER_FRONTEND_MIGRATION_PLAN_V1.md`

## 1. Decision

The Football Research Laboratory will progressively migrate its GUI from Streamlit to a **React + Next.js** frontend backed by the existing Python research/query layer, with **FastAPI** as the explicit frontend-facing API boundary where required.

This is not a rewrite of the Laboratory.

The goal is to build the FRL's intended **visual research platform**, not reproduce the Streamlit screens one-for-one.

The migration remains subordinate to the Master Prompt, Risk Strategy Framework, Non-Destruction Assurance, relationship/identity contracts, data-platform architecture, visualisation contract, GUI Design Contract and UI Design System.

## 2. Current visual identity is authoritative

The current site no longer uses the older dark charcoal / blue-black main canvas described by earlier GUI documentation.

The live theme in `gui/theme.py` is authoritative.

The current FRL visual system is:

- warm off-white application background;
- warm white analytical surfaces;
- slightly darker warm raised surfaces;
- near-black primary text;
- muted warm-grey secondary/metadata text;
- orange-red primary accent;
- restrained olive/green secondary/positive accent;
- subtle charcoal borders;
- a dark sidebar used specifically as a navigation surface.

The migration must preserve this current visual identity.

The migration must also preserve the FRL typography/font family, hierarchy, spacing rhythm, compact analytical layout, editorial tone, restrained accent usage and same-tab navigation character.

No generic React/SaaS design language is to replace the FRL identity.

## 3. Architecture

```text
NEXT.JS / REACT
      ↓
interaction + presentation
      ↓
HTTP / JSON
      ↓
FASTAPI
      ↓
QUERY LAYER + HISTORICAL STATE + RESEARCH SERVICES + MODEL SERVICES
      ↓
DUCKDB / PARQUET where adopted
      ↓
CANONICAL FRL DATA
```

Next.js/React is not the statistical engine.

Python remains the primary environment for statistical research and modelling.

The frontend must not duplicate business logic that belongs in the research/query/model layers.

## 4. Identity and route boundary

The frontend/API boundary must preserve canonical FRL semantics exactly.

### Fixture

Canonical identity:

```text
(season, fixture_id)
```

Source-specific match IDs are attached evidence, not competing fixture identities.

### Team

Season-local source identities must remain distinct from persistent longitudinal club identities.

```text
season-local team identity
        ↓
verified mapping
        ↓
persistent club identity
```

### Player

Player identity remains season-aware and fail-closed.

```text
season + source player identifier
        ↓
verified identity mapping
        ↓
canonical player identity
```

### Relationships

Player–Fixture:

```text
(season, fixture_id, canonical player identity)
```

Team–Fixture uses the verified team identity/context appropriate to the canonical relationship model.

Season and competition are contextual dimensions, not substitute entity identities.

Display names are labels, not identity keys.

Unknown, ambiguous or conflicting identity mappings must never be guessed in React, TypeScript or client-side state.

Routes, API payloads and client caches must carry the canonical identity/context needed to resolve a research object unambiguously.

## 5. Research Result contract

The migration should standardise around a reusable **Research Result** for analytical presentation.

A Research Result is a presentation-ready representation of a trusted query/research result. It must not silently alter analytical semantics.

Where applicable, it carries:

- result data;
- population definition;
- filters and exclusions;
- season/competition scope;
- temporal/as-of semantics;
- canonical entity/relationship references;
- provenance/source lineage;
- metric/feature version;
- sample size;
- uncertainty and limitations;
- missing-data semantics;
- methodology/reproducibility metadata.

One Research Result may drive:

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

The first frontend implementation should make this pattern concrete early rather than treating it as a late abstraction.

## 6. Data visualisation becomes an early core capability

Data visualisation is one of the main reasons for migrating the frontend.

The FRL should build reusable visual research primitives early and improve analytical capability continuously as the migration proceeds.

### Plotly

Use Plotly through the React ecosystem when its mature analytical chart primitives are appropriate.

Initial high-value uses include:

- player/team comparison plots;
- rolling performance;
- league-position trajectories;
- distributions;
- home/away splits;
- H2H/matchup views;
- event/goal timelines;
- probability distributions;
- calibration charts;
- prediction-vs-actual views;
- uncertainty intervals;
- historical-state visualisations.

### Bespoke React visualisations

Do not force every research output through Plotly.

Use bespoke React components where interaction itself is analytically useful, including:

- clickable fixture timelines;
- entity-linked charts;
- coordinated chart/table selection;
- brushing/selection workflows;
- expandable evidence;
- historical/as-of exploration;
- research-population controls;
- custom comparison interfaces.

Plotly is an implementation tool, not the FRL visual identity.

## 7. Statistical modelling is an early migration priority

The new frontend should make statistical modelling easier to inspect, compare and understand while model logic remains in Python.

Model outputs should be presented as research objects exposing, where applicable:

- prediction;
- probability/distribution;
- model/version;
- relevant feature/input summary;
- training window/population;
- evaluation period;
- evaluation metrics;
- calibration;
- uncertainty;
- baseline comparison;
- provenance/reproducibility metadata.

The frontend must distinguish clearly between:

```text
model output
≠
model validity
```

Model validity remains governed by the Risk Strategy Framework.

## 8. Analytical comparison and inspection

Build reusable patterns that let a user move naturally from:

```text
entity
  ↓
context
  ↓
research result
  ↓
visual explanation
  ↓
exact table/detail
  ↓
provenance/methodology
```

Comparison should be a first-class capability across players, teams, fixtures, seasons, models and research populations where the underlying analytical contract supports it.

## 9. Historical-state presentation

Historical/as-of semantics should be exposed through the frontend, not hidden from the user.

Where relevant, the UI should allow investigation of:

- what had happened by a date;
- what information was available by that date;
- how a historical research state differs from final-season knowledge;
- the underlying fixtures/events supporting the historical state.

The frontend must not reconstruct historical state independently from trusted services.

## 10. Local-first and free/self-hosted requirement

The migration must remain viable with a zero mandatory software-platform bill.

Preferred stack:

- React + Next.js;
- Python + FastAPI;
- DuckDB;
- Parquet;
- Plotly / React visualisation tooling;
- standard open web technologies.

Hosted commercial services may be added later for operational convenience only where justified. They are not foundational requirements.

## 11. Migration phases

### Phase 1 — Foundation

Build:

- Next.js shell;
- current FRL colour/theme tokens;
- current FRL font family and typography hierarchy;
- route/navigation architecture;
- shared UI primitives;
- typed API boundary;
- first Research Result representation;
- development/test workflow.

The foundation spike must prove that the existing visual identity can be reproduced faithfully.

### Phase 2 — Core research workspaces

Migrate and improve:

- Fixture Explorer;
- Fixture Landing;
- Team Research;
- Player Research.

Use the existing information architecture and canonical identities. Improve interaction and presentation rather than reproducing Streamlit limitations.

### Phase 3 — Visual research layer

Build:

- reusable analytical chart components;
- Plotly integration;
- bespoke FRL visual components;
- linked chart/table/comparison patterns;
- interactive timelines;
- historical-state views;
- evidence/provenance inspection patterns.

### Phase 4 — Research Result and comparison layer

Build:

- reusable Research Result objects;
- comparison engine interfaces;
- richer team/player/fixture comparisons;
- research-population controls;
- historical-state comparison;
- methodology/provenance inspection.

### Phase 5 — Modelling and evaluation layer

Progressively expose and improve:

- Poisson;
- Elo;
- Monte Carlo;
- walk-forward evaluation;
- calibration;
- robustness;
- baseline comparisons;
- model diagnostics;
- model-vs-model comparison.

### Phase 6 — Research Laboratory experience

Build toward:

- experiment comparison;
- saved/reproducible research objects;
- deeper historical-state exploration;
- richer natural-language research interfaces;
- an eventual "ask a football question" workflow that links answers back to Research Results and underlying evidence.

## 12. Non-destruction and validation

The migration must not:

- rewrite canonical data unnecessarily;
- change fixture/team/player identities;
- alter relationship semantics;
- bypass provenance;
- introduce temporal leakage;
- move source identifiers into canonical identity by convenience;
- duplicate analytical/business logic in the frontend;
- delete useful Streamlit implementation history before validated parity.

For each stage:

```text
establish baseline
      ↓
define exact change surface
      ↓
minimal implementation
      ↓
targeted validation
      ↓
identity/query/provenance checks
      ↓
26/26 regression baseline
      ↓
project-health gate
      ↓
review result
```

## 13. Immediate first spike

The first Next.js foundation spike must prove all of the following before larger migration work:

1. current FRL palette and typography reproduce faithfully;
2. shared GUI design rules can be implemented as reusable components/tokens;
3. one typed Research Result can drive an exact table and an interactive chart;
4. canonical fixture/team/player identifiers survive the API boundary unchanged;
5. entity navigation preserves the existing same-tab contract;
6. historical/as-of context can be carried without frontend recomputation;
7. the stack remains free/self-hostable;
8. the existing Python query layer remains authoritative.

Only after this spike passes should workspace-by-workspace migration begin.
