# Football Research Laboratory — Deployment & Access Contract V1

**Status:** Foundational deployment/access contract
**Date:** 20 August 2026
**Scope:** Next.js frontend migration and future shared/public access

## 1. Deployment principle

The FRL is **private-first, public-ready**.

The system should support three deployment states without requiring a new application architecture between them:

```text
LOCAL
  ↓
PRIVATE SHARED
  ↓
PUBLIC
```

### Local

Development and research work performed by the owner on the local machine.

### Private shared

The intended near-term shared state: the owner plus a small invited group (currently approximately three additional users).

### Public

A future state in which selected or all approved FRL functionality is publicly accessible.

Moving from private shared to public should primarily be an access, deployment and governance decision rather than a frontend rewrite.

## 2. Stable shareable URLs

Canonical football entities and substantive research objects should have stable, shareable URLs where appropriate.

Illustrative forms include:

```text
/fixtures/{season}/{fixture_id}
/teams/{persistent_team_identity}
/players/{canonical_player_identity}
/research/{research_object_id}
/models/{model_or_experiment_id}
```

The exact route structure must follow the canonical identity contracts and must never replace contextual identity with an ambiguous display label or source-local numeric ID.

A shared URL should open the same canonical research object/context for every authorised user rather than depending on transient browser session state.

## 3. Access control

Private deployment must protect the application and API independently of the browser UI.

The frontend must not assume that hiding a navigation item makes a resource private.

FastAPI/API resources requiring access control must enforce it server-side.

Public release must be deliberate. A resource should become public only when its data, provenance, methodology, licensing/source-boundary requirements and intended presentation have been reviewed.

## 4. Public/private separation

The public FRL does not have to expose every internal research artefact.

The architecture should allow a distinction between:

```text
PRIVATE RESEARCH
- exploratory work
- draft experiments
- internal model development
- unreleased datasets/configuration

PUBLIC RESEARCH
- approved research results
- approved visualisations
- methodology/provenance
- selected canonical entity/fixture/team/player views
```

The same core application architecture should support both.

## 5. Canonical identity requirement

Shareable URLs, API payloads and frontend state must preserve FRL identity semantics exactly.

Fixture identity remains:

```text
(season, fixture_id)
```

Team routes must use the verified persistent longitudinal identity where a longitudinal club route is intended; season-local source IDs remain contextual source identifiers.

Player routes must use the verified canonical player identity; season-specific provider IDs remain source identities.

Player–Fixture and Team–Fixture resources must retain the appropriate season/context required by the relationship contracts.

A display name such as "Arsenal" or "Salah" is never itself a sufficient canonical key.

## 6. Research sharing

A shareable research URL should eventually allow users to move through a reproducible chain such as:

```text
shared research object
      ↓
Research Result
      ↓
visualisation / table / comparison
      ↓
methodology / uncertainty
      ↓
provenance / underlying evidence
```

Shared presentation must not silently recalculate the underlying research differently from the trusted research/query layer.

## 7. Same-tab navigation

Entity and workspace navigation should remain same-tab by default unless a future UX decision explicitly changes the contract.

Deep-linking must therefore complement, not replace, the FRL navigation model.

No migration step may introduce new-tab behaviour merely as a technical convenience.

## 8. Free/self-hosted principle

The deployment architecture must remain viable without a mandatory paid software platform.

The preferred stack remains:

- Next.js / React;
- Python / FastAPI;
- DuckDB;
- Parquet;
- Plotly / React visualisation tooling;
- standard web authentication/access-control mechanisms.

Hosted services may be introduced for convenience later, but no hosted vendor should become an unavoidable architectural dependency without explicit review.

## 9. Scale assumption

Near-term usage is intentionally small.

The architecture should be efficient for a handful of trusted users rather than prematurely engineered for public-scale traffic.

Public-scale performance and infrastructure should be addressed only when the FRL is actually approaching public release.

The requirement is **public-ready architecture**, not public-scale infrastructure today.

## 10. Validation requirements

Before moving from local to private shared:

- stable canonical routes must resolve correctly;
- API access control must work server-side;
- canonical fixture/team/player identities must remain unchanged;
- research results must preserve provenance and temporal semantics;
- same-tab navigation must remain intact;
- 26/26 regression tests must remain green where the change is presentation/deployment-only;
- project-health gates must remain acceptable.

Before moving from private shared to public:

- source/licensing and redistribution constraints must be reviewed;
- public/private data boundaries must be explicit;
- public research results must have appropriate provenance and methodology;
- authentication/authorisation assumptions must be removed or deliberately retained;
- public URLs must remain stable and canonical;
- privacy/security review must be completed.

## 11. Governing principle

> **Design the FRL so that private sharing and eventual public access are deployment states of the same trusted research platform, not separate products.**
