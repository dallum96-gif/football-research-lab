from __future__ import annotations

import fixture_context_research as context


def _route(monkeypatch):
    monkeypatch.setattr(
        context,
        "canonical_fixture",
        lambda season, fixture_id: {
            "season": season,
            "fixture_id": str(fixture_id),
            "home_team_id": "10",
            "away_team_id": "20",
        },
    )
    monkeypatch.setattr(
        context,
        "resolve_source_match",
        lambda season, fixture_id: {
            "source_match_id": "999",
            "relationship_status": "VERIFIED",
            "resolution_basis": "CANONICAL_FIXTURE",
        },
    )
    monkeypatch.setattr(
        context,
        "load_snapshot",
        lambda source_match_id: ({"resources": {}}, "/tmp/match-999/snapshot.json"),
    )
    monkeypatch.setattr(context, "resource_meta", lambda snapshot, resource: {"endpoint": resource})


def test_fixture_events_preserves_event_grain_and_explicit_identity_bridge(monkeypatch):
    _route(monkeypatch)
    monkeypatch.setattr(context, "resource_payload", lambda snapshot, resource: {"payload": resource})
    monkeypatch.setattr(
        context,
        "normalise_events",
        lambda payload: [
            {
                "event_id": "e1",
                "type": "goal",
                "side": "home",
                "minute": "34",
                "seconds": 34,
                "primary_source_player_id": "501",
                "secondary_source_player_id": "502",
                "detail": {"goal_type": "Normal", "card_type": None, "period": "FIRST_HALF", "timestamp": None},
            }
        ],
    )
    monkeypatch.setattr(
        context,
        "resolve_pulselive_player_identity",
        lambda season, fixture_id, source_id: {
            "pulselive_source_player_id": str(source_id),
            "relationship_status": "VERIFIED" if str(source_id) == "501" else "UNRESOLVED",
            "player_match_source_player_id": "pm-501" if str(source_id) == "501" else None,
        },
    )

    result = context.fixture_events("2025-26", "123")

    assert result["query_type"] == "fixture_event_evidence"
    assert result["event_count"] == 1
    row = result["results"][0]
    assert row["fixture_id"] == "123"
    assert row["source_match_id"] == "999"
    assert row["frl_team_id"] == "10"
    assert row["primary_source_player_id"] == "501"
    assert row["primary_player_identity"]["relationship_status"] == "VERIFIED"
    assert row["secondary_player_identity"]["relationship_status"] == "UNRESOLVED"
    assert result["provenance"]["resource"] == "events"


def test_fixture_tactical_context_attaches_verified_fixture_side_without_inventing_manager_identity(monkeypatch):
    _route(monkeypatch)
    monkeypatch.setattr(context, "resource_payload", lambda snapshot, resource: {"payload": resource})
    monkeypatch.setattr(
        context,
        "normalise_lineups",
        lambda payload: {
            "players": [
                {
                    "side": "away",
                    "source_player_id": "601",
                    "name": "Away Player",
                    "position": "MID",
                    "shirt_number": "8",
                    "source_team_id": "source-away",
                    "source_formation_order": {"line_index": 2, "slot_index": 1, "line_size": 3},
                }
            ],
            "formations": {
                "home": {"status": "AVAILABLE", "value": "4-3-3"},
                "away": {"status": "AVAILABLE", "value": "4-2-3-1"},
            },
            "placements": {"home": [], "away": [{"source_player_id": "601", "x": 50, "y": 60}]},
            "managers": {
                "status": "AVAILABLE",
                "items": [{"side": "away", "source_manager_id": "m2", "first_name": "A", "last_name": "Coach", "type": "manager"}],
            },
            "team_context": {"home": "source-home", "away": "source-away"},
            "raw_team_payload_present": {"home": True, "away": True},
        },
    )
    monkeypatch.setattr(
        context,
        "resolve_pulselive_player_identity",
        lambda season, fixture_id, source_id: {
            "pulselive_source_player_id": str(source_id),
            "relationship_status": "VERIFIED",
            "player_match_source_player_id": "pm-601",
        },
    )

    result = context.fixture_tactical_context("2025-26", "123")

    assert result["query_type"] == "fixture_tactical_context"
    assert result["players"][0]["frl_team_id"] == "20"
    assert result["players"][0]["player_identity"]["relationship_status"] == "VERIFIED"
    assert result["formations"]["home"]["frl_team_id"] == "10"
    assert result["formations"]["away"]["value"] == "4-2-3-1"
    assert result["managers"]["items"][0]["source_manager_id"] == "m2"
    assert "manager_identity" not in result["managers"]["items"][0]
    assert result["provenance"]["resource"] == "lineups"


def test_fixture_context_fails_closed_when_snapshot_is_missing(monkeypatch):
    monkeypatch.setattr(
        context,
        "canonical_fixture",
        lambda season, fixture_id: {"season": season, "fixture_id": str(fixture_id)},
    )
    monkeypatch.setattr(
        context,
        "resolve_source_match",
        lambda season, fixture_id: {"source_match_id": "999"},
    )
    monkeypatch.setattr(context, "load_snapshot", lambda source_match_id: (None, None))

    try:
        context.fixture_events("2025-26", "123")
    except context.FixtureContextUnavailableError as exc:
        assert "snapshot unavailable" in str(exc).casefold()
    else:
        raise AssertionError("Missing preserved snapshot must fail closed")
