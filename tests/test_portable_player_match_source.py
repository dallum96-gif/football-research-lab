from pathlib import Path

import frl_data_paths
import player_match_stats


def test_player_match_root_honours_environment(monkeypatch, tmp_path):
    configured = tmp_path / "external-player-match"
    monkeypatch.setenv("FRL_PLAYER_MATCH_ROOT", str(configured))

    assert frl_data_paths.player_match_root() == configured


def test_missing_player_match_source_is_unavailable_not_an_exception(tmp_path):
    missing = tmp_path / "does-not-exist"
    original_root = player_match_stats.PL_ROOT
    player_match_stats._season_player_match_files.cache_clear()
    player_match_stats._source_match_records.cache_clear()
    player_match_stats._player_match_pair_index.cache_clear()

    try:
        player_match_stats.PL_ROOT = Path(missing)
        assert player_match_stats._season_player_match_files("2025-26") == ()
        assert player_match_stats.available_seasons() == ()
        assert player_match_stats.player_season_totals("2025-26") == {}
    finally:
        player_match_stats.PL_ROOT = original_root
        player_match_stats._season_player_match_files.cache_clear()
        player_match_stats._source_match_records.cache_clear()
        player_match_stats._player_match_pair_index.cache_clear()
