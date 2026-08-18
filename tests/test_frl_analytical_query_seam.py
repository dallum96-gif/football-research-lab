from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import frl_analytical
import query_api


def test_research_result_contract_is_complete() -> None:
    result = frl_analytical.league_table("2025-26")
    payload = result.to_dict()

    required = {
        "query_type",
        "query_version",
        "parameters",
        "columns",
        "rows",
        "population",
        "provenance",
        "temporal_context",
        "limitations",
        "generated_at",
    }
    assert required.issubset(payload)
    assert payload["query_type"] == "league_table"
    assert payload["population"]["team_rows"] == 20
    assert len(payload["rows"]) == 20


def test_league_table_matches_trusted_query_api() -> None:
    analytical = frl_analytical.league_table("2025-26")
    trusted = query_api.league_table("2025-26")

    fields = [
        "team",
        "played",
        "wins",
        "draws",
        "losses",
        "goals_for",
        "goals_against",
        "goal_difference",
        "points",
        "position",
    ]

    for expected, actual in zip(trusted["teams"], analytical.rows):
        for field in fields:
            assert str(expected[field]) == str(actual[field])


def test_team_fixture_result_is_reusable() -> None:
    result = frl_analytical.team_fixtures("2025-26", "Arsenal")
    assert result.query_type == "team_fixtures"
    assert result.population["requested_team"] == "Arsenal"
    assert result.rows
    assert {row["venue"] for row in result.rows} <= {"home", "away"}
    assert all(row["team"] == "Arsenal" for row in result.rows)
