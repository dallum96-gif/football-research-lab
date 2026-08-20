# FRL Visualisation — Research Result Addendum V1

## Principle

The FRL treats data visualisation and statistical/model diagnostics as first-class research outputs.

A visualisation should be generated from a trusted Research Result or equivalent analytical result object rather than becoming an independent calculation path.

## Shared-result pattern

```text
trusted analytical/query result
              ↓
        Research Result
       ↙       ↓       ↘
    table     chart   comparison
       ↘       ↓       ↙
        timeline / distribution
              ↓
      provenance / methodology
```

All representations should preserve the same population, filters, temporal scope, values, uncertainty and analytical semantics.

## Interactive analysis

The frontend should support, where useful:

- fast entity selection;
- contextual filtering;
- hover detail;
- range selection;
- chart/table coordination;
- comparison selection;
- drill-down;
- historical/as-of exploration;
- research-population inspection;
- provenance and methodology inspection.

Interaction must make its effect on the analytical population or presentation explicit.

## Visualisation stack

Use Plotly/React Plotly where mature analytical chart primitives provide a clear advantage.

Use bespoke React visualisations when custom interaction, entity linkage, historical exploration or research workflow requires finer control.

Do not let a visualisation library dictate the FRL visual identity.

## Statistical modelling views

Model diagnostics should be visual research outputs in their own right.

The frontend should progressively support:

- probability distributions;
- calibration plots;
- prediction-vs-actual views;
- residual/error views where appropriate;
- model comparison;
- baseline comparison;
- uncertainty intervals;
- walk-forward performance;
- robustness/sensitivity views.

These views must remain downstream of validated model outputs and evaluation evidence.
