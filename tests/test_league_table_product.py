import query_api
from api.league_table import get_league_table


SEASON = "2026-27"


def _rows_by_team(result):
    return {
        row.persistent_team_code: row
        for row in result.rows
    }


def test_current_league_table_uses_governed_completed_results() -> None:
    result = get_league_table(SEASON)

    assert result.view == "overall"
    assert result.season == SEASON
    assert result.competition == "Premier League"
    assert result.total_fixtures == 380
    assert 0 < result.completed_fixtures < result.total_fixtures
    assert result.scheduled_fixtures == (
        result.total_fixtures - result.completed_fixtures
    )
    assert len(result.rows) == 20
    assert sum(row.played for row in result.rows) == (
        result.completed_fixtures * 2
    )
    assert all(len(row.form) <= 5 for row in result.rows)
    assert all(
        row.played == row.wins + row.draws + row.losses
        for row in result.rows
    )

    # Release metadata is optional for a living season. If the canonical
    # fixture state has moved beyond the pinned release, the API must fail
    # closed rather than attach a stale boundary to newer standings.
    assert (result.information_available_as_of is None) == (
        result.source_release_sha is None
    )


def test_current_league_table_preserves_team_identity_and_result_state() -> None:
    result = get_league_table(SEASON)
    source = query_api.league_table(SEASON)

    arsenal = next(
        row
        for row in result.rows
        if row.persistent_team_code == "3"
    )
    source_arsenal = next(
        row
        for row in source["teams"]
        if str(row.get("persistent_team_code") or "") == "3"
    )

    assert arsenal.display_name == "Arsenal"
    assert arsenal.local_team_id == str(source_arsenal["team_id"])
    assert arsenal.position == int(source_arsenal["position"])
    assert arsenal.played == int(source_arsenal["played"])
    assert arsenal.wins == int(source_arsenal["wins"])
    assert arsenal.draws == int(source_arsenal["draws"])
    assert arsenal.losses == int(source_arsenal["losses"])
    assert arsenal.goals_for == int(source_arsenal["goals_for"])
    assert arsenal.goals_against == int(source_arsenal["goals_against"])
    assert arsenal.goal_difference == int(source_arsenal["goal_difference"])
    assert arsenal.points == int(source_arsenal["points"])
    assert len(arsenal.form) == min(5, arsenal.played)


def test_home_and_away_tables_reconstruct_overall_team_records() -> None:
    overall = get_league_table(SEASON, "overall")
    home = get_league_table(SEASON, "home")
    away = get_league_table(SEASON, "away")

    assert home.view == "home"
    assert away.view == "away"
    assert sum(row.played for row in home.rows) == overall.completed_fixtures
    assert sum(row.played for row in away.rows) == overall.completed_fixtures

    overall_rows = _rows_by_team(overall)
    home_rows = _rows_by_team(home)
    away_rows = _rows_by_team(away)

    assert overall_rows.keys() == home_rows.keys() == away_rows.keys()

    for team_code, overall_row in overall_rows.items():
        home_row = home_rows[team_code]
        away_row = away_rows[team_code]

        assert home_row.played + away_row.played == overall_row.played
        assert home_row.wins + away_row.wins == overall_row.wins
        assert home_row.draws + away_row.draws == overall_row.draws
        assert home_row.losses + away_row.losses == overall_row.losses
        assert home_row.goals_for + away_row.goals_for == overall_row.goals_for
        assert home_row.goals_against + away_row.goals_against == overall_row.goals_against
        assert home_row.points + away_row.points == overall_row.points


def test_last_five_table_is_bounded_and_uses_its_selected_population() -> None:
    result = get_league_table(SEASON, "last5")

    assert result.view == "last5"
    assert len(result.rows) == 20
    assert all(row.played <= 5 for row in result.rows)
    assert all(len(row.form) == row.played for row in result.rows)
    assert all(len(row.form) <= 5 for row in result.rows)
