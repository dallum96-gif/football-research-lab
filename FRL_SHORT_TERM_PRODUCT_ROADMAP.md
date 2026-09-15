# Football Research Laboratory — Short-Term Product Roadmap

**Status:** active near-term planning document  
**Last updated:** 15 September 2026

For repository-memory governance see `FRL_DOCUMENTATION_SYNC_CONTRACT.md`.

Current-state detail belongs in `CURRENT_WORK.md`. The 13 September repository reconciliation is recorded in `FRL_REPOSITORY_RECONCILIATION_2026-09-13.md`; the Player Profile foundation checkpoint is recorded in `FRL_PLAYER_PROFILE_UNIVERSAL_FOUNDATION_V1_2026-09-15.md`.

## Purpose

This roadmap turns FRL's governed research/data foundation into a coherent product without allowing presentation work to outrun evidence quality, identity, provenance, temporal discipline or validation.

The durable information-architecture rule remains:

> **Profiles describe entities. Stats analyse entities. Rankings analyse populations. Compare analyses selected entities together. Research tests the questions these surfaces reveal.**

Product lenses remain shared projections over one governed evidence layer rather than separate statistical systems.

## Completed / established foundations

The following are standing foundations or validated historical/feature checkpoints rather than unstarted tasks:

- canonical fixture, team and player identity rules;
- fixture correction provenance and temporal/as-of discipline;
- Universal Research Access and governed source-routing work;
- the 553-path preserved PulseLive source universe;
- reconciliation of the 249 team-match statistical paths, including governed generic access and preserved raw-only routing;
- exhaustive Player-Match source-universe accounting;
- archive-wide fixture event/tactical-context routing;
- Team and Player Stats/Rankings analytical shells;
- 2026/27 governed living-season integration process;
- Player Profile Universal Foundation V1 as a validated feature-branch integration candidate, including explicit cross-source Profile identity, packaged biography, transfer-aware club context and one Player-Season Profile representation for participation plus MID V1 comparison;
- Team State V1 research object;
- Adaptive Dixon-Coles V1 as the frozen experimental forecasting control for the next controlled experiment;
- Head-to-Head / BetBuilder evidence as a governed descriptive product layer.

These remain subject to their own coverage and validation limitations; “completed foundation” does not mean every future football question is solved or integrated into `main`.

## Active product phase — reference branch reconciliation

The immediate integration priority remains to turn the current product/reference work into a trustworthy integrated development state while preserving newer local work.

Reference branch:

`design/bet-builder-reference-v1`

Draft PR:

`#53 — UI: premium FRL shell, Matchday builder and Fixtures reference design`

Player Profile foundation candidate:

`feat/player-profile-universal-foundation-v1`

The Profile candidate was isolated from the tracked reference-branch head so that Daniel's uninspected local Windows work would not be overwritten. It must be reconciled with that live local state before merge.

### Definition of done for reference-branch integration

- live local working-tree state established and protected;
- feature/reference branches reconciled without destructive cleanup;
- supporting backend/API diffs reviewed for compatibility;
- targeted regressions pass;
- club-profile/reference-data validation passes where implicated;
- Next.js typecheck/build pass;
- relevant project-health checks pass where the local environment permits them;
- documentation-sync gate passes;
- known target-branch blockers are resolved or explicitly carried;
- PR scope and validation status accurately describe tracked state.

## Workstream 1 — Fixture Intelligence / Matchday

**Priority:** high after/alongside branch reconciliation.

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

**Priority:** active; universal foundation established on a validated feature candidate.

Objective:

> **Make it possible to understand what type of player someone is, what they are doing well, their role/context, and the evidence limitations in seconds — then drill deeper.**

### Established V1 foundation

The Ødegaard first-draft page is the universal **composition reference**, not a licence to copy one player's data pathway to every player.

The governed foundation now provides:

- explicit seasonal route → research/source identity relationships;
- correct cross-season route navigation when IDs change;
- separate portrait/source identity;
- packaged biography rather than a local-workspace runtime dependency;
- transfer-aware club context that withholds unresolved primary club rather than guessing;
- one pinned Player-Season representation for Profile participation and all six MID V1 per-90 dimensions;
- all-or-nothing fallback for descriptive participation rather than mixed-representation rows;
- explicit unavailable states for non-MID comparative templates.

The current pinned Ødegaard checkpoint is 3 appearances, 3 starts and 224 Player-Season minutes; Forward passing is 45 / 224 × 90 = 18.0804 per 90.

### Next progression

1. reconcile/merge the universal foundation candidate only after checking Daniel's live local state;
2. stress-test the same Profile composition across clubs, missing portraits, historical seasons and genuine transfer cases;
3. research and govern DEF, FWD and GKP analytical templates independently;
4. revisit midfielder role/cohort semantics beyond the broad FPL MID classification only through explicit research;
5. audit broader Player Stats/rich Player-Match denominator provenance separately rather than assuming the Profile-specific repair proves equivalence elsewhere;
6. deepen Stats/History drill-down without turning Profile into a metric wall.

Important constraints remain:

- position/role/minutes cohorts must be explicit;
- source-period coverage remains visible;
- unsupported carry/progression capabilities remain unavailable until genuine evidence exists;
- take-ons are not carrying;
- percentile/rank displays require governed population semantics;
- source identifiers must not be collapsed into one canonical ID by coincidence.

## Workstream 4 — Stats / Rankings / Compare

The signature vertical-list / multi-tile language remains useful for fast browsing, but it is a component pattern rather than the whole product architecture.

Next work should improve:

- relationship between entity value and league context;
- cohort/population clarity;
- full-ledger progressive disclosure;
- comparison of selected teams/players using shared governed results;
- coverage/eligibility visibility;
- navigation between metric, entity and ranking contexts;
- denominator/source-representation provenance where existing Player Stats calculations mix source families.

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

## Workstream 7 — Portability, integration and technical debt

Product growth now makes a few technical debts more important:

- hard-coded local Player-Match/source paths in legacy enrichment routes outside the packaged Player Profile biography path;
- mixed-generation API/runtime seams;
- the target/reference branch's tracked `api/frl_api.py` import of absent `team_records_materialization`;
- broader Player Stats/rich Player-Match denominator provenance outside Profile;
- frontend dependency-security debt surfaced by clean npm validation;
- visual-token migration from older warm-root tokens to the current dark editorial design language;
- branch divergence and long-lived reference branches;
- validation paths that still depend on Daniel's local source workspace.

Resolve these at established seams rather than through broad rewrites.

## Current design direction

The intended product language remains **dark, premium, editorial, analytical and football-first**.

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

> **Complete documentation/PR closeout for `PLAYER_PROFILE_UNIVERSAL_FOUNDATION_V1`, then reconcile that validated feature candidate with Daniel's live local state before merging it into the experimental `design/bet-builder-reference-v1` line.**

In parallel, keep the broader reference-branch/API reconciliation explicit. Once the Profile candidate is integrated safely, proceed to cross-player visual stress-testing and separate DEF/FWD/GKP analytical research while continuing Fixture Intelligence, Team analytical work and the controlled modelling programme from the same governed evidence foundation.
