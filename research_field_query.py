"""Coverage-aware generic query access for the broad FRL source universe.

This layer is intentionally evidence-first. It exposes source-native fields for
research without silently turning them into canonical FRL concepts.

Design constraints:
- source identifiers remain source-local;
- fields must exist in the requested season before values are returned;
- fixture-scoped team/player-match access must pass the existing verified bridge;
- player-season/squad access remains source-native until identity promotion;
- result objects retain field, family, season and source identity context;
- no temporal/as-of claim is made unless the caller supplies one through a
  future availability-aware layer.
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
    families = (family,) if family else FAMILIES
    output = []
    for selected in families:
        registry = {spec.source_field: spec for spec in fields_for_family(selected)}
        source_fields = set(available_fields(selected, season)) if season else set(registry)
        for field in sorted(source_fields | set(registry)):
            spec = registry.get(field)
            output.append({
                "family": selected,
                "source_field": field,
                "registry_status": spec.semantic_status if spec else "UNCATALOGUED",
                "frl_field": spec.frl_field if spec else None,
                "notes": spec.notes if spec else "Field discovered in source; semantic review pending.",
                "present_in_season": field in source_fields if season else None,
            })
    return tuple(output)


def _require_field(family: str, season: str, field: str) -> None:
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
    """Return both sides of one canonical fixture for a team-match field."""
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
    """Return player-match values for one canonical fixture."""
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
    """Return source-native player-season values for a season."""
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
    """Return source-native squad metadata for a season."""
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
    """Rank numeric player-season source fields without inventing a new metric."""
    rows = player_season_source_rows(season)
    _require_field("player_season", season, field)
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
    spec = next(
        (item for item in fields_for_family(family) if item.source_field == field),
        None,
    )
    return {
        "query_type": "source_field_values",
        "family": family,
        "season": season,
        "field": field,
        "registry_status": spec.semantic_status if spec else "UNCATALOGUED",
        "frl_field": spec.frl_field if spec else None,
        "source_rows": len(values),
        "results": values,
        "temporal_note": "Source retrieval does not by itself establish historical availability time.",
    }
