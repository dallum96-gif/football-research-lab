from __future__ import annotations
import variable_resolver

def _raw(**extra):
    return {"results":[{"value":"1"}],"coverage":{"source_rows":1,"matched_rows":1},"temporal_note":"as_of=2024-25","limitations":[],**extra}

def test_backend_acceptance_all_public_families(monkeypatch):
    monkeypatch.setattr(variable_resolver,"player_match_field_values",lambda *a,**k:_raw())
    monkeypatch.setattr(variable_resolver,"fixture_field_values",lambda *a,**k:_raw())
    monkeypatch.setattr(variable_resolver,"player_season_field_values",lambda *a,**k:_raw())
    monkeypatch.setattr(variable_resolver,"squad_field_values",lambda *a,**k:_raw())
    monkeypatch.setattr(variable_resolver,"fpl_player_gameweek_values",lambda **k:_raw(research_family="FPL"))
    results=(
        variable_resolver.resolve_variable("successfulDribbles",season="2024-25",fixture_id="1",player_id="p1"),
        variable_resolver.resolve_variable("goalsFor",season="2024-25",fixture_id="1",family="team_match",team_id="t1"),
        variable_resolver.resolve_variable("appearances",season="2024-25",family="player_season",player_id="p1"),
        variable_resolver.resolve_variable("playerId",season="2024-25",family="squad",player_id="p1"),
        variable_resolver.resolve_variable("total_points",season="2024-25",family="fpl",player_id="p1",gameweek="1"),
    )
    for result in results:
        assert result["results"]
        assert result["coverage"]["source_rows"]==1
        assert result["temporal_note"]=="as_of=2024-25"
        assert result["limitations"]==[]
