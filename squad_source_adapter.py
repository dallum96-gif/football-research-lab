"""Fail-closed adapter for Pulselive team-squad payloads.

The adapter only promotes a squad payload to a canonical team-season when an
external, audited source_season_id -> FRL season mapping is supplied and the
source team id resolves uniquely to the verified seasonal team registry.
Player identity remains source-native until the existing player identity
contracts independently prove a bridge.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from relationship_contracts import get_relationship_contract

ROOT = Path(__file__).resolve().parent
DEFAULT_SQUAD_FILE = ROOT / "data" / "live_pl_api_cache" / "team_squad.json"
TEAM_SEASONS_FILE = ROOT / "identity" / "team_seasons.csv"


def _n(value: object) -> str:
    return str(value or "").strip()


def load_squad_payload(path: Path = DEFAULT_SQUAD_FILE) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Squad payload must be a JSON object")
    return payload


def load_team_season_registry(path: Path = TEAM_SEASONS_FILE) -> tuple[dict[str, str], ...]:
    if not path.is_file():
        return ()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return tuple(csv.DictReader(handle))


def squad_context(payload: dict) -> dict[str, str]:
    body = payload.get("payload") or {}
    ident = body.get("id") or {}
    team = body.get("team") or {}
    season_id = _n(ident.get("seasonId"))
    competition_id = _n(ident.get("competitionId"))
    team_id = _n(team.get("id"))
    team_name = _n(team.get("name"))
    if not season_id or not team_id:
        raise ValueError("Squad payload lacks explicit payload.id.seasonId or payload.team.id")
    return {
        "source_season_id": season_id,
        "source_competition_id": competition_id,
        "source_team_id": team_id,
        "source_team_name": team_name,
    }


def resolve_team_season(
    payload: dict,
    *,
    source_season_map: dict[str, str],
    registry: Iterable[dict[str, str]] | None = None,
) -> dict[str, object]:
    """Resolve a squad payload using an already-audited season-id map."""
    get_relationship_contract("canonical_team_season_to_source_team")
    context = squad_context(payload)
    season = _n(source_season_map.get(context["source_season_id"]))
    if not season:
        return {"status": "UNRESOLVED_SEASON", **context}

    rows = tuple(registry if registry is not None else load_team_season_registry())
    matches = [
        row
        for row in rows
        if _n(row.get("season")) == season
        and _n(row.get("local_team_id")) == context["source_team_id"]
        and _n(row.get("mapping_status")) in ("", "VERIFIED")
    ]

    if len(matches) != 1:
        return {
            "status": "AMBIGUOUS_OR_MISSING_TEAM_SEASON",
            **context,
            "season": season,
            "candidate_count": len(matches),
        }

    row = matches[0]
    return {
        "status": "VERIFIED_TEAM_SEASON_ROUTE",
        **context,
        "season": season,
        "team_season_id": _n(row.get("team_season_id")),
        "canonical_name": _n(row.get("canonical_name")),
        "persistent_team_code": _n(row.get("persistent_team_code")),
        "local_team_id": _n(row.get("local_team_id")),
    }


def squad_player_rows(payload: dict) -> tuple[dict, ...]:
    players = (payload.get("payload") or {}).get("players") or []
    if not isinstance(players, list):
        raise ValueError("Squad payload players must be a list")
    return tuple(dict(row) for row in players if isinstance(row, dict))
