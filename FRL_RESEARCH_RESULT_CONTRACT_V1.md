# Football Research Laboratory — Research Result Contract V1

**Status:** Architectural contract / implementation boundary  
**Date:** 17 August 2026

## Purpose

A research result is the reusable analytical output produced by the FRL query layer. It is the boundary between analytical computation and every downstream consumer: tables, charts, comparisons, exports, research pages and future models.

## Required properties

Every research result must carry:

- `query_type` — stable semantic identifier for the query;
- `query_version` — version of the query logic;
- `parameters` — explicit query inputs;
- `columns` — ordered result fields;
- `rows` — tabular result data;
- `population` — what observations were eligible and how many contributed;
- `provenance` — source/lineage information sufficient to reproduce the result;
- `temporal_context` — season/date/as-of semantics where relevant;
- `limitations` — known gaps, exclusions or uncertainty;
- `generated_at` — generation timestamp.

## Separation of concerns

The analytical layer owns meaning and calculation. Consumers must not silently recalculate the result from presentation data.

A visualisation consumes the result. A table consumes the result. An export consumes the result. A future model may consume the result.

## Canonical rule

Two presentations of the same research result should differ in appearance, not in analytical meaning.

## Failure rule

A query must fail closed when the required identity or provenance chain cannot be established. It must not silently substitute a different population or unresolved identity.

## Initial scope

V1 supports the existing canonical fixture/team analytical materialisation and is intentionally small. It is designed to grow toward player, event, multi-league, combined-metric and modelling outputs without changing the result envelope.
