from __future__ import annotations
import research_access

SEASONS=[f"{year}-{str(year+1)[-2:]}" for year in range(2016,2026)]

def test_discover_exposes_core_domains():
    result=research_access.discover(); families={row["family"] for row in result["results"]}
    assert {"player_match","team_match","player_season","squad"}.issubset(families)

def test_discover_exposes_fpl_domain():
    result=research_access.discover(family="fpl")
    assert result["count"]>0
    assert {row["family"] for row in result["results"]}=={"fpl"}

def test_validate_cross_domain():
    requests=(
        research_access.ResearchRequest("successfulDribbles","2024-25","player_match",fixture_id="1",player_id="p1"),
        research_access.ResearchRequest("goalsFor","2024-25","team_match",fixture_id="1",team_id="t1"),
        research_access.ResearchRequest("appearances","2024-25","player_season",player_id="p1"),
        research_access.ResearchRequest("playerId","2024-25","squad",player_id="p1"),
        research_access.ResearchRequest("elements[].assists","2024-25","fpl",player_id="p1",gameweek="1"),
    )
    for request in requests:
        result=research_access.validate(request)
        assert result["valid"] is True
        assert result["definition"]["family"]==request.family
        assert result["provenance"]["access_layer"]=="FRL universal research access"

def test_successful_dribbles_coverage_across_ten_seasons_has_expected_shape():
    result=research_access.coverage(variable="successfulDribbles",family="player_match",seasons=SEASONS)
    assert result["season_count"]==10
    assert len(result["results"])==10
    assert result["provenance"]["access_layer"]=="FRL universal research access"
