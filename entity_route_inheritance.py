"""Explicit FRL variable-to-entity route inheritance rules.

This module turns the established source-family relationship contracts into a
small, reusable inheritance layer. It does not resolve identities, perform
joins, or promote canonical relationships.

A variable may inherit an entity route from its source grain/family only when
that family already has a documented relationship contract. The returned
status is deliberately evidence-neutral: actual identity verification remains
a separate concern.
"""
from __future__ import annotations

from dataclasses import dataclass

from variable_dictionary_relationships import relationship_for


@dataclass(frozen=True)
class EntityRoute:
    entity: str
    route_family: str
    relationship_contract: str
    route_kind: str
    evidence_required: tuple[str, ...]
    inherited_from: str


ENTITY_ROUTES: dict[str, tuple[EntityRoute, ...]] = {
    "team_match": (
        EntityRoute(
            "FIXTURE",
            "CANONICAL_FIXTURE_TO_SOURCE_MATCH",
            "canonical_fixture_to_source_match",
            "CONTEXT_INHERITANCE",
            (
                "canonical fixture exists",
                "season-local team identity is verified",
                "source match resolves uniquely",
                "home and away sides are consistent",
            ),
            "team_match -> fixture context",
        ),
        EntityRoute(
            "TEAM",
            "CANONICAL_TEAM_SEASON_TO_SOURCE_TEAM",
            "canonical_team_season_to_source_team",
            "OBSERVATION_INHERITANCE",
            (
                "season-local canonical team identity is verified",
                "source team identifier agrees with the verified seasonal mapping",
            ),
            "team_match -> team-season side",
        ),
    ),
    "player_match": (
        EntityRoute(
            "FIXTURE",
            "CANONICAL_FIXTURE_TO_SOURCE_MATCH",
            "canonical_fixture_to_source_match",
            "CONTEXT_INHERITANCE",
            (
                "canonical fixture exists",
                "season-local team identity is verified",
                "source match resolves uniquely",
                "home and away sides are consistent",
            ),
            "player_match -> fixture context",
        ),
        EntityRoute(
            "PLAYER",
            "PLAYER_IDENTITY_TO_PLAYER_MATCH",
            "player_identity_to_player_match_observations",
            "OBSERVATION_INHERITANCE",
            (
                "player identity is already verified",
                "fixture/source match is verified",
                "observation belongs to that player in that fixture",
            ),
            "player_match -> verified player identity",
        ),
    ),
    "player_season": (
        EntityRoute(
            "PLAYER",
            "SOURCE_PLAYER_TO_PLAYER_SEASON",
            "source_player_identity_to_player_season",
            "ENTITY_INHERITANCE",
            (
                "same source-player namespace is established",
                "season is known",
                "player ID resolves uniquely",
            ),
            "player_season -> source player identity",
        ),
    ),
    "player": (
        EntityRoute(
            "PLAYER",
            "PLAYER_IDENTITY",
            "source_player_identity_to_player_season",
            "ENTITY_INHERITANCE",
            (
                "source-local player identities are reconciled",
                "cross-season identity evidence is verified",
            ),
            "player -> reconciled player identity",
        ),
    ),
    "team": (
        EntityRoute(
            "TEAM",
            "CANONICAL_TEAM_SEASON_TO_SOURCE_TEAM",
            "canonical_team_season_to_source_team",
            "ENTITY_INHERITANCE",
            (
                "season-local canonical team identity is verified",
                "source team identifier is present",
                "source identifier agrees with the verified seasonal mapping",
            ),
            "team -> team-season identity",
        ),
    ),
    "squad": (
        EntityRoute(
            "TEAM",
            "CANONICAL_TEAM_SEASON_TO_SOURCE_TEAM",
            "canonical_team_season_to_source_team",
            "CONTEXT_INHERITANCE",
            (
                "season-local canonical team identity is verified",
                "source team identifier is present in the squad observation",
                "source identifier agrees with the verified seasonal mapping",
            ),
            "squad -> team-season context",
        ),
    ),
    "fixture": (
        EntityRoute(
            "FIXTURE",
            "CANONICAL_FIXTURE_TO_SOURCE_MATCH",
            "canonical_fixture_to_source_match",
            "ENTITY_INHERITANCE",
            (
                "canonical fixture exists",
                "season-local team identity is verified",
                "source match resolves uniquely",
                "home and away sides are consistent",
            ),
            "fixture -> source match",
        ),
    ),
    "match": (
        EntityRoute(
            "FIXTURE",
            "CANONICAL_FIXTURE_TO_SOURCE_MATCH",
            "canonical_fixture_to_source_match",
            "ENTITY_INHERITANCE",
            (
                "canonical fixture exists",
                "season-local team identity is verified",
                "source match resolves uniquely",
                "home and away sides are consistent",
            ),
            "match -> canonical fixture",
        ),
    ),
    "event": (
        EntityRoute(
            "FIXTURE",
            "CANONICAL_FIXTURE_TO_SOURCE_MATCH",
            "canonical_fixture_to_source_match",
            "OBSERVATION_INHERITANCE",
            (
                "verified source match/canonical fixture context exists",
                "native event ID is retained",
            ),
            "event -> fixture/match context",
        ),
    ),
}


def _normalise(value: str | None) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def routes_for_grain(grain: str | None) -> tuple[EntityRoute, ...]:
    """Return explicit routes for a source grain; empty means no inheritance rule."""
    return ENTITY_ROUTES.get(_normalise(grain), ())


def route_for_entity(grain: str | None, entity: str) -> EntityRoute | None:
    target = _normalise(entity).upper()
    for route in routes_for_grain(grain):
        if route.entity == target:
            return route
    return None


def relationship_contract_for(grain: str | None, entity: str) -> str | None:
    route = route_for_entity(grain, entity)
    if route is not None:
        return route.relationship_contract
    metadata = relationship_for("", _normalise(grain))
    return metadata.identity_contract or None
