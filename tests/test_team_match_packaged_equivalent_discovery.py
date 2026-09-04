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
    assert row['semantic_guard_status'] == 'QUALIFIER_GUARD_APPLIED'
    assert 'does not establish' in row['governance_note']


def test_weak_name_match_stays_fail_closed():
    result = suggest_equivalents(
        [{'source_field': 'mysteryPressureCode', 'reconciliation_status': 'RAW_SNAPSHOT_ONLY'}],
        ['totalPass', 'accurateCross', 'saves'],
    )
    row = result[0]

    assert row['route_discovery_lane'] == 'NO_STRONG_PACKAGED_EQUIVALENT_BY_NAME'


def test_generic_goals_conceded_does_not_match_penalty_goals_conceded():
    result = suggest_equivalents(
        [{'source_field': 'goalsConceded', 'reconciliation_status': 'RAW_SNAPSHOT_ONLY'}],
        ['penGoalsConceded', 'totalPass'],
    )
    row = result[0]

    assert row['best_candidate'] != 'penGoalsConceded'
    assert row['semantic_conflict_candidates_rejected'] >= 1


def test_headed_goal_does_not_match_penalty_goal_or_own_goal():
    result = suggest_equivalents(
        [{'source_field': 'attHdGoal', 'reconciliation_status': 'RAW_SNAPSHOT_ONLY'}],
        ['attPenGoal', 'attIboxOwnGoal', 'headedGoals'],
    )
    row = result[0]

    assert row['best_candidate'] == 'headedGoals'
    assert row['semantic_conflict_candidates_rejected'] >= 2
