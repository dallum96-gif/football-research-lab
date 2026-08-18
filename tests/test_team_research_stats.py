from team_research_stats import team_season_stats_by_name


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
