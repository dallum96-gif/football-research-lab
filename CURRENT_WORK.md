# Current Work — Football Research Laboratory

**Last updated:** 26 August 2026

## Current platform state

The Universal Research Access backend is complete and has been promoted into `main`.

Backend closeout recorded in `FRL_BACKEND_CLOSEOUT_2026-08-26.md`:

- Universal Research Access: **9/9 implementation steps complete**
- Closeout suite: **30/30**
- Cross-domain acceptance: **27/27**
- Contract hardening: **17/17**
- Coverage / temporal / provenance gates: **passed**
- Broader backend validation: **passed**
- Project health: **passed**
- Core Query Lab: **passed**
- Player Research V0.2 gate: **passed**

This marks the governed research-access layer as ready for frontend consumption.

## Current architectural position

The frontend should consume governed research results through the universal research-access layer rather than reaching directly into source-specific storage mechanisms.

The durable conceptual flow is:

```text
SOURCE / VALIDATED DATA
        ↓
CANONICAL + HISTORICAL STATE
        ↓
UNIVERSAL RESEARCH ACCESS
        ↓
FRONTEND / VISUALISATION / FUTURE LLM INTERFACE
```

The underlying variable universe is deliberately richer than the UI. Preserve atomic source-backed facets and expose them through focused research experiences rather than turning the interface into a data dump.

## Current product phase

The immediate priority has shifted from backend construction to **frontend/productisation**.

The project is now focused on the **Next.js + React** application. Streamlit is legacy and should not be treated as the active frontend architecture.

The first major UI target is the **fixture/result experience**:

```text
Fixtures
    ↓
select fixture
    ↓
Fixture / Match Result workspace
```

The objective is to finish the established fixture/result design and apply it consistently across fixtures.

## Fixture/result UX direction

The fixture page should feel like a polished desktop-first **web application**, not a traditional football statistics website.

Desired interaction model:

- focused sections/tabs rather than one long information wall;
- easy movement between categories of match information;
- strong visual hierarchy;
- rich information available on demand;
- minimal unnecessary interface chrome.

The primary match view should immediately communicate:

- score and match identity;
- goals / key events;
- who played;
- basic match statistics.

Deeper match information can then be accessed through focused sections such as:

```text
MATCH | TIMELINE | LINEUPS | STATS | PLAYERS | CONTEXT
```

Exact labels and final navigation should follow the established UI design decisions in the active frontend work.

The visual target is informed by:

- Linear / Vercel for clean, premium software aesthetics;
- FotMob app for compact, category-based sports-app interaction;
- Football Manager / FBref / analytical football products for depth of information.

Do not reproduce any of these products literally. The FRL should develop its own visual language.

## Research direction after frontend milestone

Once the fixture experience is stable and usable, the next phase should increasingly exploit the universal research-access layer for real investigation:

- historical precedent and comparable situations;
- arbitrary derived conditions;
- statistical analysis;
- predictive modelling;
- probabilistic reasoning;
- model evaluation;
- eventual market/betting analysis where justified.

The system must preserve historical/as-of semantics so questions such as “who was top scorer on date X?” or “how many goals had team Y conceded by date X?” can be reconstructed from information available at that time.

## Research and commercial priorities

The FRL is intended to support both football understanding and predictive research. Betting is a downstream application, not the definition of the platform.

Commercial discovery is also an active strategic concern. The project should remain open to revenue opportunities both inside and outside FRL where evidence suggests a materially stronger probability of success.

Commercial hypotheses should be treated like research hypotheses: investigate demand, test cheaply, preserve evidence, and avoid committing substantial resources merely because an idea is exciting.

## Working method

For substantial workstreams, establish:

- objective;
- definition of done;
- necessary steps;
- current step;
- review point.

Separate **research mode** (explore, question, test, decide) from **build mode** (implement an established decision).

When new ideas appear, distinguish between:

- required for the current objective;
- important to the long-term architecture;
- worth recording and parking for later.

The highest-value next action is not necessarily code. It may be research, validation, product work, customer discovery, or deliberately deciding not to build something.

## Repository and state discipline

Treat `main` as the stable integration line and preserve branch/local experiments unless explicitly asked to clean them up.

Before substantive changes:

1. establish the current branch/state;
2. inspect the relevant code and documentation;
3. preserve trusted backend/query contracts unless the task genuinely requires changes;
4. make the smallest sensible change;
5. validate targeted behaviour and regression safety.

`FRL_BACKEND_CLOSEOUT_2026-08-26.md` is the authoritative closeout record for the completed Universal Research Access backend milestone.

`CURRENT_WORK.md` is the short-lived current checkpoint and should be updated when the project's phase or immediate objective materially changes.

## Active short-term product roadmap

The next several product sessions should use `FRL_SHORT_TERM_PRODUCT_ROADMAP.md` as the active near-term planning spine.

The current sequence is deliberately product-facing:

1. finish Fixture Workspace V1 with the rich historical evidence and repair the PulseLive → Player-Match identity join;
2. generate a structured FRL Variable Capability Inventory and a human-readable FRL Data Capability Brochure;
3. build Team Profile and Team Stats surfaces;
4. build Player Profile and Player Stats surfaces;
5. build League Table and League Stats surfaces;
6. productise the existing Poisson model in a Next.js Prediction Lab;
7. build a Head-to-Head / Match Research workspace that distinguishes descriptive patterns from predictive evidence;
8. extend the governed data pipeline to 2026/27;
9. preserve the architecture for later cross-league expansion described in `FUTURE_LEAGUE_COMBINE_PLAN.md`.

This roadmap is intentionally a short-term priority spine rather than a permanent architecture contract. The variable capability inventory should inform which statistics and research experiences are genuinely supported before Team, Player, League and model pages are populated.