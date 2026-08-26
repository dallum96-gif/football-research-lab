"""Explicit relationship contracts for the Football Research Laboratory.

These contracts describe *what a relationship means* and what evidence is
required before a downstream adapter may treat it as verified.  They do not
perform joins and they do not create identity records.

The important distinction is between:

- identity relationships: one source identity -> another source/FRL identity;
- observational relationships: statistics that belong to an already-resolved
  entity but may legitimately have no row (for example, a player with no
  league appearance);
- source availability: whether a field exists in a source/season at all.

No relationship may be inferred merely because two datasets contain a similar
name or because a downstream observation exists.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


RelationshipKind = Literal["IDENTITY", "OBSERVATION", "SOURCE_AVAILABILITY"]
EvidenceClass = Literal[
    "VERIFIED",
    "UNAVAILABLE",
    "UNRESOLVED",
    "AMBIGUOUS",
    "CONTRADICTORY",
]


@dataclass(frozen=True)
class RelationshipContract:
    name: str
    kind: RelationshipKind
    left_entity: str
    right_entity: str
    required_evidence: tuple[str, ...]
    forbidden_inference: tuple[str, ...]
    absent_means: str


RELATIONSHIP_CONTRACTS: tuple[RelationshipContract, ...] = (
    RelationshipContract(
        name="canonical_fixture_to_source_match",
        kind="IDENTITY",
        left_entity="canonical_fixture",
        right_entity="source_match",
        required_evidence=(
            "canonical fixture exists",
            "season-local team identity is verified",
            "source match resolves uniquely",
            "home and away sides are consistent",
        ),
        forbidden_inference=(
            "scoreline alone",
            "name-only matching",
            "fixture-order assumptions",
        ),
        absent_means="UNRESOLVED",
    ),
    RelationshipContract(
        name="canonical_team_season_to_source_team",
        kind="IDENTITY",
        left_entity="canonical_team_season",
        right_entity="source_team",
        required_evidence=(
            "season-local canonical team identity is verified",
            "source team identifier is present",
            "source identifier agrees with the verified seasonal mapping",
        ),
        forbidden_inference=(
            "current club name used as historical identity",
            "cross-season numeric ID assumed persistent",
            "name-only matching where competing candidates exist",
        ),
        absent_means="UNRESOLVED",
    ),
    RelationshipContract(
        name="fpl_player_to_frl_player_identity",
        kind="IDENTITY",
        left_entity="fpl_seasonal_player",
        right_entity="frl_player_identity",
        required_evidence=(
            "season is known",
            "FPL player identity is present",
            "verified seasonal team evidence is available, or an explicitly "
            "audited equivalent source bridge exists",
            "source player identity resolves uniquely",
        ),
        forbidden_inference=(
            "name-only matching",
            "FPL element treated as longitudinal without proof",
            "cross-season code continuity treated as proof by itself",
            "fuzzy name match used as canonical identity",
        ),
        absent_means="UNAVAILABLE",
    ),
    RelationshipContract(
        name="source_player_match_to_source_player_identity",
        kind="IDENTITY",
        left_entity="source_player_match",
        right_entity="source_player_identity",
        required_evidence=(
            "source player ID resolves deterministically",
            "fixture context is known",
        ),
        forbidden_inference=(
            "raw player name alone",
            "lineup order alone",
            "same-name assumption across teams",
        ),
        absent_means="UNRESOLVED",
    ),
    RelationshipContract(
        name="source_player_identity_to_player_season",
        kind="IDENTITY",
        left_entity="source_player_identity",
        right_entity="player_season_row",
        required_evidence=(
            "same source-player namespace is established",
            "season is known",
            "player ID resolves uniquely",
        ),
        forbidden_inference=(
            "row order",
            "name-only matching",
            "statistical similarity",
        ),
        absent_means="UNRESOLVED",
    ),
    RelationshipContract(
        name="player_identity_to_player_match_observations",
        kind="OBSERVATION",
        left_entity="frl_player_identity",
        right_entity="player_match_observation",
        required_evidence=(
            "player identity is already verified",
            "fixture/source match is verified",
            "observation belongs to that player in that fixture",
        ),
        forbidden_inference=(
            "absence of an observation treated as identity failure",
            "player registration treated as appearance",
        ),
        absent_means="UNAVAILABLE",
    ),
    RelationshipContract(
        name="source_field_to_season_availability",
        kind="SOURCE_AVAILABILITY",
        left_entity="source_field",
        right_entity="season_source_family",
        required_evidence=(
            "field is present in the source schema/data for the season",
        ),
        forbidden_inference=(
            "field absence treated as broken identity",
            "field absence in one season filled from another season",
        ),
        absent_means="UNAVAILABLE",
    ),
)


CONTRACT_BY_NAME = {contract.name: contract for contract in RELATIONSHIP_CONTRACTS}


def get_relationship_contract(name: str) -> RelationshipContract:
    try:
        return CONTRACT_BY_NAME[name]
    except KeyError as exc:
        raise KeyError(f"Unknown relationship contract: {name}") from exc


def classify_identity_status(
    *,
    source_context_available: bool,
    candidate_count: int,
    contradiction: bool = False,
) -> EvidenceClass:
    """Classify a relationship without ever promoting an uncertain join."""
    if contradiction:
        return "CONTRADICTORY"
    if not source_context_available:
        return "UNAVAILABLE"
    if candidate_count == 0:
        return "UNRESOLVED"
    if candidate_count == 1:
        return "VERIFIED"
    return "AMBIGUOUS"
