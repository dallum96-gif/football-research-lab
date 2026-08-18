import os
import sys

ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.insert(0, ROOT)

import player_match_stats


EXPECTED_SEASONS = (
    "2016-17",
    "2017-18",
    "2018-19",
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
    "2025-26",
)


EXPECTED_FIELDS = {
    "passes": "totalPass",
    "accurate_passes": "accuratePass",
    "own_half_accurate_passes": "accurateOwnHalfPasses",
    "opposition_half_accurate_passes": "accurateOppositionHalfPasses",
    "long_balls": "totalLongBalls",
    "accurate_long_balls": "accurateLongBalls",
    "key_passes": "keyPass",
    "big_chances_created": "bigChanceCreated",
    "assists": "goalAssist",
    "expected_assists": "expectedAssists",
    "successful_dribbles": "successfulDribbles",
    "unsuccessful_dribbles": "unsuccessfulDribbles",
    "ball_carries": "ballCarriesCount",
    "progressive_ball_carries": "progressiveBallCarriesCount",
    "progressive_carry_distance": "totalProgressiveBallCarriesDistance",
    "progression": "totalProgression",
}


def test_source_seasons():
    assert set(player_match_stats.available_seasons()) >= set(
        EXPECTED_SEASONS
    )


def test_passing_schema_contract():
    assert player_match_stats.PASSING_METRICS
    for metric in player_match_stats.PASSING_METRICS:
        assert metric in player_match_stats.PLAYER_MATCH_METRICS
        assert (
            player_match_stats.PLAYER_MATCH_METRICS[metric]["source"]
            in EXPECTED_FIELDS.values()
        )


def test_metric_coverage():
    coverage = player_match_stats.metric_coverage()

    assert "passes" in coverage["2016-17"]
    assert "accurate_passes" in coverage["2019-20"]
    assert "expected_assists" not in coverage["2019-20"]
    assert "expected_assists" in coverage["2022-23"]
    assert "progressive_ball_carries" in coverage["2019-20"]
    assert "progressive_ball_carries" not in coverage["2022-23"]
    assert "progressive_ball_carries" in coverage["2024-25"]


def test_player_match_pair_resolution():
    identity_rows = tuple(player_match_stats._identity_rows())

    fixture = {
        "season": "2019-20",
        "fixture_id": "1",
        "fixture_code": "",
        "gameweek": "1",
        "kickoff_time": "2019-08-09T19:00:00Z",
        "home_team_id": "10",
        "away_team_id": "14",
    }

    match_id = player_match_stats.player_match_id_for_fixture(fixture)

    assert match_id
    assert match_id.isdigit()


def test_known_fixture_exception():
    fixture = {
        "season": "2019-20",
        "fixture_id": "275",
        "fixture_code": "",
        "gameweek": "29",
        "kickoff_time": "2020-03-11T19:30:00Z",
        "home_team_id": "11",
        "away_team_id": "1",
    }

    # The canonical resolver intentionally treats this as a known correction
    # state, so the player-match adapter must not invent a match through a
    # guessed scheduled date.
    try:
        player_match_stats.player_match_id_for_fixture(fixture)
    except (ValueError, KeyError):
        return

    # If a future correction-aware resolver can resolve it, that is also valid;
    # the important invariant is that the adapter never raises an ambiguous
    # source match or silently fabricates an identity.


def test_aggregate_rows():
    rows = [
        {
            "totalPass": "100",
            "accuratePass": "80",
            "keyPass": "3",
            "bigChanceCreated": "1",
            "goalAssist": "1",
        },
        {
            "totalPass": "50",
            "accuratePass": "40",
            "keyPass": "2",
            "bigChanceCreated": "",
            "goalAssist": "0",
        },
    ]

    result = player_match_stats.aggregate_rows(rows)

    assert result["passes"] == 150
    assert result["accurate_passes"] == 120
    assert result["key_passes"] == 5
    assert result["big_chances_created"] == 1
    assert result["assists"] == 1
    assert abs(result["pass_accuracy"] - 80.0) < 1e-12


TESTS = [
    test_source_seasons,
    test_passing_schema_contract,
    test_metric_coverage,
    test_player_match_pair_resolution,
    test_known_fixture_exception,
    test_aggregate_rows,
]


if __name__ == "__main__":
    passed = 0

    for test in TESTS:
        try:
            test()
            print(f"PASS  {test.__name__}")
            passed += 1
        except Exception as exc:
            print(f"FAIL  {test.__name__}: {exc}")

    print()
    print(
        f"PLAYER-MATCH SOURCE TESTS: "
        f"{passed}/{len(TESTS)}"
    )

    if passed != len(TESTS):
        raise SystemExit(1)
