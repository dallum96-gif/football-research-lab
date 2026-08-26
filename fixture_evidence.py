"""Universal fixture-level evidence adapter over preserved PulseLive snapshots.

The adapter starts from canonical ``(season, fixture_id)`` identity, resolves the
verified source match, then reads the already-mapped PulseLive match-centre
resources from the local source archive. Source IDs remain source-native.
"""
from __future__ import annotations

from typing import Any

from relationship_contracts import get_relationship_contract
from source_family_adapters import canonical_fixture, resolve_source_match
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
    teams = lineup_data.get("team_context", {})
    for side in ("home", "away"):
        observed = _text(teams.get(side))
        if observed and expected[side] and observed != expected[side]:
            raise ValueError(
                f"PulseLive lineup team mismatch for {side}: "
                f"expected {expected[side]}, observed {observed}"
            )


def _player_name_index(lineup_data: dict) -> dict[str, str]:
    output: dict[str, str] = {}
    for player in lineup_data.get("players", []):
        source_id = _text(player.get("source_player_id"))
        name = _text(player.get("name"))
        if source_id and name:
            output[source_id] = name
    return output


def _decorate_events(events: list[dict], names: dict[str, str]) -> list[dict]:
    output: list[dict] = []
    for event in events:
        item = dict(event)
        primary_id = _text(item.get("primary_source_player_id"))
        secondary_id = _text(item.get("secondary_source_player_id"))
        item["primary_player"] = {
            "source_player_id": primary_id,
            "name": names.get(primary_id) if primary_id else None,
        }
        item["secondary_player"] = {
            "source_player_id": secondary_id,
            "name": names.get(secondary_id) if secondary_id else None,
        }
        # For goals secondary_player is an assist; for substitutions it is the
        # player-off identity. The raw event type remains authoritative.
        if item["type"] == "goal":
            item["assist"] = item["secondary_player"] if secondary_id else None
        else:
            item["assist"] = None
        output.append(item)
    return output


def fixture_evidence(season: str, fixture_id: str) -> dict:
    """Return one canonical fixture's preserved event/lineup evidence."""
    fixture = canonical_fixture(season, fixture_id)
    if fixture is None:
        raise ValueError(f"Canonical fixture not found: {season}/{fixture_id}")

    source_match = resolve_source_match(season, fixture_id)
    source_match_id = str(source_match["source_match_id"])
    snapshot, path = load_snapshot(source_match_id)
    if snapshot is None:
        return {
            "query_type": "fixture_evidence",
            "status": "UNAVAILABLE",
            "season": season,
            "fixture_id": str(fixture_id),
            "fixture": {
                "home_team_id": str(fixture.get("home_team_id") or ""),
                "away_team_id": str(fixture.get("away_team_id") or ""),
            },
            "events": [],
            "lineup": [],
            "formation": {
                "home": {"status": "UNAVAILABLE", "value": None},
                "away": {"status": "UNAVAILABLE", "value": None},
            },
            "managers": {"status": "UNAVAILABLE", "items": []},
            "coverage": {
                "events": "UNAVAILABLE",
                "lineup": "UNAVAILABLE",
                "formation": "UNAVAILABLE",
                "managers": "UNAVAILABLE",
            },
            "provenance": {
                "source_family": "pulselive_match",
                "source_match_id": source_match_id,
                "source_path": None,
                "relationship_contract": "canonical_fixture_to_source_match",
                "relationship_status": source_match["relationship_status"],
            },
            "limitations": [
                "No preserved PulseLive snapshot was found for the verified source match.",
            ],
        }

    events_payload = resource_payload(snapshot, "events")
    lineups_payload = resource_payload(snapshot, "lineups")
    events = normalise_events(events_payload)
    lineup_data = normalise_lineups(lineups_payload)

    _validate_team_context(source_match, lineup_data)
    names = _player_name_index(lineup_data)
    events = _decorate_events(events, names)

    lineup = []
    for player in lineup_data.get("players", []):
        item = dict(player)
        source_player_id = _text(item.get("source_player_id"))
        item["player"] = {
            "source_player_id": source_player_id,
            "name": item.pop("name", None),
        }
        lineup.append(item)

    relationship_contract = get_relationship_contract("canonical_fixture_to_source_match")
    status = "AVAILABLE" if (events or lineup) else "UNAVAILABLE"

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
        "events": events,
        "lineup": lineup,
        "formation": lineup_data["formations"],
        "managers": lineup_data["managers"],
        "coverage": {
            "events": "AVAILABLE" if events else "UNAVAILABLE",
            "event_count": len(events),
            "lineup": "AVAILABLE" if lineup else "UNAVAILABLE",
            "player_count": len(lineup),
            "formation": {
                side: value["status"] for side, value in lineup_data["formations"].items()
            },
            "managers": lineup_data["managers"]["status"],
        },
        "provenance": {
            "source_family": "pulselive_match",
            "source_match_id": source_match_id,
            "source_path": str(path),
            "relationship_contract": relationship_contract.name,
            "relationship_status": source_match["relationship_status"],
            "resources": {
                "events": resource_meta(snapshot, "events"),
                "lineups": resource_meta(snapshot, "lineups"),
            },
            "snapshot_retrieved_at": snapshot.get("retrieved_at"),
        },
        "limitations": [
            "PulseLive source identifiers remain source-native and are not canonical FRL identities.",
            "Lineup placement is only exposed when explicit placement coordinates are present in the preserved source; the adapter never infers tactical coordinates from formation or position labels.",
        ],
    }


__all__ = ["fixture_evidence"]
