"""Empirical catalog over the complete approved source-field universe.

This layer supplements the curated semantic registry. A discovered source field
can therefore be searchable before it has been semantically promoted, while
coverage and source provenance remain visible.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from player_metadata_source import source_fields as squad_source_fields
from source_family_adapters import (
    player_match_source_fields,
    player_season_source_fields,
    team_match_source_fields,
)
from source_field_registry import fields_for_family

ROOT = Path(__file__).resolve().parent
SEASONS = (
    "2016-17", "2017-18", "2018-19", "2019-20", "2020-21",
    "2021-22", "2022-23", "2023-24", "2024-25", "2025-26",
)
FAMILIES = ("team_match", "player_match", "player_season", "squad")


def _source_fields(family: str, season: str) -> tuple[str, ...]:
    if family == "team_match":
        return team_match_source_fields(season)
    if family == "player_match":
        return player_match_source_fields(season)
    if family == "player_season":
        return player_season_source_fields(season)
    return squad_source_fields(season)


def build_catalog(
    seasons: tuple[str, ...] = SEASONS,
    families: tuple[str, ...] = FAMILIES,
) -> tuple[dict, ...]:
    observed: dict[tuple[str, str], set[str]] = defaultdict(set)
    for season in seasons:
        for family in families:
            for field in _source_fields(family, season):
                observed[(family, field)].add(season)

    registry = {
        (spec.family, spec.source_field): spec
        for family in families
        for spec in fields_for_family(family)
    }

    rows: list[dict] = []
    for (family, field), present in sorted(observed.items()):
        seasons_present = len(present)
        spec = registry.get((family, field))
        if seasons_present == len(seasons):
            coverage = "CORE_DECADE"
        elif seasons_present >= 5:
            coverage = "LONG_RUN"
        elif seasons_present >= 2:
            coverage = "INTERMITTENT"
        else:
            coverage = "SINGLE_SEASON"

        rows.append({
            "family": family,
            "source_field": field,
            "registry_status": spec.semantic_status if spec else "UNCATALOGUED",
            "frl_field": spec.frl_field if spec else None,
            "notes": spec.notes if spec else "Discovered in approved source; semantic review pending.",
            "first_seen_season": min(present),
            "last_seen_season": max(present),
            "seasons_present": seasons_present,
            "seasons_total": len(seasons),
            "coverage_class": coverage,
        })
    return tuple(rows)


def field_metadata(family: str, field: str, seasons: tuple[str, ...] = SEASONS) -> dict:
    for row in build_catalog(seasons=seasons, families=(family,)):
        if row["source_field"] == field:
            return row
    raise ValueError(f"Unknown source field: {family}.{field}")
