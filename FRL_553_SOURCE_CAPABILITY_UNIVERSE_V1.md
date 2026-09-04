# FRL 553 Source Capability Universe V1

**Status:** Active source-capability hierarchy  
**Date:** 2026-09-04  
**Parent product direction:** `FRL_PRODUCT_NORTH_STAR_AND_EXPERIENCE_ARCHITECTURE_V1.md`

---

## Master source universe

The preserved PulseLive snapshot audit established **553 distinct scalar raw paths** across 3,800 snapshots.

That **553-path inventory is the master snapshotted source universe** for this archive.

It must not be silently redefined around a smaller analytical subset.

The hierarchy is:

```text
553 MASTER SNAPSHOTTED RAW SOURCE PATHS
│
├── 181 CAPTURE / PROVENANCE PATHS
│   └── retrieval, source, validation and evidence context
│
└── 372 FOOTBALL / MATCH PATHS
    │
    ├── 249 TEAM-MATCH STATISTICAL PATHS
    │   └── Phase 1 analytical industrialisation target
    │
    └── 123 OTHER FOOTBALL / MATCH PATHS
        └── events, lineups, managers, identity and match/team context
```

The numbers describe raw source paths, not independently governed canonical variables.

---

## Why all 553 remain important

The 372 football/match paths are the primary analytical subset, but the 181 capture/provenance paths are not disposable noise.

They help establish:

- where evidence came from;
- when it was captured;
- which source/resource produced it;
- whether a request/materialisation succeeded;
- archive and retrieval context;
- reproducibility;
- validation/audit evidence;
- temporal and source provenance.

FRL's product surfaces should not present these as football statistics, but the research/data architecture should preserve them because they make the football evidence defensible.

Therefore the master objective is not "turn all 553 into metrics".

It is:

> **Understand, preserve and appropriately route the full 553-path source universe, while promoting legitimate football capabilities into governed analytical access and retaining provenance paths as evidence infrastructure.**

---

## Capability subsets

### 553 — Master source universe

The exhaustive raw-path inventory.

Source of truth:

`data/audits/pulselive_raw_variables/pulselive_raw_variable_catalogue.csv`

Every raw path belongs here regardless of whether it is:

- a football statistic;
- an event;
- a lineup/context field;
- an identity relationship;
- retrieval metadata;
- provenance evidence.

### 372 — Football / match subset

The non-capture subset used for football capability industrialisation.

This is the primary universe for:

- semantic football understanding;
- research access;
- analytical derivation;
- scouting;
- Opposition Report;
- Matchday;
- modelling;
- Stats/Rankings.

It is a subset of the 553, not the master universe.

### 249 — Team-match statistical subset

The largest coherent analytical block inside the 372.

It is Phase 1 because its shared source family and grain make it the best place to prove generic FRL capability industrialisation.

It is not the final capability boundary.

### 123 — Remaining football / match subset

These remain explicitly in scope after the 249 and include:

- events;
- goals/cards/substitutions;
- player lineups/roles;
- team lineups/formations;
- managers;
- team/match context;
- match resource/context fields;
- identity/relationship evidence.

---

## Architecture rule

FRL must preserve different roles for different source paths:

```text
RAW SOURCE PATH
      ↓
SOURCE ROLE CLASSIFICATION
      ↓
┌────────────────────────────┬──────────────────────────────┐
│ FOOTBALL / MATCH EVIDENCE  │ CAPTURE / PROVENANCE       │
│                            │                              │
│ semantic review            │ preserve retrieval context  │
│ grain                      │ source evidence              │
│ coverage/missingness       │ reproducibility             │
│ identity                   │ validation/audit             │
│ derivation                 │ temporal provenance         │
└──────────────┬─────────────┴───────────────┬──────────────┘
               │                             │
               ↓                             ↓
     GOVERNED FOOTBALL CAPABILITY      EVIDENCE INFRASTRUCTURE
               ↓
     ANALYTICAL / PRODUCT LAYERS
```

A provenance path can be essential to FRL without ever becoming a football metric.

A football path can be valuable source evidence without immediately becoming a canonical variable.

---

## Execution order

1. Preserve and catalogue all **553** raw paths.
2. Industrialise the **249** team-match statistical subset as the first generic analytical proof.
3. Industrialise the remaining **123** football/match paths by grain and role: Events → Lineups/Roles → Match/Team/Manager Context.
4. Keep the **181** capture/provenance paths governed as evidence infrastructure and use them to strengthen reproducibility, temporal reconstruction and auditability.
5. Compare the resulting governed capability against product requirements for Player Scouting, Team Scouting, Opposition Report, Matchday and Research Explorer.
6. Only then score genuine data gaps and evaluate supplementary/current-season sources.

---

## Product doctrine

The master source universe should be broad and defensible.

Product surfaces should remain curated and easy to navigate.

The governing rule remains:

> **Curate presentation, not away the underlying source and research capability.**
