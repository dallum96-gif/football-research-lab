from __future__ import annotations

from api.fixture_player_performance_api import _leader, _metric_value, _percentage


def test_derived_percentages() -> None:
    assert _percentage("6", "8") == 75.0
    assert _percentage("0", "0") is None
    assert _percentage(None, "8") is None


def test_canonical_metric_mapping() -> None:
    row = {
        "wonTackle": "6",
        "totalTackle": "8",
        "interceptionWon": "4",
        "accuratePass": "91",
        "totalPass": "100",
        "keyPass": "5",
        "successfulDribbles": "3",
        "onTargetScoringAttempt": "2",
    }
    assert _metric_value(row, "tackle_won_pct") == 75.0
    assert _metric_value(row, "interceptions_won") == 4.0
    assert _metric_value(row, "pass_completion_pct") == 91.0
    assert _metric_value(row, "key_passes") == 5.0
    assert _metric_value(row, "successful_dribbles") == 3.0
    assert _metric_value(row, "shots_on_target") == 2.0


def test_leader_uses_positive_minutes_and_deterministic_tie_break() -> None:
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
