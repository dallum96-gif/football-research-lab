# Upstream Data Preservation Contract

## Purpose

FRL preserves a local, versioned copy of upstream data that it decides to retain. The upstream provider is the factual source; the local archive is FRL's durable copy of that source evidence.

## Rules

1. Discover upstream capabilities before defining the FRL variable universe.
2. Audit variables before promotion; discovery never implies canonical trust.
3. Retained upstream data must be snapshotted locally in a machine-readable form, with CSV used for tabular datasets.
4. Preserve source-native values and identifiers before deriving FRL metrics.
5. Record provenance: source family, upstream endpoint/file, observation/snapshot date, season, and extraction version where available.
6. Do not silently discard upstream fields because an intermediate scraper does not publish them.
7. Fields may be preserved without being canonical or exposed in the research UI.
8. Exclusions must be explicit and documented rather than inferred from absence.
9. The FRL database/research layer derives from the local preserved archive, not from live API calls on page refresh.
10. Raw/local preservation and semantic promotion are separate concerns.

## Universe layers

- **Upstream capability universe:** everything the underlying source/API exposes and FRL can verify.
- **Published upstream universe:** what an intermediate repository/scraper currently exports.
- **FRL preserved universe:** what FRL has deliberately archived locally.
- **FRL semantic universe:** preserved variables with established meaning, taxonomy and provenance.
- **Research/UI universe:** variables exposed to search, profiles and derived research outputs.

## Current preservation direction

The current upstream lineage registry is `upstream_variable_universe.csv`.

It is a discovery/lineage registry, not a replacement for the raw preserved data archive. As source datasets are accepted into FRL, their actual observations should be snapshotted locally and represented as CSVs (or an equivalent raw representation where the source is inherently nested/non-tabular), with the registry retaining the provenance and semantic status.
