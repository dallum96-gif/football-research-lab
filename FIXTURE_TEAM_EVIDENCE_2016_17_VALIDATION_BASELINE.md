# Fixture Team Evidence — 2016/17 Validation Baseline

## Status

Validated on development branch `feature/complete-player-match-evidence-2026-08-19`.

## Reference population

- Canonical fixtures: 380
- Fixture-team evidence rows: 760
- Expected grain: `(season, fixture_id, venue)`
- Resolved fixture states: 380/380
- Unresolved/error states: 0

## Source-schema preservation

The approved upstream `events_stats` source was audited across 20 season files.

- Upstream source-native fields: 194
- FRL preserved source-native fields: 194
- Missing source fields in evidence: 0
- Unexpected source fields in evidence: 0

All upstream event/team fields are retained under `source_*` in the complete fixture-team evidence layer.

## Compatibility

The existing curated `data/fixture_match_stats.csv` remains unchanged for existing consumers. The complete evidence layer is additive and is intended to provide the full source-native backend foundation for future research and GUI work.

## Architectural rule

Do not infer, zero-fill, or discard unavailable source fields. Preserve the upstream value and its missingness semantics. Derived/curated team metrics remain replaceable analytical products built above this evidence layer.

## Next validation target

Use a known 2016/17 fixture, including the previously validated Arsenal–Liverpool case, to confirm the fixture-team evidence exposes the expected home/away rows and source-native statistics before wider-season promotion.
