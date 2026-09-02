from __future__ import annotations

import math

import pytest

import poisson_model


def test_load_source_fixtures_retains_completed_zero_scores(monkeypatch):
    rows = [
        {"season": poisson_model.SOURCE_SEASON, "fixture_id": "1", "home_score": "1", "away_score": "0"},
        {"season": poisson_model.SOURCE_SEASON, "fixture_id": "2", "home_score": "0", "away_score": "1"},
        {"season": poisson_model.SOURCE_SEASON, "fixture_id": "3", "home_score": 0, "away_score": 0},
        {"season": poisson_model.SOURCE_SEASON, "fixture_id": "4", "home_score": None, "away_score": "2"},
        {"season": poisson_model.SOURCE_SEASON, "fixture_id": "5", "home_score": "2", "away_score": ""},
        {"season": poisson_model.SOURCE_SEASON, "fixture_id": "6", "home_score": " ", "away_score": "1"},
        {"season": "other-season", "fixture_id": "7", "home_score": "0", "away_score": "0"},
    ]
    monkeypatch.setattr(poisson_model.query_lab, "load_fixtures", lambda: rows)

    fixtures = poisson_model.load_source_fixtures()

    assert [fixture["fixture_id"] for fixture in fixtures] == ["1", "2", "3"]


def test_expected_goal_rates_apply_home_away_attack_and_defence_strengths():
    league = {"home_goals": 1.5, "away_goals": 1.2}
    home = {"home_attack": 1.2, "home_defence": 0.8}
    away = {"away_attack": 1.1, "away_defence": 1.3}

    home_lambda, away_lambda = poisson_model.expected_goal_rates(
        league,
        home,
        away,
    )

    assert home_lambda == pytest.approx(1.5 * 1.2 * 1.3)
    assert away_lambda == pytest.approx(1.2 * 1.1 * 0.8)


def test_score_matrix_preserves_probability_mass_and_market_complements():
    scores = poisson_model.score_matrix(1.75, 1.10)
    probabilities = poisson_model.market_probabilities(scores)

    assert sum(scores.values()) == pytest.approx(1.0, abs=1e-12)
    assert (
        probabilities["home_win"]
        + probabilities["draw"]
        + probabilities["away_win"]
    ) == pytest.approx(1.0, abs=1e-12)
    assert probabilities["over_2_5"] + probabilities["under_2_5"] == pytest.approx(1.0)
    assert probabilities["btts"] + probabilities["btts_no"] == pytest.approx(1.0)


def test_prediction_from_strengths_exposes_interpretable_inputs_and_markets():
    fitted = {
        "source_season": "2024-25",
        "fixture_count": 380,
        "strength_method": "test strength method",
        "league_environment": {
            "home_goals": 1.5,
            "away_goals": 1.2,
            "total_goals": 2.7,
            "home_advantage_ratio": 1.25,
            "matches": 380,
        },
    }
    home = {
        "home_attack": 1.2,
        "home_defence": 0.9,
        "away_attack": 1.0,
        "away_defence": 1.0,
        "home_matches": 19,
        "away_matches": 19,
    }
    away = {
        "home_attack": 1.0,
        "home_defence": 1.0,
        "away_attack": 1.1,
        "away_defence": 1.2,
        "home_matches": 19,
        "away_matches": 19,
    }

    prediction = poisson_model.prediction_from_strengths(
        "Home FC",
        "Away FC",
        fitted,
        home,
        away,
        target_season="2025-26",
    )

    assert prediction["model"] == poisson_model.MODEL_VERSION
    assert prediction["expected_goals"]["home"] == pytest.approx(2.16)
    assert prediction["expected_goals"]["away"] == pytest.approx(1.188)
    assert prediction["inputs"]["source_matches"] == 380
    assert len(prediction["correct_scores"]) == 10
    assert prediction["fair_odds"]["home_win"] == pytest.approx(
        1.0 / prediction["probabilities"]["home_win"]
    )


def test_fit_source_season_uses_verified_identity_and_records_match_exposure(monkeypatch):
    fixtures = [
        {
            "season": "2024-25",
            "fixture_id": "1",
            "home_team_id": "A",
            "away_team_id": "B",
            "home_score": "2",
            "away_score": "1",
        },
        {
            "season": "2024-25",
            "fixture_id": "2",
            "home_team_id": "B",
            "away_team_id": "A",
            "home_score": "1",
            "away_score": "1",
        },
    ]
    identity = [
        {
            "season": "2024-25",
            "local_team_id": "A",
            "canonical_name": "Alpha_FC",
            "mapping_status": "VERIFIED",
        },
        {
            "season": "2024-25",
            "local_team_id": "B",
            "canonical_name": "Beta_FC",
            "mapping_status": "VERIFIED",
        },
        {
            "season": "2024-25",
            "local_team_id": "X",
            "canonical_name": "Ignored_FC",
            "mapping_status": "UNVERIFIED",
        },
    ]

    monkeypatch.setattr(poisson_model.query_lab, "load_fixtures", lambda: fixtures)
    monkeypatch.setattr(poisson_model.query_lab, "load_identity_registry", lambda: identity)

    fitted = poisson_model.fit_source_season("2024-25")

    assert set(fitted["team_strengths"]) == {"Alpha FC", "Beta FC"}
    assert fitted["fixture_count"] == 2
    assert fitted["team_strengths"]["Alpha FC"]["home_matches"] == 1
    assert fitted["team_strengths"]["Alpha FC"]["away_matches"] == 1
    assert fitted["league_environment"]["home_goals"] == pytest.approx(1.5)
    assert fitted["league_environment"]["away_goals"] == pytest.approx(1.0)


def test_backtest_excludes_teams_without_source_season_strength(monkeypatch):
    fitted = {
        "source_season": "2024-25",
        "fixture_count": 380,
        "strength_method": "test",
        "league_environment": {
            "home_goals": 1.5,
            "away_goals": 1.2,
            "total_goals": 2.7,
            "home_advantage_ratio": 1.25,
            "matches": 380,
        },
        "team_strengths": {
            "Alpha FC": {
                "home_attack": 1.1,
                "home_defence": 0.9,
                "away_attack": 1.0,
                "away_defence": 0.9,
                "home_matches": 19,
                "away_matches": 19,
            },
            "Beta FC": {
                "home_attack": 0.9,
                "home_defence": 1.1,
                "away_attack": 1.0,
                "away_defence": 1.1,
                "home_matches": 19,
                "away_matches": 19,
            },
        },
    }
    target_fixtures = [
        {
            "fixture_id": "1",
            "home_team_id": "A",
            "away_team_id": "B",
            "home_score": "2",
            "away_score": "1",
        },
        {
            "fixture_id": "2",
            "home_team_id": "C",
            "away_team_id": "A",
            "home_score": "1",
            "away_score": "0",
        },
    ]
    names = {"A": "Alpha FC", "B": "Beta FC", "C": "Promoted FC"}

    monkeypatch.setattr(poisson_model, "fit_source_season", lambda season: fitted)
    monkeypatch.setattr(poisson_model, "load_source_fixtures", lambda season: target_fixtures)
    monkeypatch.setattr(
        poisson_model,
        "_team_name_for_id",
        lambda season, local_id: names[str(local_id)],
    )

    result = poisson_model.backtest_previous_season("2025-26", "2024-25")

    assert result["evaluated_fixtures"] == 1
    assert result["excluded_fixtures"] == 1
    assert result["exclusions"] == {"TEAM_NOT_IN_SOURCE_SEASON": 1}
    assert result["metrics"]["mean_brier_1x2"] >= 0
    assert math.isfinite(result["metrics"]["mean_log_loss"])


def test_compare_bookmaker_odds_rejects_invalid_decimal_prices():
    prediction = {
        "probabilities": {
            "home_win": 0.5,
            "draw": 0.25,
            "away_win": 0.25,
        }
    }

    with pytest.raises(ValueError):
        poisson_model.compare_bookmaker_odds(
            prediction,
            1.0,
            4.0,
            4.0,
        )
