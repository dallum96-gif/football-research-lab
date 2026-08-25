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
* `FRL_SOURCE_ARCHIVE_AND_DATABASE_DECISION_V1.md`
* `FRL_NEXT_SESSIONS_PLAN_V1.md`
* `FRL_DATA_RESIDENCY_LINEAGE_INVENTORY_V1.md`
* `FRL_ANALYTICAL_DATA_LAYOUT_V1.md`
* `FRL_VISUALISATION_DATA_CONTRACT.md`
* `FRL_PLAYER_METADATA_SOURCE_ASSESSMENT_V1.md`
* `FRL_DATA_ECOSYSTEM_DISCOVERY_CONTRACT.md`
* `FRL_SOURCE_NORMALISATION_CONTRACT.md`
* `FRL_SOURCE_BOUNDARY_CONTRACT.md`
* `SESSION_START_PROTOCOL.md`
* `FRL_MASTER_FRONTEND_MIGRATION_PLAN_V2.md` when doing frontend, GUI, visualisation or modelling-presentation architecture work
* `FRL_RESEARCH_RESULT_CONTRACT_V1.md` when implementing analytical-result presentation or API contracts
* `FRL_FRONTEND_MIGRATION_RISK_ADDENDUM_V1.md` and `FRL_FRONTEND_MIGRATION_NON_DESTRUCTION_ADDENDUM_V1.md` when changing frontend architecture

Then inspect the relevant code and establish the current branch/state before doing anything.

Do not ask me to re-explain the project when the information can be recovered from the repository and project documentation.

The fresh-session sequence is therefore:

**read orientation → read current work → read the governing vision/data/architecture/relationship/residency/layout/visualisation/source/discovery/normalisation/source-boundary/archive/database/roadmap contracts → establish repo/branch state → inspect working/archived/local mechanisms where needed → run the relevant validation gates → only then start substantive work.**

## Frontend migration recovery rule

`FRL_MASTER_FRONTEND_MIGRATION_PLAN_V2.md` is now the authoritative frontend migration plan. It supersedes V1.

The migration is a presentation/interaction architecture change, not a rewrite of trusted football data or research semantics.

The live `gui/theme.py` implementation is authoritative for current GUI colour. The current site uses a warm light analytical canvas with warm white surfaces, near-black text, muted warm-grey metadata, orange-red primary accent, restrained olive/green secondary accent, subtle borders and a dark navigation sidebar. Older dark charcoal / blue-black application-canvas wording is superseded for current GUI work.

The existing `GUI_DESIGN_CONTRACT.md` and `UI_DESIGN_SYSTEM.md` remain authoritative for typography, hierarchy, spacing, interaction character and visual restraint.

The migration must preserve canonical identities and relationship semantics, particularly:

```text
Fixture        = (season, fixture_id)
Player–Fixture = (season, fixture_id, canonical player identity)
season-local team identity -> verified persistent club identity
season-aware source player identity -> verified canonical player identity
```

The migration should build reusable Research Results so that the same trusted analytical result can drive tables, charts, comparisons, timelines, distributions, summaries and provenance views without changing semantics.

Data visualisation and statistical-model presentation are first-class early migration capabilities. Plotly is an analytical tool where appropriate; bespoke React components should be used where custom interaction or research workflow requires them. Python remains the statistical/model engine behind the frontend API boundary.

The migration must remain free/self-hostable and must preserve the existing same-tab navigation behaviour unless explicitly changed by a future product decision.

## Upstream source boundary

The current football-data source boundary is deliberately hard and is governed by `FRL_SOURCE_BOUNDARY_CONTRACT.md`.

Until the FRL expands beyond **2008-09** or adds another **league/competition**, the Laboratory must source football data exclusively from:

`imadeddine-belkat/Premier-League-Stats`

and the upstream feeds used by that repository itself.

The current FRL operating pattern is to take the repository's source CSV evidence and write/copy controlled source artefacts into the FRL repository before validation, canonicalisation or derivation.

No alternative football-data provider or third-party football dataset may be introduced during this scope period merely to fill a perceived gap. The first response to a missing capability is deeper discovery within this approved source boundary.

Do not confuse:

```text
upstream source evidence
        ↓
FRL imported evidence
        ↓
FRL canonical data
        ↓
FRL derived research data
```

with separate independent sources. The upstream repository and its own documented feeds are the sole football evidence boundary until the stated expansion trigger is reached.

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

If destructive ref movement is genuinely required, create a named safety branch at the current tip and record why the ref is being moved.

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

The current source-boundary contract is stricter: before the FRL expands beyond 2008-09 or adds another league/competition, such external football data must **not** be promoted into the FRL at all.

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

Read the governing hierarchy, relationship, platform, residency, analytical-layout, visualisation, discovery, normalisation, source-boundary, source-archive and database documents named above before making architecture changes.

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
2. rich retained source evidence and permanent local raw-source preservation;
3. temporal/historical reconstruction;
4. interconnected player/team/fixture research and scouting views;
5. a durable local analytical/data-store layer behind the research engine;
6. a genuinely navigable football database UI;
7. reusable analytical/query services and rich data visualisation;
8. future combined metrics and research querying;
9. future replaceable mathematical/statistical models;
10. only then explicit market/betting applications.

The navigable database UI and research laboratory are complementary goals. The UI should let users browse the same verified graph used by research queries: seasons, teams, players, player-seasons, fixtures, match observations and provenance.

Do not add infrastructure merely because it is technically interesting. Add it when it materially improves scalability, reproducibility, provenance, reliability or future research capability.

## Immediate roadmap

The current multi-session roadmap is authoritative in `FRL_NEXT_SESSIONS_PLAN_V1.md`.

The working sequence is:

1. finish source-field semantic review and conservative promotion;
2. consolidate relationship and provenance contracts;
3. formalise the immutable local source-archive contract;
4. design the local database / analytical store around the proven relationship graph;
5. implement the local store and prove it can be rebuilt from the preserved source archive;
6. move research/query workloads only after equivalence validation;
7. build the navigable football database UI;
8. build structured and natural-language research interfaces and visualisation;
9. expand into modelling and evaluation only after the evidence/data platform is stable.

Standing rule:

> **Do not build a higher layer to compensate for an unproven lower layer.**

Storage technology is replaceable; source evidence, relationships, provenance and research semantics are not.

## Working philosophy

Build the house in stages, but keep the long-term shape of the house in mind.

The blueprint will evolve as we learn more about the data and the research problems. That is expected.

Preserve the underlying architecture so that new questions, variables, derived metrics, scouting classifications and models can be added without repeatedly rebuilding the foundations.

**Build the foundations first. Discover the models later.**

# MASTER PROMPT V2 — MATURE PROJECT RECOVERY PROTOCOL

The FRL is now a mature, multi-layered research platform.

Before substantive work, recover the actual current project state. Do not infer architecture from a single branch, document, inventory or count.

## Mandatory recovery

1. Read the governing project documents and relevant contracts.
2. Establish current branch, commit, working-tree state and divergence from main.
3. Identify the current project phase.
4. Identify authoritative artefacts and their architectural layer.
5. Locate established mechanisms before designing replacements.
6. Inspect approved local/source-audit/archived mechanisms where necessary.
7. Locate and run the current validation gates.
8. Only then begin substantive implementation.

## Architectural layer rule

Never treat counts from different layers as interchangeable.

Current known distinction:

- 447 retained source fields = source-field inventory.
- 1,414 authoritative canonical variables = canonical-variable universe.

The 447 source-field universe is NOT the 1,414 canonical-variable universe.

Never rebuild a higher-level authoritative artefact from a lower-level inventory without first proving that the existing artefact is unavailable.

## Existing-system recovery rule

Before creating a new mechanism, search for:

- canonical mappings;
- variable dictionaries;
- routed-variable registries;
- attachment matrices;
- identity registries;
- relationship contracts;
- source-family adapters;
- research/query services;
- analytical services;
- GUI consumers;
- archived implementations;
- relevant tests.

Reuse established mechanisms before creating replacements.

## Protected systems

See FRL_PROTECTED_SYSTEMS.md.

Use FRL_PROJECT_STATE.yaml as the machine-readable project-state anchor, and verify it against the repository.

## Variable architecture

Variables belong to their natural analytical grain.

The standard consumer path is:

validated/canonical variable
→ canonical metadata
→ natural grain
→ verified identity/relationship bridge
→ existing research/query layer
→ structured value + provenance
→ authorised consumer.

Do not create bespoke page-specific extraction paths when established query infrastructure can be extended.

## Identity safety

Source identifiers are not automatically interchangeable.

Never infer canonical identity merely because numbers match, names look similar, or a convenient join works.

Ambiguous identity must fail closed.

## Temporal safety

Historical state and historical information availability are distinct.

Never backfill missing historical fields from later seasons or convert missing evidence into zero.

## Branch safety

Do not assume main is automatically the only current implementation state.

When branches diverge:

1. determine the merge base;
2. inspect each side's architectural contribution;
3. identify complementary, superseded and required work;
4. integrate on a safety branch;
5. validate;
6. only then promote the result.

Never casually reset, rebase, force-push or discard substantial project work.

## Validation

Do not rely on stale test filenames or stale documentation.

Locate the current validation gates in the actual checkout.

At minimum establish:

- project health;
- Core Query Lab;
- current Player Research gate;
- relevant identity/relationship tests;
- relevant Universal Variable Access tests;
- relevant GUI/frontend smoke tests.

Never claim a gate passed unless it was actually executed.

## Stop conditions

Stop and investigate if:

- authoritative artefacts appear contradictory;
- multiple plausible current branches exist;
- a requested variable already exists in the canonical universe;
- an apparently missing mechanism may exist elsewhere;
- identity evidence is ambiguous;
- temporal semantics are unclear;
- a branch is already in merge/rebase/conflict state;
- the current project phase is unclear.

## Governing principle

> Recover before building. Classify before interpreting. Reuse before replacing. Preserve before deleting. Validate before declaring success.

Do not make the next session reconstruct what the current session can make explicit.
