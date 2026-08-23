# Football Research Laboratory — Data Residency & Lineage Inventory V1

**Status:** Initial inventory / architecture evidence
**Date:** 17 August 2026
**Branch:** `design/player-filter-tiles`
**Governing documents:** `MASTER_PROMPT.md`, `FRL_DATA_PLATFORM_ARCHITECTURE_V1.md`, `FRL_DATA_HIERARCHY_RELATIONSHIP_CONTRACT.md`, `DATA_CONSTRUCTION.md`, `RISK_STRATEGY_FRAMEWORK.md`, `NON_DESTRUCTION_ASSURANCE.md`

## 1. Purpose

This document records where the FRL's important data currently lives, what role each dataset plays, how it enters the research system, and which consumers depend upon it.

This is an inventory, not a migration plan. No existing dataset should be deleted, relocated, or replaced merely because a future storage architecture has been proposed.

The key distinction is:

```text
SOURCE ORIGIN
    ↓
RAW / LOCAL SNAPSHOT
    ↓
VALIDATED
    ↓
CANONICAL
    ↓
DERIVED / FEATURE
    ↓
QUERY / RESEARCH / MODEL
```

A copy is not automatically a source of truth. Every important dataset should eventually have an explicit role and lineage.

## 2. Residency categories

### GitHub-tracked FRL data

Data committed to the repository and therefore recoverable from a Git checkout of the relevant branch.

Typical examples:

- canonical fixture artefacts;
- packaged fixture statistics;
- historical player/gameweek datasets currently used by Player Research;
- identity registries and provenance records;
- historical match-state feature files;
- validated player-match support files.

### Local research/source workspace

Data present on the user's local machine but not necessarily committed to the FRL repository.

This includes richer upstream source families and working/inspection material used to construct or investigate FRL data.

### Future object storage

Reserved for immutable raw snapshots and large/rapidly growing analytical datasets when Git storage becomes the wrong operational boundary.

No cloud provider is fixed by this contract.

## 3. Current canonical datasets

| Dataset | Current location | Role | Canonical? | Main consumers | Lineage / notes |
|---|---|---|---|---|---|
| `fixtures_master_corrected.csv` | GitHub / development branch | Canonical fixture master | Yes | `query_lab.py`, Fixtures, Fixture Landing Page, historical state | Key is `season + fixture_id`; corrections are provenance-preserving |
| `identity/team_seasons.csv` | GitHub / development branch | Season-local → persistent team identity registry | Yes | `query_lab.py`, team queries, fixture resolution | Must not be replaced by a single global source-team ID |
| `identity/data_quality/fixture_corrections.csv` | GitHub / development branch | Explicit fixture correction provenance | Yes | health gate, canonical interpretation | Additive correction record; do not silently overwrite evidence |
| `data/fixture_match_stats.csv` | GitHub / development branch | Packaged fixture statistics | Yes for packaged rows | `match_stats.py`, fixture research | Keyed by `season + fixture_id`; source match IDs retained |
| `identity/team_seasons_provenance.csv` | GitHub / development branch | Identity/provenance support | Supporting | identity/data-quality tooling | Preserve alongside identity mappings |
| `identity/data_quality/missing_fixture_results.csv` | GitHub / development branch | Known missing-result evidence | Supporting | project health / inspection | Represents an explicit known data condition |

## 4. Historical state and derived feature datasets

| Dataset | Current location | Role | Derived? | Consumers | Important invariant |
|---|---|---|---|---|---|
| `features/historical_match_state_v1.csv` | GitHub / development branch | Historical pre-match state | Yes | research/model preparation | State is constructed before current fixture is added to history |
| `features/historical_match_state_v2.csv` | GitHub / development branch | Revised historical-state representation | Yes | research/model preparation | Must retain explicit version identity; never silently replace v1 semantics |
| `features/*` future | Intended analytical layer | Model/research features | Yes | Query / models | Every feature should retain lineage to canonical rows |

Historical state is particularly sensitive: later data must not contaminate pre-match features. Retrieval and information-availability cutoffs are part of the meaning of these datasets.

## 5. Player Research data

The development branch currently tracks historical player/gameweek datasets under:

```text
_merged/players/<season>_all_players_gw.csv
```

These are used by the current Player Research query layer.

| Dataset family | Current location | Role | Consumer | Notes |
|---|---|---|---|---|
| `_merged/players/*_all_players_gw.csv` | GitHub / development branch | Historical player/gameweek evidence used by current research | `player_research.py`, Player Research UI | Preserve historical season coverage and source meaning |
| `players/<player>/<season>_gw_stats.csv` | GitHub / development branch for tracked records | Player-level supporting records | Player Research / identity work | These are evidence records, not automatic longitudinal truth |
| `player_identity_registry.csv` | GitHub / development branch | Player cross-season identity registry | player-match research | Identity evidence must be fail-closed |
| `player_identity_registry.py` | GitHub / development branch | Identity-resolution mechanism | player-match enrichment | Code, not data, but part of lineage |

The player layer should preserve useful source variables even where the current GUI does not expose them.

## 6. Player-match and event source families

The richer upstream source workspace is documented as separate from the FRL repository.

Known source families include:

```text
pl_stats/<club>/players_match_stats/<season>_players_match_stats.csv
pl_stats/<club>/events_stats/<season>_events_stats.csv
```

These are treated as source/evidence families unless and until they are deliberately promoted into a canonical FRL representation.

Important identity rule:

```text
upstream player/team/match identifiers
        ≠ automatically canonical FRL identifiers
```

Existing audited crosswalks and registries must be used for reconciliation.

## 7. Source-origin clarification

The FRL was initially built by scraping/downloading source material from GitHub-hosted football data onto the local research workspace.

That means the conceptual flow is:

```text
external / GitHub-hosted source material
        ↓
scraped/downloaded local source copy
        ↓
FRL processing + validation
        ↓
selected canonical / derived artefacts
        ↓
GitHub-tracked FRL project state
```

The Streamlit application does **not** live-scrape those historical source datasets at page-load time. It consumes the existing FRL data/query layer.

## 8. Current query consumers

The principal research boundary is:

```text
source/canonical data
        ↓
query_lab.py
        ↓
query_api.py
        ↓
GUI / research consumers
```

Important current query capabilities include:

- league tables;
- team summaries;
- multi-season team comparison;
- fixtures;
- fixture detail;
- head-to-head;
- form/streak queries;
- Player Research;
- player-match enrichment where verified.

The GUI should not create parallel data joins that bypass these contracts.

## 9. Data residency decision rules

### Keep in GitHub when:

- the file is part of a schema/contract;
- the file is small enough for practical version control;
- the file benefits materially from Git history and review;
- it is a selected canonical/reference artefact;
- it is provenance metadata, validation output or configuration.

### Prefer Parquet / analytical storage when:

- the data is tabular and primarily analytical;
- row counts are growing rapidly;
- repeated scans make CSV increasingly inefficient;
- multiple research consumers need the same analytical representation;
- the dataset can be regenerated or reconciled through an explicit contract.

### Prefer object storage when:

- the data is raw source evidence;
- snapshots are large;
- retention is long-term;
- the dataset is expected to grow materially;
- immutable/versioned source history is more important than Git diff semantics.

### Keep local-only temporarily when:

- the source is not yet ready for canonical promotion;
- it is an inspection/research artefact;
- committing it would create unnecessary repository weight;
- provenance or redistribution rights have not yet been established.

Local-only does not mean unimportant. Important local source data should be discoverable and its role documented.

## 10. Migration safety contract

Before moving any current dataset from CSV/Git-backed storage to a new representation, the new representation must demonstrate:

1. schema equivalence;
2. identifier/key equivalence;
3. row-count equivalence or an explicit explained delta;
4. metric/value equivalence for trusted outputs;
5. provenance preservation;
6. temporal semantics preservation;
7. consumer/query equivalence;
8. rollback availability.

The existing trusted representation remains active until the replacement has passed these checks.

## 11. Current gaps identified by this inventory

### Gap A — original canonical build is not fully reproducible

`DATA_CONSTRUCTION.md` records that the original one-off construction pipeline for the canonical fixture master and complete team identity registry is not yet committed as a single end-to-end rebuild process.

This is a reproducibility gap and should eventually be addressed before large-scale storage migration.

### Gap B — raw-source residency is not yet fully catalogued

The local `pl_stats` source workspace contains important source families, but the FRL does not yet have a machine-readable inventory of every source family, snapshot date and checksum.

### Gap C — GitHub currently carries some large datasets

The development branch contains large historical player CSVs and other data artefacts. This is acceptable for the current state, but reinforces the need for a future scale-aware storage boundary.

### Gap D — no canonical Parquet promotion pipeline yet exists

Parquet is the preferred direction, but there is not yet a validated export/promotion mechanism that can prove equivalence with current CSV-backed query results.

### Gap E — no cloud object-store implementation yet

This is intentional. Cloud storage is a future deployment option, not a requirement of V1.

## 12. Immediate next implementation milestone

The next practical platform task is **not** a full migration.

It is:

```text
select one large trusted dataset
        ↓
write an explicit Parquet schema
        ↓
export locally
        ↓
query with DuckDB
        ↓
compare outputs against the existing CSV/query path
        ↓
record evidence
```

The first candidate should be chosen by measurable analytical usefulness and size, not convenience.

Only after equivalence is demonstrated should the FRL consider promoting the pattern to additional datasets or cloud object storage.

## 13. Governance principle

The guiding rule for future work is:

> **Preserve broadly, classify explicitly, promote carefully, and migrate only after equivalence.**

The purpose of the data platform is to make the FRL more scalable without making the research environment less trustworthy.
