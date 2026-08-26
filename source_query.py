"""Generic research access to source-native variables.

The query layer deliberately accepts source-field names rather than requiring a
new bespoke metric function for every variable. Results preserve the source
field, FRL relationship keys, source IDs and availability notes so exploratory
queries remain evidence-bearing.
"""
from __future__ import annotations

from collections import defaultdict
from functools import lru_cache

from source_family_adapters import (
    player_match_source_fields,
    player_match_source_rows,
    player_season_source_fields,
    player_season_source_rows,
    team_match_source_fields,
    team_match_source_rows,
)
from player_metadata_source import available_fields as squad_source_fields
from player_metadata_source import source_rows as squad_source_rows
from source_field_registry import fields_for_family


FAMILIES = ("team_match", "player_match", "player_season", "squad")


def searchable_fields(family: str | None = None, season: str | None = None) -> tuple[str, ...]:
    """Return source fields that can currently be queried through adapters.

    When season is supplied, the result is restricted to fields actually
    present in that season's source files. Registry metadata remains available
    separately and does not hide source fields merely because they are not yet
    semantically classified.
    """
    families = (family,) if family else FAMILIES
    fields: set[str] = set()
    for selected in families:
        if selected == "team_match" and season:
            fields.update(team_match_source_fields(season))
        elif selected == "player_match" and season:
            fields.update(player_match_source_fields(season))
        elif selected == "player_season" and season:
            fields.update(player_season_source_fields(season))
        elif selected == "squad":
            fields.update(squad_source_fields(season))
        else:
            fields.update(
                spec.source_field for spec in fields_for_family(selected)
            )
    return tuple(sorted(fields))


def _require_field(family: str, field: str, season: str) -> None:
    if family not in FAMILIES:
        raise ValueError(f"Unknown source family: {family}")
    available = set(searchable_fields(family, season))
    if field not in available:
        raise ValueError(
            f"Source field '{field}' is not available in {family} for {season}."
        )


def source_field_values(
    family: str,
    season: str,
    field: str,
    *,
    fixture_id: str | None = None,
    team_id: str | None = None,
    player_id: str | None = None,
) -> dict:
    """Return raw source-field values with FRL/source relationship context."""
    _require_field(family, field, season)
    values: list[dict] = []

    if family == "team_match":
        if fixture_id:
            fixture_ids = (str(fixture_id),)
        else:
            # Enumerating canonical fixtures is intentionally left to callers
            # that need season-wide data; this function accepts a fixture ID
            # for direct evidence retrieval.
            raise ValueError("team_match source queries require fixture_id")

        for fid in fixture_ids:
            home, away = team_match_source_rows(season, fid)
            for venue, row in (("home", home), ("away", away)):
                if team_id and str(row.get("team_id", "")) != str(team_id):
                    continue
                values.append({
                    "season": season,
                    "fixture_id": str(fid),
                    "venue": venue,
                    "source_match_id": str(row.get("matchId", "")),
                    "source_team_id": str(row.get("team_id", "")),
                    "source_field": field,
                    "value": row.get(field),
                })

    elif family == "player_match":
        rows = player_match_source_rows(season, fixture_id) if fixture_id else ()
        for row in rows:
            source_id = str(row.get("playerId", "")).strip()
            if player_id and source_id != str(player_id).strip():
                continue
            values.append({
                "season": season,
                "fixture_id": str(fixture_id) if fixture_id else None,
                "source_match_id": str(row.get("matchId", "")),
                "source_player_id": source_id,
                "source_team_id": str(row.get("team_id", "")),
                "source_field": field,
                "value": row.get(field),
            })

    elif family == "player_season":
        for row in player_season_source_rows(season):
            source_id = str(row.get("playerId", "")).strip()
            if player_id and source_id != str(player_id).strip():
                continue
            values.append({
                "season": season,
                "source_player_id": source_id,
                "source_team_id": str(row.get("team_id", "")),
                "source_field": field,
                "value": row.get(field),
            })

    else:
        for row in squad_source_rows(season):
            source_id = str(row.get("playerId", "")).strip()
            if player_id and source_id != str(player_id).strip():
                continue
            values.append({
                "season": season,
                "source_player_id": source_id,
                "source_field": field,
                "value": row.get(field),
            })

    return {
        "query_type": "source_field_values",
        "family": family,
        "season": season,
        "field": field,
        "filters": {
            "fixture_id": fixture_id,
            "team_id": team_id,
            "player_id": player_id,
        },
        "source_rows": len(values),
        "results": values,
    }


def top_source_field(
    family: str,
    season: str,
    field: str,
    *,
    limit: int = 10,
) -> dict:
    """Rank numeric source fields at the natural searchable entity grain."""
    _require_field(family, field, season)
    totals: defaultdict[str, float] = defaultdict(float)
    labels: dict[str, str] = {}

    if family == "player_match":
        rows = player_match_source_rows(season, "")
        # Season-wide player-match ranking is not routed through a fake fixture.
        rows = []
        raise ValueError("Use source_field_values for fixture-scoped player_match fields")

    if family == "player_season":
        for row in player_season_source_rows(season):
            key = str(row.get("playerId", "")).strip()
            raw = row.get(field)
            try:
                totals[key] += float(raw)
            except (TypeError, ValueError):
                continue
            labels[key] = row.get("playerName", key)
    elif family == "squad":
        raise ValueError("Squad metadata is descriptive, not a ranking source")
    else:
        raise ValueError("Use fixture-scoped team_match values for team-match ranking")

    ranked = sorted(totals.items(), key=lambda item: (-item[1], labels[item[0]].casefold()))[:limit]
    return {
        "query_type": "top_source_field",
        "family": family,
        "season": season,
        "field": field,
        "results": [
            {"rank": i, "source_player_id": key, "player": labels[key], "value": value}
            for i, (key, value) in enumerate(ranked, start=1)
        ],
    }
