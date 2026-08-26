import research_access


def test_universal_research_access_public_surface():
    assert callable(research_access.discover)
    assert callable(research_access.validate)
    assert callable(research_access.coverage)
    assert callable(research_access.query)


def test_research_request_keeps_temporal_context_out_of_resolver_payload():
    request = research_access.ResearchRequest(
        variable="successfulDribbles",
        season="2024-25",
        family="player_match",
        fixture_id="1",
        player_id="p1",
        as_of_date="2024-12-01",
        information_available_as_of="2024-12-01",
    )
    payload = request.resolver_dict()
    assert payload["variable"] == "successfulDribbles"
    assert payload["season"] == "2024-25"
    assert "as_of_date" not in payload
    assert "information_available_as_of" not in payload


def test_discovery_and_result_contract_names_are_stable(monkeypatch):
    discovery = research_access.discover(search="successfulDribbles")
    assert discovery["query_type"] == "capability_discovery"
    assert "access_version" in discovery
    assert "provenance" in discovery

    monkeypatch.setattr(
        research_access,
        "resolve_variable",
        lambda **kwargs: {
            "results": [{"value": 1}],
            "coverage": {"source_rows": 1, "matched_rows": 1},
            "population": 1,
            "source_rows": [{"value": 1}],
            "limitations": [],
            "provenance": {"test": True},
        },
    )

    result = research_access.query(
        research_access.ResearchRequest(
            variable="successfulDribbles",
            season="2024-25",
            family="player_match",
            fixture_id="1",
            player_id="p1",
        )
    )
    assert result["query_type"] == "research_access"
    assert result["results"]
    assert "temporal" in result
    assert "provenance" in result
    assert "limitations" in result
