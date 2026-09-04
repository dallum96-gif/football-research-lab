from __future__ import annotations

from scripts.build_football_capability_ledger import build_ledger


def test_ledger_keeps_team_stats_and_remaining_football_paths_in_scope():
    rows = [
        {
            'resource': 'stats',
            'path': '[].stats.totalPass',
            'leaf_name': 'totalPass',
            'entity_level': 'Team-match statistic',
            'logical_family': 'Passing',
            'snapshot_count': '3800',
            'snapshot_coverage_pct': '100.0',
            'value_types': 'integer',
            'sample_values': '500',
            'example_match_ids': '1',
        },
        {
            'resource': 'events',
            'path': 'homeTeam.goals[].minute',
            'leaf_name': 'minute',
            'entity_level': 'Event',
            'logical_family': 'Events',
            'snapshot_count': '3000',
            'snapshot_coverage_pct': '78.9',
            'value_types': 'string',
            'sample_values': '33',
            'example_match_ids': '1',
        },
        {
            'resource': '__snapshot_meta__',
            'path': 'captured_at',
            'leaf_name': 'captured_at',
            'entity_level': 'Capture metadata',
            'logical_family': 'Capture & provenance',
            'snapshot_count': '3800',
            'snapshot_coverage_pct': '100.0',
            'value_types': 'string',
            'sample_values': '2026-01-01',
            'example_match_ids': '1',
        },
    ]

    result = build_ledger(rows)

    assert result['north_star_football_paths'] == 2
    assert result['team_match_statistical_paths'] == 1
    assert result['remaining_football_paths'] == 1
    assert {row['north_star_status'] for row in result['rows']} == {'IN_SCOPE_372'}
    assert {row['workstream'] for row in result['rows']} == {
        'TEAM_MATCH_STATISTICS',
        'EVENTS',
    }


def test_ledger_routes_lineups_and_managers_to_separate_workstreams():
    rows = [
        {
            'resource': 'lineups',
            'path': 'homeTeam.players[].position',
            'leaf_name': 'position',
            'entity_level': 'Player / lineup',
            'logical_family': 'Lineups & roles',
        },
        {
            'resource': 'match',
            'path': 'managers[].name',
            'leaf_name': 'name',
            'entity_level': 'Manager',
            'logical_family': 'Managers',
        },
    ]

    result = build_ledger(rows)
    by_path = {row['path']: row for row in result['rows']}

    assert by_path['homeTeam.players[].position']['workstream'] == 'PLAYER_LINEUP_CONTEXT'
    assert by_path['managers[].name']['workstream'] == 'MANAGERS'
