"""First-class FRL FPL evidence access.

FPL is intentionally isolated from the core football-stat source families.
This module consumes already-built FPL evidence artefacts and performs no
identity inference or canonical relationship creation of its own.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent
PLAYER_GW = ROOT / "data" / "fpl_player_gw_evidence.csv"
FIXTURE = ROOT / "data" / "fpl_fixture_evidence.csv"
FPL_REGISTRY = ROOT / "data" / "fpl_canonical_variable_registry_v1.csv"


class FPLVariableUnavailableError(ValueError):
    """Raised when an FPL variable is not exposed or not evidenced."""


def _load(path: Path) -> tuple[dict[str, str], ...]:
    if not path.exists():
        return ()
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return tuple(csv.DictReader(fh))


def _terminal_field(field_name: str) -> str:
    text = str(field_name or "").replace("[]", "")
    return text.split(".")[-1]


def fpl_catalogue() -> tuple[dict[str, str], ...]:
    """Return research-facing FPL variables from the local canonical registry."""
    rows = _load(FPL_REGISTRY)
    return tuple(row for row in rows if row.get("research_exposed", "").upper() == "YES")


def fpl_variable_definition(name: str) -> dict[str, str]:
    """Return one research-facing FPL variable definition or fail closed."""
    for row in fpl_catalogue():
        if row.get("field_name") == name:
            return row
    raise FPLVariableUnavailableError(
        f"FPL variable '{name}' is not exposed by the authoritative FPL registry."
    )


def _require_source_column(rows: Iterable[dict[str, str]], field_name: str) -> str:
    source_field = _terminal_field(field_name)
    key = f"source_{source_field}"
    for row in rows:
        if key in row:
            return key
    raise FPLVariableUnavailableError(
        f"FPL source field '{source_field}' is not present in the available evidence table."
    )


def player_gameweek_values(
    *,
    season: str,
    player_id: str,
    field_name: str,
    gameweek: str | None = None,
) -> dict:
    """Resolve an FPL player/gameweek variable from approved evidence."""
    fpl_variable_definition(field_name)
    rows = _load(PLAYER_GW)
    candidate_rows = tuple(
        row for row in rows
        if str(row.get("frl_season", "")) == str(season)
        and str(row.get("frl_fpl_player_key", "")) == str(player_id)
        and (gameweek is None or str(row.get("frl_fpl_gameweek", "")) == str(gameweek))
    )
    key = _require_source_column(candidate_rows if candidate_rows else rows, field_name)

    results = [
        {
            "season": season,
            "player_id": str(player_id),
            "gameweek": row.get("frl_fpl_gameweek", ""),
            "fixture": row.get("source_fixture", ""),
            "source_field": _terminal_field(field_name),
            "value": row.get(key),
        }
        for row in candidate_rows
    ]
    return {
        "query_type": "frl_fpl_variable",
        "research_family": "FPL",
        "variable": field_name,
        "subclass": fpl_variable_definition(field_name).get("subclass"),
        "season": season,
        "player_id": str(player_id),
        "results": results,
        "provenance": {
            "evidence_table": str(PLAYER_GW),
            "source_field": _terminal_field(field_name),
        },
    }


def fixture_values(*, season: str, fixture_id: str, field_name: str) -> dict:
    """Resolve an FPL fixture variable from approved evidence."""
    fpl_variable_definition(field_name)
    rows = _load(FIXTURE)
    candidate_rows = tuple(
        row for row in rows
        if str(row.get("frl_season", "")) == str(season)
        and str(row.get("frl_fpl_fixture_key", "")) == str(fixture_id)
    )
    key = _require_source_column(candidate_rows if candidate_rows else rows, field_name)

    results = [
        {
            "season": season,
            "fixture_id": str(fixture_id),
            "source_field": _terminal_field(field_name),
            "value": row.get(key),
        }
        for row in candidate_rows
    ]
    return {
        "query_type": "frl_fpl_variable",
        "research_family": "FPL",
        "variable": field_name,
        "subclass": fpl_variable_definition(field_name).get("subclass"),
        "season": season,
        "fixture_id": str(fixture_id),
        "results": results,
        "provenance": {
            "evidence_table": str(FIXTURE),
            "source_field": _terminal_field(field_name),
        },
    }


__all__ = [
    "FPLVariableUnavailableError",
    "fixture_values",
    "fpl_catalogue",
    "fpl_variable_definition",
    "player_gameweek_values",
]
