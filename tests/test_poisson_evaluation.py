from __future__ import annotations

import pytest

from scripts import evaluate_poisson_v1


def test_calibration_bins_compare_mean_prediction_with_observed_rate():
    rows = [
        {"home_win": 0.22, "draw": 0.30, "away_win": 0.48, "actual": "away_win"},
        {"home_win": 0.28, "draw": 0.29, "away_win": 0.43, "actual": "home_win"},
        {"home_win": 0.74, "draw": 0.16, "away_win": 0.10, "actual": "home_win"},
    ]

    bins = evaluate_poisson_v1.calibration(rows, "home_win", bins=10)

    assert bins[0]["count"] == 2
    assert bins[0]["mean_prediction"] == pytest.approx(0.25)
    assert bins[0]["observed_rate"] == pytest.approx(0.5)
    assert bins[1]["count"] == 1
    assert bins[1]["observed_rate"] == 1.0


def test_aggregate_reports_weights_metrics_by_fixture_not_season():
    reports = [
        {
            "source_season": "2022-23",
            "target_season": "2023-24",
            "evaluated_fixtures": 2,
            "excluded_fixtures": 1,
            "exclusions": {"TEAM_NOT_IN_SOURCE_SEASON": 1},
            "metrics": {},
            "rows": [
                {
                    "home_win": 0.5,
                    "draw": 0.3,
                    "away_win": 0.2,
                    "actual": "home_win",
                    "brier_1x2": 0.38,
                    "log_loss": 0.69,
                    "correct": True,
                },
                {
                    "home_win": 0.4,
                    "draw": 0.3,
                    "away_win": 0.3,
                    "actual": "away_win",
                    "brier_1x2": 0.74,
                    "log_loss": 1.20,
                    "correct": False,
                },
            ],
        },
        {
            "source_season": "2023-24",
            "target_season": "2024-25",
            "evaluated_fixtures": 1,
            "excluded_fixtures": 0,
            "exclusions": {},
            "metrics": {},
            "rows": [
                {
                    "home_win": 0.2,
                    "draw": 0.3,
                    "away_win": 0.5,
                    "actual": "away_win",
                    "brier_1x2": 0.38,
                    "log_loss": 0.69,
                    "correct": True,
                }
            ],
        },
    ]

    summary = evaluate_poisson_v1.aggregate_reports(reports)

    assert summary["evaluated_fixtures"] == 3
    assert summary["excluded_fixtures"] == 1
    assert summary["metrics"]["mean_brier_1x2"] == pytest.approx(0.5)
    assert summary["metrics"]["mean_log_loss"] == pytest.approx((0.69 + 1.20 + 0.69) / 3)
    assert summary["metrics"]["top_outcome_accuracy"] == pytest.approx(2 / 3)
