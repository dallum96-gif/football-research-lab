# FRL Source Archive and Database Decision V1

**Status:** Architectural decision / durable project memory
**Date:** 22 August 2026
**Governing documents:** `MASTER_PROMPT.md`, `RISK_STRATEGY_FRAMEWORK.md`, `FRL_DATA_PLATFORM_ARCHITECTURE_V1.md`, `FRL_RELATIONSHIP_INTEGRITY_CONTRACT.md`

## Purpose

This document records the storage and product direction agreed after reviewing the source-archive, database, provenance and relationship architecture together.

## 1. Upstream source remains authoritative

The upstream football source remains the authority for source facts.

FRL must not treat an internal transformation, CSV, database row or derived metric as a replacement for the upstream source definition.

The architectural distinction is:

```text
UPSTREAM SOURCE
      ↓
IMMUTABLE LOCAL SOURCE ARCHIVE
      ↓
INGESTION / VALIDATION
      ↓
FRL DATA STORE
      ↓
RELATIONSHIPS / RESEARCH
      ↓
GUI / OUTPUTS
```

## 2. Permanent local source preservation is a hard requirement

Whenever FRL ingests source data, it should preserve a durable local copy of exactly what was received.

The local source archive exists so that FRL can:

- recover if the upstream source disappears or changes;
- reproduce an ingestion later;
- inspect the original source evidence independently of downstream transformations;
- compare historical source snapshots;
- investigate whether an anomaly arose upstream or during FRL processing.

CSV is an acceptable and useful archive format for this purpose because it is portable, human-readable and easy to retain independently of the application/database stack.

The CSV is **not a competing canonical truth**. It is an immutable source artefact / evidence snapshot.

## 3. Database is the application data store

FRL should not require the application to pull from the upstream API on each page refresh.

The normal runtime path is:

```text
USER / UI
    ↓
QUERY / RESEARCH LAYER
    ↓
LOCAL OR FUTURE SHARED DATABASE / ANALYTICAL STORE
```

The scraper/ingestion process is separate:

```text
UPSTREAM SOURCE
    ↓
SCRAPER / ADAPTER
    ↓
LOCAL RAW ARCHIVE
    ↓
INGEST / VALIDATE / RECONCILE
    ↓
DATABASE / ANALYTICAL STORE
```

The database may initially run locally on the developer's machine. Cloud infrastructure is optional and should only be introduced when operational requirements justify it.

## 4. Storage technology is replaceable

The relationship contracts, provenance contracts and research semantics must not depend on whether FRL stores data in CSV, Parquet, DuckDB, PostgreSQL or a later cloud system.

The storage representation can evolve while preserving:

- canonical identities;
- relationship semantics;
- source-local identifiers;
- temporal semantics;
- provenance;
- fail-closed behaviour;
- research-query meaning.

## 5. Existing source pathways remain intact

The source-family adapters, identity registries, relationship contracts, field catalogue and evidence pathways already established in FRL remain part of the architecture.

A future database is an additional storage/query layer, not a reason to discard those pathways.

The migration target is therefore:

```text
CURRENT
CSV / SOURCE ARCHIVE
      ↓
ADAPTERS + RELATIONSHIPS
      ↓
RESEARCH QUERIES

TARGET
CSV / SOURCE ARCHIVE
      ↓
DATABASE / ANALYTICAL STORE
      ↓
ADAPTERS + RELATIONSHIPS
      ↓
RESEARCH QUERIES
```

The exact placement of adapters may evolve, but the logical contracts survive.

## 6. Non-destruction rule

No database or storage migration may delete the only known source copy, silently alter identity relationships, or replace a working query path before equivalence has been demonstrated.

The local source archive is retained even after a database representation has been validated.

## 7. Product vision

FRL is intended to be both:

1. a **navigable football database** where users can explore seasons, teams, players, fixtures, statistics and historical relationships; and
2. a **football research laboratory** where users can ask arbitrary research questions, construct derived metrics, compare situations, investigate historical states, evaluate models and inspect provenance.

These are complementary interfaces over the same underlying football evidence graph.

A representative navigation path is:

```text
Team
  ↓
Season
  ↓
Player
  ↓
Player-season
  ↓
Matches
  ↓
Fixture
  ↓
Player-match / team-match evidence
  ↓
Source provenance
```

The navigation must always follow the same verified relationship contracts used by research queries.

## 8. Current implementation direction

FRL remains local-first.

The existing architecture already identifies Parquet/DuckDB as the preferred first analytical representation. That direction should be treated as a practical implementation choice rather than a reason to remove the raw CSV/source archive.

The immediate goal is to prove equivalence and reuse established semantics before changing production consumers.
