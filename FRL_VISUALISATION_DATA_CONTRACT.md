# Football Research Laboratory — Visualisation Data Contract

**Status:** Foundational analytical/UI contract
**Date:** 17 August 2026
**Governing documents:** `FRL_ANALYTICAL_DATA_LAYOUT_V1.md`, `FRL_DATA_HIERARCHY_RELATIONSHIP_CONTRACT.md`, `FRL_RELATIONSHIP_INTEGRITY_CONTRACT.md`, `FRL_DATA_PLATFORM_ARCHITECTURE_V1.md`, `GUI_DESIGN_CONTRACT.md`, `UI_DESIGN_SYSTEM.md`

## 1. Purpose

Data visualisation is a first-class FRL research output.

Charts, tables, comparison views, timelines, distributions, model diagnostics and other visualisations must be generated from validated analytical or research results. Visualisation is a presentation of research evidence, not a separate source of truth.

## 2. Single-result principle

A research result should be representable through multiple presentation forms without changing its semantics.

```text
validated query / research result
          ↓
   result object / dataset
       ↙    ↓    ↘
    table  chart  comparison
```

A chart and a table showing the same result must use the same population, filters, time window and underlying values.

## 3. Required inherited semantics

Every substantive visualisation must inherit, where applicable:

- canonical entity and relationship semantics;
- population definition;
- filters and exclusions;
- season/competition scope;
- temporal/as-of semantics;
- source lineage and provenance;
- metric/feature version;
- sample size;
- uncertainty and limitations;
- missing-data semantics;
- model/experiment version where applicable.

Visualisation code must not silently recompute a metric differently from the analytical/query layer.

## 4. Visualisation types

The FRL should support a broad visual vocabulary, including:

- analytical tables;
- time-series charts;
- rolling-window charts;
- team/player comparisons;
- scatter plots and relationship views;
- distributions;
- ranking visualisations;
- H2H and matchup views;
- event timelines;
- league-position trajectories;
- home/away splits;
- player-role and performance profiles;
- model calibration/performance charts;
- probability/distribution displays;
- historical-state visualisations;
- research-population summaries.

New visualisation types are encouraged when they make a research question easier to understand, provided they preserve the governing semantics.

## 5. GUI constraint

Analytical richness does not override the GUI contract.

All user-facing visualisations must comply with `GUI_DESIGN_CONTRACT.md` and `UI_DESIGN_SYSTEM.md`.

The visual language should remain professional, elegant, analytical, information-rich, restrained, intuitive and visually distinctive without becoming decorative dashboard clutter.

Visualisation components should feel like part of the FRL rather than generic outputs from an analytics library.

## 6. Progressive disclosure

The existence of rich underlying data does not require the first screen to expose every metric.

Prefer:

```text
headline finding
   ↓
clear visual explanation
   ↓
supporting table / detail
   ↓
provenance / methodology
```

This preserves the FRL principle of a simple research experience on top of deep evidence.

## 7. Interactivity

Interactive visualisations may provide filters, comparison selection, hover detail, range selection, entity navigation and drill-down.

Interaction must modify the research population or presentation deliberately and visibly. It must not silently change the underlying definition of the statistic.

Where possible, selections should preserve navigability back to the underlying research object, fixture, team, player or source evidence.

## 8. Missing and uncertain data

Visualisations must not convert unknown or unavailable values into misleading zeros or fabricated continuity.

Where uncertainty or incomplete coverage materially affects interpretation, the visualisation should expose it through appropriate annotation, coverage information or explanatory text.

## 9. Reproducibility

For formal research outputs, the visualisation should be reproducible from the same result definition, dataset version and transformation/model version.

A visualisation must not become the only surviving representation of an analytical result.

## 10. Research usefulness test

Before adding a visualisation, ask:

> Does this make a football question easier to investigate, compare, explain or challenge?

Prefer visualisations that reveal relationships, change over time, distributions, uncertainty or meaningful contrasts over decorative summaries.

## 11. North Star alignment

The FRL should become capable of turning complex football evidence into clear, attractive and interrogable visual research outputs.

The governing principle is:

> **Make the evidence deep, the analysis rigorous, and the visual explanation beautiful.**
