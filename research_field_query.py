"""Coverage-aware generic query access for the broad FRL source universe.

This layer is intentionally evidence-first. It exposes source-native fields for
research without silently turning them into canonical FRL concepts.
"""
from __future__ import annotations

from collections import defaultdict

from player_metadata_source import source_fields as squad_source_fields
from player_metadata_source import source_rows as squad_source_rows
from source_family_adapters import (
    player_match_source_fields,
    player_match_source_rows,
    player_season_source_fields,
    player_season_source_rows,
    team_match_source_fields,
    team_match_source_rows,
)
from source_field_catalog import build_catalog
from source_field_registry import fields_for_family

FAMILIES = ("team_match", "player_match", "player_season", "squad")


def available_fields(family: str, season: str) -> tuple[str, ...]:
    if family not in FAMILIES:
        raise ValueError(f"Unknown source family: {family}")
    if family == "team_match":
        return team_match_source_fields(season)
    if family == "player_match":
        return player_match_source_fields(season)
    if family == "player_season":
        return player_season_source_fields(season)
    return squad_source_fields(season)


def field_catalog(family: str | None = None, season: str | None = None) -> tuple[dict, ...]:
    """Return the semantic registry plus empirically discovered fields.

    When a season is supplied, the season's observed source fields are always
    included even when tests or upstream inspection provide a field that is not
    yet present in the semantic catalogue. Those fields are explicitly marked
    ``UNCATALOGUED`` rather than promoted into FRL concepts.
    """
    families = (family,) if family else FAMILIES
    rows = list(build_catalog(seasons=(season,), families=families)) if season else list(
        build_catalog(families=families)
    )

    if season:
        existing = {(row["family"], row["source_field"]) for row in rows}
        for selected in families:
            for field in sorted(available_fields(selected, season)):
                key = (selected, field)
                if key in existing:
                    continue
                rows.append({
                    "family": selected,
                    "source_field": field,
                    "registry_status": "UNCATALOGUED",
                    "frl_field": None,
                    "notes": "Field observed in requested season but not yet in the empirical catalogue; semantic review pending.",
                    "present_in_season": True,
                })

    return tuple(sorted(rows, key=lambda row: (row["family"], row["source_field"])))


def _require_field(family: str, season: str, field: str) -> None:
    if family not in FAMILIES:
        raise ValueError(f"Unknown source family: {family}")
    if field not in set(available_fields(family, season)):
        raise ValueError(
            f"Source field '{field}' is unavailable in {family} for {season}."
        )


def fixture_field_values(
    season: str,
    fixture_id: str,
    field: str,
    *,
    team_id: str | None = None,
) -> dict:
    _require_field("team_match", season, field)
    home, away = team_match_source_rows(season, fixture_id)
    values = []
    for venue, row in (("home", home), ("away", away)):
        source_team_id = str(row.get("team_id", "")).strip()
        if team_id and source_team_id != str(team_id).strip():
            continue
        values.append({
            "season": season,
            "fixture_id": str(fixture_id),
            "venue": venue,
            "source_match_id": str(row.get("matchId", "")),
            "source_team_id": source_team_id,
            "source_field": field,
            "value": row.get(field),
        })
    return _result("team_match", season, field, values)


def player_match_field_values(
    season: str,
    fixture_id: str,
    field: str,
    *,
    player_id: str | None = None,
) -> dict:
    _require_field("player_match", season, field)
    values = []
    for row in player_match_source_rows(season, fixture_id):
        source_player_id = str(row.get("playerId", "")).strip()
        if player_id and source_player_id != str(player_id).strip():
            continue
        values.append({
            "season": season,
            "fixture_id": str(fixture_id),
            "source_match_id": str(row.get("matchId", "")),
            "source_player_id": source_player_id,
            "source_team_id": str(row.get("team_id", "")),
            "source_field": field,
            "value": row.get(field),
        })
    return _result("player_match", season, field, values)


def player_season_field_values(
    season: str,
    field: str,
    *,
    player_id: str | None = None,
) -> dict:
    _require_field("player_season", season, field)
    values = []
    for row in player_season_source_rows(season):
        source_player_id = str(row.get("playerId", "")).strip()
        if player_id and source_player_id != str(player_id).strip():
            continue
        values.append({
            "season": season,
            "source_player_id": source_player_id,
            "source_team_id": str(row.get("team_id", "")),
            "source_field": field,
            "value": row.get(field),
        })
    return _result("player_season", season, field, values)


def squad_field_values(
    season: str,
    field: str,
    *,
    player_id: str | None = None,
) -> dict:
    _require_field("squad", season, field)
    values = []
    for row in squad_source_rows(season):
        source_player_id = str(row.get("playerId", "")).strip()
        if player_id and source_player_id != str(player_id).strip():
            continue
        values.append({
            "season": season,
            "source_player_id": source_player_id,
            "source_field": field,
            "value": row.get(field),
        })
    return _result("squad", season, field, values)


def top_player_season_field(
    season: str,
    field: str,
    *,
    limit: int = 10,
) -> dict:
    _require_field("player_season", season, field)
    rows = player_season_source_rows(season)
    totals: defaultdict[str, float] = defaultdict(float)
    labels: dict[str, str] = {}
    for row in rows:
        player_id = str(row.get("playerId", "")).strip()
        try:
            value = float(row.get(field, ""))
        except (TypeError, ValueError):
            continue
        totals[player_id] += value
        labels[player_id] = str(row.get("playerName") or player_id)

    ranked = sorted(
        totals.items(),
        key=lambda item: (-item[1], labels[item[0]].casefold()),
    )[:limit]
    return {
        "query_type": "top_player_season_field",
        "family": "player_season",
        "season": season,
        "field": field,
        "source_rows": len(rows),
        "results": [
            {
                "rank": rank,
                "source_player_id": player_id,
                "player": labels[player_id],
                "value": value,
            }
            for rank, (player_id, value) in enumerate(ranked, start=1)
        ],
    }


def _result(family: str, season: str, field: str, values: list[dict]) -> dict:
    catalog_row = next(
        (
            item
            for item in build_catalog(seasons=(season,), families=(family,))
            if item["source_field"] == field
        ),
        None,
    )
    registry = next(
        (item for item in fields_for_family(family) if item.source_field == field),
        None,
    )
    return {
        "query_type": "source_field_values",
        "family": family,
        "season": season,
        "field": field,
        "registry_status": registry.semantic_status if registry else "UNCATALOGUED",
        "frl_field": registry.frl_field if registry else None,
        "coverage": catalog_row,
        "source_rows": len(values),
        "results": values,
        "temporal_note": "Source retrieval does not by itself establish historical availability time.",
    }
