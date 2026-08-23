# FRL Canonical Variable Mapping Audit — 23 August 2026

## Status

Architecture/data-contract checkpoint.

## Canonical universe

- Authoritative canonical variable universe: **1,414** fields.
- All **1,414 / 1,414** fields assigned to an explicit canonical relationship or context layer.
- Grain-aware duplicate audit: **0 true duplicate mapping keys**.
- Repeated field names: **63**, all explained by distinct resource/grain/relationship combinations rather than duplicate mapping keys.

## Canonical relationship coverage

| Relationship | Variables |
|---|---:|
| Fixture | 469 |
| Team–Fixture | 207 |
| Player–Season | 170 |
| Player–Fixture | 128 |
| Player | 113 |
| Event | 40 |
| Competition context | 39 |
| Team | 23 |
| Player context | 16 |
| Player–Fixture context | 15 |
| Source configuration | 188 |
| Provenance | 6 |
| **Total** | **1,414** |

## Evidence-layer accounting

- Canonical evidence: **1,165** variables.
- Canonical context: **55** variables.
- Source metadata/configuration: **188** variables.
- Provenance: **6** variables.

## Grain-aware duplicate rule

A field name alone is not a canonical uniqueness key.

A canonical mapping is distinguished by its source/resource, source grain and canonical relationship. Therefore fields such as `expectedGoals`, `goals`, `touches`, `totalShots` and `accuratePass` may legitimately occur at Player–Fixture, Player–Season and/or Team–Fixture grain.

The audit confirmed that the full mapping key is unique across all **1,414** variables.

## Manager seam

The 1,414-variable universe contains **10 manager-related source fields** within the lineup evidence:

- home manager container;
- home manager source ID;
- home manager first name;
- home manager last name;
- home manager type;
- away manager container;
- away manager source ID;
- away manager first name;
- away manager last name;
- away manager type.

These fields are mapped conceptually to:

```text
MANAGER
  ↓
MANAGER–FIXTURE
  ↓
TEAM–FIXTURE
  ↓
FIXTURE
```

Manager data is **not** treated as a new set of ten canonical variables. These are source facets already present in the 1,414 universe and have instead been assigned an explicit relationship seam for future manager identity and tenure modelling.

Manager identity must use the verified source manager ID. Manager tenure remains a separate temporal relationship to be constructed from fixture-time evidence; names alone must not establish longitudinal identity.

## Architectural consequence

The canonical variable universe is now treated as a complete evidence mapping rather than a GUI field list.

The downstream order remains:

```text
source evidence
→ mapping
→ identity / temporal validation
→ canonical relationship
→ shared analytical services
→ research exposure
→ GUI
```

No additional variable expansion is implied by the manager relationship seam.
