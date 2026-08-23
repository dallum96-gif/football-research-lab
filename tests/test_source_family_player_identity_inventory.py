from audit_source_family_player_identity_inventory import season_from_path


def test_season_from_path_extracts_historical_season():
    assert season_from_path(__import__('pathlib').Path('2016-17_players_match_stats.csv')) == '2016-17'
    assert season_from_path(__import__('pathlib').Path('2025-26_gw_stats.csv')) == '2025-26'


def test_season_from_path_returns_none_without_season():
    assert season_from_path(__import__('pathlib').Path('players_index.json')) is None
