# Football Research Laboratory — Default Identity Schema

**Status:** Architectural contract — v1.0  
**Established:** 23 August 2026, 22:18 BST  
**Purpose:** Default identity schema for all future source, relationship and variable mapping work.

## 1. Core rule

The FRL must distinguish between:

1. a **canonical cross-source identity** that has been reconciled through an approved identity seam; and
2. a **source-native identity** that is known and stable inside one source family but has no approved downstream cross-source anchor.

A source-native identity must remain usable and queryable without being falsely promoted into another namespace.

Identity absence in one source family is **not** evidence that the underlying football entity does not exist.

## 2. Default identity graph

```text
RAW / SOURCE RECORD
       |
       v
SOURCE-NATIVE IDENTITY
       |
       +---- verified crosswalk ----> CANONICAL ENTITY
       |
       +---- longitudinal source bridge
       |         |
       |         +----> Player-Season / Team-Season / Fixture
       |
       +---- source-native bridge ----> SOURCE-NATIVE ENTITY
```

Every attachment must identify which route was used.

## 3. Player identity

The default player identity chain is:

```text
Player-Match source_player_id / pl_code
        |
        +--> verified FPL element/source-player registry
        |          |
        |          +--> Player-Season identity
        |          +--> Player Research identity
        |
        +--> longitudinal Player-Season bridge
        |
        +--> source-native Player-Match bridge
```

### Player identity rules

- Display name alone is never a canonical identity.
- A seasonal FPL `element` is season-local and must not be treated as a persistent player key.
- Player-Match `source_player_id` / `pl_code` may be longitudinal when source audits prove that semantics.
- Player-Season `playerId` is used according to the proven source semantics of that dataset.
- Research identifiers/names are enrichment or cross-source evidence; they are not a prerequisite for a source-native player entity.
- When several seasonal FPL records have the same verified player identity but different clubs, the player identity may still be unique. Team ambiguity is a separate relationship question.
- When no approved downstream anchor exists, create/use a `player_source_identity_bridge` record rather than inventing a canonical player identity.

## 4. Source-native player bridge

The source-native player bridge is the default fallback when a stable source identity exists but the source family has no approved cross-source identity mapping.

Minimum schema:

| Field | Meaning |
|---|---|
| `player_source_identity_key` | Stable FRL key, e.g. `player_match:<source_player_id>` |
| `source_family` | Owning source family |
| `source_player_id` | Source-native persistent identifier |
| `source_player_name` | Source-native display name/evidence |
| `seasons` | Seasons in which the bridge is observed |
| `observation_count` | Number of attached observations |
| `identity_status` | `SOURCE_NATIVE_VERIFIED` |
| `canonical_player_id` | Populated only after approved cross-source reconciliation |
| `player_season_id` | Populated only where an approved Player-Season anchor exists |
| `research_identity` | Populated only where an approved Research anchor exists |
| `evidence_basis` | Explicit explanation of the source-native bridge |

A source-native entity can therefore be fully functional for source-family research while remaining explicitly distinct from the canonical cross-source player namespace.

## 5. Team identity

Teams use a two-level identity model:

```text
season-local source team ID
        |
        v
identity/team_seasons.csv
        |
        v
persistent club identity
```

The `identity/team_seasons.csv` seam is the approved bridge between season-local team identities and persistent club identity.

Team identity is independent from player identity. A player may have multiple verified team candidates in one season; fixture-level team context resolves the specific club relationship where required.

## 6. Fixture identity

Fixture identity is canonical at:

```text
(season, fixture_id)
```

Source-specific match IDs are evidence and must be mapped onto the canonical fixture rather than creating competing fixture identities.

Fixture identity resolution must preserve correction/provenance information where a source record differs from the canonical fixture master.

## 7. Player–Fixture relationship

Canonical grain:

```text
(season, fixture_id, player_id)
```

A Player-Match source observation attaches to the player through the best verified identity route available:

1. canonical verified registry route;
2. longitudinal source-player -> Player-Season route;
3. source-native player bridge.

The route must be recorded explicitly.

## 8. Team–Fixture relationship

Canonical grain:

```text
(season, fixture_id, team_id)
```

Team membership in a fixture is resolved using canonical fixture context and the verified season-local team mapping.

## 9. Player–Team relationship

Player-Team membership is temporal and must not be inferred solely from name.

Where a player has multiple clubs in a season:

```text
player identity = one player
team relationship = season/fixture-specific relationship
```

The identity layer should not create duplicate players merely because a player changed clubs.

## 10. Identity route contract

Every attachment should expose, directly or through provenance, the route used:

- `REGISTRY_*` — canonical registry/crosswalk route
- `LONGITUDINAL_*` — longitudinal source identity bridge
- `SOURCE_NATIVE_*` — verified source-native identity bridge

A future mapping must not silently replace one route with another.

## 11. Fail-closed rule

When identity evidence is insufficient:

```text
NO EVIDENCE
   -> UNRESOLVED

CONFLICTING EVIDENCE
   -> REVIEW / AMBIGUOUS

VERIFIED SOURCE-NATIVE EVIDENCE
   -> SOURCE_NATIVE_VERIFIED

VERIFIED CROSS-SOURCE EVIDENCE
   -> VERIFIED
```

The FRL must never use fuzzy similarity as a substitute for an approved identity bridge.

## 12. Provenance rule

Every identity edge must be explainable as:

```text
source field / identifier
        |
        v
identity bridge / rule
        |
        v
attached entity
        |
        v
confidence / status / evidence basis
```

A new source or variable cannot become trusted merely because its values look familiar.

## 13. Variable mapping rule

When mapping a source variable, identity mapping is a prerequisite to research exposure, but not necessarily to source inventory.

For each variable, record at minimum:

- source family;
- source field;
- observation grain;
- identity contract;
- relationship contract;
- transformation / aggregation;
- availability semantics;
- provenance status;
- permitted fallback.

This allows the wider source-variable universe to be classified even when a variable is not yet safe for canonical research use.

## 14. Historical and temporal semantics

Identity is not the same as historical state.

The FRL must preserve:

- event-time;
- availability-time where relevant;
- ingestion/version information where required;
- season-local identity;
- longitudinal identity.

A player identity must not be used to leak future information into a historical state reconstruction.

## 15. Player-Match completion milestone

As of 23 August 2026, the Player-Match attachment layer contains:

- **145,571 / 145,571 observations attached**
- **145,571 VERIFIED attachment states**
- **0 REVIEW**
- **0 UNRESOLVED**

This includes a source-native bridge for player identities not represented by the approved Player-Season / Research namespaces.

The milestone was established through the reconciliation recorded in:

`docs/IDENTITY_MILESTONE_2026-08-23.md`

and the source-native bridge stored in:

`data/player_source_identity_bridge.csv`

## 16. Fresh-session rule

Any new ChatGPT session or contributor working on identity or source mapping should read this document before changing identity logic.

Do not restart the historical player identity reconciliation unless a regression or new source evidence requires it.

This document is the default FRL identity contract for future source-variable mapping and relationship work.
