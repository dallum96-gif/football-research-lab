import pytest

import team_research_stats
from team_research_stats import team_season_stats_by_name


def _season_stats(monkeypatch, rows):
    monkeypatch.setattr(
        team_research_stats,
        "team_match_stats",
        lambda season, team_code: tuple(rows),
    )
    return team_research_stats.team_season_stats("2099-00", "TEST")


def test_team_stats_expose_match_stat_universe():
    stats = team_season_stats_by_name("2025-26", "Arsenal")
    assert stats["status"] == "AVAILABLE"
    assert stats["matches"] > 0
    assert "Shots_per_match" in stats
    assert "Shots on target_per_match" in stats
    assert "Possession_per_match" in stats
    assert "Expected goals_per_match" in stats
    assert "Tackles_per_match" in stats


def test_team_stats_derive_results_and_efficiency():
    stats = team_season_stats_by_name("2025-26", "Arsenal")
    assert stats["points_per_match"] >= 0
    assert 0 <= stats["win_rate"] <= 1
    assert 0 <= stats["clean_sheet_rate"] <= 1
    assert 0 <= stats["failed_to_score_rate"] <= 1


def test_complete_metric_uses_all_eligible_matches(monkeypatch):
    stats = _season_stats(
        monkeypatch,
        [
            {"fixture_id": "1", "kickoff_time": None, "home": True, "Shots": 10.0},
            {"fixture_id": "2", "kickoff_time": None, "home": False, "Shots": 0.0},
            {"fixture_id": "3", "kickoff_time": None, "home": True, "Shots": 5.0},
        ],
    )

    assert stats["matches"] == 3
    assert stats["Shots"] == pytest.approx(15.0)
    assert stats["Shots_per_match"] == pytest.approx(5.0)
    assert stats["metric_coverage"]["Shots"] == {
        "eligible_matches": 3,
        "observed_matches": 3,
        "missing_matches": 0,
        "observed_total": 15.0,
        "per_observed_match": 5.0,
        "coverage_complete": True,
        "coverage_status": "COMPLETE",
    }


def test_partial_metric_uses_only_observed_matches_and_preserves_zero(monkeypatch):
    stats = _season_stats(
        monkeypatch,
        [
            {"fixture_id": "1", "kickoff_time": None, "home": True, "Expected goals": 1.2},
            {"fixture_id": "2", "kickoff_time": None, "home": False, "Expected goals": None},
            {"fixture_id": "3", "kickoff_time": None, "home": True, "Expected goals": 0.0},
        ],
    )

    assert stats["Expected goals"] == pytest.approx(1.2)
    assert stats["Expected goals_per_match"] == pytest.approx(0.6)
    assert stats["metric_coverage"]["Expected goals"] == {
        "eligible_matches": 3,
        "observed_matches": 2,
        "missing_matches": 1,
        "observed_total": 1.2,
        "per_observed_match": 0.6,
        "coverage_complete": False,
        "coverage_status": "PARTIAL",
    }


def test_partial_xg_cannot_produce_full_season_overperformance(monkeypatch):
    stats = _season_stats(
        monkeypatch,
        [
            {
                "fixture_id": "1",
                "kickoff_time": None,
                "home": True,
                "goals_for": 2.0,
                "goals_against": 0.0,
                "Expected goals": 1.2,
            },
            {
                "fixture_id": "2",
                "kickoff_time": None,
                "home": False,
                "goals_for": 1.0,
                "goals_against": 1.0,
                "Expected goals": None,
            },
        ],
    )

    assert stats["Expected goals_per_match"] == pytest.approx(1.2)
    assert stats["metric_coverage"]["Expected goals"]["coverage_status"] == "PARTIAL"
    assert stats["xg_overperformance"] is None


def test_complete_xg_coverage_permits_overperformance(monkeypatch):
    stats = _season_stats(
        monkeypatch,
        [
            {
                "fixture_id": "1",
                "kickoff_time": None,
                "home": True,
                "goals_for": 2.0,
                "goals_against": 0.0,
                "Expected goals": 1.2,
            },
            {
                "fixture_id": "2",
                "kickoff_time": None,
                "home": False,
                "goals_for": 0.0,
                "goals_against": 1.0,
                "Expected goals": 0.3,
            },
        ],
    )

    assert stats["Expected goals_per_match"] == pytest.approx(0.75)
    assert stats["metric_coverage"]["Expected goals"]["coverage_status"] == "COMPLETE"
    assert stats["xg_overperformance"] == pytest.approx(0.5)
