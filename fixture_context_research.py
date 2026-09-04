"""Governed source-native fixture event and tactical-context research seam.

This module connects preserved PulseLive snapshots to FRL's verified fixture
relationship and existing PulseLive->Player-Match identity bridge.  It does not
promote source event fields into canonical analytical variables, infer missing
player identities, or derive tactical meaning beyond what the source explicitly
supplies.
"""
from __future__ import annotations

from typing import Any

from pulselive_fixture_evidence import (
    load_snapshot,
    normalise_events,
    normalise_lineups,
    resource_meta,
    resource_payload,
)
from source_family_adapters import (
    canonical_fixture,
    resolve_pulselive_player_identity,
    resolve_source_match,
)


class FixtureContextUnavailableError(ValueError):
    """Raised when governed fixture context cannot be retrieved."""


def _fixture_route(season: str, fixture_id: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str]:
    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise FixtureContextUnavailableError(f"Canonical fixture not found: {season}/{fixture_id}")

    try:
        resolved = resolve_source_match(season, fixture_id)
    except ValueError as exc:
        raise FixtureContextUnavailableError(str(exc)) from exc

    source_match_id = str(resolved["source_match_id"])
    snapshot, snapshot_path = load_snapshot(source_match_id)
    if snapshot is None or snapshot_path is None:
        raise FixtureContextUnavailableError(
            f"Preserved PulseLive snapshot unavailable for source match {source_match_id}."
        )
    return fixture, resolved, snapshot, str(snapshot_path)


def _team_id_for_side(fixture: dict[str, Any], side: str) -> str | None:
    key = "home_team_id" if side == "home" else "away_team_id"
    value = str(fixture.get(key) or "").strip()
    return value or None


def _player_bridge(season: str, fixture_id: str, source_player_id: object) -> dict[str, Any] | None:
    source_id = str(source_player_id or "").strip()
    if not source_id:
        return None
    return resolve_pulselive_player_identity(season, fixture_id, source_id)


def fixture_events(season: str, fixture_id: str) -> dict[str, Any]:
    """Return normalised source-native goal/card/substitution evidence for a fixture.

    Event identity remains source-native.  Player references are accompanied by
    the existing governed bridge decision to Player-Match source identity; a
    missing or ambiguous bridge is retained explicitly rather than inferred.
    """
    fixture, resolved, snapshot, snapshot_path = _fixture_route(season, fixture_id)
    payload = resource_payload(snapshot, "events")
    rows: list[dict[str, Any]] = []

    for event in normalise_events(payload):
        item = dict(event)
        side = str(item.get("side") or "")
        primary_bridge = _player_bridge(
            season, fixture_id, item.get("primary_source_player_id")
        )
        secondary_bridge = _player_bridge(
            season, fixture_id, item.get("secondary_source_player_id")
        )
        item.update(
            {
                "season": season,
                "fixture_id": str(fixture_id),
                "source_match_id": str(resolved["source_match_id"]),
                "frl_team_id": _team_id_for_side(fixture, side),
                "primary_player_identity": primary_bridge,
                "secondary_player_identity": secondary_bridge,
            }
        )
        rows.append(item)

    return {
        "query_type": "fixture_event_evidence",
        "season": season,
        "fixture_id": str(fixture_id),
        "source_match_id": str(resolved["source_match_id"]),
        "event_count": len(rows),
        "results": rows,
        "provenance": {
            "source_family": "PulseLive preserved match-centre snapshot",
            "resource": "events",
            "snapshot_path": snapshot_path,
            "resource_meta": resource_meta(snapshot, "events"),
            "fixture_relationship_status": resolved.get("relationship_status"),
            "fixture_resolution_basis": resolved.get("resolution_basis"),
        },
        "limitations": [
            "Event records remain source-native evidence rather than canonical event variables.",
            "Player identity is not inferred when the governed bridge is missing or ambiguous.",
            "Event presence in a preserved snapshot does not by itself establish historical information-availability time.",
        ],
    }


def fixture_tactical_context(season: str, fixture_id: str) -> dict[str, Any]:
    """Return source-native lineup, formation and manager context for a fixture."""
    fixture, resolved, snapshot, snapshot_path = _fixture_route(season, fixture_id)
    payload = resource_payload(snapshot, "lineups")
    context = normalise_lineups(payload)

    players: list[dict[str, Any]] = []
    for source in context.get("players", []):
        item = dict(source)
        side = str(item.get("side") or "")
        item["season"] = season
        item["fixture_id"] = str(fixture_id)
        item["source_match_id"] = str(resolved["source_match_id"])
        item["frl_team_id"] = _team_id_for_side(fixture, side)
        item["player_identity"] = _player_bridge(
            season, fixture_id, item.get("source_player_id")
        )
        players.append(item)

    managers: list[dict[str, Any]] = []
    manager_block = context.get("managers") or {}
    for source in manager_block.get("items", []) if isinstance(manager_block, dict) else []:
        item = dict(source)
        side = str(item.get("side") or "")
        item["frl_team_id"] = _team_id_for_side(fixture, side)
        managers.append(item)

    formations: dict[str, Any] = {}
    for side, formation in dict(context.get("formations") or {}).items():
        formations[side] = {
            **dict(formation),
            "frl_team_id": _team_id_for_side(fixture, side),
        }

    placements: dict[str, Any] = {}
    for side, values in dict(context.get("placements") or {}).items():
        placements[side] = {
            "frl_team_id": _team_id_for_side(fixture, side),
            "items": list(values or []),
        }

    return {
        "query_type": "fixture_tactical_context",
        "season": season,
        "fixture_id": str(fixture_id),
        "source_match_id": str(resolved["source_match_id"]),
        "players": players,
        "formations": formations,
        "placements": placements,
        "managers": {
            "status": manager_block.get("status") if isinstance(manager_block, dict) else "UNAVAILABLE",
            "items": managers,
        },
        "source_team_context": context.get("team_context"),
        "raw_team_payload_present": context.get("raw_team_payload_present"),
        "provenance": {
            "source_family": "PulseLive preserved match-centre snapshot",
            "resource": "lineups",
            "snapshot_path": snapshot_path,
            "resource_meta": resource_meta(snapshot, "lineups"),
            "fixture_relationship_status": resolved.get("relationship_status"),
            "fixture_resolution_basis": resolved.get("resolution_basis"),
        },
        "limitations": [
            "Formation and placement values are source-native; FRL does not infer tactical geometry when the source does not explicitly provide it.",
            "Manager identity remains source-native until a separate governed manager identity relationship exists.",
            "Player identity is not inferred when the governed bridge is missing or ambiguous.",
        ],
    }


__all__ = [
    "FixtureContextUnavailableError",
    "fixture_events",
    "fixture_tactical_context",
]
