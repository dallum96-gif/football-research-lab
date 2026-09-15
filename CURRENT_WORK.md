# Current Work — Football Research Laboratory

**Last updated:** 15 September 2026
**Checkpoint:** `PLAYER_PROFILE_FORWARD_PASSING_V1`

For documentation-governance rules see `FRL_DOCUMENTATION_SYNC_CONTRACT.md` and `data/frl_documentation_state_v1.json`. The current Player Profile promotion is recorded in `FRL_PLAYER_PROFILE_SOURCE_CAPABILITY_AUDIT_2026-09-14.md`; repository reconciliation context remains in `FRL_REPOSITORY_RECONCILIATION_2026-09-13.md`.

## Current platform state

FRL is a governed football research and modelling environment. The active frontend is **Next.js + React**, with **FastAPI** as the frontend-facing API. Python remains authoritative for source routing, identity, temporal semantics, provenance, analytical definitions and modelling. Streamlit is legacy/reference only.

Standing rules remain unchanged:

- canonical fixture/team/player identity, never source-ID coincidence;
- preserved source-native evidence with provenance;
- temporal/as-of reconstruction;
- explicit missing/partial/unresolved/unavailable states rather than silent zero or fallback behaviour;
- governed source routing and explicit derivation;
- reproducible materialisation from pinned evidence;
- shared analytical services so product surfaces do not invent separate definitions or populations.

The durable research North Star remains `FRL_MASTER_PROMPT.md`. The durable product architecture remains `FRL_PRODUCT_NORTH_STAR_AND_EXPERIENCE_ARCHITECTURE_V1.md`.

## Repository / branch state

Stable `main` remains at:

`0626878838b0734b7df8d79f966e814db75a61ed`

The current integration/reference base `design/analyst-workspace-v1` has advanced beyond that stable-main commit.

The active product/reference work is on:

`design/bet-builder-reference-v1`

Draft PR: **#53 — UI: premium FRL shell, Matchday builder and Fixtures reference design**.

At the start of the 13 September reconciliation, that branch was at `ce8fa1493553923306cd0011c6146f821101b66e`, 79 commits ahead of its merge base and 4 commits behind the then-current `design/analyst-workspace-v1` head. Documentation reconciliation commits follow that code head.

This branch is therefore **active experimental/product work, not a validated integration candidate**.

Important boundary: repository state described here is the tracked remote state. Daniel's live local Windows working tree may contain newer uncommitted work and must be inspected before merge/rebase/destructive operations.

## Active product phase

FRL has moved beyond the earlier source-industrialisation checkpoint into a substantial product/reference-design phase over the governed evidence layer.

The active branch currently includes:

- a two-level top navigation shell for the reference experience;
- a premium Fixtures experience and fixture-result workspace;
- a Matchday Bet Builder reference route;
- Team Profile / Team Overview reference work;
- club crest and stadium imagery support;
- a governed club-profile reference registry plus visual overrides;
- supporting fixture-evidence, player-performance and runtime/API changes;
- regression/registry tests for several of the added evidence paths.

The branch is not frontend-only. It contains supporting backend/research-access changes and must be reviewed and validated accordingly.

## Current visual direction

The intended FRL visual language is now **dark, premium, editorial and football-first**.

Current direction:

- near-black / charcoal structural surfaces;
- warm ivory / cream primary text;
- muted greys for secondary hierarchy;
- restrained coral/orange as the main brand/action emphasis;
- green/olive used semantically or as a supporting signal rather than as default decoration;
- no lime-green visual language;
- typography, spacing, thin rules and composition should carry more of the design than dashboard chrome.

The older warm parchment root tokens still exist in parts of the current CSS and some surfaces remain mid-migration. They are **implementation debt, not current design authority for new work**. See `UI_DESIGN_SYSTEM.md` and `FRL_LUXURY_DESIGN_CONSTITUTION.md`.

## Preserved source capability — validated foundation

The preserved PulseLive archive contains **3,800 Premier League fixture snapshots** across 2016/17–2025/26.

Master preserved source universe:

```text
553 MASTER SNAPSHOTTED RAW SOURCE PATHS
├── 181 capture / provenance paths
└── 372 football / match paths
    ├── 249 team-match statistical paths
    └── 123 other football / match paths
```

The validated team-match milestone remains:

```text
249 TEAM-MATCH STATISTICAL PATHS
├── 176 canonical/governed + generic access verified
├──   8 governed retained source fields
├──   6 governed restricted source fields
└──  59 raw-only source representations with governed preserved-snapshot route
```

The Player-Match source universe remains exhaustively accounted:

```text
86 PLAYER-MATCH SOURCE FIELDS
├── 81 exposed for generic research access
├──  4 retained metadata/source-context fields
└──  1 restricted duplicate CSV column
```

Standing missingness rule:

> **A source blank is missing by default. Structural zero requires specific evidence for that concept, representation and period.**

## Fixture event and tactical context

The established `fixture_context_research.py` checkpoint remains valid historical evidence:

- event route: 3,800 PASS / 0 FAIL;
- tactical-context route: 3,800 PASS / 0 FAIL;
- 50,182 normalised events;
- 145,637 lineup-player rows;
- formation context across 7,600/7,600 team-sides;
- 7,728 manager rows.

Unresolved identities remain explicit and are never guessed.

## 2026/27 living-season evidence

The latest formally documented integration checkpoint remains based on pinned upstream evidence from `imadeddine-belkat/Premier-League-Stats`.

The last **formally validated rich Player capability checkpoint** remains:

- 387 participating players with minutes greater than zero;
- 79/83 Player product capabilities runtime-supported through GW1–3;
- unavailable quartet: `ball_carries`, `progressive_carries`, `progressive_carry_distance`, `total_progression`.

Later local/current-season work may be newer, but it must be revalidated before replacing these standing capability claims.

## Player Profile Player-Season promotion

The midfielder Player Profile now uses source-native **Forward passing** in place of the intermittently observed Carrying axis for every season template.

The first governed Player-Season Product projection is:

- runtime module: `player_season_source_projection.py`;
- materialised evidence: `data/player_season_source_stats_v1.csv`;
- provenance: `data/player_season_source_stats_v1.metadata.json`;
- native source field: Player-Season `forwardPasses`;
- upstream release: `115d889df4e2efab5e7c1d8ca0f3ca86ecfd2ae6` (9 September 2026);
- preserved coverage: 6,639 unique player-season source identities from 2016-17 through 2026-27;
- missingness: source blanks and unresolved identity relationships remain unavailable, never zero;
- comparison: `forward_passes_per_90` against the qualified same-season, same-position population.

For 2026-27, all 108 midfielders meeting the Profile's 90-minute threshold have an observed forward-pass value. Ødegaard's Profile uses 45 source forward passes over 221 governed Profile minutes (18.3258 per 90), restoring a complete six-dimension comparison. Historical populations may remain partial where the existing verified FPL-element identity route does not resolve; no name-based runtime join was added.

Progressive carries remain preserved as a separate metric where the Player-Match representation exists. They are not treated as take-ons, forward passes or structural zero.

See `FRL_PLAYER_PROFILE_SOURCE_CAPABILITY_AUDIT_2026-09-14.md` for coverage, identity and spatial-source conclusions.

## Team State and forecasting

`Team State V1` remains available as a pre-fixture research object with recent-5, recent-10, season-to-date and prior-season windows. Historical source-publication-time equivalence remains explicitly unproven.

Adaptive Dixon-Coles V1 remains the frozen **experimental forecasting control** from the earlier controlled evaluation. It improved the common-population holdout metrics over Poisson V1, including log loss, Brier score and accuracy, but it is **not a trusted production model and no betting-market edge is claimed**.

The earlier control status remains:

`CONTROL_FREEZE_SUPPORTED_FOR_NEXT_EXPERIMENT`

## Head-to-Head / Matchday / BetBuilder evidence

The governed Head-to-Head and BetBuilder work remains part of the active product programme.

The key interpretation rule is unchanged:

> **`evidence_index` is descriptive evidence synthesis, not a calibrated betting probability.**

Matchday/Fixture Intelligence now has a broader product surface on the reference branch, including richer fixture presentation and Bet Builder experimentation. Football evidence, model output, market price and staking/strategy must remain distinct layers.

## Club/profile reference evidence

The active branch adds a governed club-profile reference registry and visual overrides, plus club crest and stadium-image assets. These are product/reference inputs and must preserve provenance/rights metadata where applicable.

They do not replace canonical club identity. Canonical/season-local/persistent identity rules still govern joins and deep links.

## Validation status

The pre-reconciliation active branch head `ce8fa1493553923306cd0011c6146f821101b66e` had **no GitHub Actions workflow run attached**.

Therefore the current reference branch must not be described as fully validated.

Before integration, current validation should include:

- base-branch reconciliation/conflict review;
- targeted Python/regression tests for changed evidence/API seams;
- club-profile/reference-data validation;
- Next.js `npm run typecheck`;
- Next.js `npm run build`;
- `project-health.ps1` where canonical/query/data behaviour is implicated and the required local source environment is available;
- `python scripts/check_documentation_sync.py --base-ref <appropriate-base>`;
- explicit API compatibility review, especially around the large `api/frl_api.py` branch diff.

Dated historical pass counts remain checkpoint evidence only.

## Immediate objective

> **Reconcile and validate the active product/reference branch so FRL can continue product development from a trustworthy current state rather than from stale documentation or an unverified design prototype.**

Immediate sequence:

1. keep living documentation aligned with the 13 September reconciliation;
2. reconcile `design/bet-builder-reference-v1` with the newer base-branch commits without destroying local/uncommitted work;
3. establish the live local working-tree state before merge/rebase;
4. run current backend/frontend/documentation validation;
5. resolve API/backend regressions and visual-token migration debt;
6. then continue Fixture Intelligence / Matchday, Team and Player analytical profiles, Rankings/Compare and Research Explorer from the governed evidence layer;
7. extend the governed Player-Season promotion pattern to other source-present variables only after field-specific semantic, identity, missingness and comparability review;
8. run the pre-registered Adaptive DC + Team State experiment without allowing model work to displace the broader research/product programme.

## Non-negotiables

- Never manufacture semantic equivalence from field-name similarity.
- Never convert source blanks to zero without concept-specific audited approval.
- Never collapse raw source path → source field → canonical variable into one layer.
- Never discard a legitimate variable solely because coverage begins later than 2016/17.
- Never force event/tactical objects through a scalar-variable interface merely for uniformity.
- Never let product surfaces invent independent definitions of governed football concepts.
- Never present descriptive BetBuilder evidence as a calibrated probability or guaranteed betting return.
- Never treat an experimental branch or uncommitted local work as stable integrated state without explicit validation and integration evidence.
