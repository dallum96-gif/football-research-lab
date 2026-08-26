from __future__ import annotations
import research_access

def test_validate_exposes_distinct_temporal_semantics():
    request=research_access.ResearchRequest(variable="successfulDribbles",season="2024-25",family="player_match",fixture_id="1",player_id="p1",as_of_date="2025-02-01",information_available_as_of="2025-02-01")
    result=research_access.validate(request)
    assert result["valid"] is True
    assert result["temporal"]["season_state_requested"]=="2024-25"
    assert result["temporal"]["as_of_date"]=="2025-02-01"
    assert result["temporal"]["information_available_as_of"]=="2025-02-01"
    assert result["temporal"]["historical_state_and_information_availability_distinct"] is True
    assert result["temporal"]["information_availability_status"]=="requested"

def test_query_keeps_temporal_and_provenance_envelope(monkeypatch):
    request=research_access.ResearchRequest(variable="successfulDribbles",season="2024-25",family="player_match",fixture_id="1",as_of_date="2025-02-01")
    monkeypatch.setattr(research_access,"resolve_variable",lambda **kwargs:{"results":[{"value":4}],"provenance":{"adapter":"player_match"}})
    result=research_access.query(request)
    assert result["temporal"]["as_of_date"]=="2025-02-01"
    assert result["temporal"]["information_availability_status"]=="not_assessed"
    assert result["provenance"]["family"]=="player_match"
    assert result["provenance"]["source_field"]=="successfulDribbles"
    assert result["provenance"]["adapter"]=="player_match"

def test_coverage_marks_information_availability_as_not_assessed(monkeypatch):
    monkeypatch.setattr(research_access,"_coverage_core",lambda family,season,field:{"season":season,"family":family,"variable":field,"field_present":True,"population":10,"observed":10,"missing":0,"coverage_pct":100.0})
    result=research_access.coverage(variable="successfulDribbles",seasons=["2023-24","2024-25"],family="player_match")
    assert result["coverage_pct"]==100.0
    assert result["temporal"]["historical_state_and_information_availability_distinct"] is True
    assert result["temporal"]["information_availability_status"]=="not_assessed"
