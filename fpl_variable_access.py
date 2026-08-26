"""First-class FRL FPL variable access layer.

FPL variables are intentionally separate from the core football-stat families.
This module reads already-built FPL evidence tables and does not perform
identity inference or create new canonical relationships.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PLAYER_GW = ROOT / "data" / "fpl_player_gw_evidence.csv"
FIXTURE = ROOT / "data" / "fpl_fixture_evidence.csv"


def _load(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _source_field(field_name: str) -> str:
    text = str(field_name or "").replace("[]", "")
    return text.split(".")[-1]


def player_gameweek_values(
    *,
    season: str,
    player_id: str,
    field_name: str,
    gameweek: str | None = None,
) -> dict:
    rows = _load(PLAYER_GW)
    source_field = _source_field(field_name)
    key = f"source_{source_field}"

    results = []
    for row in rows:
        if str(row.get("frl_season", "")) != str(season):
            continue
        if str(row.get("frl_fpl_player_key", "")) != str(player_id):
            continue
        if gameweek is not None and str(row.get("frl_fpl_gameweek", "")) != str(gameweek):
            continue
        results.append({
            "season": season,
            "player_id": str(player_id),
            "gameweek": row.get("frl_fpl_gameweek", ""),
            "fixture": row.get("source_fixture", ""),
            "source_field": source_field,
            "value": row.get(key, ""),
        })

    return {
        "query_type": "frl_fpl_variable",
        "research_family": "FPL",
        "subclass": "player_gameweek",
        "variable": field_name,
        "season": season,
        "player_id": str(player_id),
        "results": results,
        "provenance": {
            "evidence_table": str(PLAYER_GW),
            "source_field": source_field,
        },
    }


def fixture_values(
    *,
    season: str,
    fixture_id: str,
    field_name: str,
) -> dict:
    rows = _load(FIXTURE)
    source_field = _source_field(field_name)
    key = f"source_{source_field}"

    results = []
    for row in rows:
        if str(row.get("frl_season", "")) != str(season):
            continue
        if str(row.get("frl_fpl_fixture_key", "")) != str(fixture_id):
            continue
        results.append({
            "season": season,
            "fixture_id": str(fixture_id),
            "source_field": source_field,
            "value": row.get(key, ""),
        })

    return {
        "query_type": "frl_fpl_variable",
        "research_family": "FPL",
        "subclass": "fixture",
        "variable": field_name,
        "season": season,
        "fixture_id": str(fixture_id),
        "results": results,
        "provenance": {
            "evidence_table": str(FIXTURE),
            "source_field": source_field,
        },
    }


__all__ = ["fixture_values", "player_gameweek_values"]
