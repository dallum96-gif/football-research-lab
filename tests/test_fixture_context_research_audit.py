from __future__ import annotations

import scripts.audit_fixture_context_research as audit


def test_fixture_context_audit_summarises_event_tactical_and_identity_coverage(monkeypatch):
    monkeypatch.setattr(
        audit,
        "season_fixtures",
        lambda season: ({"fixture_id": "1"}, {"fixture_id": "2"}),
    )

    def events(season, fixture_id):
        return {
            "results": [
                {
                    "type": "goal",
                    "primary_player_identity": {"relationship_status": "VERIFIED"},
                    "secondary_player_identity": {"relationship_status": "UNRESOLVED"},
                },
                {
                    "type": "card",
                    "primary_player_identity": {"relationship_status": "VERIFIED"},
                    "secondary_player_identity": None,
                },
            ]
        }

    def tactical(season, fixture_id):
        return {
            "players": [
                {"player_identity": {"relationship_status": "VERIFIED"}},
                {"player_identity": {"relationship_status": "UNRESOLVED"}},
            ],
            "formations": {
                "home": {"status": "AVAILABLE", "value": "4-3-3"},
                "away": {"status": "UNAVAILABLE", "value": None},
            },
            "managers": {"status": "AVAILABLE", "items": [{"source_manager_id": "m1"}]},
        }

    monkeypatch.setattr(audit, "fixture_events", events)
    monkeypatch.setattr(audit, "fixture_tactical_context", tactical)

    result = audit.build_audit(seasons=("2025-26",))

    assert result["fixture_count"] == 2
    assert result["event_status_counts"] == {"PASS": 2}
    assert result["tactical_context_status_counts"] == {"PASS": 2}
    assert result["total_events"] == 4
    assert result["event_type_counts"] == {"goal": 2, "card": 2, "substitution": 0}
    assert result["event_identity_counts"]["primary_verified"] == 4
    assert result["event_identity_counts"]["secondary_unresolved"] == 2
    assert result["lineup_player_rows"] == 4
    assert result["lineup_identity_counts"] == {"verified": 2, "unresolved": 2}
    assert result["formation_sides_available"] == 2
    assert result["manager_rows"] == 2


def test_fixture_context_audit_retains_unavailable_state(monkeypatch):
    monkeypatch.setattr(audit, "season_fixtures", lambda season: ({"fixture_id": "1"},))

    def unavailable(*args, **kwargs):
        raise audit.FixtureContextUnavailableError("snapshot unavailable")

    monkeypatch.setattr(audit, "fixture_events", unavailable)
    monkeypatch.setattr(audit, "fixture_tactical_context", unavailable)

    result = audit.build_audit(seasons=("2025-26",))

    assert result["event_status_counts"] == {"UNAVAILABLE": 1}
    assert result["tactical_context_status_counts"] == {"UNAVAILABLE": 1}
    assert result["rows"][0]["events_error"] == "snapshot unavailable"
    assert result["rows"][0]["tactical_context_error"] == "snapshot unavailable"
