# Football Research Laboratory — Short-Term Product Roadmap

**Status:** active near-term planning document  
**Last updated:** 13 September 2026

For repository-memory governance see `FRL_DOCUMENTATION_SYNC_CONTRACT.md`.

Current-state detail belongs in `CURRENT_WORK.md`. The 13 September reconciliation is recorded in `FRL_REPOSITORY_RECONCILIATION_2026-09-13.md`.

## Purpose

This roadmap turns FRL's governed research/data foundation into a coherent product without allowing presentation work to outrun evidence quality, identity, provenance, temporal discipline or validation.

The durable information-architecture rule remains:

> **Profiles describe entities. Stats analyse entities. Rankings analyse populations. Compare analyses selected entities together. Research tests the questions these surfaces reveal.**

Product lenses remain shared projections over one governed evidence layer rather than separate statistical systems.

## Completed / established foundations

The following are no longer 'next tasks'; they are standing foundations or validated historical checkpoints:

- canonical fixture, team and player identity rules;
- fixture correction provenance and temporal/as-of discipline;
- Universal Research Access and governed source-routing work;
- the 553-path preserved PulseLive source universe;
- reconciliation of the 249 team-match statistical paths, including governed generic access and preserved raw-only routing;
- exhaustive Player-Match source-universe accounting;
- archive-wide fixture event/tactical-context routing;
- Team and Player Stats/Rankings analytical shells;
- 2026/27 governed living-season integration process;
- Team State V1 research object;
- Adaptive Dixon-Coles V1 as the frozen experimental forecasting control for the next controlled experiment;
- Head-to-Head / BetBuilder evidence as a governed descriptive product layer.

These remain subject to their own coverage and validation limitations; 'completed foundation' does not mean every future football question is solved.

## Active product phase — reference branch reconciliation

The immediate priority is to turn the current product/reference work into a trustworthy integration candidate.

Active branch:

`design/bet-builder-reference-v1`

Draft PR:

`#53 — UI: premium FRL shell, Matchday builder and Fixtures reference design`

The branch contains substantial frontend/product work **and supporting backend/evidence changes**. It is also behind newer commits on its current base branch and therefore must be reconciled before integration.

### Definition of done for this phase

- live local working-tree state established and protected;
- active branch reconciled with the current base without destructive cleanup;
- supporting backend/API diffs reviewed for compatibility;
- targeted regressions pass;
- club-profile/reference-data validation passes;
- Next.js typecheck/build pass;
- relevant project-health checks pass where the local environment permits them;
- documentation-sync gate passes;
- current design tokens/direction are no longer contradicted by living docs;
- PR #53 accurately describes its real scope and validation status.

## Workstream 1 — Fixture Intelligence / Matchday

**Priority:** high after branch reconciliation.

Objective:

> **For any fixture, show what the governed evidence says about the matchup, why it says it, what remains uncertain, and which downstream questions are worth testing.**

Current building blocks include Fixtures, result workspace, Matchday, Head-to-Head and Bet Builder reference work.

Near-term progression:

- keep fixture-first navigation coherent;
- deepen attack-v-opponent-defence matchup evidence;
- improve player-level evidence where source semantics/coverage support it;
- keep descriptive hit-rate evidence visually/conceptually separate from calibrated model probabilities;
- preserve explicit sample size and missingness;
- remove hard-coded/local-only data-path dependencies from product-critical routes where practical;
- treat bookmaker/market price as a downstream layer rather than an input to football truth unless a research question explicitly requires it.

## Workstream 2 — Team Profile → Team Scouting

**Priority:** high / parallel product work where it reuses governed evidence.

Objective:

> **Describe the club clearly, then let the user move naturally into how the team plays and what is unusual about it.**

Current reference work includes richer club identity, crest/stadium context and Team Overview experimentation.

Next progression should connect profile identity to governed analytical families such as:

- attacking output and chance creation;
- territory/possession/passing;
- defensive behaviour;
- discipline/set pieces;
- form/state and tactical context;
- personnel dependencies;
- league/population context.

Do not turn Team Profile into a metric wall. Profile and Team Stats remain distinct but connected surfaces.

## Workstream 3 — Player Profile / Player Scouting

**Priority:** active after/alongside current product reconciliation.

Objective:

> **Make it possible to understand what type of player someone is, what they are doing well, their role/context, and the evidence limitations in seconds — then drill deeper.**

Use the existing governed player capability/cohort work rather than inventing browser-side player semantics.

Important constraints:

- position/role/minutes cohorts must be explicit;
- later-period rich technical fields remain partial-period evidence rather than universal history;
- the four currently unsupported carry/progression product capabilities must remain unavailable until genuine evidence exists;
- percentile/rank displays require governed population semantics.

## Workstream 4 — Stats / Rankings / Compare

The signature vertical-list / multi-tile language remains useful for fast browsing, but it is a component pattern rather than the whole product architecture.

Next work should improve:

- relationship between entity value and league context;
- cohort/population clarity;
- full-ledger progressive disclosure;
- comparison of selected teams/players using shared governed results;
- coverage/eligibility visibility;
- navigation between metric, entity and ranking contexts.

## Workstream 5 — Research Explorer / natural-language depth

**Status:** architectural progression rather than one page sprint.

Objective:

Keep the full governed capability universe discoverable underneath curated product surfaces.

Progressively support:

- variable/concept discovery;
- source representation and natural grain;
- season availability;
- definitions and derivations;
- coverage/missingness;
- populations/cohorts;
- ranks/distributions/splits/rolling windows;
- provenance;
- as-of reconstruction;
- eventual natural-language investigation that links back to evidence and research objects.

## Workstream 6 — Controlled modelling progression

Do not allow modelling work to become an unstructured search for a profitable backtest.

Near-term modelling sequence:

1. preserve Adaptive Dixon-Coles V1 as the frozen experimental control;
2. run the pre-registered Team State incremental-information experiment;
3. use time-respecting evaluation and explicit holdouts;
4. distinguish predictive improvement, calibration and economic value;
5. keep market price / edge / staking strategy downstream and explicit.

No descriptive evidence index should be upgraded into a betting probability by presentation alone.

## Workstream 7 — Portability and technical debt

Product growth now makes a few technical debts more important:

- hard-coded local Player-Match/source paths in legacy enrichment routes;
- mixed-generation API/runtime seams;
- visual-token migration from older warm-root tokens to the current dark editorial design language;
- branch divergence and long-lived reference branches;
- validation that depends on Daniel's local source workspace.

Resolve these at established seams rather than through broad rewrites.

## Current design direction

The intended product language is now **dark, premium, editorial, analytical and football-first**.

See `UI_DESIGN_SYSTEM.md` and `FRL_LUXURY_DESIGN_CONSTITUTION.md`.

The earlier warm parchment token system remains in parts of the codebase during migration, but it is not the design authority for new work.

External products may inspire information hierarchy, but FRL must retain its own identity and avoid generic SaaS/dashboard/sportsbook styling.

## Validation / safety

For each implementation slice:

- inspect the existing mechanism first;
- establish objective and definition of done;
- reuse governed analytical seams;
- preserve source/identity/temporal/missingness contracts;
- prefer the smallest reversible change;
- validate targeted invariants first;
- run relevant API/data/query regressions;
- run Next.js typecheck/build for frontend changes;
- run project-health where appropriate and possible;
- run documentation-sync validation when project state changes;
- preserve unrelated tracked/untracked/local work;
- perform a convergence check against the original objective before declaring completion.

## Current next step

> **Finish the 13 September repository/branch reconciliation and validate the active reference branch before treating it as integrated current state.**

Once that is complete, continue Fixture Intelligence, Team/Player analytical product work and the controlled modelling programme from the same governed evidence foundation.
