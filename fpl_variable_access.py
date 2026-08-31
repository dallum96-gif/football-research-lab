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
HISTORICAL_PLAYER_FIXTURES = ROOT / "_merged" / "players"


class FPLVariableUnavailableError(ValueError):
    """Raised when an FPL variable is not exposed by the FPL registry."""


HISTORICAL_PLAYER_FIXTURE_FIELDS = {
    "dribbles",
}


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


def _representation(field_name: str) -> str:
    if field_name.startswith("history[]."):
        return "FPL_PLAYER_FIXTURE"
    if field_name.startswith("fixtures[]."):
        return "FPL_FIXTURE"
    return "UNCONNECTED_FPL_REGISTRY_SURFACE"


def _require_representation(field_name: str, expected: str) -> None:
    actual = _representation(field_name)
    if actual != expected:
        raise FPLVariableUnavailableError(
            f"FPL variable '{field_name}' belongs to {actual}, not {expected}. "
            "Source-native registry surfaces are not silently coalesced."
        )


def _row_provenance(rows: tuple[dict[str, str], ...], evidence_table: Path, field_name: str) -> dict:
    releases = sorted({row.get("source_release_sha", "") for row in rows if row.get("source_release_sha")})
    source_paths = sorted({row.get("source_path", "") for row in rows if row.get("source_path")})
    source_hashes = sorted({row.get("source_sha256", "") for row in rows if row.get("source_sha256")})
    retrieved = sorted({row.get("source_retrieved_at", "") for row in rows if row.get("source_retrieved_at")})
    return {
        "evidence_table": str(evidence_table),
        "source_field": _source_field(field_name),
        "source_representation": _representation(field_name),
        "source_release_shas": releases,
        "source_paths": source_paths,
        "source_sha256": source_hashes,
        "information_available_as_of": retrieved,
        "source_family": "FPL",
        "historical_opta_equivalence_asserted": False,
    }


def player_fixture_rows(*, season: str, fixture_id: str) -> tuple[dict[str, str], ...]:
    """Return governed source-native FPL player-fixture rows."""
    return tuple(
        row
        for row in _load(PLAYER_GW)
        if str(row.get("frl_season", "")) == str(season)
        and str(row.get("frl_fixture_id", "")) == str(fixture_id)
        and str(row.get("frl_fixture_relationship_status", "")) == "VERIFIED"
    )


def player_gameweek_values(
    *,
    season: str,
    player_id: str,
    field_name: str,
    gameweek: str | None = None,
    fixture_id: str | None = None,
) -> dict:
    """Resolve an FPL player/gameweek variable from approved evidence."""
    definition = fpl_variable_definition(field_name)
    _require_representation(field_name, "FPL_PLAYER_FIXTURE")
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
            or str(row.get("frl_fixture_id", "")) == str(fixture_id)
        )
    )
    key = _require_source_column(candidate_rows if candidate_rows else rows, field_name)

    results = [
        {
            "season": season,
            "player_id": str(player_id),
            "gameweek": row.get("frl_fpl_gameweek", ""),
            "fixture_id": row.get("frl_fixture_id", ""),
            "source_fixture_code": row.get("source_fixture_code", ""),
            "source_player_code": row.get("source_player_code", ""),
            "source_team_code": row.get("source_team_code", ""),
            "team_id": row.get("frl_team_id", ""),
            "opponent_team_id": row.get("frl_opponent_team_id", ""),
            "was_home": row.get("frl_was_home", ""),
            "player_identity_key": row.get("frl_player_identity_key", ""),
            "player_identity_status": row.get("frl_player_identity_status", ""),
            "player_identity_route": row.get("frl_player_identity_route", ""),
            "participation_status": row.get("frl_participation_status", ""),
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
        "provenance": _row_provenance(candidate_rows, PLAYER_GW, field_name),
    }


def historical_player_fixture_values(*, season: str, fixture_id: str, field_name: str) -> dict:
    """Resolve an approved historical FPL player-fixture field.

    The decade-spanning historical player/gameweek materialisation stores its
    fixture relationship directly in ``fixture``. This function keeps that
    evidence behind the FPL access seam so GUI consumers do not read the CSV.
    """
    if field_name not in HISTORICAL_PLAYER_FIXTURE_FIELDS:
        raise FPLVariableUnavailableError(
            f"Historical FPL player-fixture field '{field_name}' is not supported by this access seam."
        )

    path = HISTORICAL_PLAYER_FIXTURES / f"{season}_all_players_gw.csv"
    rows = _load(path)
    candidate_rows = tuple(
        row
        for row in rows
        if str(row.get("fixture", "")).strip() == str(fixture_id)
    )

    results = []
    for row in candidate_rows:
        raw_value = row.get(field_name)
        if raw_value in (None, ""):
            continue
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            continue
        results.append(
            {
                "season": season,
                "fixture_id": str(fixture_id),
                "player_id": str(row.get("element", "")).strip(),
                "player_name": row.get("name", ""),
                "minutes": row.get("minutes", ""),
                "team": row.get("team", ""),
                "opponent_team": row.get("opponent_team", ""),
                "was_home": row.get("was_home", ""),
                "source_field": field_name,
                "value": value,
            }
        )

    return {
        "query_type": "frl_fpl_variable",
        "research_family": "FPL",
        "variable": field_name,
        "subclass": "PERFORMANCE",
        "season": season,
        "fixture_id": str(fixture_id),
        "results": results,
        "provenance": {
            "evidence_table": str(path),
            "source_field": field_name,
            "relationship": "historical FPL player-fixture evidence",
        },
    }


def player_fixture_values(*, season: str, fixture_id: str, field_name: str) -> dict:
    """Resolve an FPL player variable for one historical fixture."""
    if field_name in HISTORICAL_PLAYER_FIXTURE_FIELDS:
        return historical_player_fixture_values(
            season=season,
            fixture_id=fixture_id,
            field_name=field_name,
        )

    definition = fpl_variable_definition(field_name)
    _require_representation(field_name, "FPL_PLAYER_FIXTURE")
    rows = _load(PLAYER_GW)
    candidate_rows = tuple(
        row
        for row in rows
        if str(row.get("frl_season", "")) == str(season)
        and str(row.get("frl_fixture_id", "")) == str(fixture_id)
    )
    key = _require_source_column(candidate_rows if candidate_rows else rows, field_name)

    results = [
        {
            "season": season,
            "fixture_id": str(fixture_id),
            "player_id": str(row.get("frl_fpl_player_key", "")),
            "player_code": str(row.get("source_player_code", "")),
            "player_name": " ".join(
                part for part in (row.get("source_first_name", ""), row.get("source_second_name", "")) if part
            ),
            "position": row.get("source_position", ""),
            "minutes": row.get("source_minutes", ""),
            "team_id": row.get("frl_team_id", ""),
            "opponent_team_id": row.get("frl_opponent_team_id", ""),
            "was_home": row.get("frl_was_home", ""),
            "player_identity_key": row.get("frl_player_identity_key", ""),
            "player_identity_status": row.get("frl_player_identity_status", ""),
            "player_identity_route": row.get("frl_player_identity_route", ""),
            "participation_status": row.get("frl_participation_status", ""),
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
            **_row_provenance(candidate_rows, PLAYER_GW, field_name),
            "relationship": "governed canonical fixture to source-native FPL player-fixture evidence",
        },
    }


def fixture_values(*, season: str, fixture_id: str, field_name: str) -> dict:
    """Resolve an FPL fixture variable from approved evidence."""
    definition = fpl_variable_definition(field_name)
    _require_representation(field_name, "FPL_FIXTURE")
    rows = _load(FIXTURE)
    candidate_rows = tuple(
        row
        for row in rows
        if str(row.get("frl_season", "")) == str(season)
        and str(row.get("frl_fixture_id", "")) == str(fixture_id)
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
        "provenance": _row_provenance(candidate_rows, FIXTURE, field_name),
    }


__all__ = [
    "FPLVariableUnavailableError",
    "fixture_values",
    "fpl_catalogue",
    "fpl_variable_definition",
    "historical_player_fixture_values",
    "player_fixture_rows",
    "player_fixture_values",
    "player_gameweek_values",
]
