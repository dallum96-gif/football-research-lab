# Football Research Laboratory — Master Prompt

We’re working on the **Football Research Laboratory**.

## North Star

The Football Research Laboratory is intended to become a **serious, extensible football research and modelling platform, football intelligence and scouting environment**, not merely a football statistics website or a single betting model.

Its purpose is to allow a researcher, analyst or scout to start with a football question or hypothesis and progressively:

**interrogate the underlying data → identify patterns → understand what is happening → understand players/teams and their roles → construct derived metrics → build and evaluate predictive models → apply useful models where appropriate, including betting and decision support.**

The system should ultimately allow the user to **query almost anything that can reasonably be answered from the available football data**, including through a future natural-language interface in which questions can be asked in plain English and answered with evidence and links back to the relevant underlying data and research objects.

The initial implementation may be relatively small in scope, beginning with approximately a decade of Premier League data, but the architecture should be **deliberately extensible** toward much larger league, team, fixture, player, event and scouting datasets.

## Core principles

### 1. Data is infrastructure.

Build a rich, well-understood and historically useful data foundation. Preserve useful source variables even when their eventual analytical application is not yet known.

### 2. The architecture must support discovery.

Do not design the system around today’s hypotheses or today’s preferred metrics. The underlying data and architecture should outlive any individual metric, research question or predictive model.

### 3. Derived metrics and models are experiments.

Metrics, features, player/team classifications and predictive models should be straightforward to construct, compare, revise and replace. There is no assumption that one permanent model or classification is the “correct” one.

### 4. Research comes before betting.

Betting is an eventual application of predictive research, not the purpose of the underlying platform. No betting application should be treated as trustworthy merely because a model appears convincing in-sample; predictive claims must be challenged and evaluated appropriately.

### 5. Explanation matters as well as prediction.

The Laboratory should help us understand football phenomena, players, teams and roles, not merely produce predictions. A model that predicts well and a relationship that explains something interesting are both valuable research outputs.

### 6. Data quality and provenance come before presentation.

Interfaces, visualisations and analytical outputs must not outrun the reliability, coverage, provenance or understanding of the underlying data.

### 7. The user should not need to know the database schema to research football.

The complexity of the backend should be accessible through structured exploration and, eventually, natural-language querying. The backend may be considerably richer than what is directly exposed in the UI.

### 8. The project should grow deliberately.

Start small enough to build reliably, but do not make architectural decisions that unnecessarily prevent future expansion.

### 9. Research must be reproducible.

Serious research outputs should be traceable through the chain:

**source data → transformations → derived metrics/features → population/sample → model/version → result.**

Where practical, the Laboratory should allow an analysis to be reproduced rather than merely displaying its final result.

### 10. Temporal reconstruction is a core capability.

The Laboratory should preserve sufficient temporal information to reconstruct the state of football at a specified point in time.

### 11. Historical state and information availability must be distinguishable.

Where relevant, the Laboratory must distinguish between:

**what had happened by a given point in time**

and

**what information would actually have been available to a researcher, bettor, scout or predictive model at that point in time.**

### 12. Uncertainty and limitations must remain visible.

The Laboratory should distinguish between source facts, derived statistics, analytical interpretations, scouting classifications and model outputs.

Where data is incomplete, estimated, inconsistent, uncertain or insufficient to answer a question reliably, the system should expose that limitation rather than create false precision.

### 13. The backend should preserve optionality.

The data foundation should be richer and more stable than any individual analytical layer built upon it.

Do not prematurely discard potentially useful source information merely because it does not have a current UI representation or known modelling use. Collect and preserve useful data responsibly, while keeping its provenance and meaning clear.

### 14. The Laboratory should support exploration, research, scouting and formal analysis.

Exploration may be iterative and provisional; formal research and scouting outputs should be identifiable as such and supported by appropriate validation, provenance and reproducibility.

### 15. Foundational decisions become durable project memory.

When an architectural, data, ingestion, UI, modelling, provenance, safety, source-acquisition or repository decision becomes fundamentally important to the long-term Laboratory, the authoritative detail must be written into the appropriate repository document and committed to the active development branch.

The Master Prompt should contain the recovery rule and point to the authoritative document; it should not attempt to hold every architectural detail itself.

Repository documentation is the project’s durable memory. Conversation is working context.

## Universal variable accessibility

Every **validated** FRL variable should be discoverable and retrievable through one standard programmatic access seam without requiring downstream consumers, including the GUI, to know the variable’s source schema, storage location or source-family-specific retrieval mechanism.

The governing contract is:

`FRL_UNIVERSAL_VARIABLE_ACCESS_CONTRACT.md`

The intended flow is:

```text
VARIABLE CATALOGUE
      ↓
VARIABLE RESOLVER
      ↓
QUERY / RESEARCH SERVICES
      ↓
GUI / OTHER CONSUMERS
```

This does **not** mean every discovered source field is automatically GUI-visible. The FRL retains explicit lifecycle states such as discovered, catalogued, validated, resolvable and GUI-accessible. The GUI may expose variables progressively, but it must not become a second variable registry or analytical engine.

## Project-state recovery

Treat `dallum96-gif/football-research-lab` as the **source of truth**.

Before doing substantive work, read:

* `PROJECT_ORIENTATION.md`
* `CURRENT_WORK.md`
* `DATA_CONSTRUCTION.md`
* `RISK_STRATEGY_FRAMEWORK.md`
* `NON_DESTRUCTION_ASSURANCE.md`
* `UI_DESIGN_SYSTEM.md`
* `PROJECT_VISION.md`
* `FRL_DATA_HIERARCHY_RELATIONSHIP_CONTRACT.md`
* `FRL_RELATIONSHIP_INTEGRITY_CONTRACT.md`
* `FRL_DATA_PLATFORM_ARCHITECTURE_V1.md`
* `FRL_DATA_RESIDENCY_LINEAGE_INVENTORY_V1.md`
* `FRL_ANALYTICAL_DATA_LAYOUT_V1.md`
* `FRL_VISUALISATION_DATA_CONTRACT.md`
* `FRL_PLAYER_METADATA_SOURCE_ASSESSMENT_V1.md`
* `FRL_DATA_ECOSYSTEM_DISCOVERY_CONTRACT.md`
* `FRL_SOURCE_NORMALISATION_CONTRACT.md`
* `SESSION_START_PROTOCOL.md`

Then inspect the relevant code and establish the current branch/state before doing anything.

Do not ask me to re-explain the project when the information can be recovered from the repository and project documentation.

The fresh-session sequence is therefore:

**read orientation → read current work → read the governing vision/data/architecture/relationship/residency/layout/visualisation/source/discovery/normalisation contracts → establish repo/branch state → inspect working/archived/local mechanisms where needed → run 26/26 → run project health → only then start substantive work.**

### Branch safety

After establishing the current branch, compare it with `main` before any write.

Treat `main` as the stable/trusted integration line and the active feature/redesign/research branch as the development line.

**Never write development, experimental or research work directly to `main`.** When using GitHub tools/connectors with an optional branch parameter, always pass the intended development branch explicitly. Never rely on the repository default branch for a development write.

If the active branch is behind `main`, inspect the main-only commits before creating new work.

If the active branch is ahead of `main` by substantial work, do not casually rebase, force-push, reset or merge it. First establish:

* the merge base;
* commits unique to each side;
* which branch contains the intended trusted state;
* whether any work has accidentally been written to `main`.

If destructive ref movement is genuinely required, create a named safety branch at the current tip first and record why the ref is being moved.

Development work should reach `main` through an explicit, validated integration/release decision rather than by moving the `main` ref directly.

When the active branch has become the effective current project state, that does not automatically make it the new `main`. Decide deliberately when and how integration occurs.

## Relationship and identity safety

`FRL_RELATIONSHIP_INTEGRITY_CONTRACT.md` is authoritative for canonical join semantics.

Do not infer relationships from column names or numeric coincidence.

A format or storage migration is only equivalent when these canonical relationship and identity semantics survive, together with fail-closed behaviour. Matching row counts and columns is necessary but not sufficient.

## Player metadata and scouting-source safety

`FRL_PLAYER_METADATA_SOURCE_ASSESSMENT_V1.md` is authoritative for the current assessment of detailed player metadata sources.

Desired future metadata includes fixture-level position, detailed role/position labels where genuinely supported, preferred foot and related scouting information.

Do not make an external provider a foundational FRL ingestion dependency merely because a scraper or community API demonstrates that the field exists. Assess source rights, access stability, historical coverage, field semantics, identity resolution, reproducibility and redistribution before promotion.

The preferred pattern is:

```text
source player/fixture evidence
        ↓
verified identity / fixture crosswalk
        ↓
player-fixture evidence
        ↓
derived role/position classification
        ↓
player research / scouting / modelling
```

Preserve source observations and derivation logic separately. Do not silently overwrite trusted canonical data.

## Long-term data architecture

The FRL should be treated as a connected football evidence system with a data platform underneath the UI.

Read the governing hierarchy, relationship, platform, residency, analytical-layout, visualisation, discovery, normalisation and player-metadata source documents named above before making architecture changes.

The guiding principle is:

> **Retain broadly. Validate rigorously. Expose progressively. Promote empirically.**

The intended long-term separation is:

```text
EXTERNAL SOURCES
      ↓
INGESTION / SNAPSHOTS
      ↓
RAW EVIDENCE
      ↓
VALIDATION / RECONCILIATION
      ↓
CANONICAL FRL DATA
      ↓
DERIVED STATE / FEATURES
      ↓
ANALYTICAL LAYER
      ↓
RESEARCH / SCOUTING / MODELS
      ↓
QUERY API
      ↓
VISUALISATION
      ↓
GUI
```

GitHub is primarily the versioned control plane for code, schemas, contracts, tests, transformations, provenance and selected reproducible artefacts. Large/raw evidence should not be allowed to turn Git into a permanent data warehouse merely because it is convenient today.

The target architecture is local-first and scalable: columnar datasets such as Parquet with an analytical engine such as DuckDB initially, with object storage and orchestration introduced only when the data volume or operational requirements justify them. Do not perform a wholesale migration merely for architectural fashion.

Different leagues and providers are expected to have different source schemas. The FRL must use explicit source adapters and normalisation contracts to translate source-specific field names, grains, identifiers, units and definitions into canonical FRL meanings without erasing the native evidence. See `FRL_SOURCE_NORMALISATION_CONTRACT.md`.

The analytical layer must preserve the FRL graph rather than collapse it into a universal mega-table. Its primary canonical grains are:

```text
Fixture        = (season, fixture_id)
Team–Fixture   = (season, fixture_id, persistent_team_code)
Player–Fixture = (season, fixture_id, canonical player identity)
```

Identity bridge datasets and source-local identifiers remain explicit. Derived datasets and materialisations must retain a traceable route to their canonical inputs.

### Visualisation is a first-class research capability

Data visualisation is a major part of the FRL, not decoration added after the analysis is finished.

The platform should make it straightforward to build beautiful, useful and interactive charts, tables, comparisons, distributions, timelines, model diagnostics and bespoke visual research tools.

Visualisations are downstream research views over trusted analytical outputs and must inherit population, filters, provenance, temporal semantics, uncertainty and methodology. All user-facing visualisation must comply with `GUI_DESIGN_CONTRACT.md` and `UI_DESIGN_SYSTEM.md`.

## Current architectural priorities

Distinguish between:

* **what belongs in the long-term Laboratory**;
* **what needs to be built now**;
* **what is interesting but should be parked for later**.

The current architecture prioritises:

1. trustworthy canonical football entities and relationships;
2. rich retained source evidence;
3. temporal/historical reconstruction;
4. interconnected player/team/fixture research and scouting views;
5. reusable analytical/query services;
6. rich data visualisation and comparison capabilities;
7. future combined metrics and research querying;
8. future replaceable mathematical/statistical models;
9. only then explicit market/betting applications.

Do not add infrastructure merely because it is technically interesting. Add it when it materially improves scalability, reproducibility, provenance, reliability or future research capability.

## Working philosophy

Build the house in stages, but keep the long-term shape of the house in mind.

The blueprint will evolve as we learn more about the data and the research problems. That is expected.

Preserve the underlying architecture so that new questions, variables, derived metrics, scouting classifications and models can be added without repeatedly rebuilding the foundations.

**Build the foundations first. Discover the models later.**
