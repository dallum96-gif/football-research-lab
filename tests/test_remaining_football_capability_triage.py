from __future__ import annotations

from scripts.triage_remaining_football_capabilities import build_triage, triage_rows


def _rows():
    return [
        {
            "resource": "stats",
            "path": "[].stats.totalPass",
            "leaf_name": "totalPass",
            "entity_level": "Team-match statistic",
            "logical_family": "Passing",
        },
        {
            "resource": "events",
            "path": "homeTeam.goals[].minute",
            "leaf_name": "minute",
            "entity_level": "Event",
            "logical_family": "Events",
        },
        {
            "resource": "lineups",
            "path": "homeTeam.players[].position",
            "leaf_name": "position",
            "entity_level": "Player / lineup",
            "logical_family": "Lineups & roles",
        },
        {
            "resource": "lineups",
            "path": "homeTeam.formation",
            "leaf_name": "formation",
            "entity_level": "Team / lineup",
            "logical_family": "Lineups & roles",
        },
        {
            "resource": "match",
            "path": "managers[].name",
            "leaf_name": "name",
            "entity_level": "Manager",
            "logical_family": "Managers",
        },
        {
            "resource": "__snapshot_meta__",
            "path": "captured_at",
            "leaf_name": "captured_at",
            "entity_level": "Capture metadata",
            "logical_family": "Capture & provenance",
        },
    ]


def test_triage_excludes_team_stats_and_capture_metadata():
    rows = triage_rows(_rows())

    assert len(rows) == 4
    assert all(row["workstream"] != "TEAM_MATCH_STATISTICS" for row in rows)
    assert all(row["entity_level"] != "Capture metadata" for row in rows)


def test_triage_routes_event_timing_and_lineup_tactics():
    rows = triage_rows(_rows())
    by_path = {row["path"]: row for row in rows}

    assert by_path["homeTeam.goals[].minute"]["subworkstream"] == "EVENT_GOALS_AND_ASSISTS"
    assert by_path["homeTeam.goals[].minute"]["analytical_role"] == "ANALYTICAL_EVENT_EVIDENCE"
    assert by_path["homeTeam.goals[].minute"]["product_priority"] == "P0"

    assert by_path["homeTeam.players[].position"]["subworkstream"] == "PLAYER_LINEUP_ROLE_POSITION"
    assert by_path["homeTeam.formation"]["subworkstream"] == "TEAM_FORMATION"
    assert by_path["homeTeam.formation"]["product_priority"] == "P0"


def test_build_triage_preserves_remaining_path_count():
    result = build_triage(_rows())

    assert result["remaining_football_match_paths"] == 4
    assert result["workstream_counts"]["EVENTS"] == 1
    assert result["workstream_counts"]["PLAYER_LINEUP_CONTEXT"] == 1
    assert result["workstream_counts"]["TEAM_LINEUP_CONTEXT"] == 1
    assert result["workstream_counts"]["MANAGERS"] == 1
