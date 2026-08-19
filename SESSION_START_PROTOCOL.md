# Football Research Laboratory — Mandatory Session Start Protocol

This protocol is mandatory for any new coding/research session working on the Football Research Laboratory.

## Before changing anything

1. Treat `dallum96-gif/football-research-lab` as the GitHub source of truth for tracked project code and documentation.
2. Read `PROJECT_ORIENTATION.md`, `CURRENT_WORK.md`, `DATA_CONSTRUCTION.md`, `RISK_STRATEGY_FRAMEWORK.md`, `NON_DESTRUCTION_ASSURANCE.md`, `UI_DESIGN_SYSTEM.md`, `FRL_DATA_HIERARCHY_RELATIONSHIP_CONTRACT.md`, `FRL_DATA_PLATFORM_ARCHITECTURE_V1.md`, `FRL_RELATIONSHIP_INTEGRITY_CONTRACT.md`, `FRL_DATA_ECOSYSTEM_DISCOVERY_CONTRACT.md`, and `FRL_SOURCE_BOUNDARY_CONTRACT.md` before substantive work.
3. Establish the current branch and repository state and distinguish committed work from local/untracked experiments.
4. Compare the active branch with `main` before substantive work. Record the merge-base and whether the branch is ahead, behind or diverged.
5. If the active branch is behind `main`, inspect the main-only commits before creating new work.
6. If the active branch is ahead of `main` by substantial work, do not casually rebase, force-push or merge it. First audit what the commits represent and decide which history is intended to become trusted project state.
7. **Never write development or experimental work directly to `main`.** When using GitHub APIs or connectors that have an optional branch parameter, always pass the intended development branch explicitly. Never rely on a default branch when making a development write.
8. Before any destructive ref movement, create a named safety branch pointing to the current tip and record why the ref is being moved.
9. Inspect the current working application and relevant archived/backup implementation before replacing an established capability.
10. If a capability or classification is not obvious in GitHub, inspect the local source tree and trace the mechanism from source → retrieval/transformation → aggregation/classification → existing consumer.
11. Do not infer that a capability is absent merely because it cannot be found by an intuitive filename, metric name, or GitHub search.
12. Preserve existing retrieval, identity and classification mechanisms wherever possible. Reuse the established seam rather than creating a parallel mechanism.
13. **Do not infer relationship semantics from column names or numeric coincidence.** Before designing joins, inspect the relevant relationship contract and actual consumer code and determine whether each identifier is source-local, season-local, persistent/canonical, or derived context.

## Foundational-decision memory rule

The Master Prompt is a **compressed recovery protocol**, not the authoritative storage location for project architecture.

Whenever a decision becomes **fundamentally important to the long-term Laboratory**, do both of the following:

1. **Commit the authoritative detail to the repository** in the most appropriate governing document, contract, architecture record or data/research documentation.
2. **Update the Master Prompt / session-start instructions** so future sessions know that the new decision exists and exactly which repository document must be read to recover it.

Examples of decisions that should normally be promoted into project memory include:

- data architecture or storage boundaries;
- canonical entity/relationship contracts;
- branch/repository safety rules;
- provenance or temporal-integrity rules;
- ingestion/build contracts;
- major GUI/navigation architecture;
- research/model governance;
- reproducibility or validation requirements;
- source-acquisition and source-boundary rules.

Do not rely on conversation history to preserve such decisions. The repository is the durable project memory; the Master Prompt should point into that memory.

## Full data-ecosystem discovery rule

`FRL_DATA_ECOSYSTEM_DISCOVERY_CONTRACT.md` is authoritative for discovery completeness.

**Failure to find a field, metric, classification or capability in one repository location is never sufficient evidence that the FRL does not have it.**

Before concluding that information is absent, inspect the approved source ecosystem in full, including where applicable:

- current working application and query layer;
- archived, backup and previous implementations;
- all relevant GitHub-tracked datasets and directory trees;
- the approved upstream GitHub source repository and its source directories;
- the upstream feeds used by that repository;
- partitioned datasets such as `by_position`;
- identity registries and crosswalks;
- merged and derived datasets;
- neighbouring fields that may encode the concept under another name or grain;
- source documentation and provenance notes.

Do not search only for the expected column name.

The audit should establish:

```text
source family
      ↓
dataset / file / endpoint
      ↓
grain
      ↓
relevant fields
      ↓
source identifiers
      ↓
coverage
      ↓
transformation / derivation
      ↓
existing consumer
      ↓
FRL suitability
```

A capability may exist at a different grain, under another field name, inside a partitioned dataset, in an upstream source, or as a documented derived quantity.

If the approved ecosystem audit genuinely finds no defensible source or derivation, record that conclusion. Do **not** substitute another football-data provider while the current source-boundary rule remains active.

## Hard upstream source boundary

`FRL_SOURCE_BOUNDARY_CONTRACT.md` is a mandatory source-governance rule.

Until the FRL expands beyond **2008-09** or adds another **league/competition**, all football data used by the FRL must come exclusively from:

`imadeddine-belkat/Premier-League-Stats`

and the upstream feeds used by that repository itself.

The operating pattern is to take the upstream repository's CSV/source evidence and write or copy controlled source artefacts into the FRL repository before validation, canonicalisation or derivation.

Do not introduce Transfermarkt, StatsBomb, another GitHub football dataset, another API, a third-party injury dataset, or any other independent football-data provider into the FRL during this scope period merely because it appears to fill a data gap.

External sources may be discussed conceptually, but they are not approved FRL evidence until the expansion trigger occurs and a formal source-acquisition decision is made.

## Source-diversity / multi-league rule

The FRL must be designed for future leagues and competitions whose sources may use different field names, schemas, identifier systems, grains, units and metric definitions.

Do not assume that one provider schema is universal.

Use explicit source adapters / normalisation contracts:

```text
SOURCE A
   ↓
adapter A ─┐
            ├→ FRL canonical meaning
SOURCE B   │
   ↓       │
adapter B ─┤
            │
SOURCE C   ─┘
```

When the source-boundary expansion trigger eventually occurs, new source families must be assessed under `FRL_SOURCE_NORMALISATION_CONTRACT.md` and `FRL_SOURCE_BOUNDARY_CONTRACT.md` before promotion.

## Relationship-integrity rule

The FRL's canonical relationship semantics are governed by `FRL_RELATIONSHIP_INTEGRITY_CONTRACT.md`.

In particular:

```text
Fixture (season, fixture_id)
        ↓
season-local home/away team IDs
        ↓
team_seasons.local_team_id
        ↓
verified persistent team identity
```

and:

```text
season-specific player source
        ↓
season context derived from the source/load operation
        ↓
(season, fpl_element)
        ↓
verified player identity registry
        ↓
source player identity
```

Do not replace these with direct provider-to-provider joins merely because identifiers look numerically compatible.

A data-format migration is only successful when canonical relationships, identity semantics and fail-closed behaviour survive, not merely when rows and columns are preserved.

## Branch model

`main` is the **stable/trusted integration line**.

Feature, redesign, research and experiment branches contain work in progress. They may be substantially ahead of `main`, but that state must be intentional and documented.

The normal lifecycle is:

```text
main
  ↓
feature / redesign branch
  ↓
validation + review
  ↓
controlled integration
  ↓
main
```

A long-lived development branch is not a second `main`.

When a branch has become the effective current project state, do not silently promote it by moving `main`. Instead, perform an explicit integration/release decision after the appropriate validation gates have passed.

## Mandatory validation gate

The project's **26/26 research tests are an imperative regression baseline**. They are not optional and must be run before a change is considered safe.

The project also has a separate PowerShell health gate:

```powershell
.\project-health.ps1
```

The health gate is distinct from the 26/26 research-test baseline.

### Interpretation of the health gate

- `GREEN LIGHT - PROJECT HEALTH CHECK PASSED` = pass.
- `GREEN LIGHT - PASSED WITH WARNINGS` = **also a pass**, provided the warnings are understood and are consistent with documented/known project states.
- `RED LIGHT - PROJECT HEALTH CHECK FAILED` = fail; do not treat the change as safe until the failure is understood and resolved or explicitly accepted as an existing baseline condition.

The current documented warning is the known 2019–20 Manchester City v Arsenal fixture with missing score data. The health gate intentionally warns about this rather than inventing a result.

### Research-test baseline

The current research validation contract is:

- Core Query Lab: 14/14
- Player Research V0.1: 6/6
- Player Research V0.2: 6/6
- Total: **26/26**

If `pytest` is unavailable, do **not** install a new testing framework merely to satisfy the session. Inspect the repository's existing test scripts and health-gate mechanism and use the project's established validation path.

## Non-destruction rule

For every change:

```text
Understand existing behaviour
        ↓
Identify exact change surface
        ↓
Inspect source + consumer + classification
        ↓
Predict failure modes
        ↓
Make the smallest change possible
        ↓
Run the mandatory validation gate
        ↓
Inspect the application/result
        ↓
Only then treat the change as safe
```

A UI-only request must not silently change the trusted query/data layer. A source-backed metric must not be reimplemented merely because its existing retrieval path is not immediately obvious.

## Design principle

The Laboratory should balance:

> **serious enough to trust, fun enough to explore.**

The current visual language treats coral/red as a first-class brand accent alongside green, not merely as an error colour. New pages should preserve the same analytical clarity and playful finishing touches rather than inventing independent palettes.
