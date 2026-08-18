# Football Research Laboratory — Relationship Integrity Contract

**Status:** Foundational relationship contract — v1.0
**Date:** 17 August 2026

This contract records the verified relationship semantics that must be preserved across ingestion, canonicalisation, analytical storage, research services and future migrations.

## 1. Fixture-to-team relationship

The canonical fixture master stores `home_team_id` and `away_team_id` as **season-local team identifiers**.

They must not be treated as persistent longitudinal club identities.

The authoritative relationship is:

```text
fixtures_master_corrected.csv
        |
        | season + home_team_id / away_team_id
        v
identity/team_seasons.csv
        |
        | season + local_team_id
        v
persistent_team_code / club_id
```

Therefore:

```text
fixture.home_team_id
        -> team_seasons.local_team_id
        -> verified persistent team identity
```

and likewise for the away team.

A direct join from fixture `home_team_id` / `away_team_id` to persistent `club_id` is prohibited unless an explicit source contract establishes that equivalence for the relevant dataset.

## 2. Fixture identity

The canonical fixture identity is:

```text
(season, fixture_id)
```

Source-specific match IDs such as `source_match_id` are attached evidence, not competing canonical identities.

Fixture statistics therefore join to the fixture master through:

```text
season + fixture_id
```

## 3. Player identity

The canonical player relationship is season-aware and fail-closed.

For the season-specific FPL player source used by Player Research:

```text
source file name
    -> season context
    -> (season, fpl_element)
    -> player_identity_registry.csv
    -> verified source_player_id
```

The raw season-specific player CSV does not itself need a physical `season` column. The existing Player Research loader derives `_season` from the season being loaded and adds that contextual field to the materialised records.

Unknown, ambiguous or conflicting identity mappings must remain unresolved rather than being guessed.

## 4. Player–fixture relationship

The canonical Player–Fixture grain is:

```text
(season, fixture_id, player_id)
```

When an upstream player-match source uses a different namespace, it must resolve through the existing verified player identity mechanism before enrichment is promoted.

## 5. Evidence-layer rule

Relationship validation is part of data validation, not merely presentation validation.

A dataset may be structurally valid while still being relationally invalid.

Therefore platform promotion must test:

- orphan fixture-stat records;
- orphan fixture/team relationships;
- duplicate canonical identity keys;
- unresolved or conflicting player identities;
- verified identity records without a corresponding source record;
- preserved canonical fixture keys.

## 6. Migration rule

Any new representation such as Parquet/DuckDB must preserve these relationship semantics exactly.

A format migration is not equivalent merely because it preserves row counts and columns.

The minimum relationship-equivalence requirement is:

```text
old representation
      |
      | canonical relationship checks
      v
new representation
```

with identical valid joins, identifiers and fail-closed behaviour.

## 7. Foundational principle

> **Never make a provider ID or season-local identifier into a longitudinal FRL identity merely because the values happen to look compatible.**

The verified identity registry and canonical relationship seams are the authority.
