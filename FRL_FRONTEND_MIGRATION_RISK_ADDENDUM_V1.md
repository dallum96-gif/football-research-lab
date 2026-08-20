# FRL Frontend Migration — Risk Strategy Addendum V1

## 1. Purpose

This addendum applies the Risk Strategy Framework to the React/Next.js migration.

## 2. GUI remains the least authoritative layer

The frontend may render, filter, compare and visualise trusted results, but it must not define:

- source precedence;
- canonical identity mappings;
- metric definitions;
- historical-state definitions;
- availability-time rules;
- leakage rules;
- fallback semantics;
- model methodology.

Those semantics remain in the canonical, analytical, research and modelling layers.

## 3. Research Result integrity

Every substantive analytical view should be driven by a trusted Research Result or equivalent query result object.

The result definition should preserve population, filters, temporal scope, provenance, uncertainty and limitations. A chart, table or comparison is not independently authoritative merely because it renders correctly.

## 4. Identity integrity

Frontend/API migrations must preserve canonical identity semantics exactly:

```text
Fixture        = (season, fixture_id)
Player–Fixture = (season, fixture_id, canonical player identity)
Team identity  = season-local source ID -> verified persistent club identity
Player identity = season-aware source ID -> verified canonical player identity
```

Provider IDs, season-local IDs and display names must never be promoted to longitudinal FRL identity by frontend convenience.

## 5. Historical and temporal risk

Client-side filtering, caching and visualisation must not replace historical/as-of semantics with present-day values.

When a historical result is requested, the frontend should carry the explicit temporal context returned by the trusted research layer rather than reconstructing it independently.

## 6. Analytical visualisation risk

Interactivity must be visible and deliberate. A visual control that changes the research population must also update the represented result definition.

Charts and tables showing the same analysis should share the same underlying result rather than independently recomputing statistics.

## 7. Model presentation risk

Frontend presentation must distinguish:

```text
model output
!=
model validity
```

Evaluation, calibration, robustness, baseline comparison and unseen-data evidence remain authoritative. Visual polish must not imply predictive quality.

## 8. Migration release gate

For presentation-only changes, the existing 26/26 regression baseline and project-health gate remain required. Identity, relationship, temporal, provenance and query-equivalence checks are also required whenever the frontend-facing contract changes.
