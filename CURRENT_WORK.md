# Current Work — Football Research Laboratory

**Last updated:** 23 August 2026

## Active branch

`feat/source-family-adapters-2026-08-21`

This is the active source/data-platform development line. `main` remains the stable integration line.

## Current platform checkpoint

The FRL data-platform work remains deliberately additive and local-first.

Validated during the current source/relationship phase:

- source-family adapters are covered by targeted tests;
- relationship contracts and enforcement are green;
- fixture relationship enforcement is green;
- player identity/relationship enforcement is fail-closed;
- all-season relationship matrix is using the shared contract layer;
- canonical player identity reconciliation is fail-closed;
- source-field universe audit covers 10 seasons and 4 source families;
- semantic review queue and conservative priority ranking are in place;
- the broad variable universe and routed-variable registry are established;
- fixture, home-team and away-team edges are independently verified across the full 145,571 player-match observation population;
- source player identity is independently verified across the full 145,571 player-match observation population;
- the remaining broad Player-Match gap is specifically the canonical FRL-player edge, not a failure of fixture/team/source-player evidence.

The known 2019–20 Manchester City v Arsenal fixture anomaly remains a known source/data-state warning and must not be “fixed” by inventing data.

## Frozen variable/entity attachment architecture

`FRL_VARIABLE_ENTITY_ATTACHMENT_SCHEMA_V1.md` is now the frozen architecture target for variable/entity attachment work.

The model is:

```text
source observation
   ├── fixture edge
   ├── home-team edge
   ├── away-team edge
   └── player edge
```

Each edge is independent and carries its own attachment status, identity contract/evidence basis and provenance reference.

Core entities:

- `variable`
- `source_variable_observation`
- `fixture`
- `team_season`
- `player`
- `player_source_identity`
- `player_fixture_observation`

Natural grain-to-entity applicability:

- `player_match` → Player + Fixture + Team
- `player_season` → Player + Team + Season
- `team_match` → Team + Fixture
- `squad` → Team + Season + Player
- `sample_payload` → source evidence until grain is established

Important invariant:

> A verified source-player identity or FPL seasonal key is not itself a canonical FRL `player_id`.

The new V1 materialisation seam therefore preserves `source_player_id` and a separate `source_player_identity_status`, while leaving `player_entity_id` empty unless a canonical FRL-player relationship is actually verified.

## New V1 implementation seam

Added:

- `FRL_VARIABLE_ENTITY_ATTACHMENT_SCHEMA_V1.md`
- `entity_attachment_resolver.py`
- `materialize_variable_entity_attachment_schema_v1.py`
- `tests/test_entity_attachment_resolver.py`
- `tests/test_variable_entity_attachment_schema_v1.py`

The new materialiser is intentionally additive. It wraps the existing routed observation materialiser rather than replacing it.

Existing observation production and identity registries remain authoritative. The new seam normalises legacy status strings into the frozen V1 vocabulary and does not infer or promote identities.

## Discovery boundary

Discovery of the entity schema is complete for this phase. Future work should measure coverage against the frozen V1 architecture rather than reopening the entity model.

The remaining work is now implementation/coverage work:

1. validate the new V1 tests and materialiser locally;
2. run the existing 26/26 research gate and project-health gate;
3. reconcile the V1 output against the trusted existing observation counts;
4. expand source-variable observations and provenance without creating variable×observation Cartesian products;
5. close additional verified Player identity coverage only where existing identity evidence supports it.

Standing rule:

> **Do not reopen the schema because an identity edge remains unresolved. Preserve the edge as unresolved and continue building the rest of the verified graph.**

## Existing durable architecture decisions

Read:

- `FRL_SOURCE_ARCHIVE_AND_DATABASE_DECISION_V1.md`
- `FRL_NEXT_SESSIONS_PLAN_V1.md`

Key decisions:

1. Preserve an immutable local copy of exactly what FRL receives from the approved upstream source.
2. CSVs remain useful portable source artefacts and recovery evidence; they are not a competing canonical truth.
3. The application should not call the external API on each refresh. It should query a local/future shared data store.
4. Storage technology is replaceable; source evidence, relationships, provenance and research semantics are not.
5. The source-family adapters, relationship contracts and identity pathways already established must remain intact through any storage migration.
6. FRL is both a navigable football database and a research laboratory. The database UI and research interface should traverse the same verified relationship graph.
7. FRL should preserve a very broad source-variable universe and manage complexity through taxonomy, search, filters, grouping and presentation rather than unnecessary data exclusion.

## Source-field review checkpoint

The source-field review has moved from simple discovery into a two-track process:

### Semantic evidence track

- all 325 currently uncatalogued fields have been reviewed for observed coverage;
- source-value evidence confirms all 325 are present in the approved local source archive;
- 75 were identified by conservative name/family triage as likely direct metrics;
- the remainder remain in semantic review because names alone do not establish exact provider definitions;
- no field is promoted merely because it appears to be obvious from its name.

### Navigation taxonomy track

`source_field_taxonomy.py` provides a presentation-oriented first taxonomy inspired by the intended FRL product direction:

- Identity & Context
- Playing Time
- Shooting & Finishing
- Chance Creation
- Passing & Distribution
- Crossing & Set Pieces
- Dribbling & Carrying
- Possession & Ball Security
- Duels & Aerials
- Defending
- Goalkeeping
- Discipline
- Team Attack
- Team Defence
- Tactical & Match Context
- Physical & Tracking
- Unclassified Review

The taxonomy is deliberately independent of semantic promotion. A field can be navigable/categorised without being considered semantically approved, canonical, model-eligible or UI-visible.

## Multi-session roadmap

1. **Source-field semantic review** — establish field meanings, coverage, units, missingness and stability; promote only defensible fields.
2. **Relationship/provenance consolidation** — make the full fixture/team/player/player-season/player-match/source-field graph explicit and fail-closed.
3. **Raw-source archive specification** — formalise the immutable local source-copy and provenance contract.
4. **Database / analytical-store design** — design around the proven relationship graph rather than current queries.
5. **Local data-store implementation** — build a reversible local store and prove it can be rebuilt from the source archive.
6. **Database equivalence** — move research/query workloads only after results match the trusted current paths.
7. **Navigable football database UI** — seasons, teams, players, player-seasons, fixtures, match observations and provenance; expose the broad variable universe through taxonomy and advanced filtering rather than a flat wall of fields.
8. **Research interface + visualisation** — structured queries first, natural language later; one trusted result object should drive tables/charts/comparisons.
9. **Modelling/evaluation** — only after the evidence/data platform is stable.

## Current analytical representation direction

The existing architectural direction remains Parquet + DuckDB as the first local analytical representation, subject to equivalence testing. This does not replace or remove the permanent raw-source archive requirement.

Existing CSV-backed query paths remain active until a replacement has passed equivalence and non-destruction gates.
