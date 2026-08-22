from audit_upstream_pl_stats_schema_by_season import choose_representatives, season_from_path


def test_season_from_path():
    assert season_from_path('fpl_stats/events_stats/2024-25/team_1.csv') == '2024-25'


def test_choose_one_file_per_grain_season():
    files = [
        {'path':'a/2024-25.csv','grain':'team_match','season':'2024-25'},
        {'path':'b/2024-25.csv','grain':'team_match','season':'2024-25'},
        {'path':'c/2025-26.csv','grain':'team_match','season':'2025-26'},
    ]
    reps = choose_representatives(files)
    assert [(r['grain'], r['season']) for r in reps] == [('team_match','2024-25'), ('team_match','2025-26')]
    assert reps[0]['path'] == 'a/2024-25.csv'
