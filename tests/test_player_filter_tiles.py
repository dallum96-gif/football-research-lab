from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_player_filter_tile_renderer_shape():
    path = ROOT / "gui" / "player_filter_tiles_v3.py"
    text = path.read_text(encoding="utf-8-sig")

    assert "def render_player_research_ui_tiles" in text
    assert "frl-filter-kicker" in text
    assert "stVerticalBlockBorderWrapper" in text
    assert "st.popover(" not in text
    assert 'font-family:"Source Sans"' in text


def test_players_workspace_routes_to_v3_tile_renderer():
    text = (ROOT / "gui" / "ui_shell.py").read_text(encoding="utf-8-sig")
    assert "player_filter_tiles_v3" in text
    assert "render_player_research_ui_tiles" in text
    assert 'selected == "players"' in text


def test_player_filter_tiles_are_light_and_on_brand():
    text = (ROOT / "gui" / "player_filter_tiles_v3.py").read_text(encoding="utf-8-sig")
    assert "background:transparent" in text
    assert "background:var(--frl-surface)" in text
    assert "var(--frl-accent)" in text
    assert "var(--frl-text)" in text
    assert "background:#000" not in text.lower()
    assert "background:black" not in text.lower()


def test_no_dark_selector_surfaces():
    text = (ROOT / "gui" / "player_filter_tiles_v3.py").read_text(encoding="utf-8-sig")
    assert '[data-baseweb="menu"]' in text
    assert "background:var(--frl-surface)" in text
    assert "background:transparent" in text
    assert "background:#000" not in text.lower()
    assert "background:black" not in text.lower()


def test_player_filter_tiles_keep_verified_passing_boundary():
    text = (ROOT / "gui" / "player_filter_tiles_v3.py").read_text(encoding="utf-8-sig")
    assert "player_research_player_match" in text
    assert "player_match_passes" in text
    assert "player_match_accurate_passes" in text
    assert "player_match_key_passes" in text
    assert "player_match_big_chances_created" in text


def test_fmt_dependency_is_explicit():
    text = (ROOT / "gui" / "player_filter_tiles_v3.py").read_text(encoding="utf-8-sig")
    assert "fmt" in text.split("from gui.player_research_ui import", 1)[1]
