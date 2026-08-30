from __future__ import annotations

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
