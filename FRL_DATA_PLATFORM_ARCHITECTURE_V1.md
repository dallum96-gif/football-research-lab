# Football Research Laboratory — Data Platform Architecture V1

**Status:** Architectural contract / proposed implementation direction
**Date:** 17 August 2026
**Governing principles:** Master Prompt, `FRL_DATA_HIERARCHY_RELATIONSHIP_CONTRACT.md`, `DATA_CONSTRUCTION.md`, `RISK_STRATEGY_FRAMEWORK.md`, `NON_DESTRUCTION_ASSURANCE.md`

## 1. Purpose

The Football Research Laboratory is intended to grow from a relatively small Premier League research application into a scalable football research and modelling platform.

The data platform must therefore support:

- substantially larger datasets than the current repository can reasonably hold as its primary storage layer;
- repeated ingestion from external source systems;
- immutable source snapshots and provenance;
- canonical football entities and event relationships;
- historical and temporal reconstruction;
- reproducible derived features and research populations;
- analytical workloads over millions or substantially more records;
- replaceable ingestion implementations and analytical engines;
- future expansion to additional leagues, competitions, teams, players and source families.

This document defines the intended separation of responsibilities between source storage, ingestion, canonical data, analytical querying, research/model layers and the GUI.

## 2. Core decision

**GitHub is the software and research-control plane, not the permanent bulk-data warehouse.**

GitHub should remain the authoritative home for:

- application code;
- ingestion/transformation code;
- schemas and data contracts;
- tests and validation logic;
- project architecture and risk documentation;
- provenance metadata and correction records;
- model definitions and experiment definitions;
- small/reference datasets where version-control semantics are useful;
- selected reproducible canonical artefacts where their size and update pattern remain appropriate.

Large, rapidly growing or immutable source datasets should not be forced into Git merely because the repository currently contains some CSV data.

Existing committed data is not to be deleted or migrated destructively as part of adopting this architecture.

## 3. Target platform shape

The target architecture is:

```text
EXTERNAL SOURCES
      ↓
INGESTION / SOURCE ADAPTERS
      ↓
RAW SOURCE SNAPSHOTS
      ↓
VALIDATION / SCHEMA CHECKS
      ↓
IDENTITY RECONCILIATION
      ↓
CANONICAL DATA + EVENT LAYER
      ↓
DERIVED HISTORICAL STATE / FEATURES
      ↓
ANALYTICAL QUERY ENGINE
      ↓
RESEARCH / COMPARABLES / COMBINED METRICS
      ↓
MATHEMATICAL & PREDICTIVE MODELS
      ↓
DECISION / MARKET LAYER
      ↓
QUERY API
      ↓
GUI
```

GitHub sits across the system as the versioned control plane:

```text
GitHub
├── code
├── contracts
├── schemas
├── tests
├── transformations
├── provenance rules
├── model definitions
└── version / configuration metadata
```

## 4. Storage layers

### 4.1 Raw source layer

Purpose:

- preserve source evidence as received or captured;
- allow reconstruction of what the ingestion process actually saw;
- support provenance, checksums, snapshots and future reprocessing;
- avoid forcing raw source history into the canonical model.

Target storage:

- object storage/data-bucket architecture;
- local filesystem may remain a development cache and source workspace;
- immutable or versioned snapshots should be preferred.

The raw layer is not the research truth. It is evidence.

### 4.2 Validated source layer

Purpose:

- schema-normalised source datasets;
- explicit validation status;
- source-specific cleaning that does not yet claim canonical FRL meaning.

Every promoted dataset should retain enough metadata to answer:

- source family;
- source snapshot/version;
- retrieval timestamp where known;
- transformation version;
- validation status;
- checksum or equivalent content identity where practical.

### 4.3 Canonical FRL layer

Purpose:

- stable football entities and relationships;
- persistent identities alongside season-local source identities;
- canonical fixture identity;
- player-fixture, team-fixture and event relationships;
- provenance-preserving corrections;
- temporal semantics needed by historical reconstruction.

Current canonical examples remain authoritative:

- `fixtures_master_corrected.csv`;
- `identity/team_seasons.csv`;
- `identity/data_quality/fixture_corrections.csv`;
- `data/fixture_match_stats.csv`;
- validated player-match evidence mechanisms.

Future canonical datasets may use columnar formats and analytical tables rather than CSV, but their semantic contracts must remain explicit.

### 4.4 Derived / feature layer

Purpose:

- historical match state;
- rolling windows;
- per-90 metrics;
- opponent-strength measures;
- combined metrics;
- model-ready feature matrices;
- research populations.

Derived data must always retain a route back to the canonical rows that produced it.

A derived feature is not a new source of truth.

## 5. File format direction

The intended scalable analytical representation is **columnar data, with Parquet as the preferred first implementation target**.

Reasons for this architectural preference:

- efficient analytical access;
- portable storage independent of one GUI/application;
- practical compatibility with local and cloud object storage;
- easier separation between raw/canonical/derived datasets;
- suitability for analytical engines without requiring a traditional transactional database for every research workload.

This is a direction, not a command to convert every existing CSV immediately.

Existing CSV artefacts remain valid where they are currently the trusted contract.

## 6. Analytical engine direction

The initial analytical engine should favour a local-first architecture capable of querying columnar datasets directly.

**DuckDB is the preferred first analytical-engine candidate for this role**, subject to validation against the actual FRL workloads.

The architecture must keep the analytical engine replaceable. The research contract belongs to the query/data semantics, not to a specific database product.

Possible future evolution:

```text
local DuckDB
    ↓
larger shared analytical deployment
    ↓
warehouse / distributed analytics where justified by scale
```

The FRL should not adopt an enterprise warehouse prematurely simply because one may eventually be useful.

## 7. Ingestion architecture

Ingestion should be implemented as explicit source adapters with a common contract.

Conceptually:

```text
source adapter
    ↓
raw snapshot
    ↓
schema validation
    ↓
normalisation
    ↓
identity reconciliation
    ↓
canonical promotion
    ↓
quality gate
```

The ingestion language is intentionally not fixed.

Python remains a valid and preferred implementation where it suits data processing and existing research code.

TypeScript may be used selectively where it provides a material advantage for a particular source adapter, runtime environment or orchestration requirement.

The platform must not encode the assumption that all ingestion must be written in one language.

## 8. Orchestration

A workflow orchestrator may eventually coordinate scheduled ingestion and promotion jobs.

`n8n` is an acceptable candidate for this orchestration role, but it is **not** the canonical home for football research logic.

Orchestration should coordinate explicit version-controlled jobs such as:

```text
schedule
  ↓
fetch source snapshot
  ↓
run adapter
  ↓
validate
  ↓
reconcile identities
  ↓
publish validated data
  ↓
run quality gates
  ↓
record provenance
```

Core football transformations must remain inspectable, testable code rather than opaque workflow configuration.

## 9. Object storage direction

When raw and large analytical datasets outgrow practical Git storage, the target data-lake/object-storage layer should support a bucket architecture such as:

```text
football-research-lab/
├── raw/
├── validated/
├── canonical/
├── events/
├── player_match/
├── team_match/
├── historical_state/
├── features/
├── model_inputs/
└── snapshots/
```

The exact cloud provider is intentionally undecided at V1.

S3-compatible object storage, GCP Cloud Storage or another equivalent service can satisfy the storage contract. The contract should not hard-code a provider unnecessarily.

## 10. Provenance contract

Every promoted data state should be traceable through:

```text
source
  ↓
snapshot
  ↓
ingestion version
  ↓
validation result
  ↓
identity mapping
  ↓
canonical dataset version
  ↓
derivation / feature version
  ↓
research population
  ↓
model / experiment version
  ↓
result
```

Where practical, store:

- source identifier;
- source location/family;
- retrieval timestamp;
- snapshot/version identifier;
- content checksum;
- transformation version;
- validation result;
- identity mapping version;
- canonical dataset version;
- feature/metric version;
- model version.

The system must never require a user to trust a number merely because it appears in the GUI.

## 11. Temporal integrity

The data platform must preserve both:

1. **what had happened by a specified point in time**; and
2. **what information was actually available by that point in time**.

Source snapshots and retrieval metadata are therefore part of the platform design, not optional administrative information.

Historical state and model features must not use future information merely because a later canonical snapshot contains it.

The architecture must support as-of reconstruction without silently replacing historical knowledge with present-day truth.

## 12. Scale principle

The platform should be designed so that rapid growth in row count does not require a foundational redesign.

The architecture should remain sensible if the FRL grows from:

```text
thousands
  ↓
tens of thousands
  ↓
millions
  ↓
tens / hundreds of millions
```

This does **not** mean engineering for extreme scale in advance.

It means avoiding decisions that make moderate growth painful and force a future emergency migration.

## 13. What we are not doing now

V1 explicitly does **not** require:

- immediate migration of all current CSV files;
- deleting data from GitHub because object storage is planned;
- a full enterprise warehouse deployment;
- distributed compute infrastructure;
- rewriting Python ingestion in TypeScript;
- introducing n8n before repeated workflows justify orchestration;
- replacing `query_lab.py` / `query_api.py` with a new data access layer;
- redesigning the GUI around the new storage architecture.

The purpose of V1 is to establish the correct boundaries before scale forces a decision.

## 14. Immediate implementation sequence

The first practical implementation should be local and reversible:

```text
1. inventory existing source/canonical/derived datasets
2. record data residency and lineage
3. define canonical Parquet schemas for selected large datasets
4. build a local reproducible export/promotion step
5. validate equivalence against current trusted CSV outputs
6. prove DuckDB can answer current query workloads
7. only then consider object-storage deployment
8. introduce orchestration only where repeated ingestion creates operational work
```

Existing CSV-backed query paths remain active until a new representation has passed equivalence checks.

## 15. Non-destruction requirement

No storage migration may:

- delete the only known copy of source evidence;
- overwrite canonical truth without provenance;
- silently change identifiers;
- change query semantics merely because storage changed;
- change historical-state definitions;
- remove an existing validated consumer before the replacement is proven equivalent.

Migration must be additive first and subtractive only after equivalence and rollback are established.

## 16. Decision rule for future infrastructure

Adopt a new tool or infrastructure component only when it solves a demonstrated problem in the FRL.

The decision sequence is:

```text
Observed bottleneck / scale requirement
        ↓
Define measurable problem
        ↓
Test smallest viable solution
        ↓
Validate against existing contracts
        ↓
Adopt only if materially better
```

This prevents technology-led architecture while still preserving scale optionality.

## 17. Relationship to the FRL North Star

This architecture exists to support the long-term Laboratory rather than to become the project itself.

Its purpose is to make the following increasingly achievable without repeatedly rebuilding the foundations:

- arbitrary football research questions;
- deep fixture/player/team event exploration;
- combined metrics;
- comparable-match research;
- historical reconstruction;
- player/team influence analysis;
- independent predictive models;
- ensembles and research consensus;
- future market/decision tooling;
- natural-language research queries.

The governing principle remains:

> **Preserve the evidence broadly, keep the research experience simple, and make every analytical layer replaceable.**
