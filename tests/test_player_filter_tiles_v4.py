from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_v4_advanced_tile_is_art_directed():
    text = (ROOT / "gui" / "player_filter_tiles_v4.py").read_text(encoding="utf-8-sig")
    assert "render_player_research_ui_tiles" in text
    assert "Build a shortlist" in text
    assert "content:\"＋\"" in text
    assert "Explore stats, thresholds & combinations" in text
    assert "data-baseweb=\"menu\"" in text


def test_v4_removes_toggle_visual_chrome():
    text = (ROOT / "gui" / "player_filter_tiles_v4.py").read_text(encoding="utf-8-sig")
    assert "opacity:0" in text
    assert "background:transparent" in text
    assert "box-shadow:none" in text


def test_v4_keeps_player_match_renderer_boundary():
    v3 = (ROOT / "gui" / "player_filter_tiles_v3.py").read_text(encoding="utf-8-sig")
    assert "player_research_player_match" in v3
    assert "player_match_passes" in v3
    assert "player_match_accurate_passes" in v3
