"""Query-facing extension for broad source-field research.

This module is intentionally separate from the established Query Lab dispatch
until the new evidence query contract has passed the full FRL assurance gates.
It provides a stable callable surface for future natural-language/query APIs.
"""
from __future__ import annotations

from research_field_query import (
    available_fields,
    field_catalog,
    fixture_field_values,
    player_match_field_values,
    player_season_field_values,
    squad_field_values,
    top_player_season_field,
)


def dispatch(query: str, **params):
    queries = {
        "field-catalog": field_catalog,
        "fixture-field": fixture_field_values,
        "player-match-field": player_match_field_values,
        "player-season-field": player_season_field_values,
        "squad-field": squad_field_values,
        "top-player-season-field": top_player_season_field,
        "available-fields": available_fields,
    }
    if query not in queries:
        raise ValueError(
            f"Unknown source-field query '{query}'. "
            f"Available: {', '.join(sorted(queries))}"
        )
    return queries[query](**params)
