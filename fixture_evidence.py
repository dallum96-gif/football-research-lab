"""Universal fixture-level evidence adapter over existing FRL source evidence."""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from relationship_contracts import get_relationship_contract
from source_family_adapters import (
    canonical_fixture,
    fixture_metadata,
    resolve_pulselive_player_identity,
    resolve_source_match,
    source_player_season_identity,
)
from player_match_stats import (
    fixture_player_match_rows,
    classify_participation,
    source_player_id,
)
from pulselive_fixture_evidence import (
    load_snapshot,
    normalise_events,
    normalise_lineups,
    resource_meta,
    resource_payload,
)


def _text(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value).strip() or None


def _source_team_id(row: dict[str, Any]) -> str | None:
    return _text(row.get("teamId")) or _text(row.get("team_id")) or _text(row.get("id"))


def _validate_team_context(source_match: dict, lineup_data: dict) -> None:
    expected = {
        "home": _source_team_id(source_match["home"]),
        "away": _source_team_id(source_match["away"]),
    }
    observed = lineup_data.get("team_context", {})
    for side in ("home", "away"):
        source_team = _text(observed.get(side))
        expected_team = expected[side]
        if source_team and expected_team and source_team != expected_team:
            raise ValueError(
                f"PulseLive lineup team mismatch for {side}: expected {expected_team}, found {source_team}"
            )


@lru_cache(maxsize=None)
def _identity_status(season: str, source_player_id: str | None) -> str:
    if not source_player_id:
        return "UNAVAILABLE"
    try:
        result = source_player_season_identity(season, source_player_id)
    except (FileNotFoundError, ValueError):
        return "UNRESOLVED"
    return "VERIFIED" if result.get("verified") else _text(result.get("status")) or "UNRESOLVED"


def _player_name_index(lineup_data: dict) -> dict[str, str]:
    return {
        str(player["source_player_id"]): str(player["name"])
        for player in lineup_data.get("players", [])
        if player.get("source_player_id") and player.get("name")
    }


def _decorate_pulselive_player(
    season: str,
    fixture_id: str,
    pulselive_player_id: str | None,
    name: str | None,
) -> dict[str, Any]:
    bridge = resolve_pulselive_player_identity(season, fixture_id, pulselive_player_id)
    player_match_source_id = _text(bridge.get("player_match_source_player_id"))
    bridge_status = _text(bridge.get("relationship_status")) or "UNRESOLVED"
    player_season_identity_status = (
        # The exact bridge proves that this PulseLive ID is PM ``pl_code``;
        # that is the established Player-Season-facing namespace.  The
        # distinct PM source_player_id is retained for URA observation lookup.
        _identity_status(season, pulselive_player_id)
        if bridge_status == "VERIFIED" and pulselive_player_id
        else bridge_status
    )
    identity_status = (
        player_season_identity_status
        if player_season_identity_status == "VERIFIED"
        else "SOURCE_NATIVE_VERIFIED"
        if bridge_status == "VERIFIED" and player_match_source_id
        else player_season_identity_status
    )
    return {
        # Backward-compatible source ID: this remains the original PulseLive ID.
        "source_player_id": pulselive_player_id,
        "source_player_id_namespace": bridge["pulselive_source_player_id_namespace"],
        "player_match_source_player_id": player_match_source_id,
        "player_match_source_player_id_namespace": bridge.get(
            "player_match_source_player_id_namespace"
        ),
        "player_season_identity_source_player_id": (
            pulselive_player_id if bridge_status == "VERIFIED" else None
        ),
        "player_season_identity_source_player_id_namespace": (
            "players_match_stats.pl_code" if bridge_status == "VERIFIED" else None
        ),
        "name": name,
        "identity_status": identity_status,
        "player_season_identity_status": player_season_identity_status,
        "identity_bridge": bridge,
    }


def _decorate_events(
    events: list[dict],
    names: dict[str, str],
    season: str,
    fixture_id: str,
) -> list[dict]:
    output: list[dict] = []
    for event in events:
        item = dict(event)
        primary_id = _text(item.get("primary_source_player_id"))
        secondary_id = _text(item.get("secondary_source_player_id"))
        item["primary_player"] = _decorate_pulselive_player(
            season,
            fixture_id,
            primary_id,
            names.get(primary_id) if primary_id else None,
        )
        secondary = _decorate_pulselive_player(
            season,
            fixture_id,
            secondary_id,
            names.get(secondary_id) if secondary_id else None,
        )
        item["secondary_player"] = secondary
        item["assist"] = secondary if event["type"] == "goal" and secondary_id else None
        output.append(item)
    return output


def _attach_placement(lineup_data: dict, player: dict) -> dict[str, Any] | None:
    placements = lineup_data.get("placements", {}).get(player.get("side"), [])
    source_id = player.get("source_player_id")
    placement = next((row for row in placements if row.get("source_player_id") == source_id), None)
    if placement is None:
        return None
    return {
        **placement,
        "status": "SOURCE_EXPLICIT",
        "provenance": {
            "classification": "SOURCE_EVIDENCE",
            "source_field": "pulselive_match.lineups.formation.lineup",
            "source_coordinate_fields": ["x", "y"],
            "explicit_source_coordinates": True,
        },
    }


def _lineup_from_player_match(fixture: dict, season: str, fixture_id: str, source_match_id: str) -> list[dict[str, Any]]:
    """Build the universal fixture lineup from the existing Playerâ€“Match evidence source.

    This is the fallback when no preserved PulseLive lineup snapshot exists. It does not
    infer tactical placement or formation. It exposes only source-backed participation,
    position and minutes.
    """
    rows = fixture_player_match_rows(fixture)
    output: list[dict[str, Any]] = []
    for row in rows:
        player_match_source_match_id = _text(row.get("matchId"))
        source_id = source_player_id(row)
        side = _text(row.get("venue"))
        if side:
            side = side.lower()
            if side not in {"home", "away"}:
                side = None
        name = _text(row.get("playerName")) or _text(row.get("player_name")) or _text(row.get("name"))
        position = _text(row.get("position"))
        participation = classify_participation(row)
        minutes_raw = row.get("minutesPlayed")
        try:
            minutes = float(minutes_raw) if minutes_raw not in (None, "") else 0.0
        except (TypeError, ValueError):
            minutes = None

        output.append({
            "player": {
                "source_player_id": source_id,
                "name": name,
                "identity_status": "SOURCE_NATIVE_VERIFIED" if source_id else "UNRESOLVED",
            },
            "side": side,
            "position": position,
            "shirt_number": _text(row.get("shirtNumber")) or _text(row.get("shirt_number")),
            "placement": None,
            "participation": participation,
            "minutes": minutes,
            "provenance": {
                "season": season,
                "fixture_id": str(fixture_id),
                "source_match_id": source_match_id,
                "source_match_id_namespace": "events_stats.matchId",
                "player_match_source_match_id": player_match_source_match_id,
                "player_match_source_match_id_namespace": "players_match_stats.matchId",
                "source_family": "player_match_stats",
                "source_file": row.get("_source_file"),
                "relationship_contract": "source_player_identity_to_player_season",
                "relationship_status": "SOURCE_NATIVE_VERIFIED" if source_id else "UNRESOLVED",
            },
        })
    return output


def fixture_evidence(season: str, fixture_id: str) -> dict:
    """Return fixture-level events, lineup, formation and manager evidence."""
    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(f"Canonical fixture not found: {season}/{fixture_id}")
    source_match = resolve_source_match(season, fixture_id)
    source_match_id = str(source_match["source_match_id"])
    snapshot, path = load_snapshot(source_match_id)

    if snapshot is None:
        lineup = _lineup_from_player_match(fixture, season, fixture_id, source_match_id)
        player_match_source_match_ids = sorted({
            _text((row.get("provenance") or {}).get("player_match_source_match_id"))
            for row in lineup
            if _text((row.get("provenance") or {}).get("player_match_source_match_id"))
        })
        return {
            "query_type": "fixture_evidence",
            "status": "AVAILABLE" if lineup else "UNAVAILABLE",
            "season": season,
            "fixture_id": str(fixture_id),
            "fixture": {
                "home_team_id": str(fixture.get("home_team_id") or ""),
                "away_team_id": str(fixture.get("away_team_id") or ""),
                "source_match_id": source_match_id,
            },
            "metadata": fixture_metadata(season, fixture_id),
            "events": [],
            "lineup": lineup,
            "formation": {
                "home": {"status": "UNAVAILABLE", "value": None},
                "away": {"status": "UNAVAILABLE", "value": None},
            },
            "managers": {"status": "UNAVAILABLE", "items": []},
            "coverage": {
                "events": "UNAVAILABLE",
                "lineup": {"status": "AVAILABLE" if lineup else "UNAVAILABLE", "count": len(lineup)},
                "formation": {"home": "UNAVAILABLE", "away": "UNAVAILABLE"},
                "managers": "UNAVAILABLE",
            },
            "provenance": {
                "source_family": "player_match_stats",
                "source_match_id": source_match_id,
                "source_match_id_namespace": "events_stats.matchId",
                "player_match_source_match_id": player_match_source_match_ids[0] if len(player_match_source_match_ids) == 1 else None,
                "player_match_source_match_ids": player_match_source_match_ids,
                "player_match_source_match_id_namespace": "players_match_stats.matchId",
                "source_path": "per-club seasonal player-match files",
                "relationship_contract": get_relationship_contract("canonical_fixture_to_source_match").name,
                "relationship_status": source_match["relationship_status"],
                "resolution_basis": source_match.get("resolution_basis"),
                "fixture_correction": source_match.get("fixture_correction"),
            },
            "limitations": [
                "Lineup is supplied from the existing Playerâ€“Match evidence source because no preserved PulseLive lineup snapshot is available.",
                "Formation, managers and tactical placement remain unavailable because they are not present in this Playerâ€“Match evidence grain.",
            ],
        }

    events_payload = resource_payload(snapshot, "events")
    lineups_payload = resource_payload(snapshot, "lineups")
    events = normalise_events(events_payload)
    lineup_data = normalise_lineups(lineups_payload)
    _validate_team_context(source_match, lineup_data)
    names = _player_name_index(lineup_data)
    events = _decorate_events(events, names, season, str(fixture_id))

    lineup: list[dict[str, Any]] = []
    identity_failures = 0
    for player in lineup_data.get("players", []):
        pulselive_player_id = _text(player.get("source_player_id"))
        player_identity = _decorate_pulselive_player(
            season,
            str(fixture_id),
            pulselive_player_id,
            player.get("name"),
        )
        status = str(player_identity["identity_status"])
        if status not in {"VERIFIED", "SOURCE_NATIVE_VERIFIED"}:
            identity_failures += 1
        placement = _attach_placement(lineup_data, player)
        lineup.append({
            "player": player_identity,
            "side": player.get("side"),
            "position": player.get("position"),
            "shirt_number": player.get("shirt_number"),
            "placement": placement,
            "source_formation_order": player.get("source_formation_order"),
            "participation": player.get("participation"),
            "minutes": player.get("minutes"),
            "provenance": {
                "season": season,
                "fixture_id": str(fixture_id),
                "source_match_id": source_match_id,
                "source_family": "pulselive_match_lineups",
                "pulselive_source_player_id": pulselive_player_id,
                "pulselive_source_player_id_namespace": player_identity[
                    "source_player_id_namespace"
                ],
                "player_match_source_player_id": player_identity[
                    "player_match_source_player_id"
                ],
                "player_match_source_player_id_namespace": player_identity[
                    "player_match_source_player_id_namespace"
                ],
                "identity_bridge_route": player_identity["identity_bridge"][
                    "identity_route"
                ],
                "identity_bridge_contract": player_identity["identity_bridge"][
                    "relationship_contract"
                ],
                "identity_bridge_status": player_identity["identity_bridge"][
                    "relationship_status"
                ],
                "relationship_contract": "source_player_identity_to_player_season",
                "relationship_status": player_identity[
                    "player_season_identity_status"
                ],
            },
        })

    formation = lineup_data["formations"]
    managers = lineup_data["managers"]
    status = "AVAILABLE" if (events or lineup) else "UNAVAILABLE"
    limitations = [
        "PulseLive source identifiers remain source-native and are never promoted to canonical FRL IDs by this adapter.",
        "Explicit tactical coordinates are source evidence only when numeric x/y values are present in the preserved formation lineup object.",
        "Source formation-line ordering is preserved separately so the frontend research-result seam may derive a clearly labelled presentation-only layout.",
    ]
    if identity_failures:
        limitations.append(f"{identity_failures} source-player relationships did not resolve uniquely and remain fail-closed.")

    return {
        "query_type": "fixture_evidence",
        "status": status,
        "season": season,
        "fixture_id": str(fixture_id),
        "fixture": {
            "home_team_id": str(fixture.get("home_team_id") or ""),
            "away_team_id": str(fixture.get("away_team_id") or ""),
            "source_match_id": source_match_id,
        },
        "metadata": fixture_metadata(season, fixture_id),
        "events": events,
        "lineup": lineup,
        "formation": formation,
        "managers": managers,
        "coverage": {
            "events": {"status": "AVAILABLE" if events else "UNAVAILABLE", "count": len(events)},
            "lineup": {"status": "AVAILABLE" if lineup else "UNAVAILABLE", "count": len(lineup)},
            "formation": {side: value["status"] for side, value in formation.items()},
            "managers": managers["status"],
        },
        "provenance": {
            "source_family": "pulselive_match",
            "source_match_id": source_match_id,
            "source_path": str(path),
            "relationship_contract": get_relationship_contract("canonical_fixture_to_source_match").name,
            "relationship_status": source_match["relationship_status"],
            "resolution_basis": source_match.get("resolution_basis"),
            "fixture_correction": source_match.get("fixture_correction"),
            "snapshot_retrieved_at": snapshot.get("retrieved_at"),
            "resources": {
                "events": resource_meta(snapshot, "events"),
                "lineups": resource_meta(snapshot, "lineups"),
            },
            "player_identity_bridge": {
                "identity_route": "PULSELIVE_PLAYER_ID_TO_PLAYER_MATCH_PL_CODE_TO_SOURCE_PLAYER_ID",
                "source_namespace": "pulselive_match.playerId",
                "bridge_source_field": "players_match_stats.pl_code",
                "target_namespace": "player_match_stats.source_player_id()",
                "relationship_contract": "source_player_match_to_source_player_identity",
            },
        },
        "limitations": limitations,
    }


__all__ = ["fixture_evidence"]
