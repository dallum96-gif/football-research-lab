# FRL contributor instructions

These rules apply to all work in this repository. They summarise operating constraints; the linked contracts remain authoritative.

## Re-enter the project before changing it

- Treat stable `main` and `dallum96-gif/football-research-lab` as the authoritative integrated state. Do not assume another branch, worktree, backup, or archived implementation is integrated.
- At the start of substantive work, check the current branch, working tree, remotes, upstream, and ahead/behind state; fetch before relying on remote state.
- Read `FRL_MASTER_PROMPT.md`, `PROJECT_ORIENTATION.md`, and `CURRENT_WORK.md`. Inspect the relevant implementation and contracts before proposing a change. Historical status documents may be stale; reconcile them with current `main` and newer authoritative documents.
- Do not ask the user to reconstruct information that can be recovered from the repository, working implementation, relevant history, or known upstream source workspace.
- State the objective, definition of done, change surface, validation plan, and whether the task is research/audit work or implementation work. Do not silently broaden scope.

## Preserve the established architecture

- FRL is a provenance-aware, historical football research environment, not one dashboard, metric, or betting model. Research and explanation precede downstream modelling, market, and betting decisions.
- Preserve the conceptual flow: source evidence -> validated/canonical data -> historical state -> Universal Research Access -> API -> frontend/visualisation/future LLM consumers.
- Next.js + React under `web/` is the active frontend architecture. Python remains authoritative for query, identity, temporal, provenance, statistical, and modelling semantics; FastAPI is the frontend-facing boundary. Streamlit is legacy unless a task explicitly concerns it.
- Use established seams such as `query_lab.py`, `query_api.py`, `research_access.py`, the variable/relationship resolvers, and the FastAPI routes. Never add browser-side reads of source files or source-specific storage paths, and do not duplicate research/business logic in TypeScript.
- Universal Research Access is the governed capability-discovery, validation, coverage, and query layer. Extend or compose it through existing adapters/contracts rather than creating an ad hoc source-specific frontend path.
- A source field existing does not prove that a research metric exists; a research metric existing does not prove that it belongs in the primary UI. Trace source -> identity/relationship -> transformation -> governed result -> consumer.
- When a capability is not found, inspect the working consumer, relevant archived/backup implementations, repository datasets, identity registries, and the known upstream source workspace before declaring it absent or designing a replacement. Follow `FRL_DATA_ECOSYSTEM_DISCOVERY_CONTRACT.md`.

## Fixture/result seams

- Fixture identity is always `(season, fixture_id)`. Preserve canonical deep links and do not create a second fixture universe.
- The Fixture Explorer lives at `web/src/components/FixtureExplorer.tsx` and consumes typed fixture Research Results through FastAPI. The result workspace lives at `web/src/app/fixtures/[season]/[fixtureId]/`.
- Canonical fixture detail/statistics flow through `query_api.fixture_detail()` and `query_lab.py`. Event, lineup, formation, manager, and participation evidence flows through `fixture_evidence.py` -> `fixture_research_access.py`, using verified source-match relationships and Universal Research Access where defined.
- Preserve the known 2019-20 Manchester City v Arsenal correction (`season=2019-20`, `fixture_id=275`) and its additive provenance. Do not “fix” it by overwriting evidence or weakening the relationship contract.
- Missing optional statistics, events, formation, managers, placement, participation, or other evidence are valid states. Render or return them explicitly as unavailable/partial/known-exception; never fabricate values.

## Identity, relationship, temporal, and provenance rules

- Read `DATA_CONSTRUCTION.md`, `FRL_DEFAULT_IDENTITY_SCHEMA_V1.md`, `FRL_IDENTITY_RELATIONSHIP_CONTRACT_V1.md`, and `PLAYER_MATCH_SOURCE_BRIDGE.md` before changing identity, joins, fixture enrichment, or player-match access.
- Source identifiers are evidence, not canonical identifiers. Never join bare numeric IDs across source families or use display-name/fuzzy matching as a substitute for an approved bridge.
- Keep season-local team identity separate from persistent club identity. Keep FPL seasonal element, Player-Match source ID/`pl_code`, Player-Season ID, Research identity, canonical player identity, and source-native player identity distinct.
- Record the identity route and evidence basis. Prefer verified canonical bridges, then approved longitudinal bridges, then explicit source-native bridges. Fail closed as unresolved/review when evidence is insufficient or conflicting.
- Player identity, team membership, and fixture identity are separate relationships. Multi-club seasons change the temporal team relationship, not necessarily the player identity.
- Preserve event time, information-availability time, and ingestion time as distinct concepts. Historical/as-of results may use only information available at the relevant cutoff; do not infer availability from final source evidence.
- Preserve source lineage, transformation/version metadata, limitations, coverage, and correction history. Never convert missing evidence into zero without an explicit semantic contract.

## Source acquisition and rights guardrails

- Read `FRL_SOURCE_RIGHTS_REGISTER.md` before adding, extending, or operationalising a new external data-acquisition path.
- Do not treat a public endpoint, unauthenticated API, public GitHub repository, or downloadable file as proof that bulk reuse, redistribution, or commercial use is permitted.
- Prefer explicitly open/licensed downloadable data, official APIs with clearly permitted automated use, and providers with explicit research/reuse terms.
- Do not make recurring or large-scale direct API extraction a foundational FRL dependency unless the intended automated use is expressly permitted or has been reviewed and accepted for the intended use case.
- Treat ambiguous sources case by case. Record the acquisition channel, original provider, applicable repository/code licence, underlying-data terms, intended FRL use, attribution requirements, redistribution restrictions, and commercial-use status where known.
- Preserve already-acquired source evidence and its provenance, but do not infer public/commercial redistribution rights merely because FRL can technically access or store it.

## Change and repository safety

- Prefer the smallest sensible, reversible change at an established seam. Preserve trusted query/data contracts for presentation-only work.
- Follow `NON_DESTRUCTION_ASSURANCE.md` and `RISK_STRATEGY_FRAMEWORK.md`. Establish the baseline, predict failure modes, validate the changed behaviour, and check relevant regressions.
- Do not modify canonical data, schemas, identity registries, generated research artefacts, or architecture merely to make a UI task easier unless the task explicitly authorises that change and the governing contracts are satisfied.
- Preserve unrelated tracked, untracked, generated, experimental, backup, and worktree content. Do not use `git reset --hard`, `git clean`, force push, history rewriting, branch deletion, stash dropping, broad staging, or destructive data/schema operations.
- Surface uncertainty, conflicts, and incomplete coverage. Do not guess or describe “not found” as “absent.”

## Validation and design references

- Choose checks proportionate to the change: targeted tests first, then relevant research-access/identity/query gates, Next.js `typecheck`/`build` for frontend work, and `project-health.ps1` when canonical/query/data behaviour may be affected.
- Validation counts in old documents are historical checkpoints. Use `CURRENT_WORK.md`, current tests, and actual command output; never claim a gate passed unless it was run in the current work.
- For frontend work, follow `FRL_MASTER_FRONTEND_MIGRATION_PLAN_V2.md`, `FRL_RESEARCH_RESULT_CONTRACT_V1.md`, `FRL_FIXTURE_EVIDENCE_ARCHITECTURE_V1.md`, and `UI_DESIGN_SYSTEM.md`. Preserve the current warm-light FRL tokens and restrained, desktop-first, editorial product language unless a newer explicit design decision supersedes them.
- `FRL_BACKEND_CLOSEOUT_2026-08-26.md` records the completed Universal Research Access milestone. Do not reopen or replace that architecture without new evidence and explicit task scope.
