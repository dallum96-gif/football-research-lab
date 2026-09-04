from __future__ import annotations

import json
from pathlib import Path

from scripts.catalogue_pulselive_snapshot_variables import catalogue_archive, write_catalogue


def _write_snapshot(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding='utf-8')


def test_catalogue_classifies_team_player_event_and_metadata_fields(tmp_path: Path) -> None:
    snapshot = tmp_path / 'match-123' / 'snapshot.json'
    _write_snapshot(
        snapshot,
        {
            'fixture': {'id': '123', 'kickoff': '2026-08-20T19:00:00Z'},
            'source_match_id': '123',
            'resources': {
                'stats': {
                    'endpoint': '/stats/123',
                    'retrieved_at': '2026-08-20T21:00:00Z',
                    'payload': [
                        {
                            'teamId': 1,
                            'stats': {
                                'totalPass': 500,
                                'accuratePass': 450,
                                'possessionPercentage': 58.0,
                                'totalTackle': 12,
                                'totalScoringAtt': 15,
                            },
                        }
                    ],
                },
                'lineups': {
                    'payload': {
                        'homeTeam': {
                            'players': [
                                {
                                    'playerId': 'p1',
                                    'displayName': 'Example Player',
                                    'position': 'M',
                                    'shirtNumber': 8,
                                }
                            ]
                        }
                    }
                },
                'events': {
                    'payload': {
                        'homeTeam': {
                            'goals': [
                                {
                                    'id': 'g1',
                                    'playerId': 'p1',
                                    'assistPlayerId': 'p2',
                                    'minute': '33',
                                }
                            ]
                        }
                    }
                },
            },
        },
    )

    result = catalogue_archive(tmp_path)
    by_key = {(row['resource'], row['path']): row for row in result['rows']}

    assert result['snapshot_files_scanned'] == 1
    assert result['snapshots_read'] == 1

    passes = by_key[('stats', '[].stats.totalPass')]
    assert passes['entity_level'] == 'Team-match statistic'
    assert passes['logical_family'] == 'Passing'
    assert passes['snapshot_coverage_pct'] == 100.0
    assert passes['sample_values'] == '500'

    possession = by_key[('stats', '[].stats.possessionPercentage')]
    assert possession['logical_family'] == 'Possession & progression'

    tackle = by_key[('stats', '[].stats.totalTackle')]
    assert tackle['logical_family'] == 'Defending & duels'

    player = by_key[('lineups', 'homeTeam.players[].playerId')]
    assert player['entity_level'] == 'Player / lineup'
    assert player['logical_family'] == 'Identity & relationships'

    assist = by_key[('events', 'homeTeam.goals[].assistPlayerId')]
    assert assist['entity_level'] == 'Event'
    assert assist['logical_family'] == 'Creation & assists'

    endpoint = by_key[('__resource_meta__:stats', 'endpoint')]
    assert endpoint['entity_level'] == 'Capture metadata'
    assert endpoint['logical_family'] == 'Capture & provenance'


def test_catalogue_tracks_snapshot_coverage_and_is_read_only(tmp_path: Path) -> None:
    first = tmp_path / 'match-1' / 'snapshot.json'
    second = tmp_path / 'match-2' / 'snapshot.json'
    _write_snapshot(first, {'resources': {'stats': {'payload': [{'stats': {'totalPass': 400}}]}}})
    _write_snapshot(second, {'resources': {'stats': {'payload': [{'stats': {'totalPass': 510, 'totalCross': 17}}]}}})

    before = {path: path.read_bytes() for path in (first, second)}
    result = catalogue_archive(tmp_path)
    after = {path: path.read_bytes() for path in (first, second)}

    by_key = {(row['resource'], row['path']): row for row in result['rows']}
    total_pass = by_key[('stats', '[].stats.totalPass')]
    total_cross = by_key[('stats', '[].stats.totalCross')]

    assert total_pass['snapshot_count'] == 2
    assert total_pass['snapshot_coverage_pct'] == 100.0
    assert total_pass['scalar_observations'] == 2
    assert total_cross['snapshot_count'] == 1
    assert total_cross['snapshot_coverage_pct'] == 50.0
    assert before == after


def test_write_catalogue_emits_csv_and_json_without_touching_archive(tmp_path: Path) -> None:
    archive = tmp_path / 'archive'
    snapshot = archive / 'match-1' / 'snapshot.json'
    _write_snapshot(snapshot, {'resources': {'stats': {'payload': [{'stats': {'accuratePass': 321}}]}}})
    before = snapshot.read_bytes()

    result = catalogue_archive(archive)
    output = tmp_path / 'output'
    csv_path, json_path = write_catalogue(result, output)

    assert csv_path.is_file()
    assert json_path.is_file()
    assert 'accuratePass' in csv_path.read_text(encoding='utf-8')
    assert json.loads(json_path.read_text(encoding='utf-8'))['distinct_variables'] >= 1
    assert snapshot.read_bytes() == before
