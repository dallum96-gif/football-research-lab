from __future__ import annotations
import research_access

def test_player_match_coverage_is_reported_by_season(monkeypatch):
    monkeypatch.setattr(research_access,"player_match_source_fields",lambda season:("successfulDribbles",))
    monkeypatch.setattr(research_access,"player_match_source_rows_for_season",lambda season:({"successfulDribbles":"4"},{"successfulDribbles":""},{"successfulDribbles":"2"}))
    result=research_access.coverage(variable="successfulDribbles",family="player_match",seasons=["2024-25","2025-26"])
    assert result["query_type"]=="research_coverage"
    assert result["family"]=="player_match"
    assert result["season_count"]==2
    assert result["seasons_with_field"]==2
    assert result["seasons_with_observations"]==2
    assert result["population"]==6
    assert result["observed"]==4
    assert result["missing"]==2
    assert result["coverage_pct"]==66.667
    assert [row["coverage_pct"] for row in result["results"]]==[66.667,66.667]

def test_coverage_rejects_empty_season_list():
    try: research_access.coverage(variable="successfulDribbles",family="player_match",seasons=[])
    except research_access.ResearchAccessError as exc: assert "at least one season" in str(exc)
    else: raise AssertionError("coverage() must reject an empty season list")
