# Football Research Laboratory — Identity & Relationship Contract V1

**Status:** Architectural contract  
**Created:** 23 August 2026  
**Milestone context:** Player-Match identity reconciliation completed at 145,571 / 145,571 attached observations

This document is the permanent identity/relationship reference for future FRL sessions. It exists so that a new conversation can reconstruct the identity graph without relying on chat history.

## 1. Core rule

FRL is a provenance-aware football research graph. Source identifiers are evidence, not automatically interchangeable canonical identifiers.

Every cross-source relationship must have an explicit identity bridge. The system must never infer that two source identifiers represent the same entity merely because their numbers look similar or because a display name appears similar.

The governing pattern is:

```text
RAW / SOURCE EVIDENCE
        ↓
SOURCE-SPECIFIC IDENTITY
        ↓
VERIFIED IDENTITY BRIDGE
        ↓
FRL CANONICAL ENTITY / RELATIONSHIP
        ↓
RESEARCH / ANALYTICAL STATE
```

A source can contain an entity that another source does not. Absence from a downstream source is not evidence that the entity does not exist.

---

## 2. Canonical entity and relationship grains

### Fixture

Canonical fixture identity:

```text
(season, fixture_id)
```

A source-specific match ID such as a provider `matchId` is a source identity. It becomes useful to FRL only after being mapped to the canonical fixture.

Canonical relationship:

```text
(season, fixture_id, team_id)
```

for Team–Fixture participation, and:

```text
(season, fixture_id, player_id)
```

for Player–Fixture participation.

### Team

FRL distinguishes a **season-local team identity** from a **persistent club identity**.

The trusted bridge is represented in `identity/team_seasons.csv` and follows:

```text
season + local source team ID
        ↓
verified team-season record
        ↓
persistent club identity
```

The season-local ID must not be treated as the persistent club ID.

The team-season record carries verified source/provenance context. Team names are descriptive evidence, not the primary join key.

### Player

FRL distinguishes several player identity namespaces:

```text
FPL seasonal element
Player-Match source_player_id / pl_code
Player-Season playerId
Player Research seasonal player identifier
FRL canonical player identity
FRL source-native player identity
```

These are not interchangeable.

Display name is never sufficient as canonical identity.

---

## 3. Player identity namespaces

### 3.1 FPL `element`

FPL `element` is season-local. The same numeric value can only be interpreted inside its relevant season and source dataset.

Therefore:

```text
(season, fpl_element)
```

is the relevant FPL identity key.

Never join a bare FPL element across seasons and assume it represents the same player.

### 3.2 Player-Match `source_player_id` / `pl_code`

The Player-Match source exposes a player identifier that has been demonstrated to behave longitudinally. Stable `playerId` / `pl_code` values can persist across multiple Premier League seasons.

The verified longitudinal bridge is therefore:

```text
PM source_player_id / pl_code
        ↓
all Player-Season records carrying that same source-native player identifier
        ↓
longitudinal player thread
```

This is the preferred bridge where the PM source exposes the stable identifier.

### 3.3 Player-Season `playerId`

Player-Season records are season-scoped source observations, but the source `playerId` is the identity key exposed by the Player-Season source. Where the same value is present across seasons, it can be used as the source-native longitudinal thread.

Do not confuse `playerId` with an FPL seasonal `element` merely because both are numeric.

### 3.4 Player Research identity

Player Research has its own historical player namespace and canonical-name logic. It is a research/evidence namespace, not the universal identity key for the FRL.

Research evidence can strengthen or enrich a player attachment, but the absence of a Research row must not invalidate a verified source-native player identity.

---

## 4. Player identity bridge hierarchy

Use the strongest verified bridge available, in this order:

### Route A — canonical cross-source identity

```text
PM source identity
        ↓
verified FPL / source-player registry
        ↓
FRL player identity
```

Use when the canonical registry has exactly one verified source-player candidate.

### Route B — longitudinal Player-Season bridge

```text
PM source_player_id / pl_code
        ↓
unique longitudinal Player-Season thread
        ↓
FRL player attachment
```

Use when the PM source identity is stable and the Player-Season bridge is unique.

This route was used extensively in the 23 August 2026 reconciliation.

### Route C — registry player identity with multiple Research identities

A player can have one verified FRL/FPL identity while Research contains multiple historical records or candidate Research identities.

The player attachment remains verified when the player identity itself is unique. Research fan-out is a downstream research/provenance issue and must not turn a verified player into an unresolved player.

### Route D — source-native Player-Match identity

If a PM `source_player_id` is real and stable within the PM source but there is no approved Player-Season or Player Research anchor, create a source-native player bridge rather than inventing a cross-source canonical identity.

Current implementation:

```text
data/player_source_identity_bridge.csv
```

At the 23 August 2026 milestone this contained **26 source-native player identities covering 225 PM observations**.

The bridge uses an explicit key such as:

```text
player_match:<source_player_id>
```

and is labelled `SOURCE_NATIVE_VERIFIED`.

---

## 5. Player–Fixture relationship

Canonical grain:

```text
(season, fixture_id, player_id)
```

The source row may contain:

- source_player_id / pl_code;
- fixture/match source ID;
- source team ID;
- participation/performance metrics.

The correct resolution order is:

```text
source fixture ID
        ↓
canonical fixture

source player ID
        ↓
verified player identity

source team ID
        ↓
verified team-season identity
```

A player appearing in a PM observation does not automatically create a new canonical player. The observation inherits the player identity established by the appropriate bridge.

---

## 6. Team–Fixture relationship

Canonical grain:

```text
(season, fixture_id, team_id)
```

The canonical fixture determines the two participating teams.

Source team identity must be resolved through the verified team-season mapping before it is used to identify a persistent club.

For historical club identity:

```text
fixture season + source team ID
        ↓
identity/team_seasons.csv
        ↓
persistent club
```

Team names may be used for diagnostics or evidence comparison, but a verified numeric/source mapping is preferred.

---

## 7. Fixture-source identity relationship

The canonical fixture master remains authoritative for fixture identity.

Source-specific match IDs are mapped into it through explicit fixture bridges.

Preferred pattern:

```text
source matchId
        ↓
verified source-match / fixture mapping
        ↓
(season, fixture_id)
```

Never use a source match ID as though it were the canonical FRL fixture ID without establishing the mapping.

Known historical fixture corrections must retain their provenance rather than silently changing the canonical source.

---

## 8. Team identity in player observations

A player can appear for multiple clubs in one season. This is legitimate rather than contradictory.

Example pattern:

```text
same player
    ├── Team A in first part of season
    └── Team B in later part of season
```

When a registry contains two verified candidates for the same source player in the same season and both candidates share the same player identity but have different team codes, the **player identity is not ambiguous**. The team relationship is the thing that varies.

The correct resolution is:

```text
player source ID
        ↓
unique player identity
        +
fixture/player observation team context
        ↓
correct seasonal team candidate
```

The 23 August 2026 reconciliation demonstrated this pattern for players such as Jan Bednarek, Neal Maupay, Alex Iwobi, Armando Broja, Joachim Andersen, Trevoh Chalobah, Reiss Nelson, Axel Disasi, Aaron Ramsdale and Eddie Nketiah.

---

## 9. Source-native identity versus canonical identity

This distinction is mandatory.

### Canonical verified

A player identity has a verified bridge into the FRL cross-source identity graph.

### Source-native verified

The source itself provides a stable, internally coherent player identity, but FRL has not established a cross-source anchor.

### Review

Evidence exists but the system cannot yet establish a safe unique identity under the relevant contract.

### Unresolved

No reliable player identity evidence exists.

The system must never silently turn `SOURCE_NATIVE_VERIFIED` into a cross-source canonical identity.

Conversely, it must not discard a source-native player merely because another source family has no corresponding record.

---

## 10. Identity resolution rules

1. **Do not join on a bare numeric ID across source families.**
2. **Always include season when interpreting a season-local namespace.**
3. **Prefer explicit verified source identity bridges over name matching.**
4. **Use names as supporting evidence, not as the sole canonical key.**
5. **Use verified team context to disambiguate legitimate multi-club seasons.**
6. **A missing downstream source record does not prove the player is absent.**
7. **Never create a cross-source identity merely to make an attachment complete.**
8. **Every promoted identity must retain its evidence basis and route.**
9. **Player identity and team identity are separate relationships.** A player can have multiple team relationships in one season.
10. **Fixture identity is separate from team and player identity.** A fixture is not recreated because a provider represents it differently.
11. **Source-native bridges must be additive and explicit.** They must not overwrite the canonical registry contract.
12. **Temporal semantics matter.** A relationship must be valid for the relevant season/event time rather than being inferred from a later state.

---

## 11. Identity graph

The conceptual graph is:

```text
                    ┌────────────────────┐
                    │ FRL PLAYER ENTITY  │
                    └─────────┬──────────┘
                              │
             ┌────────────────┼─────────────────┐
             │                │                 │
       FPL seasonal      Player-Match      Player Research
        identity          source ID            identity
             │                │                 │
             └─────── verified bridges ─────────┘
                              │
                    player–fixture relation
                              │
                        canonical fixture
                              │
                     team–fixture relation
                              │
                     FRL TEAM / CLUB ENTITY
```

And the source-native extension is:

```text
Player-Match source_player_id
            ↓
player_match:<source_player_id>
            ↓
SOURCE-NATIVE PLAYER ENTITY
```

This extension is still a real FRL player entity for observation attachment, but it carries an explicit statement that cross-source identity has not yet been established.

---

## 12. Current reconciliation milestone

On **23 August 2026 at 21:46 BST**, the Player-Match reconciliation reached:

```text
Total PM observations: 145,571
Verified attachments:  145,571
Review:                0
Unresolved:            0
```

The milestone commit was:

```text
3fee450
milestone: complete player-match identity attachment reconciliation
```

The reconciliation proved that the correct architecture is not "every source must contain the same player namespace". Instead, FRL maintains explicit bridges between heterogeneous source identity systems.

---

## 13. Fresh-session instructions

When a new conversation starts and identity questions arise:

1. Read this document before modifying identity logic.
2. Read `PROJECT_ORIENTATION.md` and `CURRENT_WORK.md`.
3. Inspect `identity/team_seasons.csv` before inventing team mappings.
4. Inspect the canonical player identity registry before inventing player mappings.
5. Treat PM `source_player_id` / `pl_code` as a longitudinal source-native identity where continuity has been verified.
6. Check `data/player_source_identity_bridge.csv` for source-native PM identities.
7. Never rerun a full historical identity reconciliation merely to rediscover the existing bridge.
8. Preserve provenance and route information when adding a new bridge.
9. If two sources disagree, isolate the disagreement and determine which relationship is actually varying: player identity, team identity, fixture identity, or source coverage.
10. Treat absence from Player Research or Player-Season as a coverage fact unless evidence proves a broken bridge.

This document is the permanent identity/relationship reference. Update it whenever a new canonical identity namespace, bridge type, relationship grain, or materialisation rule is established.
