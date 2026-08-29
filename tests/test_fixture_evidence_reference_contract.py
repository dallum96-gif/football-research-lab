from __future__ import annotations

import fixture_evidence
import fixture_research_access


def _verified_bridge(pulselive_player_id: str, player_match_source_player_id: str) -> dict:
    return {
        "pulselive_source_player_id": pulselive_player_id,
        "pulselive_source_player_id_namespace": "pulselive_match.playerId",
        "player_match_source_player_id": player_match_source_player_id,
        "player_match_source_player_id_namespace": "players_match_stats.playerId",
        "identity_route": "PULSELIVE_PLAYER_ID_TO_PLAYER_MATCH_PL_CODE_TO_SOURCE_PLAYER_ID",
        "bridge_source_field": "players_match_stats.pl_code",
        "relationship_contract": "source_player_match_to_source_player_identity",
        "relationship_status": "VERIFIED",
        "identity_status": "VERIFIED",
        "verified": True,
    }


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
    monkeypatch.setattr(
        fixture_evidence,
        "resolve_pulselive_player_identity",
        lambda season, fixture_id, player_id: _verified_bridge(
            str(player_id),
            f"pm-{player_id}",
        ) if player_id else {
            **_verified_bridge("", ""),
            "relationship_status": "UNAVAILABLE",
            "identity_status": "UNAVAILABLE",
            "verified": False,
            "player_match_source_player_id": None,
            "player_match_source_player_id_namespace": None,
        },
    )
    monkeypatch.setattr(fixture_evidence, "source_player_season_identity", lambda season, player_id: {"verified": True, "status": "VERIFIED"})

    result = fixture_evidence.fixture_evidence("2016-17", "8")
    assert result["status"] == "AVAILABLE"
    assert result["coverage"]["events"]["count"] == 2
    assert result["formation"]["home"]["value"] == "4-2-3-1"
    assert result["formation"]["away"]["value"] == "4-3-3"
    assert result["managers"]["status"] == "AVAILABLE"
    assert result["events"][0]["assist"]["source_player_id"] == "12"
    assert result["events"][0]["assist"]["source_player_id_namespace"] == "pulselive_match.playerId"
    assert result["events"][0]["assist"]["player_match_source_player_id"] == "pm-12"
    assert result["lineup"][0]["player"]["source_player_id"] == "11"
    assert result["lineup"][0]["player"]["player_match_source_player_id"] == "pm-11"
    assert result["lineup"][0]["provenance"]["identity_bridge_status"] == "VERIFIED"


def test_reference_composition_uses_ura_for_participation(monkeypatch) -> None:
    monkeypatch.setattr(fixture_research_access, "fixture_evidence", lambda season, fixture_id: {
        "status": "AVAILABLE",
        "lineup": [{
            "player": {"source_player_id": "11", "name": "Home Player"},
            "side": "home",
            "provenance": {"source_family": "pulselive_match_lineups"},
        }],
        "events": [], "coverage": {"lineup": {"status": "AVAILABLE", "count": 1}},
        "limitations": [], "provenance": {},
    })
    monkeypatch.setattr(
        fixture_research_access,
        "resolve_pulselive_player_identity",
        lambda season, fixture_id, player_id: _verified_bridge(str(player_id), "pm-11"),
    )

    def fake_query(request):
        values = {"minutesPlayed": 90, "substitute": "false", "venue": "home"}
        return {"results": [{"source_player_id": "pm-11", "value": values[request.variable]}]}

    monkeypatch.setattr(fixture_research_access.research_access, "query", fake_query)
    result = fixture_research_access.fixture_research_result("2016-17", "8")
    assert result["lineup"][0]["participation"] == "starting"
    assert result["lineup"][0]["minutes"] == 90
    assert result["lineup"][0]["player"]["source_player_id"] == "11"
    assert result["lineup"][0]["player"]["player_match_source_player_id"] == "pm-11"
    assert result["lineup"][0]["provenance"]["participation_lookup_source_player_id"] == "pm-11"


def test_reference_composition_rejects_ambiguous_bridge_for_ura(monkeypatch) -> None:
    monkeypatch.setattr(fixture_research_access, "fixture_evidence", lambda season, fixture_id: {
        "status": "AVAILABLE",
        "lineup": [{
            "player": {"source_player_id": "11", "name": "Home Player"},
            "side": "home",
            "provenance": {"source_family": "pulselive_match_lineups"},
        }],
        "events": [], "coverage": {"lineup": {"status": "AVAILABLE", "count": 1}},
        "limitations": [], "provenance": {},
    })
    monkeypatch.setattr(
        fixture_research_access,
        "resolve_pulselive_player_identity",
        lambda season, fixture_id, player_id: {
            **_verified_bridge(str(player_id), ""),
            "relationship_status": "AMBIGUOUS",
            "identity_status": "AMBIGUOUS",
            "verified": False,
            "candidate_source_player_ids": ["pm-11", "pm-12"],
            "player_match_source_player_id": None,
            "player_match_source_player_id_namespace": None,
        },
    )
    monkeypatch.setattr(
        fixture_research_access.research_access,
        "query",
        lambda request: {"results": [{"source_player_id": "pm-11", "value": 90}]},
    )

    result = fixture_research_access.fixture_research_result("2016-17", "8")

    assert result["lineup"][0]["participation"] == "unknown"
    assert result["lineup"][0]["minutes"] is None
    assert result["lineup"][0]["player"]["source_player_id"] == "11"
    assert result["lineup"][0]["player"]["player_match_source_player_id"] is None
    assert result["lineup"][0]["provenance"]["identity_bridge_status"] == "AMBIGUOUS"


def test_player_match_fallback_keeps_source_match_namespaces_distinct(monkeypatch) -> None:
    monkeypatch.setattr(fixture_evidence, "canonical_fixture", lambda season, fixture_id: {
        "season": season,
        "fixture_id": fixture_id,
        "home_team_id": "100",
        "away_team_id": "200",
    })
    monkeypatch.setattr(fixture_evidence, "resolve_source_match", lambda season, fixture_id: {
        "source_match_id": "1059976",
        "relationship_status": "VERIFIED",
        "resolution_basis": "VERIFIED_FIXTURE_CORRECTION",
        "fixture_correction": {"status": "VERIFIED_CORRECTION"},
        "home": {"team_id": "1"},
        "away": {"team_id": "2"},
    })
    monkeypatch.setattr(fixture_evidence, "load_snapshot", lambda source_match_id: (None, None))
    monkeypatch.setattr(fixture_evidence, "fixture_metadata", lambda season, fixture_id: {})
    monkeypatch.setattr(fixture_evidence, "fixture_player_match_rows", lambda fixture: ({
        "matchId": "8674008",
        "playerId": "11",
        "playerName": "Home Player",
        "venue": "Home",
        "position": "M",
        "substitute": "false",
        "minutesPlayed": "90",
        "_source_file": "player-match.csv",
    },))

    result = fixture_evidence.fixture_evidence("2019-20", "275")

    assert result["status"] == "AVAILABLE"
    assert result["provenance"]["source_match_id"] == "1059976"
    assert result["provenance"]["source_match_id_namespace"] == "events_stats.matchId"
    assert result["provenance"]["player_match_source_match_id"] == "8674008"
    assert result["provenance"]["player_match_source_match_id_namespace"] == "players_match_stats.matchId"
    assert result["provenance"]["resolution_basis"] == "VERIFIED_FIXTURE_CORRECTION"
    assert result["provenance"]["fixture_correction"]["status"] == "VERIFIED_CORRECTION"
    assert result["lineup"][0]["provenance"]["source_match_id"] == "1059976"
    assert result["lineup"][0]["provenance"]["player_match_source_match_id"] == "8674008"
