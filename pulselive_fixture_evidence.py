"""Read and normalise preserved PulseLive match-centre evidence.

This module is source-adapter code. It accepts preserved raw PulseLive snapshots
and produces a stable fixture-evidence representation while keeping source IDs
separate from FRL canonical identities.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
ARCHIVE_ENV = "FRL_PULSELIVE_ARCHIVE_ROOT"
DEFAULT_ROOTS = (
    ROOT / "data" / "raw" / "pulselive",
    ROOT / "raw" / "pulselive",
    ROOT.parent / "Premier-League-Stats" / "fpl_scraper" / "fpl_stats" / "data" / "raw" / "pulselive",
)


def archive_root() -> Path | None:
    configured = os.environ.get(ARCHIVE_ENV)
    if configured:
        path = Path(configured).expanduser().resolve()
        return path if path.is_dir() else None
    for path in DEFAULT_ROOTS:
        if path.is_dir():
            return path
    return None


def snapshot_path(source_match_id: str) -> Path | None:
    root = archive_root()
    if root is None:
        return None
    candidates = (
        root / f"match-{source_match_id}" / "snapshot.json",
        root / str(source_match_id) / "snapshot.json",
        root / f"match_{source_match_id}.json",
        root / f"{source_match_id}.json",
    )
    return next((path for path in candidates if path.is_file()), None)


def load_snapshot(source_match_id: str) -> tuple[dict[str, Any] | None, Path | None]:
    path = snapshot_path(str(source_match_id))
    if path is None:
        return None, None
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"PulseLive snapshot must be an object: {path}")
    return payload, path


def resource_payload(snapshot: dict[str, Any], name: str) -> Any:
    resources = snapshot.get("resources")
    if not isinstance(resources, dict):
        return None
    resource = resources.get(name)
    if isinstance(resource, dict) and "payload" in resource:
        return resource["payload"]
    return resource


def resource_meta(snapshot: dict[str, Any], name: str) -> dict[str, Any]:
    resources = snapshot.get("resources")
    if not isinstance(resources, dict):
        return {}
    resource = resources.get(name)
    if not isinstance(resource, dict):
        return {}
    return {
        "endpoint": resource.get("endpoint"),
        "retrieved_at": resource.get("retrieved_at"),
        "headers": resource.get("headers") if isinstance(resource.get("headers"), dict) else {},
    }


def _as_list(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        for key in ("content", "items", "data", "players", "goals", "cards", "subs"):
            candidate = value.get(key)
            if isinstance(candidate, list):
                return [item for item in candidate if isinstance(item, dict)]
    return []


def _text(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value).strip() or None


def _number(value: Any) -> int | float | None:
    if value in (None, ""):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return int(number) if number.is_integer() else number


def _event_sort_seconds(value: Any) -> int | float | None:
    """Convert source minute labels such as ``45+1`` into a sortable value."""
    if value in (None, ""):
        return None
    numeric = _number(value)
    if numeric is not None:
        return numeric
    match = re.match(r"^\s*(\d+(?:\.\d+)?)(?:\s*\+\s*(\d+(?:\.\d+)?))?", str(value))
    if not match:
        return None
    base = float(match.group(1))
    added = float(match.group(2) or 0)
    return base + added / 1000.0


def _event_time(item: dict[str, Any]) -> tuple[str | None, int | float | None]:
    label = _text(item.get("time")) or _text(item.get("minute")) or _text(item.get("timestamp"))
    seconds = _number(item.get("seconds"))
    if seconds is None:
        seconds = _number(item.get("elapsedSeconds"))
    if seconds is None:
        seconds = _event_sort_seconds(label)
    return label, seconds


def _team_sections(payload: Any) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not isinstance(payload, dict):
        return None, None
    home = payload.get("homeTeam") or payload.get("home_team")
    away = payload.get("awayTeam") or payload.get("away_team")
    return (home if isinstance(home, dict) else None, away if isinstance(away, dict) else None)


def _event_rows(payload: Any, source_event_type: str, side: str, list_key: str) -> list[dict[str, Any]]:
    home, away = _team_sections(payload)
    team = home if side == "home" else away
    if team is None:
        return []
    output: list[dict[str, Any]] = []
    for item in _as_list(team.get(list_key)):
        label, seconds = _event_time(item)
        output.append({
            "event_id": _text(item.get("id")) or _text(item.get("eventId")),
            "type": source_event_type,
            "side": side,
            "minute": label,
            "seconds": seconds,
            "primary_source_player_id": _text(item.get("playerId")) or _text(item.get("playerOnId")),
            "secondary_source_player_id": _text(item.get("assistPlayerId")) or _text(item.get("playerOffId")),
            "detail": {
                "goal_type": _text(item.get("goalType")),
                "card_type": _text(item.get("type")) if source_event_type == "card" else None,
                "period": _text(item.get("period")),
                "timestamp": _text(item.get("timestamp")),
            },
        })
    return output


def normalise_events(payload: Any) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for event_type, key in (("goal", "goals"), ("card", "cards"), ("substitution", "subs")):
        for side in ("home", "away"):
            events.extend(_event_rows(payload, event_type, side, key))
    events.sort(key=lambda row: (
        row["seconds"] is None,
        row["seconds"] if row["seconds"] is not None else 0,
        row["event_id"] or "",
    ))
    return events


def _formation_value(team: dict[str, Any]) -> str | None:
    formation = team.get("formation")
    if not isinstance(formation, dict):
        return _text(formation)
    return _text(formation.get("formation"))


def _explicit_placement(team: dict[str, Any]) -> list[dict[str, Any]]:
    formation = team.get("formation")
    lineup = formation.get("lineup") if isinstance(formation, dict) else None
    entries = lineup.get("players") if isinstance(lineup, dict) else lineup
    output: list[dict[str, Any]] = []
    for entry in _as_list(entries):
        x = _number(entry.get("x"))
        y = _number(entry.get("y"))
        source_player_id = _text(entry.get("playerId")) or _text(entry.get("id"))
        if source_player_id and x is not None and y is not None:
            output.append({"source_player_id": source_player_id, "x": x, "y": y})
    return output


def _player_rows(team: dict[str, Any], side: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for player in _as_list(team.get("players")):
        rows.append({
            "side": side,
            "source_player_id": _text(player.get("playerId")) or _text(player.get("id")),
            "name": _text(player.get("displayName")) or " ".join(
                part for part in (_text(player.get("firstName")), _text(player.get("lastName"))) if part
            ) or None,
            "position": _text(player.get("position")),
            "shirt_number": _text(player.get("shirtNum")) or _text(player.get("shirtNumber")),
            "source_team_id": _text(team.get("teamId")) or _text(team.get("id")),
        })
    return rows


def _manager_rows(team: dict[str, Any], side: str) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for manager in _as_list(team.get("managers")):
        output.append({
            "side": side,
            "source_manager_id": _text(manager.get("id")),
            "first_name": _text(manager.get("firstName")),
            "last_name": _text(manager.get("lastName")),
            "type": _text(manager.get("type")),
        })
    return output


def normalise_lineups(payload: Any) -> dict[str, Any]:
    home, away = _team_sections(payload)
    players: list[dict[str, Any]] = []
    managers: list[dict[str, Any]] = []
    formations: dict[str, dict[str, Any]] = {}
    placements: dict[str, list[dict[str, Any]]] = {}
    team_context: dict[str, str | None] = {}

    for side, team in (("home", home), ("away", away)):
        if team is None:
            formations[side] = {"status": "UNAVAILABLE", "value": None}
            placements[side] = []
            team_context[side] = None
            continue
        team_context[side] = _text(team.get("teamId")) or _text(team.get("id"))
        players.extend(_player_rows(team, side))
        managers.extend(_manager_rows(team, side))
        value = _formation_value(team)
        formations[side] = {"status": "AVAILABLE" if value else "UNAVAILABLE", "value": value}
        placements[side] = _explicit_placement(team)

    return {
        "players": players,
        "formations": formations,
        "placements": placements,
        "managers": {"status": "AVAILABLE" if managers else "UNAVAILABLE", "items": managers},
        "team_context": team_context,
        "raw_team_payload_present": {"home": home is not None, "away": away is not None},
    }


__all__ = [
    "ARCHIVE_ENV",
    "archive_root",
    "load_snapshot",
    "normalise_events",
    "normalise_lineups",
    "resource_meta",
    "resource_payload",
    "snapshot_path",
]
