from api.league_table import get_league_table


SEASON = "2026-27"
RELEASE_SHA = "ffe99d25a5bd3a8f70c557748fead332f46ed14f"


def test_current_league_table_uses_governed_completed_results() -> None:
    result = get_league_table(SEASON)

    assert result.season == SEASON
    assert result.competition == "Premier League"
    assert result.total_fixtures == 380
    assert result.completed_fixtures == 20
    assert result.scheduled_fixtures == 360
    assert len(result.rows) == 20
    assert sum(row.played for row in result.rows) == 40
    assert result.source_release_sha == RELEASE_SHA
    assert result.information_available_as_of is not None
    assert all(len(row.form) <= 5 for row in result.rows)


def test_current_league_table_preserves_team_identity_and_result_state() -> None:
    result = get_league_table(SEASON)
    arsenal = next(row for row in result.rows if row.persistent_team_code == "3")

    assert arsenal.display_name == "Arsenal"
    assert arsenal.played == 2
    assert arsenal.wins == 2
    assert arsenal.draws == 0
    assert arsenal.losses == 0
    assert arsenal.goals_for == 4
    assert arsenal.goals_against == 0
    assert arsenal.points == 6
    assert arsenal.form == ["W", "W"]
