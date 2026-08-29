import os
import sys

import pytest

ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.insert(0, ROOT)

import match_stats
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

    # The resolver may use only the existing VERIFIED_CORRECTION actual kickoff;
    # it must not guess from the scheduled date, scoreline or display names.
    match_id = player_match_stats.player_match_id_for_fixture(fixture)
    assert match_id
    assert match_id.isdigit()

    rows = player_match_stats.fixture_player_match_rows(fixture)
    assert rows
    assert {str(row["matchId"]) for row in rows} == {match_id}

    from source_family_adapters import resolve_source_match

    resolved = resolve_source_match("2019-20", "275")
    assert resolved["relationship_status"] == "VERIFIED"
    assert resolved["resolution_basis"] == "VERIFIED_FIXTURE_CORRECTION"
    assert resolved["fixture_correction"]["status"] == "VERIFIED_CORRECTION"
    assert resolved["fixture_correction"]["scheduled_kickoff"] == fixture["kickoff_time"]


def test_verified_fixture_correction_rejects_canonical_contradiction(monkeypatch):
    fixture = {
        "season": "2019-20",
        "fixture_id": "275",
        "kickoff_time": "2020-03-11T19:30:00Z",
        "home_team_id": "11",
        "away_team_id": "1",
    }
    monkeypatch.setattr(match_stats, "fixture_corrections", lambda: {
        ("2019-20", "275"): {
            "season": "2019-20",
            "fixture_id": "275",
            "scheduled_kickoff": "2020-03-11T19:30:00Z",
            "actual_kickoff": "2020-06-17T19:15:00Z",
            "home_team_id": "999",
            "away_team_id": "1",
            "status": "VERIFIED_CORRECTION",
        }
    })

    with pytest.raises(ValueError, match="contradicts canonical fixture"):
        match_stats.verified_fixture_correction(fixture)


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
