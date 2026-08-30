# Football Research Laboratory — 2026/27 Incremental Season Integration Plan

**Status:** Governing implementation plan — integration not yet started

**Established:** 30 August 2026

**Scope:** Living 2026/27 Premier League season from the known, preserved Premier-League-Stats ecosystem

Read this plan together with:

- `AGENTS.md`;
- `DATA_CONSTRUCTION.md`;
- `FRL_DATA_PLATFORM_ARCHITECTURE_V1.md`;
- `FRL_ANALYTICAL_DATA_LAYOUT_V1.md`;
- `FRL_DEFAULT_IDENTITY_SCHEMA_V1.md`;
- `FRL_IDENTITY_RELATIONSHIP_CONTRACT_V1.md`;
- `FRL_SOURCE_NORMALISATION_CONTRACT.md`;
- `FRL_SOURCE_ROUTING_CONTRACT.md`;
- `FRL_SOURCE_RIGHTS_REGISTER.md`;
- `RISK_STRATEGY_FRAMEWORK.md`;
- `NON_DESTRUCTION_ASSURANCE.md`.

This document governs the expansion. It does not itself establish that any 2026/27 source has been promoted, connected or validated.

## 1. Purpose and boundaries

The first 2026/27 objective is:

> **Integrate the authoritative evidence already preserved or released through the known Premier-League-Stats ecosystem as far as existing FRL contracts safely permit, measure the resulting capability honestly, and only then assess supplementary providers against explicit gaps.**

The initial integration must:

- extend the existing canonical, identity, source, temporal and research architecture rather than create a current-season shortcut;
- preserve source-native evidence before canonical promotion or derivation;
- use the governed FPL and Universal Research Access seams where they apply;
- retain missing, partial, ambiguous and unavailable states explicitly;
- remain repeatable as the living season receives additions and corrections.

The initial integration must not:

- call or scrape the live Premier League/PulseLive service;
- acquire a new external football dataset or provider;
- fabricate fixtures, scores, participation, statistics or relationships;
- infer cross-source equivalence from similar field names or values;
- weaken canonical identity, relationship, provenance, temporal or fail-closed rules;
- present FPL player-fixture evidence as historical Opta-derived `players_match_stats`.

## 2. Confirmed source position and release pinning

The known upstream distribution channel is the Premier-League-Stats workspace/repository associated with `imadeddine-belkat/Premier-League-Stats`. Its underlying FPL and Premier League/PulseLive-derived source families retain the rights status recorded in `FRL_SOURCE_RIGHTS_REGISTER.md`.

The expected 2026/27 release surface may include:

- fixture evidence;
- FPL player-fixture evidence;
- team, index or other supporting source evidence present in the pinned release;
- richer `pl_stats` source families only if those files actually exist in that pinned release.

These are expectations to inspect, not frozen coverage claims. Every integration run must determine the release state again and record:

```text
distribution repository / workspace
+ exact commit SHA or immutable release identity
+ source path
+ content hash for every consumed file
+ retrieval / inspection timestamp
+ schema and row count
+ provider / source-family attribution
+ acquisition and rights classification
```

The source release used by a run must be pinned before materialisation. A mutable branch tip, upload date or gameweek label is not sufficient provenance.

Upload date and gameweek must not establish fixture identity. A source fixture identifier must resolve through an explicit governed relationship to canonical `(season, fixture_id)`.

The presence or absence of 2026/27 `events_stats`, `players_match_stats`, `players_stats`, squad or other `pl_stats` evidence must be determined from the pinned release and reported. Absence from one release or connected route is not automatically absence from the wider preserved ecosystem.

## 3. Grain and missingness semantics

Where a FPL history row carries a source fixture relationship, its source-native grain is:

```text
FPL player × fixture evidence
```

This is not a season aggregate and is not merely a gameweek total. The source fixture relationship remains authoritative even in a double, postponed or rearranged gameweek.

The source may contain a row for a registered player who played zero minutes. Such rows are retained. Integration must distinguish:

| State | Meaning |
|---|---|
| `ZERO` | The source supplied an observed numeric zero for the field under its documented semantics. |
| `NON_PARTICIPATION` | A player-fixture source row exists and records no participation, normally through source-backed zero minutes. |
| `MISSING_OBSERVATION` | The relevant source row/population exists but the field is blank, null or otherwise not observed. |
| `SOURCE_FIELD_UNAVAILABLE` | The pinned source schema does not supply the requested field for the relevant release/period. |
| `UNRESOLVED_IDENTITY` | Source evidence exists but cannot be attached through a unique verified FRL relationship. |

Zero must not be used as a replacement for any of the other states. Non-participation does not prove that every source field should be interpreted as an observed zero; field-specific source semantics still govern.

## 4. Identity requirements

The existing FRL identity graph remains authoritative.

Preserve these namespaces separately:

- canonical fixture identity `(season, fixture_id)`;
- canonical/season-local team identity and persistent club identity;
- existing FRL canonical or source-native player identity;
- season-local FPL `element`;
- FPL `player_code`;
- FPL `team_code`;
- FPL `fixture_code`.

The intended relationship shape is:

```text
FPL fixture_code
        ↓ explicit verified fixture relationship
canonical (season, fixture_id)

(season, FPL team_code)
        ↓ explicit verified team-season relationship
FRL team / persistent club identity

(season, FPL element / player_code evidence)
        ↓ strongest existing verified identity route
existing FRL player identity or explicit source-native identity
```

Rules:

1. Source identifiers remain source evidence; numeric equality across namespaces is not a bridge.
2. FPL `element` is season-local and must always be interpreted with season context.
3. `player_code` may support an identity relationship only where exact evidence and existing contracts establish the route.
4. Fixture, team and player identity are separate relationships.
5. Missing or conflicting candidates fail closed as `UNRESOLVED` or `REVIEW_REQUIRED`/`AMBIGUOUS`.
6. Display-name or fuzzy matching must not create an authoritative identity edge.
7. New evidence must extend the existing FRL player identity graph, not replace the verified historical Player-Match layer or create a second canonical player system.
8. Every promoted edge must expose its identity route, evidence basis, source namespace and status.

## 5. Living-season and temporal semantics

2026/27 is a mutable, incomplete season. A current release is evidence of what that release contained, not an immutable statement of the eventual season record.

The governed release lifecycle is:

```text
source release
    ↓
immutable preservation / pinning
    ↓
comparison with the previously integrated release
    ↓
schema, identity and relationship validation
    ↓
affected-output rebuild
    ↓
validation
    ↓
governed publication
```

Every release must retain, where available:

- fixture/event time;
- source information-availability time;
- FRL retrieval/ingestion time;
- source release/commit identity;
- file content hashes;
- transformation/materialisation version;
- correction or supersession relationship to the prior release.

A later corrected release must not erase the fact that an earlier release contained different information.

Fixture completion semantics must keep these states distinct:

- scheduled/unplayed;
- completed with legitimate zero or non-zero scores;
- postponed/rescheduled;
- abandoned or another source-defined exceptional state, if evidenced;
- score/result missing or unresolved.

Missing scores are not zero scores. A fixture must not enter completed-match analysis until the governing completion contract is satisfied.

Current-season aggregates must expose their as-of boundary and incomplete population. They must not be described as full-season totals or rates.

## 6. Capability states

2026/27 capability reporting must not collapse several different questions into one `available` flag.

| State | Meaning |
|---|---|
| `SOURCE_PRESENT` | Relevant evidence exists in the pinned preserved source ecosystem. |
| `CONNECTED` | An established FRL adapter/resolver can retrieve the representation. |
| `IDENTITY_RESOLVED` | The observation attaches through unique verified fixture/team/player relationships required by its grain. |
| `DERIVABLE` | Governed inputs and an explicit valid transformation can construct the requested concept/grain. |
| `GOVERNED` | Meaning, route, aggregation, missingness, provenance and limitations are approved. |
| `COMPARABLE` | The representation can enter the declared period/population comparison under explicit rules. |
| `PRODUCT_READY` | The capability is suitable for its declared product use, including coverage and limitation presentation. |
| `REVIEW_REQUIRED` | Evidence exists but a semantic, identity, rights, temporal or comparability question remains unresolved. |
| `UNAVAILABLE` | The requested representation cannot be supplied from the pinned source set under the declared contract. |

These states are context-specific. A player-fixture value can be `GOVERNED` for source-specific research while remaining not `COMPARABLE` with a historical provider representation.

Low coverage through one connected route must not be reported as absence from the whole preserved ecosystem.

## 7. Source-selection rules

Source selection for 2026/27 follows:

```text
canonical football concept
+ requested grain
+ competition
+ season / as-of period
+ analytical purpose
+ required completeness / comparability
        ↓
governed source representation
```

There is no universal provider hierarchy.

Forbidden behaviour includes:

- first-non-null coalescing across source families;
- silently substituting FPL values for similarly named Opta-derived values;
- silently extending a later source definition backwards;
- treating source acquisition convenience as semantic or rights equivalence.

The integration must distinguish:

### Raw/source variable

A value retained directly from one source family at its native grain and meaning.

### Normalised canonical variable

A stable FRL concept populated only after source representations have been judged semantically compatible for the declared use.

### Derived analytical metric

An explicit, versioned FRL calculation over governed inputs, with coverage and provenance.

Changing grain creates a derivation. Player-fixture values may become team-fixture metrics only where a concept-specific aggregation contract establishes contributor completeness, zero/missing semantics and agreement/limitations against independent evidence where available.

## 8. Initial integration stages

The first implementation must proceed in this order:

1. **Pin and preserve the upstream release** — record repository, commit/release identity, paths, hashes, retrieval time, schemas, counts and rights classification.
2. **Validate the fixture source schema** — compare with the preceding season and establish scheduled/completed/postponed/correction semantics.
3. **Materialise the canonical 2026/27 fixture season** — extend the existing fixture universe non-destructively while retaining source fixture identity separately.
4. **Create fixture and team relationships** — verify source fixture/team codes against canonical fixture and team-season identity.
5. **Audit and establish FPL player identities** — resolve exact season-aware identities; classify ambiguity and absence rather than guessing.
6. **Preserve/materialise FPL player-fixture evidence** — retain the complete source row and release lineage, including zero-minute rows.
7. **Connect the evidence through the existing FPL/URA route** — no browser-side file access or new source-specific consumer path.
8. **Rebuild only affected downstream artifacts** — preserve in-progress/as-of semantics and do not rewrite historical seasons.
9. **Run vertical research/API/product canaries** — prove representative evidence flows through established consumers without weakening prior behaviour.
10. **Generate an explicit capability and gap register** — distinguish route, identity, semantic, coverage and genuine source gaps.

Each stage has a reviewable output. A later stage must not conceal an unresolved failure from an earlier stage.

## 9. Validation gates

At minimum, an integration increment must validate:

### Source and schema

- source manifest, immutable release identity and file hashes;
- expected schemas and schema differences from 2025/26;
- row counts, duplicate keys and uniqueness at the declared grain;
- deterministic regeneration from the same pinned inputs.

### Identity and relationships

- unique canonical `(season, fixture_id)`;
- source fixture → canonical fixture relationships;
- source team → team-season/persistent team relationships;
- FPL element/player-code identity status;
- orphan, unresolved and ambiguous counts;
- fail-closed behaviour.

### Completion and missingness

- legitimate `1-0`, `0-1` and `0-0` results remain completed where present;
- missing-score fixtures remain uncompleted/unresolved;
- scheduled and completed fixtures remain distinct;
- zero-minute player rows remain non-participation evidence;
- zero, missing, unavailable and unresolved states remain distinct.

### Temporal and provenance

- release, retrieval and as-of metadata survive materialisation;
- release corrections/deltas remain inspectable;
- historical-state construction remains leakage-safe;
- current-season outputs expose an as-of boundary.

### Consumers and regression

- targeted fixture, identity, FPL, URA, query and API tests;
- representative URA canaries;
- affected Python regression/data-health gates;
- frontend typecheck/build only when frontend behaviour is exercised;
- documentation synchronisation when the integration milestone changes standing repository state;
- `git diff --check`.

No historical fixed test count substitutes for actual current validation output.

## 10. Capability/gap register and supplementary-source decision

The first integrated 2026/27 release must produce a reproducible gap register covering at least:

- fixture/result state;
- player participation/minutes;
- goals and assists;
- xG, xA and related expected metrics;
- shooting;
- passing and chance creation;
- possession;
- defensive actions and duels;
- goalkeeper actions;
- discipline;
- team-match statistics;
- events, lineups and formations;
- odds/markets.

The register must identify whether each gap is caused by:

- source absence;
- disconnected preserved evidence;
- identity failure;
- unresolved semantics;
- invalid or unapproved derivation;
- insufficient coverage;
- cross-period/provider incomparability;
- rights/operational restriction.

Only after this register exists should FRL evaluate Sportmonks or another supplementary provider. That evaluation must be driven by demonstrated requirements for:

- missing variables and grains;
- season/fixture coverage;
- source and identity reliability;
- semantic overlap/comparison;
- preservation and reproducibility;
- acquisition, display, redistribution and commercial rights.

A supplementary source must enter through its own adapter and identity relationships. It must not be silently coalesced into FPL or historical Opta-derived source identities.

## 11. Non-goals

This expansion plan does not authorise:

- a frontend or navigation redesign;
- another historical fixture-universe audit;
- live PulseLive acquisition;
- new external source acquisition during the initial integration;
- silent cross-provider equivalence or fallback;
- a broad analytical-kernel redesign or generic metric DSL;
- unrelated legacy Streamlit/test cleanup;
- premature Poisson, Elo, player-strength or other modelling changes;
- destructive canonical-data replacement;
- a new canonical fixture, team or player identity system.

## 12. Completion and change-control rule

The initial 2026/27 integration is complete only when:

1. the consumed release is reproducibly pinned and preserved;
2. canonical fixture and required identity relationships pass their gates;
3. source-native FPL player-fixture evidence is preserved and connected where defensible;
4. missingness, completion, temporal and provenance semantics are explicit;
5. affected consumers and regression gates pass or any unrelated failures are reported precisely;
6. the capability/gap register is generated from the integrated state;
7. standing repository memory is reconciled to the implementation that actually exists.

Any material change to source family, identity namespace, canonical grain, temporal policy, capability states or supplementary-source policy requires an explicit update to this plan or the relevant stronger contract.

> **Integrate preserved evidence first, keep the living season time-safe, and let governed gaps—not assumptions—decide what source FRL needs next.**
