from __future__ import annotations

import fixture_evidence
import fixture_research_access


def _snapshot() -> dict:
    return {
        "retrieved_at": "2026-08-27T00:00:00Z",
        "resources": {
            "events": {
                "endpoint": "https://example/events",
                "retrieved_at": "2026-08-27T00:00:00Z",
                "payload": {
                    "homeTeam": {
                        "teamId": "1",
                        "goals": [{"id": "g1", "playerId": "11", "assistPlayerId": "12", "time": "31"}],
                        "cards": [],
                        "subs": [],
                    },
                    "awayTeam": {
                        "teamId": "2",
                        "goals": [{"id": "g2", "playerId": "21", "time": "45+1"}],
                        "cards": [],
                        "subs": [],
                    },
                },
            },
            "lineups": {
                "endpoint": "https://example/lineups",
                "retrieved_at": "2026-08-27T00:00:00Z",
                "payload": {
                    "home_team": {
                        "teamId": "1",
                        "formation": {"formation": "4-2-3-1"},
                        "players": [{"playerId": "11", "displayName": "Home Player", "position": "ST", "shirtNum": "9"},
                                    {"playerId": "12", "displayName": "Assist Player", "position": "AM", "shirtNum": "10"}],
                        "managers": [{"id": "m1", "firstName": "Home", "lastName": "Manager", "type": "manager"}],
                    },
                    "away_team": {
                        "teamId": "2",
                        "formation": {"formation": "4-3-3"},
                        "players": [{"playerId": "21", "displayName": "Away Player", "position": "ST", "shirtNum": "9"}],
                        "managers": [{"id": "m2", "firstName": "Away", "lastName": "Manager", "type": "manager"}],
                    },
                },
            },
        },
    }


def test_reference_fixture_contract_keeps_formation_events_and_managers(monkeypatch) -> None:
    monkeypatch.setattr(fixture_evidence, "canonical_fixture", lambda season, fixture_id: {
        "season": season, "fixture_id": fixture_id, "home_team_id": "100", "away_team_id": "200",
    })
    monkeypatch.setattr(fixture_evidence, "resolve_source_match", lambda season, fixture_id: {
        "source_match_id": "855174", "relationship_status": "VERIFIED",
        "home": {"team_id": "1"}, "away": {"team_id": "2"},
    })
    monkeypatch.setattr(fixture_evidence, "load_snapshot", lambda source_match_id: (_snapshot(), None))
    monkeypatch.setattr(fixture_evidence, "source_player_season_identity", lambda season, player_id: {"verified": True, "status": "VERIFIED"})

    result = fixture_evidence.fixture_evidence("2016-17", "8")
    assert result["status"] == "AVAILABLE"
    assert result["coverage"]["events"]["count"] == 2
    assert result["formation"]["home"]["value"] == "4-2-3-1"
    assert result["formation"]["away"]["value"] == "4-3-3"
    assert result["managers"]["status"] == "AVAILABLE"
    assert result["events"][0]["assist"]["source_player_id"] == "12"


def test_reference_composition_uses_ura_for_participation(monkeypatch) -> None:
    monkeypatch.setattr(fixture_research_access, "fixture_evidence", lambda season, fixture_id: {
        "status": "AVAILABLE",
        "lineup": [{"player": {"source_player_id": "11", "name": "Home Player"}, "side": "home", "provenance": {}}],
        "events": [], "coverage": {"lineup": {"status": "AVAILABLE", "count": 1}},
        "limitations": [], "provenance": {},
    })

    def fake_query(request):
        values = {"minutesPlayed": 90, "substitute": "false", "venue": "home"}
        return {"results": [{"source_player_id": "11", "value": values[request.variable]}]}

    monkeypatch.setattr(fixture_research_access.research_access, "query", fake_query)
    result = fixture_research_access.fixture_research_result("2016-17", "8")
    assert result["lineup"][0]["participation"] == "starting"
    assert result["lineup"][0]["minutes"] == 90
