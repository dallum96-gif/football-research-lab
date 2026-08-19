# Football Research Laboratory — Upstream Source Boundary Contract

**Status:** Foundational source-governance rule  
**Date:** 19 August 2026  
**Scope:** Current FRL Premier League dataset boundary

## 1. Hard source rule

Until the Football Research Laboratory either:

1. expands beyond the currently supported historical boundary of **2008-09**, or
2. adds a **new football league/competition**,

**the Laboratory's football data must be sourced exclusively from the upstream GitHub repository:**

`imadeddine-belkat/Premier-League-Stats`

and from the **upstream data feeds used by that repository itself**.

No other external football-data provider, third-party football dataset, community dataset, alternative API or independent scraping source may be introduced as evidence into the FRL during this scope period.

## 2. Meaning of "source"

The upstream repository is the controlled source boundary for current FRL football evidence. Its own documented upstream feeds include, among others:

- the official Fantasy Premier League API for the FPL data family;
- Premier League / PulseLive feeds underlying the historical `pl_stats` archive.

The FRL may inspect the upstream repository's source code, schemas, CSV files and provenance documentation to understand how those datasets were produced.

## 3. FRL ingestion model

The current operating pattern is:

```text
UPSTREAM GITHUB REPOSITORY
        ↓
its upstream feeds / source pipeline
        ↓
source CSV / JSON evidence
        ↓
FRL ingestion / validation
        ↓
FRL repository data + provenance
        ↓
canonical / analytical layer
```

Where practical, source CSV files from the upstream repository are copied or written into the FRL repository as controlled evidence artefacts before downstream canonicalisation or derivation.

The FRL must preserve the distinction between:

- upstream source evidence;
- FRL-validated representations;
- FRL canonical entities and relationships;
- derived metrics/features;
- research/model outputs.

## 4. Prohibited source substitution

During the current scope period, FRL work must not introduce a second source merely because it appears to provide:

- more variables;
- cleaner lineups;
- injury classifications;
- manager histories;
- better metadata;
- easier fixture IDs;
- wider historical coverage;
- apparently missing statistics.

If the upstream repository does not currently provide a requested capability, the correct conclusion is that the capability is **not established from the current FRL source boundary** unless it can be obtained from the repository's own upstream feeds or derived defensibly from evidence already inside that boundary.

Do not substitute external providers to fill gaps during this phase.

## 5. Discovery rule within the boundary

The FRL's existing ecosystem-discovery rule still applies, but discovery must occur **inside this source boundary first**.

Before declaring a field or capability unavailable, inspect where relevant:

- the upstream repository README and documentation;
- its ingestion/scraper code;
- all relevant source directories;
- season-specific CSV files;
- parallel source families;
- merged datasets;
- indexes and crosswalks;
- partitioned data such as `by_position`;
- archived or derived outputs already produced by the upstream repository;
- the upstream feeds used by that repository.

Failure to find a capability in one file or directory is not evidence that the capability is absent from the allowed source ecosystem.

## 6. Identity and provenance

The upstream repository's identifiers remain source-local until reconciled through the FRL's verified identity contracts.

The FRL must not weaken its existing rules merely because the upstream source uses apparently convenient numeric IDs.

Any imported source artefact should retain, where practical:

- source repository and path;
- source feed/provider;
- season/competition context;
- source identifiers;
- retrieval/snapshot date where known;
- transformation or import version;
- coverage/definition limitations.

## 7. Scope expansion trigger

This hard boundary may be reconsidered when either condition below becomes true:

```text
FRL historical coverage expands beyond 2008-09
                    OR
FRL adds another league/competition
```

At that point, the project may perform a formal source-acquisition review and introduce additional providers where justified by coverage, semantics, rights/access, reproducibility and provenance.

That expansion must be documented as an explicit architectural decision. It must not happen implicitly because a developer found a convenient external dataset.

## 8. Governing principle

> **For the current Premier League scope, preserve and exploit the evidence ecosystem we already own and understand before adding another source.**

The objective is to build a deep, reproducible FRL foundation from one controlled upstream evidence boundary rather than creating competing definitions, identities and provenance chains prematurely.
