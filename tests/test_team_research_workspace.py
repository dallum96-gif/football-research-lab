from team_research_analytics import team_performance_profile, team_season_comparison


def test_team_performance_profile_contract():
    result = team_performance_profile("2024-25", "Arsenal")
    assert result.query_type == "team_performance_profile"
    assert {"kickoff_time", "fixture_id", "opponent", "result", "cumulative_ppg", "rolling_ppg"}.issubset(result.columns)
    assert result.population["completed_matches"] > 0
    assert result.population["overall"]["matches"] == result.population["completed_matches"]
    assert len(result.population["venue_splits"]) == 2
    assert len(result.population["phase_splits"]) == 3


def test_team_season_comparison_contract():
    result = team_season_comparison("Arsenal", ["2022-23", "2023-24", "2024-25"])
    assert result.query_type == "team_season_comparison"
    assert {"season", "points_per_match", "goals_for_per_match", "goals_against_per_match"}.issubset(result.columns)
    assert result.rows
    assert all(row["points_per_match"] is not None for row in result.rows)
