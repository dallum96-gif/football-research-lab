"""Pure attachment resolver for the frozen FRL variable/entity schema.

This module does not perform identity inference. It accepts source-native
observation context plus independently evaluated identity edges and returns a
stable attachment record. Unresolved edges remain unresolved without
invalidating other verified edges.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Mapping


VALID_STATUSES = {
    "VERIFIED",
    "REVIEW",
    "UNRESOLVED",
    "NOT_APPLICABLE",
}


@dataclass(frozen=True)
class AttachmentEdge:
    status: str
    identity_contract: str | None = None
    evidence_basis: str | None = None
    provenance_id: str | None = None
    entity_id: str | None = None

    def __post_init__(self) -> None:
        if self.status not in VALID_STATUSES:
            raise ValueError(f"Unknown attachment status: {self.status}")
        if self.status == "VERIFIED" and not self.entity_id:
            raise ValueError("VERIFIED attachment requires entity_id")


@dataclass(frozen=True)
class ObservationAttachment:
    observation_id: str
    variable_id: str
    season: str | None
    source_record_id: str | None
    source_player_id: str | None
    source_match_id: str | None
    source_team_id: str | None
    fixture: AttachmentEdge
    home_team: AttachmentEdge
    away_team: AttachmentEdge
    player: AttachmentEdge

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        return result


def _edge(value: Mapping[str, Any] | None) -> AttachmentEdge:
    if value is None:
        return AttachmentEdge(status="NOT_APPLICABLE")
    return AttachmentEdge(
        status=str(value.get("status", "UNRESOLVED")),
        identity_contract=value.get("identity_contract"),
        evidence_basis=value.get("evidence_basis"),
        provenance_id=value.get("provenance_id"),
        entity_id=(str(value["entity_id"]) if value.get("entity_id") is not None else None),
    )


def resolve_observation(
    source: Mapping[str, Any],
    *,
    fixture: Mapping[str, Any] | None = None,
    home_team: Mapping[str, Any] | None = None,
    away_team: Mapping[str, Any] | None = None,
    player: Mapping[str, Any] | None = None,
) -> ObservationAttachment:
    """Build an attachment record from independently verified identity edges.

    No edge is inferred from another edge. This is intentional: a verified
    fixture does not imply a verified player, and a verified source player does
    not imply a canonical FRL player.
    """
    return ObservationAttachment(
        observation_id=str(source.get("observation_id", "")),
        variable_id=str(source.get("variable_id", "")),
        season=(str(source["season"]) if source.get("season") is not None else None),
        source_record_id=(str(source["source_record_id"]) if source.get("source_record_id") is not None else None),
        source_player_id=(str(source["source_player_id"]) if source.get("source_player_id") is not None else None),
        source_match_id=(str(source["source_match_id"]) if source.get("source_match_id") is not None else None),
        source_team_id=(str(source["source_team_id"]) if source.get("source_team_id") is not None else None),
        fixture=_edge(fixture),
        home_team=_edge(home_team),
        away_team=_edge(away_team),
        player=_edge(player),
    )


def fully_attached(record: ObservationAttachment) -> bool:
    """Return True only when all applicable entity edges are verified."""
    return all(
        edge.status in {"VERIFIED", "NOT_APPLICABLE"}
        for edge in (
            record.fixture,
            record.home_team,
            record.away_team,
            record.player,
        )
    )


def edge_statuses(record: ObservationAttachment) -> dict[str, str]:
    return {
        "fixture": record.fixture.status,
        "home_team": record.home_team.status,
        "away_team": record.away_team.status,
        "player": record.player.status,
    }
