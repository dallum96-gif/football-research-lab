"""First-class FRL FPL variable access.

FPL is intentionally isolated from the core football-stat source families.
This module consumes the existing FPL evidence artefacts and the authoritative
FPL variable registry. It performs no identity inference or canonical
relationship creation.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PLAYER_GW = ROOT / "data" / "fpl_player_gw_evidence.csv"
FIXTURE = ROOT / "data" / "fpl_fixture_evidence.csv"
FPL_REGISTRY = ROOT / "data" / "fpl_canonical_variable_registry_v1.csv"


class FPLVariableUnavailableError(ValueError):
    """Raised when an FPL variable is not exposed by the FPL registry."""


def _load(path: Path) -> tuple[dict[str, str], ...]:
    if not path.exists():
        return ()
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return tuple(csv.DictReader(fh))


def _source_field(field_name: str) -> str:
    text = str(field_name or "").replace("[]", "")
    return text.split(".")[-1]


def fpl_catalogue() -> tuple[dict[str, str], ...]:
    """Return only research-facing FPL variables from the authoritative registry."""
    rows = _load(FPL_REGISTRY)
    return tuple(
        row
        for row in rows
        if str(row.get("research_exposed", "")).upper() == "YES"
    )


def fpl_variable_definition(name: str) -> dict[str, str]:
    """Return one research-facing FPL definition or fail closed."""
    for row in fpl_catalogue():
        if row.get("field_name") == name:
            return row
    raise FPLVariableUnavailableError(
        f"FPL variable '{name}' is not exposed by the authoritative FPL registry."
    )


def _require_source_column(rows: tuple[dict[str, str], ...], field_name: str) -> str:
    source_field = _source_field(field_name)
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
    fixture_id: str | None = None,
) -> dict:
    """Resolve an FPL player/gameweek variable from approved evidence.

    ``fixture_id`` is supported because the historical FPL player evidence
    contains the canonical fixture relationship via its ``source_fixture``
    column. This allows fixture-level consumers to access player variables
    without creating a second data pathway.
    """
    definition = fpl_variable_definition(field_name)
    rows = _load(PLAYER_GW)
    candidate_rows = tuple(
        row
        for row in rows
        if str(row.get("frl_season", "")) == str(season)
        and str(row.get("frl_fpl_player_key", "")) == str(player_id)
        and (
            gameweek is None
            or str(row.get("frl_fpl_gameweek", "")) == str(gameweek)
        )
        and (
            fixture_id is None
            or str(row.get("source_fixture", "")) == str(fixture_id)
        )
    )
    key = _require_source_column(candidate_rows if candidate_rows else rows, field_name)

    results = [
        {
            "season": season,
            "player_id": str(player_id),
            "gameweek": row.get("frl_fpl_gameweek", ""),
            "fixture": row.get("source_fixture", ""),
            "source_field": _source_field(field_name),
            "value": row.get(key, ""),
        }
        for row in candidate_rows
    ]

    return {
        "query_type": "frl_fpl_variable",
        "research_family": "FPL",
        "variable": field_name,
        "subclass": definition.get("subclass"),
        "season": season,
        "player_id": str(player_id),
        "gameweek": str(gameweek) if gameweek is not None else None,
        "fixture_id": str(fixture_id) if fixture_id is not None else None,
        "results": results,
        "provenance": {
            "evidence_table": str(PLAYER_GW),
            "source_field": _source_field(field_name),
        },
    }


def player_fixture_values(*, season: str, fixture_id: str, field_name: str) -> dict:
    """Resolve an FPL player variable for one historical fixture.

    The FPL player evidence stores the player/gameweek observations, including
    their fixture relationship. Results retain the FPL season-local player key
    and the source fixture so downstream consumers can apply the existing
    verified identity bridge.
    """
    definition = fpl_variable_definition(field_name)
    rows = _load(PLAYER_GW)
    candidate_rows = tuple(
        row
        for row in rows
        if str(row.get("frl_season", "")) == str(season)
        and str(row.get("source_fixture", "")) == str(fixture_id)
    )
    key = _require_source_column(candidate_rows if candidate_rows else rows, field_name)

    results = [
        {
            "season": season,
            "fixture_id": str(fixture_id),
            "player_id": str(row.get("frl_fpl_player_key", "")),
            "source_field": _source_field(field_name),
            "value": row.get(key, ""),
        }
        for row in candidate_rows
        if str(row.get("frl_fpl_player_key", "")).strip()
    ]

    return {
        "query_type": "frl_fpl_variable",
        "research_family": "FPL",
        "variable": field_name,
        "subclass": definition.get("subclass"),
        "season": season,
        "fixture_id": str(fixture_id),
        "results": results,
        "provenance": {
            "evidence_table": str(PLAYER_GW),
            "source_field": _source_field(field_name),
            "relationship": "historical FPL player-fixture evidence",
        },
    }


def fixture_values(*, season: str, fixture_id: str, field_name: str) -> dict:
    """Resolve an FPL fixture variable from approved evidence."""
    definition = fpl_variable_definition(field_name)
    rows = _load(FIXTURE)
    candidate_rows = tuple(
        row
        for row in rows
        if str(row.get("frl_season", "")) == str(season)
        and str(row.get("frl_fpl_fixture_key", "")) == str(fixture_id)
    )
    key = _require_source_column(candidate_rows if candidate_rows else rows, field_name)

    results = [
        {
            "season": season,
            "fixture_id": str(fixture_id),
            "source_field": _source_field(field_name),
            "value": row.get(key, ""),
        }
        for row in candidate_rows
    ]

    return {
        "query_type": "frl_fpl_variable",
        "research_family": "FPL",
        "variable": field_name,
        "subclass": definition.get("subclass"),
        "season": season,
        "fixture_id": str(fixture_id),
        "results": results,
        "provenance": {
            "evidence_table": str(FIXTURE),
            "source_field": _source_field(field_name),
        },
    }


__all__ = [
    "FPLVariableUnavailableError",
    "fixture_values",
    "fpl_catalogue",
    "fpl_variable_definition",
    "player_fixture_values",
    "player_gameweek_values",
]
