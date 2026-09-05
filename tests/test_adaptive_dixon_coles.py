from __future__ import annotations

from datetime import datetime, timezone

import pytest

import adaptive_dixon_coles as adc
import poisson_model


def _config() -> adc.AdaptiveDCConfig:
    return adc.AdaptiveDCConfig(learning_rate=0.02, half_life_days=365.0)


def test_dixon_coles_score_matrix_is_positive_normalized_and_changes_low_scores():
    independent = poisson_model.score_matrix(1.5, 1.1)
    adjusted = adc.dixon_coles_score_matrix(1.5, 1.1, -0.05)
    assert sum(adjusted.values()) == pytest.approx(1.0, abs=1e-12)
    assert all(value > 0 for value in adjusted.values())
    assert adjusted[(0, 0)] != pytest.approx(independent[(0, 0)])
    assert adjusted[(1, 1)] != pytest.approx(independent[(1, 1)])


def test_new_team_prior_produces_valid_probabilities_without_fake_history():
    model = adc.OnlineDixonColes(_config())
    prediction = model.predict("NEW_HOME", "NEW_AWAY")
    probabilities = prediction["probabilities"]
    assert sum(probabilities.values()) == pytest.approx(1.0, abs=1e-10)
    assert all(0.0 < value < 1.0 for value in probabilities.values())
    assert prediction["home_prior_matches"] == 0
    assert prediction["away_prior_matches"] == 0
    assert prediction["home_representation"] == "LEAGUE_AVERAGE_NEW_TEAM_PRIOR"
    assert prediction["away_representation"] == "LEAGUE_AVERAGE_NEW_TEAM_PRIOR"


def test_observed_result_updates_strength_state_and_match_counts():
    model = adc.OnlineDixonColes(_config())
    before = model.predict("HOME", "AWAY")
    model.update("HOME", "AWAY", 3, 0)
    after = model.predict("HOME", "AWAY")
    assert model.matches_seen["HOME"] == 1
    assert model.matches_seen["AWAY"] == 1
    assert after["home_representation"] == "ADAPTIVE_LEARNED_STRENGTH"
    assert after["away_representation"] == "ADAPTIVE_LEARNED_STRENGTH"
    assert after["expected_goals"] != before["expected_goals"]
    assert -0.15 <= model.rho <= 0.0


def test_candidate_grid_and_holdout_are_fixed_and_disjoint():
    assert len(adc.CANDIDATE_CONFIGS) == 6
    assert len({config.key for config in adc.CANDIDATE_CONFIGS}) == 6
    assert all(config.learning_rate > 0 for config in adc.CANDIDATE_CONFIGS)
    assert all(config.half_life_days > 0 for config in adc.CANDIDATE_CONFIGS)
    assert set(adc.DEVELOPMENT_SCORE_SEASONS).isdisjoint(adc.HOLDOUT_SCORE_SEASONS)
    assert adc.DEVELOPMENT_SCORE_SEASONS[-1] < adc.HOLDOUT_SCORE_SEASONS[0]


def test_same_kickoff_matches_are_predicted_before_any_result_update(monkeypatch):
    kickoff = datetime(2025, 1, 1, 15, 0, tzinfo=timezone.utc)
    fixtures = [
        {
            "season": "2024-25",
            "fixture_id": "1",
            "kickoff": kickoff,
            "kickoff_time": "2025-01-01T15:00:00+00:00",
            "home_team_code": "A",
            "away_team_code": "B",
            "home_team": "A",
            "away_team": "B",
            "home_goals": 7,
            "away_goals": 0,
        },
        {
            "season": "2024-25",
            "fixture_id": "2",
            "kickoff": kickoff,
            "kickoff_time": "2025-01-01T15:00:00+00:00",
            "home_team_code": "C",
            "away_team_code": "D",
            "home_team": "C",
            "away_team": "D",
            "home_goals": 0,
            "away_goals": 0,
        },
    ]
    monkeypatch.setattr(adc, "canonical_completed_fixtures", lambda seasons=adc.DEFAULT_SEASONS: fixtures)

    initial = adc.OnlineDixonColes(_config()).predict("C", "D")["probabilities"]
    report = adc.run_online_backtest(
        config=_config(),
        all_seasons=("2024-25",),
        score_seasons=("2024-25",),
    )
    second = next(row for row in report["rows"] if row["fixture_id"] == "2")
    assert second["home_win"] == pytest.approx(initial["home_win"])
    assert second["draw"] == pytest.approx(initial["draw"])
    assert second["away_win"] == pytest.approx(initial["away_win"])
    assert report["temporal_contract"]["same_kickoff_batching"] is True
    assert report["final_state"]["updates"] == 2
