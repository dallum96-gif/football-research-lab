"""Universal fixture-level evidence adapter over preserved PulseLive snapshots."""
from __future__ import annotations

from typing import Any

from relationship_contracts import get_relationship_contract
from source_family_adapters import (
    canonical_fixture,
    fixture_metadata,
    resolve_source_match,
    source_player_season_identity,
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


def _decorate_events(events: list[dict], names: dict[str, str], season: str) -> list[dict]:
    output: list[dict] = []
    for event in events:
        item = dict(event)
        primary_id = _text(item.get("primary_source_player_id"))
        secondary_id = _text(item.get("secondary_source_player_id"))
        item["primary_player"] = {
            "source_player_id": primary_id,
            "name": names.get(primary_id) if primary_id else None,
            "identity_status": _identity_status(season, primary_id),
        }
        secondary = {
            "source_player_id": secondary_id,
            "name": names.get(secondary_id) if secondary_id else None,
            "identity_status": _identity_status(season, secondary_id) if secondary_id else "UNAVAILABLE",
        }
        item["secondary_player"] = secondary
        item["assist"] = secondary if event["type"] == "goal" and secondary_id else None
        output.append(item)
    return output


def _attach_placement(lineup_data: dict, player: dict) -> dict[str, Any] | None:
    placements = lineup_data.get("placements", {}).get(player.get("side"), [])
    source_id = player.get("source_player_id")
    match = next((row for row in placements if row.get("source_player_id") == source_id), None)
    return match


def fixture_evidence(season: str, fixture_id: str) -> dict:
    """Return fixture-level events, lineup, formation and manager evidence."""
    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(f"Canonical fixture not found: {season}/{fixture_id}")
    source_match = resolve_source_match(season, fixture_id)
    source_match_id = str(source_match["source_match_id"])
    snapshot, path = load_snapshot(source_match_id)

    if snapshot is None:
        return _unavailable_result(season, fixture_id, source_match_id, source_match)

    events_payload = resource_payload(snapshot, "events")
    lineups_payload = resource_payload(snapshot, "lineups")
    events = normalise_events(events_payload)
    lineup_data = normalise_lineups(lineups_payload)
    _validate_team_context(source_match, lineup_data)
    names = _player_name_index(lineup_data)
    events = _decorate_events(events, names, season)

    lineup: list[dict[str, Any]] = []
    identity_failures = 0
    for player in lineup_data.get("players", []):
        source_player_id = _text(player.get("source_player_id"))
        status = _identity_status(season, source_player_id)
        if status != "VERIFIED":
            identity_failures += 1
        placement = _attach_placement(lineup_data, player)
        lineup.append({
            "player": {
                "source_player_id": source_player_id,
                "name": player.get("name"),
                "identity_status": status,
            },
            "side": player.get("side"),
            "position": player.get("position"),
            "shirt_number": player.get("shirt_number"),
            "placement": placement,
            "provenance": {
                "season": season,
                "fixture_id": str(fixture_id),
                "source_match_id": source_match_id,
                "source_family": "pulselive_match_lineups",
                "relationship_contract": "source_player_identity_to_player_season",
                "relationship_status": status,
            },
        })

    formation = lineup_data["formations"]
    managers = lineup_data["managers"]
    status = "AVAILABLE" if (events or lineup) else "UNAVAILABLE"
    limitations = [
        "PulseLive source identifiers remain source-native and are never promoted to canonical FRL IDs by this adapter.",
        "Lineup placement is returned only when explicit numeric x/y coordinates are present in the preserved formation lineup object.",
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
            "snapshot_retrieved_at": snapshot.get("retrieved_at"),
            "resources": {
                "events": resource_meta(snapshot, "events"),
                "lineups": resource_meta(snapshot, "lineups"),
            },
        },
        "limitations": limitations,
    }


def _unavailable_result(season: str, fixture_id: str, source_match_id: str, source_match: dict) -> dict:
    return {
        "query_type": "fixture_evidence",
        "status": "UNAVAILABLE",
        "season": season,
        "fixture_id": str(fixture_id),
        "fixture": {"source_match_id": source_match_id},
        "events": [],
        "lineup": [],
        "formation": {
            "home": {"status": "UNAVAILABLE", "value": None},
            "away": {"status": "UNAVAILABLE", "value": None},
        },
        "managers": {"status": "UNAVAILABLE", "items": []},
        "coverage": {"events": "UNAVAILABLE", "lineup": "UNAVAILABLE", "formation": "UNAVAILABLE", "managers": "UNAVAILABLE"},
        "provenance": {
            "source_family": "pulselive_match",
            "source_match_id": source_match_id,
            "source_path": None,
            "relationship_contract": "canonical_fixture_to_source_match",
            "relationship_status": source_match["relationship_status"],
        },
        "limitations": ["No preserved PulseLive snapshot was found for the verified source match."],
    }


__all__ = ["fixture_evidence"]
