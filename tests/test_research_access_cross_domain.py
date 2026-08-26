from __future__ import annotations

import pytest

import research_access


SEASONS = [f"{year}-{str(year + 1)[-2:]}" for year in range(2016, 2026)]


def test_discover_exposes_core_domains():
    result = research_access.discover()
    families = {row["family"] for row in result["results"]}
    assert {"player_match", "team_match", "player_season", "squad"}.issubset(families)


def test_discover_exposes_fpl_domain():
    result = research_access.discover(family="fpl")
    assert result["count"] > 0
    assert {row["family"] for row in result["results"]} == {"fpl"}


@pytest.mark.parametrize(
    "variable,family,kwargs",
    [
        ("successfulDribbles", "player_match", {"fixture_id": "1", "player_id": "p1"}),
        ("goalsFor", "team_match", {"fixture_id": "1", "team_id": "t1"}),
        ("appearances", "player_season", {"player_id": "p1"}),
        ("playerId", "squad", {"player_id": "p1"}),
        ("elements[].assists", "fpl", {"player_id": "p1", "gameweek": "1"}),
    ],
)
def test_validate_cross_domain(variable, family, kwargs):
    result = research_access.validate(
        research_access.ResearchRequest(
            variable=variable,
            season="2024-25",
            family=family,
            **kwargs,
        )
    )
    assert result["valid"] is True
    assert result["definition"]["family"] == family
    assert result["provenance"]["access_layer"] == "FRL universal research access"
    assert result["temporal"]["historical_state_and_information_availability_distinct"] is True


def test_successful_dribbles_coverage_across_ten_seasons_has_expected_shape():
    result = research_access.coverage(
        variable="successfulDribbles",
        family="player_match",
        seasons=SEASONS,
    )
    assert result["variable"] == "successfulDribbles"
    assert result["family"] == "player_match"
    assert result["season_count"] == 10
    assert len(result["results"]) == 10
    assert result["provenance"]["access_layer"] == "FRL universal research access"
    assert result["temporal"]["historical_state_and_information_availability_distinct"] is True


def test_query_separates_temporal_and_information_availability(monkeypatch):
    monkeypatch.setattr(
        research_access,
        "resolve_variable",
        lambda **kwargs: {
            "results": [{"value": 1}],
            "coverage": {"source_rows": 1, "matched_rows": 1},
            "population": 1,
            "source_rows": 1,
            "limitations": [],
            "provenance": {"fixture": "test"},
        },
    )
    result = research_access.query(
        research_access.ResearchRequest(
            variable="successfulDribbles",
            season="2024-25",
            family="player_match",
            fixture_id="1",
            player_id="p1",
            as_of_date="2024-09-01",
            information_available_as_of="2024-09-02",
        )
    )
    assert result["temporal"]["as_of_date"] == "2024-09-01"
    assert result["temporal"]["information_available_as_of"] == "2024-09-02"
    assert result["provenance"]["fixture"] == "test"


def test_cross_domain_contract_is_storage_agnostic(monkeypatch):
    monkeypatch.setattr(
        research_access,
        "resolve_variable",
        lambda **kwargs: {"results": [{"value": 1}], "coverage": {}, "limitations": []},
    )
    for request in (
        research_access.ResearchRequest("successfulDribbles", "2024-25", "player_match", fixture_id="1", player_id="p1"),
        research_access.ResearchRequest("goalsFor", "2024-25", "team_match", fixture_id="1", team_id="t1"),
        research_access.ResearchRequest("appearances", "2024-25", "player_season", player_id="p1"),
        research_access.ResearchRequest("playerId", "2024-25", "squad", player_id="p1"),
    ):
        result = research_access.query(request)
        assert result["results"]
        assert result["definition"]["family"] == request.family
