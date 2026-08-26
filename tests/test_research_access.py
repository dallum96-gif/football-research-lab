from __future__ import annotations

import research_access


def test_validate_core_request():
    request = research_access.ResearchRequest(
        variable="successfulDribbles",
        season="2024-25",
        family="player_match",
        fixture_id="1",
        player_id="p1",
    )

    result = research_access.validate(request)

    assert result["valid"] is True
    assert result["definition"]["family"] == "player_match"
    assert result["definition"]["source_field"] == "successfulDribbles"


def test_validate_fpl_request_uses_registry_path():
    request = research_access.ResearchRequest(
        variable="elements[].assists",
        season="2024-25",
        family="fpl",
        player_id="123",
        gameweek="1",
    )

    result = research_access.validate(request)

    assert result["valid"] is True
    assert result["definition"]["family"] == "fpl"
    assert result["definition"]["source_field"] == "elements[].assists"


def test_query_preserves_governed_result_semantics(monkeypatch):
    request = research_access.ResearchRequest(
        variable="successfulDribbles",
        season="2024-25",
        family="player_match",
        fixture_id="1",
        player_id="p1",
    )

    monkeypatch.setattr(
        research_access,
        "resolve_variable",
        lambda **kwargs: {
            "results": [{"value": 4}],
            "coverage": {"source_rows": 1, "matched_rows": 1},
            "population": {"requested": 1, "observed": 1},
            "source_rows": 1,
            "temporal_note": "as_of=2024-25",
            "limitations": ["illustrative fixture scope"],
            "provenance": {"source_field": "successfulDribbles"},
        },
    )

    result = research_access.query(request)

    assert result["results"] == [{"value": 4}]
    assert result["coverage"]["matched_rows"] == 1
    assert result["population"]["observed"] == 1
    assert result["temporal_note"] == "as_of=2024-25"
    assert result["limitations"] == ["illustrative fixture scope"]
    assert result["provenance"]["source_field"] == "successfulDribbles"


def test_discover_can_filter_by_family_and_search():
    result = research_access.discover(family="fpl", search="assists")

    assert result["query_type"] == "capability_discovery"
    assert result["family"] == "fpl"
    assert result["count"] >= 1
    assert all(item["family"] == "fpl" for item in result["results"])
    assert any("assists" in item["variable"].casefold() for item in result["results"])
