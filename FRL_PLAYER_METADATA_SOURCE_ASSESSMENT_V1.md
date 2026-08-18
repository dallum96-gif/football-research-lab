# Football Research Laboratory — Player Metadata Source Assessment V1

**Status:** Source-acquisition assessment / no promotion approved  
**Date:** 17 August 2026  
**Branch:** `design/player-filter-tiles`

## 1. Purpose

The FRL wants richer player metadata than the current FPL-derived layer provides, especially:

- fixture-level position actually played;
- detailed positional labels where a source genuinely supports them;
- preferred foot / footedness;
- historical validity and source provenance.

This document assesses whether these fields can be acquired reliably and safely enough for FRL use.

## 2. Desired FRL representation

The preferred FRL architecture is:

```text
player-fixture evidence
        ↓
position actually recorded/played in the fixture
        ↓
minutes-weighted / evidence-weighted aggregation
        ↓
FRL primary position
        ↓
secondary positions / role history
```

Preferred foot is treated separately as player metadata, with source, validity and provenance retained.

The FRL should not collapse source-specific position semantics into a permanent player field without retaining the underlying evidence.

## 3. Current FRL gap

The current Player Research/FPL layer provides broad FPL position classes rather than the detailed positional information required for examples such as `CB`, `LCB`, `RCB`, `LB`, `LWB`, `RB` and `RWB`.

The current tracked FRL source inventory identifies richer player-match/event data in the local `pl_stats` workspace, but it does not currently establish a trusted, source-documented detailed-position/preferred-foot feed for all historical seasons.

## 4. Candidate source assessment

### A. FBref / Sports Reference

**Field suitability:** High.

A GitHub FBref scraper demonstrates fixture/player rows containing `Position played`, while another FBref API project exposes player metadata including `positions` and `footed`. The latter's example also uses Football Reference player IDs, which would be valuable for identity resolution. However, these are third-party projects and are not themselves authoritative FRL data sources.

**Historical fixture-level position:** Potentially excellent where the source rows preserve the position recorded for each match.

**Preferred foot:** Potentially available through player metadata.

**Access viability:** Poor as an unsanctioned foundational ingest. Sports Reference's current Terms prohibit automated access such as scripts, bots, scrapers and data miners without express written permission where it adversely impacts access/performance, and also restrict use that creates a competing or materially substitutive database/data store. The Terms also contain restrictions around using Site content for AI/model purposes. This makes unattended large-scale FRL scraping an unsuitable default architecture without explicit permission or a clearly applicable license/permission.

**Conclusion:** Do not make direct FBref scraping a foundational automated FRL source without permission/licensing review. A GitHub-hosted dataset that contains FBref-derived data is not automatically safe to adopt merely because its code is MIT-licensed; the underlying data rights remain separate. One example explicitly states that its code is MIT-licensed while the data belongs to FBref.

### B. SofaScore

**Field suitability:** High for current player metadata.

SofaScore player profiles expose preferred foot and broad position. SofaScore also documents that a player's main position is determined from lineup positions over the previous year, with a 50% match threshold. That is useful evidence for a current-role classifier but is not the same as a permanent historical position field.

**Historical fixture-level position:** Potentially high if match-lineup data is available for each historical fixture and preserved as a snapshot.

**Preferred foot:** Clearly available on player profiles.

**Access viability:** Poor as an unsanctioned foundational scrape. SofaScore's current Terms prohibit scraping, aggregation or reproduction of platform content without explicit consent and prohibit burdening the service with automated requests. The Terms also state that database content is protected and that extraction/copying of a significant portion requires explicit consent.

**Conclusion:** Do not make direct SofaScore scraping a foundational automated FRL source without explicit permission/licensing. Community GitHub scrapers are useful as technical evidence that the fields exist, but do not create data-use rights.

### C. FIFA / SofIFA / game-data datasets

**Field suitability:** Technically very high. These datasets often contain detailed positions such as `LCB`, `CB`, `RCB`, `LB`, `RB` and preferred foot.

**Research suitability:** Low for foundational FRL football-truth data. These are game/database attributes rather than direct evidence of the player's actual role in a particular real-world fixture. They can be useful as a separate contextual/scouting source, but should not silently become canonical match-position truth.

**Conclusion:** Not suitable as the canonical source for FRL fixture-level position. Potentially useful later as an explicitly labelled auxiliary scouting dataset if licensing permits.

## 5. GitHub-hosted datasets

GitHub is useful as a discovery and archival location, but GitHub hosting does not itself establish that the underlying football data is licensed for redistribution or commercial use.

For any candidate GitHub dataset, FRL approval requires separate review of:

1. source origin;
2. dataset licence;
3. underlying provider rights;
4. redistribution terms;
5. historical coverage;
6. field semantics;
7. update/reproducibility mechanism;
8. identity keys;
9. evidence of data-quality maintenance.

A permissively licensed scraper is not automatically a permissively licensed dataset.

## 6. Preferred acquisition strategy

The FRL should prioritise sources in this order:

### Tier 1 — licensed / explicit data feed

A provider or dataset explicitly permits the required use and provides stable historical/player-match identifiers.

### Tier 2 — openly licensed GitHub dataset

Historical data is already captured and distributed under a licence compatible with FRL use, with source attribution and provenance preserved.

### Tier 3 — permissioned extraction

A provider grants explicit permission for FRL extraction and retention.

### Tier 4 — constrained research-only acquisition

A source can be inspected manually or used experimentally under applicable law/terms, but is not suitable for automated production ingestion or redistribution. Such data remains clearly marked as exploratory/non-canonical evidence.

## 7. Identity and synchronisation contract

No player metadata source may be joined into FRL using name matching alone.

The intended route is:

```text
source player identifier
        ↓
verified source identity mapping
        ↓
canonical FRL player identity
```

For fixture-level position:

```text
source match identifier
        ↓
verified fixture crosswalk
        ↓
(season, fixture_id)
        ↓
player-fixture evidence
```

For preferred foot:

```text
source player identifier
        ↓
verified player identity
        ↓
preferred_foot + source + valid_at/valid_from + provenance
```

Unresolved or conflicting mappings remain unavailable/fail-closed.

## 8. Position derivation rule

Where fixture-level position evidence is available, the FRL should preserve the source position exactly and then derive a primary position from actual playing exposure.

A future derived position record may contain:

- primary_position;
- secondary_positions;
- minutes_by_position;
- matches_by_position;
- position_basis;
- aggregation window;
- source coverage;
- confidence/coverage flag.

The default derivation should be evidence-based rather than manually assigned.

## 9. Preferred-foot rule

Preferred foot should not be inferred from isolated match events such as which foot was used for an individual shot or pass.

It should be imported as explicit source metadata and retained with provenance. Where sources disagree, the conflict should remain visible until resolved or represented as an uncertainty/conflict state.

## 10. Source viability decision

**Current decision: DO NOT PROMOTE FBref or SofaScore scraping to a foundational FRL ingestion dependency.**

They are valuable candidate sources because they demonstrate that the desired fields exist, but their current public-use terms create material automation/redistribution risk for a long-lived FRL data platform.

The immediate FRL task should therefore be a **licensed/open-source discovery pass** for a source that provides:

- historical fixture-level player position;
- detailed positional labels where possible;
- preferred foot;
- stable player identifiers;
- stable match/fixture identifiers;
- sufficient historical Premier League coverage;
- explicit permission compatible with FRL retention and analytical use.

## 11. Promotion test

No candidate becomes an FRL source until it passes:

- source reliability assessment;
- historical coverage assessment;
- semantic field assessment;
- identity/crosswalk validation;
- fixture linkage validation;
- sample-level manual verification;
- provenance capture;
- licence/access review;
- reproducible acquisition test;
- update/re-ingestion test;
- fail-closed conflict test.

The first implementation should be additive and experimental. Existing trusted FRL data remains unchanged.

## 12. North Star alignment

This metadata is valuable because it expands the FRL beyond generic statistics into:

- football research;
- scouting / football intelligence;
- player profiling;
- tactical/role analysis;
- player-model features;
- team-strength modelling;
- future recruitment and comparison tools;
- eventually predictive and betting applications.

The guiding principle is:

> **Acquire richer evidence broadly, but promote it into trusted FRL knowledge only when the source, semantics, identity and provenance are defensible.**
