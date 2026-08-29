# Future League Combine Plan

**Status:** Future expansion plan. Not part of the current Premier League GUI operationalisation scope.

## Purpose

FRL should eventually support cross-league team and player research in the spirit of FBref-style comparison, while preserving FRL's stronger requirements around provenance, temporal integrity, identity, reproducibility and semantic comparability.

The objective is not to copy FBref. The objective is to make FRL capable of answering questions such as:

- How does a winger in La Liga compare with a Premier League winger?
- Which U23 attacking midfielders across Europe's major leagues rank highly for progressive actions and chance creation?
- How does one team's pressing, possession or chance-creation profile compare with teams in other competitions?
- Which players remain exceptional after adjusting for minutes, position, team context and league distribution?

This may require combining multiple reputable data sources rather than depending on one provider.

## Core principle

FRL should treat provider-native data as source evidence, not as the final universal schema.

The intended architecture is:

`league/provider source -> preserved raw evidence -> provider-native normalisation -> canonical FRL identity -> semantic metric layer -> governed research/API layer -> common GUI`

PulseLive-specific, StatsBomb-specific or other provider-specific assumptions must not leak upward into the universal research or GUI layer.

## 1. Multi-source data strategy

FRL should be willing to stitch together complementary sources when no single source provides complete historical coverage.

A future league could therefore use different sources for different evidence classes, for example:

- canonical fixtures and results;
- match metadata;
- team match statistics;
- player appearances and minutes;
- lineups and formations;
- event-level actions;
- expected-goals or advanced metrics;
- betting-market data.

The requirement is not that every variable originates from the same provider. The requirement is that FRL knows where every value came from, how it was transformed and whether it is genuinely comparable with equivalent values elsewhere.

## 2. Universal identity layer

Cross-league comparison requires stable FRL identities independent of provider IDs.

The identity layer should cover at least:

- competition;
- season;
- team;
- player;
- fixture.

Provider identifiers should remain namespace-specific evidence linked to those canonical entities.

### Player identity

Player identity is likely to be the hardest part of cross-source stitching.

The same player may appear under different names and IDs across providers, clubs and seasons. FRL should therefore extend its existing identity-registry approach rather than matching only on display name.

Relationships should support evidence such as:

- provider player ID;
- name variants;
- date of birth where available;
- nationality where useful;
- team and season context;
- transfer history/context;
- verified cross-provider relationships.

Ambiguous mappings should continue to fail closed rather than being silently guessed.

## 3. Semantic metric layer

Collecting similarly named variables is not enough. FRL must establish whether they mean the same thing.

For example, one provider's `tackle`, `progressive pass`, `pressure`, `assist` or `shot on target` definition may differ from another provider's definition.

FRL should therefore maintain a semantic metric layer with, for each common concept:

- FRL metric name;
- source family;
- original source variable;
- source definition where known;
- units;
- transformation logic;
- aggregation method;
- temporal grain;
- comparability status;
- limitations.

Possible common concepts include:

- minutes;
- goals;
- assists;
- shots;
- expected goals;
- expected assists;
- touches;
- passes;
- progressive actions;
- carries;
- tackles;
- interceptions;
- aerial actions;
- pressures;
- chance creation.

## 4. Comparability classes

FRL should not silently treat all cross-provider metrics as equivalent.

A useful future classification could be:

### DIRECTLY_COMPARABLE
The provider definitions and transformations are sufficiently aligned for direct comparison.

### HARMONISED
The original variables differ but FRL has an explicit, documented transformation that produces a defensible common concept.

### SOURCE_SPECIFIC
The metric is useful within a source family but should not be compared directly across providers.

### UNAVAILABLE
The required evidence does not exist for that league/source/period.

The research layer should expose these distinctions to downstream queries and models.

## 5. Unequal league coverage is acceptable

FRL should not require every competition to contain every Premier League variable before that competition can be added.

Instead, each league/source combination can expose explicit capability coverage.

For example, a league might have:

- complete canonical fixture coverage;
- complete player appearances;
- strong match statistics;
- event data for only selected seasons;
- no tactical placement evidence.

Queries should use only competitions whose evidence supports the requested concept.

A simple cross-league goals-per-90 query may therefore include many competitions, while a final-third pressure comparison may legitimately include only a subset.

Missing coverage should narrow the eligible universe rather than creating fabricated or incomparable values.

## 6. Cross-league derived comparison layer

Once canonical identity and semantic comparability are established, FRL should support common comparison transformations such as:

- totals;
- per-90 rates;
- percentages;
- rolling values;
- positional percentile ranks;
- age-group percentile ranks;
- league-season percentile ranks;
- team-possession-adjusted metrics;
- opponent-strength adjustments where defensible;
- league-context normalisation where evidence supports it.

Source-native values must remain available underneath every derived value.

## 7. Product direction

A future Player Explorer should behave as the cross-league research surface.

Potential flow:

`Player Explorer -> player-season profile -> comparison cohort -> match history -> fixture evidence -> events -> derived metrics -> modelling outputs`

Users should be able to choose or define comparison cohorts by criteria such as:

- competition;
- season;
- position;
- age;
- minutes threshold;
- team;
- metric thresholds;
- percentile thresholds.

Example future query:

> Show U23 attacking midfielders across Europe's major leagues above the 85th percentile for progressive carries and chance creation, with at least 900 league minutes.

FRL should return the result together with the evidence/comparability context required to understand it.

## 8. Proposed expansion sequence

When Premier League operationalisation is mature enough to expand:

1. Select candidate leagues based on source quality and historical depth.
2. Build the canonical competition/team/fixture universe for the candidate league.
3. Identify reputable source families for fixtures, player data, match stats and events.
4. Preserve provider-native raw evidence before transformation.
5. Build namespace-safe team/player/fixture relationships.
6. Map candidate variables into the semantic metric layer.
7. Classify cross-provider comparability explicitly.
8. Expose the league through Universal Research Access and existing APIs.
9. Reuse the existing Fixture Explorer, Player Explorer and comparison GUI rather than creating league-specific applications.
10. Add increasingly rich sources without breaking the common contract.

## 9. Source-selection principles

Future source selection should favour:

- reputable provenance;
- documented or inspectable definitions;
- stable historical coverage;
- legal/licensing compatibility;
- reproducible acquisition;
- stable identifiers where possible;
- sufficient granularity for FRL research questions.

GitHub-hosted open datasets can be useful, but FRL should distinguish an authoritative or reputable upstream source from an arbitrary mirror. Where a repository republishes another provider's data, provenance should ultimately point to the underlying source.

## 10. Long-term outcome

The desired end state is not a collection of separate league databases.

It is one governed football research environment where leagues and providers are evidence sources underneath common FRL entities and research concepts.

That should make the second league substantially easier to add than the first, and each subsequent league easier again.

The strategic rule is:

> **Preserve source-native evidence, canonicalise identity, harmonise concepts only when defensible, expose comparability explicitly, and keep the universal FRL research/UI layer provider-agnostic.**
