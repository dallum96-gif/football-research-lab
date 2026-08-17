from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_player_filter_tile_renderer_shape():
    path = ROOT / "gui" / "player_filter_tiles_v2.py"
    text = path.read_text(encoding="utf-8-sig")

    assert "def render_player_research_ui_tiles" in text
    assert "frl-filter-kicker" in text
    assert "data-testid=\"stVerticalBlockBorderWrapper\"" in text
    assert "st.popover(" not in text


def test_players_workspace_routes_to_tile_renderer():
    text = (ROOT / "gui" / "ui_shell.py").read_text(encoding="utf-8-sig")
    assert "player_filter_tiles_v2" in text
    assert "render_player_research_ui_tiles" in text
    assert 'selected == "players"' in text


def test_player_filter_tiles_are_transparent_and_on_brand():
    text = (ROOT / "gui" / "player_filter_tiles_v2.py").read_text(encoding="utf-8-sig")
    assert "background:transparent" in text
    assert "var(--frl-accent)" in text
    assert "var(--frl-text)" in text
    assert 'font-family:"Source Sans"' in text


def test_player_filter_tiles_keep_verified_passing_boundary():
    text = (ROOT / "gui" / "player_filter_tiles_v2.py").read_text(encoding="utf-8-sig")
    assert "player_research_player_match" in text
    assert "player_match_passes" in text
    assert "player_match_accurate_passes" in text
    assert "player_match_key_passes" in text
    assert "player_match_big_chances_created" in text
