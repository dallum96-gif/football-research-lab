# Football Research Laboratory — Future Manager Evidence Route

**Status:** Reserved future architecture
**Date:** 19 August 2026

## Purpose

The FRL does not currently have an approved manager-data source within its active source boundary. Manager data is therefore deliberately **not populated or inferred** in the current fixture/player-match build.

The architecture should nevertheless preserve a clean route for adding manager evidence later without redesigning the fixture relationship model.

## Current source boundary

Until the FRL expands beyond 2008-09 or adds another league/competition, football evidence may only come from:

`imadeddine-belkat/Premier-League-Stats`

and the upstream feeds used by that repository itself.

No external manager provider may be introduced during the current scope period merely to fill the gap.

## Intended future model

Manager evidence should eventually attach to the canonical fixture through the existing fixture identity:

```text
Fixture
(season, fixture_id)
      ↓
Team–Fixture
(persistent_team_code)
      ↓
Manager evidence
      ↓
manager source identity
manager name
role
start/end or effective dates
source provenance
```

The desired analytical question is:

> Who was the manager of this team at this fixture?

This requires fixture-effective temporal semantics. A season-level staff association is not sufficient if a team changed manager during the season.

## Required future behaviour

When an approved source eventually exposes manager evidence:

1. preserve the source-native manager identifier and name;
2. resolve the team through the existing FRL team identity graph;
3. attach the manager state to `(season, fixture_id, persistent_team_code)`;
4. preserve appointment/termination or other effective-date evidence where supplied;
5. distinguish source fact from any derived fixture-effective classification;
6. retain provenance and source coverage limitations;
7. fail closed where manager identity or effective date cannot be established.

## Compatibility requirement

The future manager layer must be additive. It must not:

- replace the canonical fixture identity;
- alter the player-match identity graph;
- create a second fixture table;
- infer a manager solely from club name or season;
- rewrite historical fixture evidence.

The absence of current manager data must remain an explicit availability state rather than a fabricated value.

## Relationship to future GUI work

The future fixture landing page may eventually display home and away managers alongside the lineup and player-match evidence. The backend manager evidence should be implemented independently of that presentation layer.
