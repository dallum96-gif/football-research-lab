from __future__ import annotations

from api.fixture_player_performance_api import _leader, _metric_values, _percentage


def test_derived_percentages() -> None:
    assert _percentage("6", "8") == 75.0
    assert _percentage("0", "0") is None
    assert _percentage(None, "8") is None


def test_canonical_metric_mapping_and_secondary_values() -> None:
    row = {
        "wonTackle": "6",
        "totalTackle": "8",
        "interceptionWon": "4",
        "accuratePass": "91",
        "totalPass": "100",
        "keyPass": "5",
        "successfulDribbles": "3",
        "unsuccessfulDribbles": "1",
        "onTargetScoringAttempt": "2",
        "totalScoringAttempt": "4",
    }
    assert _metric_values(row, "tackles_won") == (6.0, 75.0)
    assert _metric_values(row, "interceptions_won") == (4.0, None)
    assert _metric_values(row, "passes_completed") == (91.0, 91.0)
    assert _metric_values(row, "key_passes") == (5.0, None)
    assert _metric_values(row, "successful_dribbles") == (3.0, 75.0)
    assert _metric_values(row, "shots_on_target") == (2.0, 50.0)


def test_leader_uses_headline_count_not_percentage() -> None:
    rows = (
        {
            "venue": "Home",
            "minutesPlayed": "90",
            "accuratePass": "80",
            "totalPass": "80",
            "name": "Aaron Example",
            "playerId": "1",
        },
        {
            "venue": "Home",
            "minutesPlayed": "75",
            "accuratePass": "91",
            "totalPass": "120",
            "name": "Ben Example",
            "playerId": "2",
        },
    )
    leader = _leader(rows, "passes_completed")
    assert leader is not None
    assert leader.player_name == "Ben Example"
    assert leader.value == 91.0
    assert leader.secondary_value == 75.83333333333333


def test_leader_excludes_bench_and_tie_breaks_deterministically() -> None:
    rows = (
        {
            "venue": "Home",
            "minutesPlayed": "0",
            "keyPass": "9",
            "name": "Bench Player",
            "playerId": "1",
        },
        {
            "venue": "Home",
            "minutesPlayed": "90",
            "keyPass": "5",
            "name": "Aaron Example",
            "playerId": "2",
        },
        {
            "venue": "Home",
            "minutesPlayed": "80",
            "keyPass": "5",
            "name": "Ben Example",
            "playerId": "3",
        },
    )
    leader = _leader(rows, "key_passes")
    assert leader is not None
    assert leader.player_name == "Ben Example"
    assert leader.value == 5.0
