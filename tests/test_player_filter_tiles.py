from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_player_filter_tile_renderer_shape():
    path = ROOT / "gui" / "player_filter_tiles.py"
    text = path.read_text(encoding="utf-8-sig")

    assert "def render_player_research_ui_tiles" in text
    assert "frl-filter-tile" in text
    assert "frl-filter-row" in text
    assert "No popover filter containers are used" not in text


def test_player_filter_tiles_do_not_use_filter_popovers():
    text = (ROOT / "gui" / "player_filter_tiles.py").read_text(encoding="utf-8-sig")
    assert "with st.popover(" not in text
    assert "st.popover(" not in text


def test_players_workspace_routes_to_tile_renderer():
    text = (ROOT / "gui" / "ui_shell.py").read_text(encoding="utf-8-sig")
    assert "player_filter_tiles" in text
    assert "render_player_research_ui_tiles" in text
    assert 'selected == "players"' in text


def test_player_filter_tiles_keep_verified_passing_boundary():
    text = (ROOT / "gui" / "player_filter_tiles.py").read_text(encoding="utf-8-sig")
    assert "player_research_player_match" in text
    assert "player_match_passes" in text
    assert "player_match_accurate_passes" in text
    assert "player_match_key_passes" in text
    assert "player_match_big_chances_created" in text
