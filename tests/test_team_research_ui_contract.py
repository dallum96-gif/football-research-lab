from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_team_research_uses_route_scoped_view_state():
    source = (ROOT / "gui" / "team_research_ui.py").read_text(encoding="utf-8-sig")
    assert "frl_team_view_{route.lower()}" in source
    assert "frl_team_view" in source
    assert "default=route" in source


def test_team_research_exposes_simple_browsing_toggles():
    source = (ROOT / "gui" / "team_research_ui.py").read_text(encoding="utf-8-sig")
    assert "[\"Form\", \"Attack\", \"Defence\"]" in source
    assert "[5, 10]" in source
    assert "[\"Last 5\", \"Last 10\", \"Custom\"]" in source
    assert "[\"Performance\", \"Attack\", \"Defence\"]" in source


def test_sidebar_left_alignment_is_explicit():
    source = (ROOT / "gui" / "ui_shell.py").read_text(encoding="utf-8-sig")
    assert "justify-content:flex-start" in source
    assert "text-align:left" in source
    assert "frl-sidebar-section" in source
