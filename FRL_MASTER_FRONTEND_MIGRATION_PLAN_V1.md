# Football Research Laboratory — Master Frontend Migration Plan V1

**Status:** Foundational architecture decision
**Date:** 20 August 2026
**Scope:** Frontend/presentation architecture only. The trusted football data, research, provenance, temporal, relationship and modelling architecture remains authoritative and is not being rewritten by this plan.

## 1. Decision

The Football Research Laboratory will progressively migrate its user interface from Streamlit to a **React + Next.js** frontend backed by the existing Python research/query layer, with **FastAPI** used as the explicit frontend-facing API boundary where required.

The migration is not a rewrite of the Laboratory.

The objective is to build the FRL's intended **visual research platform** rather than reproduce the existing Streamlit dashboard one screen at a time.

The migration remains subject to the existing branch, non-destruction, provenance, temporal-integrity, relationship-integrity, source-boundary and validation contracts.

## 2. Non-negotiable preservation rules

The migration must preserve the existing FRL visual and interaction identity unless a future change is explicitly approved as a design-system decision.

### Colour scheme

Preserve the established FRL palette and semantic use of colour from `UI_DESIGN_SYSTEM.md`, `GUI_DESIGN_CONTRACT.md` and `gui/theme.py`.

In particular preserve:

- very dark charcoal / blue-black application background;
- slightly lighter charcoal surfaces where the current system uses them;
- off-white primary text;
- muted grey secondary text;
- the restrained FRL accent system and its semantic meaning;
- subtle borders and understated states.

Do not introduce a generic React/SaaS palette, gradients, neon treatment, rainbow metric colouring, or a new independent design language merely because the frontend technology changes.

### Typography

Preserve the existing FRL typography hierarchy and **the same approved font family/typography system across every workspace and component**.

The migration must not use a new framework-default font merely because Next.js makes it convenient.

Typography should continue to establish:

1. small uppercase context/eyebrow;
2. page or entity name;
3. concise context/subtitle;
4. primary analytical data;
5. supporting metadata.

### GUI contract

`GUI_DESIGN_CONTRACT.md` remains authoritative.

The migration must preserve:

- visual hierarchy;
- spacing rhythm;
- compact analytical layouts;
- subtle borders;
- restrained accent usage;
- consistent selectors and controls;
- text-led entity navigation;
- progressive disclosure;
- the requirement that UI changes do not silently modify the data/query semantics.

The migration should implement these rules more faithfully and consistently in React rather than reinterpret them.

### Existing information architecture

Existing approved FRL navigation, workspace identities, canonical fixture/team/player routes and entity relationships remain the starting point.

Do not invent a new information architecture simply because the technical frontend changes.

## 3. Target architecture

The target separation is:

```text
                 NEXT.JS / REACT
                       │
            interaction + presentation
                       │
                  HTTP / JSON
                       │
                    FASTAPI
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    QUERY LAYER     VIZ LAYER     MODEL LAYER
        │              │              │
        └──────────────┼──────────────┘
                       │
                DUCKDB / PARQUET
                       │
              CANONICAL FRL DATA
```

This preserves the FRL's existing architectural separation:

```text
canonical data
    ↓
historical state / derived features
    ↓
research / models
    ↓
query API
    ↓
visualisation
    ↓
GUI
```

Next.js/React is the presentation and interaction layer, **not the statistical engine**.

Python remains the primary environment for statistical research and modelling.

## 4. Data visualisation becomes a first-class migration priority

Visualisation is not a cosmetic stage after the migration. It is one of the main reasons for moving to the new frontend.

### Analytical visualisation workhorse

Use Plotly through the React ecosystem for high-value analytical charts where its mature interactive primitives are appropriate.

Initial targets include:

- player and team comparison plots;
- rolling performance charts;
- league-position trajectories;
- distributions;
- home/away splits;
- H2H visualisations;
- goal and event timelines;
- probability distributions;
- model calibration charts;
- prediction-vs-actual views;
- uncertainty intervals;
- historical-state visualisations.

### Bespoke FRL visualisations

Do not force every visualisation through Plotly.

Use native React visual components when the interaction itself is part of the research experience, including where appropriate:

- clickable fixture timelines;
- entity-linked charts;
- interactive comparison selectors;
- brushing/selection workflows;
- expandable evidence areas;
- research-population controls;
- custom historical-state interfaces.

Plotly is an implementation tool, **not the FRL visual identity**.

All visualisations remain subordinate to `FRL_VISUALISATION_DATA_CONTRACT.md`: the same analytical result must be able to feed tables, charts, comparisons and other presentations without changing its semantics.

## 5. Research result contract

The migration should establish a reusable frontend-facing **research result contract**.

A substantive query result should carry, where applicable:

- result data;
- population definition;
- filters and exclusions;
- season/competition scope;
- temporal/as-of semantics;
- provenance/source lineage;
- metric or feature version;
- sample size;
- uncertainty and limitations;
- missing-data semantics.

The frontend must not silently recompute analytical quantities differently from the trusted query/research layer.

## 6. Model result contract

The migration should establish a reusable **model result contract** so the GUI can render model outputs without knowing the internal implementation of the model.

A model result should be able to expose, where applicable:

- prediction;
- probability/distribution;
- relevant feature set or feature summary;
- model name/version;
- training population/window;
- evaluation period;
- evaluation metrics;
- calibration information;
- uncertainty;
- baseline comparison;
- provenance and reproducibility information.

This allows the frontend to render a model as a research object rather than a single headline number.

## 7. Statistical modelling priority

The migration should make serious statistical research easier to build, compare and inspect while leaving model logic in Python.

The long-term model layer is expected to support replaceable approaches including:

```text
models/
├── baselines/
│   ├── league_frequency.py
│   ├── elo.py
│   └── poisson.py
│
├── regression/
│   ├── logistic.py
│   ├── poisson.py
│   └── count_models.py
│
├── simulation/
│   ├── monte_carlo.py
│   └── match_simulator.py
│
├── evaluation/
│   ├── walk_forward.py
│   ├── calibration.py
│   ├── robustness.py
│   └── baselines.py
│
└── research/
    ├── comparable_matches.py
    ├── player_state.py
    └── experiment_registry.py
```

This is an architectural target, not a requirement to create every file immediately.

Model work remains governed by `RISK_STRATEGY_FRAMEWORK.md`, including time-respecting evaluation, leakage prevention, calibration, robustness and baseline comparison.

## 8. Local-first analytical stack

The target analytical stack remains compatible with the existing FRL architecture:

```text
Parquet
   ↓
DuckDB
   ↓
query result
   ↓
FastAPI / typed API contract
   ↓
React / Next.js
```

Do not introduce an expensive hosted database or data platform merely to support the frontend migration.

The FRL remains local-first and free/self-hostable unless a future operational need explicitly justifies infrastructure.

## 9. API boundary

FastAPI is the preferred explicit boundary between the React frontend and Python research/query services where a network/API boundary is needed.

API structure should emerge from existing FRL contracts and query seams rather than being invented purely for REST-style symmetry.

Illustrative future routes may include fixture, team, player, H2H, research and model resources, but the exact endpoint design must be derived from the existing query/API contract and canonical identities.

The GUI must not duplicate business logic that belongs in the Python research/query layer.

## 10. Migration phases

### Phase 1 — Foundation

Build:

- Next.js application shell;
- FRL design tokens and typography implementation;
- routing/navigation architecture;
- shared component primitives;
- Python API boundary;
- development/test workflow.

**Priority:** establish the application foundation without changing analytical semantics.

### Phase 2 — Core research workspaces

Migrate and improve:

- Fixture Explorer;
- Fixture Landing;
- Team Research;
- Player Research.

Do not perform a literal one-for-one Streamlit recreation. Reuse the approved information architecture and research contracts while improving interaction and usability.

### Phase 3 — Visual research layer

Build:

- reusable analytical chart components;
- Plotly integration where appropriate;
- bespoke FRL visual components;
- linked chart/table/comparison patterns;
- interactive timelines;
- research-population interaction patterns.

### Phase 4 — Research result and comparison layer

Build:

- reusable research-result objects;
- comparison engine interfaces;
- richer team/player/fixture comparisons;
- historical-state visualisations;
- provenance/methodology inspection views.

### Phase 5 — Modelling and evaluation layer

Progressively expose and improve:

- Poisson;
- Elo;
- Monte Carlo;
- walk-forward evaluation;
- calibration;
- robustness;
- baseline comparisons;
- model diagnostics.

Model validity must remain separate from the frontend and cannot be inferred from visual polish.

### Phase 6 — Research Laboratory experience

Build toward:

- experiment comparison;
- model diagnostics as first-class research views;
- saved/reproducible research objects;
- deeper historical-state exploration;
- eventual natural-language/"ask a football question" interfaces.

## 11. Design principles for the new frontend

The new frontend should feel:

- serious enough to trust;
- fun enough to explore;
- professional;
- elegant;
- restrained;
- analytical;
- information-rich;
- fast and responsive;
- natural to navigate.

It must not drift into generic SaaS or AI-dashboard aesthetics.

Preserve the FRL's dark charcoal/blue-black visual language, off-white text, muted secondary text, restrained accent use, approved typography and compact editorial layout.

Prefer subtle entity links over large rectangular buttons.

Use cards only when they materially improve comprehension.

Prefer progressive disclosure over showing every available metric at once.

## 12. Interactivity principles

The frontend should support rich interaction without changing research semantics silently.

Desired interaction capabilities include:

- fast entity selection;
- contextual filters;
- hover detail;
- range selection;
- chart/table coordination;
- comparison selection;
- drill-down;
- entity-to-entity navigation;
- historical/as-of exploration;
- evidence/provenance inspection;
- reversible filters and clear active-state presentation.

Interactions should feel like a coherent application rather than a collection of dashboard widgets.

## 13. Free / self-hosted requirement

The migration must remain viable with a **zero mandatory software-platform bill**.

Preferred stack elements are open-source and self-hostable:

- Next.js / React;
- Python / FastAPI;
- DuckDB;
- Parquet;
- Plotly / React visualisation tooling;
- standard open web technologies.

Commercial hosted services may be considered later for operational convenience, but must not become a foundational requirement of the Laboratory.

## 14. Preservation and non-destruction

The migration must not:

- rewrite the canonical data layer unnecessarily;
- change canonical fixture/team/player identities;
- alter relationship semantics;
- introduce source-boundary violations;
- bypass provenance;
- introduce temporal leakage;
- duplicate business logic in the frontend;
- delete useful Streamlit implementation history merely because it is being superseded.

The Streamlit frontend should remain available as historical/reference material until the new frontend reaches validated parity for the intended functionality and an explicit deprecation decision is made.

## 15. Validation requirements

Every meaningful migration step must preserve the existing research baseline and appropriate health gates.

At minimum, UI migration work must validate:

- the new workspace renders;
- navigation works in the same-tab FRL contract;
- canonical fixture/team/player identities remain unchanged;
- trusted query results remain unchanged;
- provenance remains accessible;
- incomplete data states remain safe;
- visualisation semantics remain tied to the analytical result definition;
- the 26/26 research regression baseline remains green where the change is presentation-only;
- the project-health gate remains acceptable under its documented warning rules.

## 16. Migration success criterion

Success is **not**:

> "The Streamlit pages now exist in React."

Success is:

> **The FRL has a fast, beautiful, interactive visual research environment that exposes deeper analytical and modelling capability while preserving the project's trusted data, provenance, temporal semantics, relationships, colour system, typography and GUI contract.**

## 17. Immediate next step

Do not continue speculative Streamlit UI patching while the frontend architecture decision is being adopted.

The next substantive frontend task should be a small **Next.js foundation spike** that proves:

1. the FRL visual system can be reproduced faithfully;
2. the existing Python query layer can be exposed cleanly;
3. a typed research result can drive both a table and an interactive Plotly/bespoke visualisation;
4. entity navigation preserves the FRL's same-tab behaviour and canonical route semantics;
5. the development workflow remains free/self-hostable and auditable.

Only after that spike is validated should the migration proceed to larger workspace conversion.
