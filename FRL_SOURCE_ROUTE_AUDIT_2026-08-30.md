# Football Research Laboratory — Preserved Source Route Audit

**Status:** Current source-routing evidence review  
**Date:** 30 August 2026  
**Scope:** Existing FRL repository + already-preserved local Premier-League-Stats / PulseLive ecosystem. No new live API acquisition.

## 1. Executive conclusion

FRL does **not** appear to have a broad source-routing failure.

The existing direct team-match route is generally sound for the established core match statistics. The material issue exposed by the xG investigation is narrower and more important architecturally:

> **FRL can preserve several legitimate source representations of the same football concept, at different grains and versions, while the currently connected query route may expose only one of them.**

The missing layer is therefore not a universal replacement source. It is a **governed source-routing layer** that decides which preserved representation is suitable for a requested concept, grain, period and analytical purpose without silently coalescing non-equivalent evidence.

The current Variable Capability Inventory should be read as an inventory over governed registries and currently connected research/model seams. It is not proof that the connected route is the strongest representation anywhere in the preserved ecosystem.

## 2. Governing principles

This audit follows the existing contracts:

- preserve source-native evidence;
- normalise meaning, not merely field names;
- treat grain as part of meaning;
- preserve source/version identity;
- fail closed when equivalence is unproven;
- search the whole preserved ecosystem before declaring evidence absent;
- never turn a later/richer representation into silent historical truth;
- avoid new live acquisition where existing preserved evidence is sufficient.

## 3. Important preserved source families

| Source family | Primary grain | Historical role | Current judgement |
|---|---|---|---|
| `fixtures_master_corrected.csv` | fixture | canonical fixture/result spine | Canonical route for fixture identity, participants, kickoff and results |
| `identity/*` | identity/relationship | season-local and persistent identities, corrections, bridges | Governed relationship layer; do not bypass |
| `pl_stats/*/events_stats/*` | team-match | broad historical team performance statistics | Strong default direct team-match representation for established core fields |
| `data/fixture_match_stats.csv` | team-match | packaged FRL copy of selected direct match statistics | Good operational route where coverage/semantics are understood |
| `pl_stats/*/players_match_stats/*` | player-match | player participation and performance by fixture | Strong player-match evidence; can support explicit team-match derivations for valid additive concepts |
| `pl_stats/*/players_stats/*` | player-season | source-supplied player season totals | Useful at player-season grain; not a safe substitute for missing fixture-level evidence |
| historical FPL merged data | player-gameweek / FPL observation | FPL-specific historical state and performance | Preserve as a distinct FPL source family; do not silently equate with PL/PulseLive representations |
| preserved PulseLive fixture snapshots | fixture/event/team-match/lineup | match-centre evidence, events, lineups, formations, managers, stats, commentary, snapshot provenance | Valuable versioned source-native evidence; not a blanket replacement for `events_stats` |
| `features/historical_match_state_*` | pre-match historical state | versioned derived as-of features | Keep separate as derived temporal evidence |

## 4. Direct team-match route assessment

Value-level comparison performed during the 30 August review found that the preserved PulseLive snapshot team-statistics surface does **not** broadly supersede `events_stats`.

Across the major shared team-stat fields inspected over the canonical team-side population, the values were effectively equivalent where both representations were populated.

One material version exception was identified:

- `2023-24/168` contains expected-goals / expected-assists / expected-goals-on-target values in the later preserved PulseLive snapshot that are absent from the older `events_stats` representation.

This supports the following model:

```text
same broad provider/source family
        ↓
multiple preserved representations / snapshots / versions
        ↓
explicit version-aware reconciliation
```

It does **not** support a rule such as “raw PulseLive snapshots always beat `events_stats`”.

## 5. Expected-goals finding

### Direct team-match `events_stats.expectedGoals`

Observed fixture coverage in the current packaged/direct route:

| Season | Fixtures with both-team xG | Total fixtures |
|---|---:|---:|
| 2016-17 | 0 | 380 |
| 2017-18 | 0 | 380 |
| 2018-19 | 1 | 380 |
| 2019-20 | 3 | 380 |
| 2020-21 | 5 | 380 |
| 2021-22 | 3 | 380 |
| 2022-23 | 2 | 380 |
| 2023-24 | 2 | 380 |
| 2024-25 | 170 | 380 |
| 2025-26 | 380 | 380 |

Total direct packaged coverage: **566 / 3,800 fixtures**.

### Player-match `expectedGoals`

The already-preserved player-match source provides a much stronger recent route:

| Season | Fixtures with usable player-match xG | Total fixtures |
|---|---:|---:|
| 2022-23 | 380 | 380 |
| 2023-24 | 379 | 380 |
| 2024-25 | 380 | 380 |
| 2025-26 | 380 | 380 |

The sole identified recent exception is `2023-24/45` (Manchester United 1–3 Brighton), where recorded shooters lack player-match xG. That observation should remain unavailable rather than being fabricated.

### Equivalence caveat

Summed player-match xG is close to, but **not numerically identical to**, separately supplied team-match xG on overlapping observations.

Observed overlap diagnostics from the review:

- 2024-25 mean absolute difference: approximately `0.0102` xG;
- 2025-26 mean absolute difference: approximately `0.0104` xG;
- larger individual differences also exist.

Therefore FRL must not silently coalesce these values.

The preferred recent derived representation should be explicitly versioned, for example:

`team_match_player_xg_sum_v1`

with its own provenance and aggregation contract.

## 6. Safe player-match → team-match derivation rule

For any candidate derived team-match statistic:

1. resolve the canonical fixture through the governed source bridge;
2. resolve player rows to the correct fixture team;
3. establish whether the concept is validly aggregatable;
4. distinguish structural zero from missing evidence;
5. expose contributing/observed player coverage;
6. fail closed when a required contributing observation is missing;
7. preserve the player-match source identity and derivation version;
8. compare with any independent direct team-match representation before claiming equivalence.

For player-match-derived xG specifically:

- numeric player xG values are summed by canonical fixture team;
- blank xG may contribute structural zero only where the row explicitly establishes no shooting contribution (for example `totalShots == 0` under the governed source semantics);
- a player with shots but missing xG makes the team-fixture xG observation unavailable;
- xG overperformance must use goals and xG from the exact same fixture population.

## 7. Source-route classifications

FRL source-route decisions should use the following statuses:

### `KEEP_CURRENT_ROUTE`
The connected route is already the strongest suitable preserved representation for the requested concept/grain/period.

### `BETTER_EXISTING_ROUTE`
A stronger direct preserved representation already exists and should replace or supplement the current connected route.

### `DERIVED_ROUTE_PREFERRED`
The strongest defensible representation should be produced from another governed grain through an explicit derivation.

### `MULTIPLE_SOURCE_REPRESENTATIONS`
Several legitimate representations exist and should remain distinct unless equivalence is established.

### `SEMANTIC_REVIEW_REQUIRED`
Candidate fields exist but their definition, grain, aggregation or equivalence is not sufficiently established.

### `COVERAGE_GAP`
The preserved ecosystem cannot honestly provide the requested concept/grain/period.

## 8. Current route decisions by semantic family

| Semantic family | Current decision | Notes |
|---|---|---|
| Fixture identity / schedule / results | `KEEP_CURRENT_ROUTE` | Canonical fixture master + governed identity/correction evidence |
| Standard team-match shooting counts | `KEEP_CURRENT_ROUTE` | Direct team-match grain is preferable where coverage is established |
| Standard team-match passing counts | `KEEP_CURRENT_ROUTE` | Direct representation remains default; player aggregation may be useful for corroboration only until governed |
| Possession | `KEEP_CURRENT_ROUTE` | Direct team-match measurement; not safely reconstructed through player summation |
| Standard defensive actions | `KEEP_CURRENT_ROUTE` | Direct route generally appropriate; individual fields still require semantic checks |
| Discipline | `KEEP_CURRENT_ROUTE` | Direct team-match values appropriate where source semantics/coverage hold |
| Goalkeeper actions | `SEMANTIC_REVIEW_REQUIRED` | Direct and player-match representations may coexist; aggregation/equivalence should be established per field |
| xG / xA / xGOT | `MULTIPLE_SOURCE_REPRESENTATIONS` | Direct, later snapshot and player-match-derived representations must retain distinct lineage/version semantics |
| Recent team-match xG (2022-23 onward) | `DERIVED_ROUTE_PREFERRED` candidate | Player-match derivation materially improves coverage; must remain explicitly derived/source-specific |
| Older match-level xG (2016-17 to 2021-22) | `COVERAGE_GAP` | Current preserved ecosystem cannot provide complete trustworthy fixture-level coverage |
| Player-match performance | `KEEP_CURRENT_ROUTE` | Use player-match source through governed fixture/player/team relationships |
| Player-season totals | `KEEP_CURRENT_ROUTE` | Correct for season-level questions; not a fixture-level reconstruction source |
| FPL variables | `KEEP_CURRENT_ROUTE` as FPL-specific | Preserve FPL semantics and missing-value behaviour |
| Timeline / lineups / formations / managers | `KEEP_CURRENT_ROUTE` via preserved PulseLive snapshots | Snapshot layer adds genuine match-centre evidence beyond ordinary team stats |
| Rolling form / streak / split state | `DERIVED_ROUTE_PREFERRED` | Derive once from governed fixture/team observations; do not recompute independently in UI routes |
| Historical as-of state | `KEEP_CURRENT_ROUTE` | Existing versioned historical-state artefacts remain the correct specialised representation |

## 9. Capability Inventory implication

The current capability inventory is explicitly an additive metadata view over governed registries and existing research/model seams. It should not be interpreted as “best evidence route anywhere in the preserved ecosystem”.

Future capability metadata should distinguish at least:

- `SOURCE_PRESENT` — evidence exists somewhere in the preserved ecosystem;
- `CONNECTED` — a current resolver/adapter can retrieve the representation;
- `DERIVABLE` — governed evidence exists to construct the concept at the requested grain;
- `GOVERNED` — semantics, aggregation, missingness and provenance are approved;
- `COMPARABLE` — the observation is safe to compare across the requested population/period;
- `PRODUCT_READY` — sufficient coverage and methodological clarity exist for ordinary product exposure.

A field can therefore be source-present and connected without being governed or comparable.

## 10. Source-selection architecture

Preferred conceptual flow:

```text
preserved evidence
    ↓
SourceRepresentation
    ↓
SourceRouteDecision
    ↓
GovernedVariable
    ↓
MetricDefinition / MetricObservation
    ↓
PopulationContext
    ↓
AnalysisResult
```

A source route should be selected by:

```text
football concept
+ requested grain
+ competition / season / as-of period
+ analytical purpose
        ↓
explicit governed representation
```

It should **not** be selected by “first non-null source wins”.

## 11. First routing families to govern

FRL does not need 1,414 bespoke routing decisions before useful analytical work can continue.

The first explicit routing families should be:

1. fixture/result;
2. team-match shooting;
3. team-match expected metrics;
4. team-match possession;
5. team-match passing;
6. team-match defensive actions;
7. discipline;
8. goalkeeper actions;
9. chance creation / big chances;
10. player-match attacking;
11. player-match possession/passing;
12. player-match defending;
13. player-season context;
14. FPL-specific variables;
15. derived temporal/team-state variables.

Individual fields can deviate from a family rule where evidence requires it.

## 12. Rights and operational independence

Using already-preserved GitHub/local evidence reduces the need for recurring live PulseLive acquisition. It does **not** automatically resolve underlying rights or redistribution questions.

Source route metadata must continue to distinguish:

- acquisition/distribution channel;
- original provider;
- source/version;
- intended use;
- rights/terms status.

No new recurring live PulseLive dependency is recommended by this audit.

## 13. Immediate engineering implication

Before expanding Team Stats families, establish the minimum analytical/source-routing contract against a small reference slice:

- points per match;
- goals for per match;
- goals against per match;
- shots per match;
- shots on target per match;
- possession;
- expected goals as the first multiple-representation/derived-route case.

For each, establish:

```text
concept
→ selected representation
→ grain
→ aggregation
→ missingness
→ coverage
→ comparability
→ rank eligibility
```

This is enough to prove the architecture without introducing a general metric DSL or rewriting the full variable universe.

## 14. Audit conclusion

> **FRL’s evidence ecosystem is richer than any single connected resolver. The correct upgrade is targeted governed source selection, not wholesale source replacement.**

The source layer should remain plural and provenance-preserving. The analytical layer should make representation choice explicit, reproducible and inspectable.