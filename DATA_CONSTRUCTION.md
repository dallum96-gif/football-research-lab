# Football Research Laboratory — Data Construction and Identity

## Purpose

This document records how the committed repository represents teams and fixtures, how the canonical fixture layer is consumed, what validation protects it, and what parts of the original one-off construction process are still not reproducible from committed code.

The goal is that a new session can understand not only **what the canonical database looks like**, but also **why the identifiers and relationships mean what they do**.

---

## 1. The core rule

The Laboratory does **not** treat a source team's season-local identifier as a longitudinal club identity.

Instead, the model separates:

```text
season-local source identity
        ↓
verified identity mapping
        ↓
persistent club identity
```

This is necessary because source systems can use IDs that are only meaningful within a season or source generation, while the research project needs to follow a club across multiple Premier League seasons.

The same principle applies to fixtures: a fixture is represented by a **season-scoped canonical fixture ID** and resolved through the canonical fixture master, rather than being identified by an unstable source filename or a display name alone.

---

## 2. Team identity registry

Canonical file:

`identity/team_seasons.csv`

The registry contains:

```text
team_season_id
season
club_id
canonical_name
persistent_team_code
local_team_id
source_name
mapping_status
mapping_source
```

Example:

```text
2016-17:3,2016-17,3,Arsenal,3,1,Arsenal,VERIFIED,Local PL events_stats + fixtures_master
```

This means:

- season = `2016-17`
- persistent club identity = `3`
- persistent team code = `3`
- source/local team ID for that season = `1`
- source name = `Arsenal`
- mapping status = `VERIFIED`
- mapping evidence = local Premier League `events_stats` plus the fixture master

The exact mapping is therefore evidence-backed rather than inferred from a display-name match alone.

### What the query layer does with it

`query_lab.py` loads the identity registry and resolves a team within a season using the registry. It normalises names, supports known aliases, rejects ambiguous matches, and requires the mapping to have `mapping_status = VERIFIED`.

The returned team object exposes both the persistent identity and the season-local identity, so downstream logic can use the correct identifier for the source being queried without confusing it for a longitudinal identity.

### Important invariant

A future implementation must not replace this with a single global `team_id` assumption. The distinction between local and persistent identity is part of the research contract.

---

## 3. Canonical fixture master

Canonical file:

`fixtures_master_corrected.csv`

Current schema:

```text
season
fixture_id
fixture_code
kickoff_time
gameweek
home_team_id
away_team_id
home_score
away_score
```

`fixture_id` is scoped by season. The natural fixture key is therefore:

```text
season + fixture_id
```

The master covers ten Premier League seasons from `2016-17` through `2025-26`, with 380 fixtures per completed season and 3,800 fixtures in total.

The final rows demonstrate the numbering continuing through fixture 380 within `2025-26`; the project health gate independently verifies the 380-per-season / 3,800-total invariant.

### Why this is canonical

The rest of the application reads the fixture master through the research/query layer. The GUI does not maintain a second fixture table.

The normal query path is:

```text
fixtures_master_corrected.csv
        ↓
query_lab.py
        ↓
query_api.py
        ↓
GUI
```

This means the Fixture Explorer and Fixture Landing Page must continue to resolve fixtures through the same canonical fixture identity.

---

## 4. Fixture corrections are additive provenance, not silent overwrites

Corrections are recorded separately in:

`identity/data_quality/fixture_corrections.csv`

The committed example is the 2019-20 Manchester City v Arsenal fixture:

```text
season:              2019-20
fixture_id:          275
scheduled_kickoff:   2020-03-11T19:30:00Z
actual_kickoff:      2020-06-17T19:15:00Z
home_score:          3
away_score:          0
status:               VERIFIED_CORRECTION
source:               Premier League
```

The reason is explicitly recorded: the match was postponed and later played on the restart date. The correction file retains the original scheduled time while separately recording the verified actual kickoff/result.

This is the model we want for historical correction work:

```text
original evidence
      +
verified correction record
      ↓
corrected analytical view
```

Do not silently edit away the history of the correction.

---

## 5. Project-health validation of the fixture master

`project-health.ps1` is the current operational data-health gate.

It checks, among other things:

- exactly 3,800 fixtures;
- exactly 380 fixtures for each expected Premier League season;
- no duplicate `season + fixture_id` groups;
- no missing home team IDs;
- no missing away team IDs;
- no missing kickoff timestamps;
- no fixture with identical home and away team IDs;
- valid kickoff datetimes;
- the expected 2025-26 player/fixture relationship;
- 380 unique modern fixture codes in the relevant player and fixture records.

A fixture with missing scores is currently treated as uncompleted and warned about rather than failed. The known 2019-20 fixture 275 warning is therefore expected under the current semantics.

The health gate is intentionally conservative: it should stop a new integrity failure from quietly becoming part of the trusted foundation.

---

## 6. Relationship between fixtures and player data

For modern seasons, player-level source records contain `fixture_code` values. The health gate checks the 2025-26 relationship by requiring:

```text
player fixture codes
        ↕
canonical fixture codes
```

for all 380 fixtures.

This is an example of a cross-table invariant: it is not enough for each file to look internally valid; the identifiers must join correctly where the research model says they should.

---

## 7. Relationship between fixtures and match statistics

Canonical match statistics are packaged in:

`data/fixture_match_stats.csv`

The packaged rows are keyed by:

```text
season + fixture_id
```

and include a source match ID plus core and optional home/away statistics.

`match_stats.py` first tries the packaged dataset. If packaged statistics are absent, it can reconstruct the source match by matching:

1. season;
2. verified persistent home-team identity;
3. verified persistent away-team identity;
4. canonical kickoff timestamp converted to UTC.

This is an important design feature: a source match ID is not blindly trusted as the only identity. The system resolves it through the canonical football identity model.

If multiple source matches satisfy the matching conditions, the code raises an ambiguity error rather than choosing arbitrarily.

---

## 8. Historical match-state construction

The repository also contains `build-match-state.ps1` for the historical-state layer.

It reads the fixture master, sorts fixtures chronologically, and maintains a history per:

```text
season | team_id
```

For each current fixture it constructs the pre-match feature row **before** adding the current fixture to either team's history.

That produces features such as:

- season-to-date matches/points/goals;
- last-five overall form;
- last-five home form for the home side;
- last-five away form for the away side;
- latest prior kickoff;
- rest days;
- fixture completion state.

Only completed fixtures are added to team history. An unplayed fixture therefore cannot contaminate historical state.

This ordering is an explicit anti-leakage invariant:

```text
prior completed matches
        ↓
construct current fixture state
        ↓
only then add current fixture to history
```

---

## 9. What is and is not reproduced by committed code

### Reproducible from the repository

The committed repository gives us the operational definitions for:

- the season-local / persistent identity model;
- the identity resolution rules;
- the canonical fixture schema;
- season-scoped fixture identity;
- fixture correction/provenance handling;
- fixture/statistics matching;
- the project-health invariants;
- historical match-state construction and its temporal safeguards.

### Not currently fully reproducible from committed code

The **original one-off construction script(s) that first assembled the 3,800-row canonical fixture master and the complete `team_seasons.csv` registry from the raw local historical files are not currently present as a single committed rebuild pipeline**.

The repository contains the resulting canonical artefacts and the rules by which the rest of the system consumes them, but it does not yet contain a clean end-to-end command such as:

```text
raw source files
    ↓
normalise historical schemas
    ↓
build team identity registry
    ↓
build fixture master
    ↓
apply verified corrections
    ↓
run full validation
    ↓
write canonical artefacts
```

This is a **documentation/reproducibility gap**, not evidence that the current canonical data is invalid.

Do not invent the missing original build steps in future documentation. If the original construction code is recovered from the local workspace, it should be inspected and incorporated here with its actual provenance.

---

## 10. Future recommended improvement

At some point the Laboratory should have an explicit, versioned canonical-build pipeline that can rebuild the trusted artefacts from preserved raw evidence.

That would give us:

```text
RAW EVIDENCE
    ↓
INGESTION / SCHEMA DETECTION
    ↓
IDENTITY RECONCILIATION
    ↓
FIXTURE CANONICALISATION
    ↓
CORRECTION / PROVENANCE
    ↓
DATA-QUALITY GATE
    ↓
CANONICAL DATABASE
```

That is preferable to relying forever on one-off historical construction work.

Until that exists, `fixtures_master_corrected.csv` and `identity/team_seasons.csv` should be treated as **trusted canonical artefacts under version control**, with changes made through controlled, provenance-preserving procedures.

---

## 11. Re-entry checklist for a new session

When a new session needs to understand the data foundation quickly, inspect:

1. `DATA_CONSTRUCTION.md` — this document
2. `identity/team_seasons.csv` — actual identity registry
3. `fixtures_master_corrected.csv` — actual canonical fixture records
4. `identity/data_quality/fixture_corrections.csv` — explicit corrections
5. `query_lab.py` — identity/fixture resolution and query semantics
6. `match_stats.py` — fixture-to-source-statistics matching
7. `build-match-state.ps1` — historical pre-match state construction
8. `project-health.ps1` — operational data-quality gate
9. `RISK_STRATEGY_FRAMEWORK.md` — why these rules exist

A new session should be able to reconstruct the **data contract** from these files without needing the user to re-teach the architecture.
