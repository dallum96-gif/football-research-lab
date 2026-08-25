# FRL Protected Systems

This document identifies established FRL infrastructure that must not be casually
recreated, replaced, weakened or bypassed.

Before implementing a new mechanism, determine whether an existing protected
system already provides the required capability.

## Canonical variable universe

**Status:** ESTABLISHED

The authoritative canonical variable universe contains **1,414 variables**.

This is distinct from the **447 retained source-field universe**.

**Rule:** Never regenerate or replace the canonical 1,414-variable universe from the
447 source-field inventory without first proving that the authoritative canonical
mapping is genuinely unavailable.

## Source-field universe

**Status:** ESTABLISHED

The retained source-field layer currently contains **447 distinct source fields**.

Its purpose is source-level inventory and coverage accounting.

It is not a substitute for the canonical variable universe.

## Identity architecture

**Status:** ESTABLISHED

Protected artefacts:

- FRL_DEFAULT_IDENTITY_SCHEMA_V1.md
- FRL_IDENTITY_RELATIONSHIP_CONTRACT_V1.md
- verified player identity registries and bridges
- season-aware team identity
- canonical fixture identity

Never create cross-source identity merely because a join produces a convenient result.

## Variable/entity attachment architecture

**Status:** ESTABLISHED**

Natural-grain attachment is authoritative.

Do not duplicate every variable onto Fixture, Team and Player entities simply for
GUI convenience.

## Generic research/query layer

**Status:** ESTABLISHED**

Existing generic research-field and source-family mechanisms must be reused before
creating bespoke extraction paths.

Relevant established mechanisms include:

- esearch_field_query.py
- source_family_adapters.py
- source_field_registry.py
- source_field_catalog.py
- player_match_stats.py

## Universal Variable Resolver

**Status:** ACTIVE IMPLEMENTATION**

The resolver is the standard consumer seam between canonical variables and
authorised consumers.

Do not create page-specific variable retrieval mechanisms when the resolver and
existing research/query layer can be extended instead.

## Temporal integrity

**Status:** ESTABLISHED PRINCIPLE**

Historical state must remain reconstructable.

Do not backfill missing historical fields from later seasons.

Do not convert missing evidence into zero.

Historical state must remain distinguishable from historical information availability.

## Provenance

**Status:** ESTABLISHED PRINCIPLE**

Source field, source family, identity basis, temporal semantics and derivation
information must remain available where relevant.

## Research/query consumers

**Status:** ESTABLISHED**

Research services must remain upstream of GUI presentation.

GUI components must not become independent sources of analytical truth.

## Frontend architecture

**Status:** ACTIVE MIGRATION**

The frontend is a consumer of trusted research/analytical outputs.

Do not recreate analytical logic inside pages or components.

## Protected behaviour

Do not casually remove or weaken:

- fail-closed identity behaviour;
- provenance;
- temporal safeguards;
- canonical relationship semantics;
- source-family adapter reuse;
- research/query equivalence;
- regression tests;
- established validation gates.

## General rule

> Recover existing infrastructure before inventing new infrastructure.
> Extend established seams before creating parallel systems.
> Preserve authoritative evidence before deleting or replacing it.
