"""Relationship metadata for the FRL variable dictionary.

This module maps an observed source grain to the canonical entity/relationship
surface it may attach to. It does not perform identity resolution and never
promotes a source identity into a canonical identity.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RelationshipMetadata:
    canonical_attachment: str
    relationship_kind: str
    identity_contract: str
    source_identity_required: bool
    note: str


GRAIN_MAP: dict[str, RelationshipMetadata] = {
    "fixture": RelationshipMetadata(
        "fixture", "ENTITY", "canonical_fixture_to_source_match", True,
        "Attach only after canonical fixture identity and source-match bridge are verified."
    ),
    "match": RelationshipMetadata(
        "fixture", "ENTITY", "canonical_fixture_to_source_match", True,
        "Source match remains source-local until bridged to a canonical fixture."
    ),
    "team_fixture": RelationshipMetadata(
        "team_fixture", "OBSERVATION", "canonical_team_season_to_source_team", True,
        "Team-fixture observations require verified season-local team identity."
    ),
    "team_match": RelationshipMetadata(
        "team_fixture", "OBSERVATION", "canonical_team_season_to_source_team", True,
        "Team-match source statistics attach through the verified team-fixture relationship."
    ),
    "player_match": RelationshipMetadata(
        "player_fixture", "OBSERVATION", "player_identity_to_player_match_observations", True,
        "Player-match observations require verified player and fixture identity."
    ),
    "player-fixture": RelationshipMetadata(
        "player_fixture", "OBSERVATION", "player_identity_to_player_match_observations", True,
        "Player-fixture evidence is contextual observation, not identity proof."
    ),
    "player_season": RelationshipMetadata(
        "player_season", "ENTITY", "source_player_identity_to_player_season", True,
        "Player-season rows require season-aware source-player identity."
    ),
    "player": RelationshipMetadata(
        "player", "ENTITY", "source_player_identity_to_player_season", True,
        "Longitudinal player identity must be reconciled from source-local identities."
    ),
    "team": RelationshipMetadata(
        "team", "ENTITY", "canonical_team_season_to_source_team", True,
        "Team records require explicit season/team identity mapping where source-local IDs are used."
    ),
    "competition": RelationshipMetadata(
        "competition", "ENTITY", "", False,
        "Competition context is scoped by explicit competition/season mapping rather than player/team identity."
    ),
    "standings": RelationshipMetadata(
        "standings", "OBSERVATION", "canonical_team_season_to_source_team", True,
        "Standings rows attach to verified season-local team identity."
    ),
    "event": RelationshipMetadata(
        "event", "OBSERVATION", "canonical_fixture_to_source_match", True,
        "Events attach to a verified source match/canonical fixture and retain native event IDs."
    ),
    "source_field": RelationshipMetadata(
        "source_field", "SOURCE_AVAILABILITY", "source_field_to_season_availability", False,
        "Field availability is a source-schema property, not an entity identity."
    ),
}


def _normalise(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def relationship_for(resource: str, grain: str) -> RelationshipMetadata:
    key = _normalise(grain or resource)
    if key in GRAIN_MAP:
        return GRAIN_MAP[key]
    resource_key = _normalise(resource)
    if resource_key in GRAIN_MAP:
        return GRAIN_MAP[resource_key]
    return RelationshipMetadata(
        "UNMAPPED_REVIEW", "UNKNOWN", "", False,
        "No deterministic relationship contract mapping; manual review required."
    )
