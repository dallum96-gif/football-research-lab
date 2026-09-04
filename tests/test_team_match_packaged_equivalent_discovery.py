from __future__ import annotations

from scripts.discover_team_match_packaged_equivalents import suggest_equivalents


def test_discovery_only_considers_raw_snapshot_only_rows():
    rows = [
        {'source_field': 'totalLongBall', 'reconciliation_status': 'RAW_SNAPSHOT_ONLY'},
        {'source_field': 'alreadyThere', 'reconciliation_status': 'EXISTING_EXPOSED'},
    ]
    result = suggest_equivalents(rows, ['totalLongBalls', 'accurateLongBalls'])

    assert len(result) == 1
    assert result[0]['raw_source_field'] == 'totalLongBall'


def test_close_name_is_suggested_but_not_promoted():
    result = suggest_equivalents(
        [{'source_field': 'totalLongBall', 'reconciliation_status': 'RAW_SNAPSHOT_ONLY'}],
        ['totalLongBalls', 'accuratePass'],
    )
    row = result[0]

    assert row['best_candidate'] == 'totalLongBalls'
    assert row['best_score'] > 0.8
    assert row['route_discovery_lane'] == 'STRONG_NAME_SIMILARITY_REVIEW'
    assert 'does not establish' in row['governance_note']


def test_weak_name_match_stays_fail_closed():
    result = suggest_equivalents(
        [{'source_field': 'mysteryPressureCode', 'reconciliation_status': 'RAW_SNAPSHOT_ONLY'}],
        ['totalPass', 'accurateCross', 'saves'],
    )
    row = result[0]

    assert row['route_discovery_lane'] == 'NO_STRONG_PACKAGED_EQUIVALENT_BY_NAME'
