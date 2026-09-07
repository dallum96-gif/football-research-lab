from api.league_table import get_league_table


SEASON = "2026-27"
RELEASE_SHA = "ffe99d25a5bd3a8f70c557748fead332f46ed14f"


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
