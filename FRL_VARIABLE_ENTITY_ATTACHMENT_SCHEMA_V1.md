# FRL Variable → Entity Attachment Schema V1

**Status:** Frozen architecture target for variable/entity attachment work
**Date:** 23 August 2026

## Purpose

Define the stable schema and relationship semantics for attaching FRL variables and source observations to Player, Fixture and Team/Club entities without conflating source identity with canonical FRL identity.

## Governing principles

- Preserve source-native evidence and identifiers.
- Treat grain as part of meaning.
- Resolve source identities through explicit, verified bridges.
- Keep Player, Fixture and Team/Club attachment edges independent.
- Fail closed for unresolved or ambiguous identities.
- Preserve provenance and temporal availability.
- Do not mutate canonical data merely to make an attachment appear complete.

## Entity graph

```text
                         FRL PLAYER
                             │
                    verified identity bridges
                             │
              ┌──────────────┴──────────────┐
              │                             │
        PLAYER-SEASON                 PLAYER-FIXTURE
              │                             │
       source player IDs            source observations
              │                             │
              └──────────────┬──────────────┘
                             │
                      SOURCE EVIDENCE
                             │
                    ┌────────┴────────┐
                    │                 │
                 FIXTURE          TEAM / CLUB
```

## Core schemas

### 1. `variable`

```text
variable_id
field_name
source_family
resource
grain
field_type
semantic_status
relationship_kind
source_identity_required
provenance_requirement
```

A variable is a definition, not an observation and does not itself require canonical entity foreign keys.

### 2. `source_variable_observation`

```text
observation_id
variable_id
season
source_record_id
source_player_id
source_match_id
source_team_id
value
source_field
source_file
source_version
availability_time
ingestion_time
validation_status
provenance_id
```

This is the source-native evidence layer. It may exist without canonical FRL identity attachment.

### 3. `fixture`

```text
fixture_id
season
kickoff_datetime
home_team_season_id
away_team_season_id
status
```

Canonical fixture identity:

```text
(season, fixture_id)
```

### 4. `team_season`

```text
team_season_id
season
local_team_id
persistent_team_code
club_id
canonical_name
mapping_status
```

Season-local team identity and persistent club identity remain separate.

### 5. `player`

```text
player_id
canonical_name
status
```

Keep the canonical player entity deliberately small; source-specific identifiers belong in relationship tables.

### 6. `player_source_identity`

```text
source_family
source_player_id
season
player_id
identity_status
identity_contract
evidence_basis
provenance_id
```

A source player identity may be verified at source level without being reconciled to a canonical FRL player.

### 7. `player_fixture_observation`

```text
season
fixture_id
player_id
source_player_identity_id
participation_status
```

Canonical Player–Fixture grain:

```text
(season, fixture_id, player_id)
```

## Attachment model

Every source observation exposes independent attachment edges:

```text
observation
  ├── fixture_attachment
  ├── home_team_attachment
  ├── away_team_attachment
  └── player_attachment
```

Each edge carries:

```text
attachment_status
identity_contract
evidence_basis
provenance_id
```

Therefore a valid observation may have:

```text
fixture      = VERIFIED
home_team    = VERIFIED
away_team    = VERIFIED
source_player= VERIFIED
frl_player   = UNRESOLVED
```

An unresolved Player edge does not invalidate independently verified Fixture or Team edges.

## Grain-to-entity applicability

| Grain | Natural entity attachments |
| --- | --- |
| `player_match` | Player + Fixture + Team |
| `player_season` | Player + Team + Season |
| `team_match` | Team + Fixture |
| `squad` | Team + Season + Player |
| `sample_payload` | Source evidence until grain is established |

## Promotion states

```text
RAW
  ↓
VALIDATED
  ↓
RECONCILED
  ↓
CANONICAL
```

Promotion requires explicit evidence and must preserve source lineage.

## Frozen decision

This schema is the target architecture for the current variable/entity attachment work. Future audits should measure coverage against this schema rather than reopening the entity model. Unresolved coverage is now a bounded implementation/data-evidence problem, not a reason to redesign the schema.
