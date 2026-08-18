from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _nav_items():
    source = (ROOT / "gui" / "navigation.py").read_text(encoding="utf-8-sig")
    tree = ast.parse(source)
    items = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "NavigationItem":
            if len(node.args) >= 3 and all(isinstance(arg, ast.Constant) for arg in node.args[:3]):
                items.append(tuple(str(arg.value) for arg in node.args[:3]))
    return items


def test_navigation_information_architecture():
    assert _nav_items() == [
        ("overview", "Home", "Homepage"),
        ("fixtures", "Fixtures", "General"),
        ("league-table", "League Table", "General"),
        ("team-profile", "Team Profile", "Teams"),
        ("team-stats", "Team Stats", "Teams"),
        ("player-profile", "Player Profile", "Players"),
        ("player-stats", "Player Stats", "Players"),
        ("prediction", "Projection Lab", "Matchday Centre"),
        ("head-to-head", "H2H / Stats Pack", "Matchday Centre"),
    ]


def test_sidebar_grouping_and_team_player_routes():
    shell = (ROOT / "gui" / "ui_shell.py").read_text(encoding="utf-8-sig")
    assert "frl-sidebar-section" in shell
    assert 'type="primary" if selected == item.key else "tertiary"' in shell
    assert "TEAM_VIEW_TARGETS" in shell
    assert "PLAYER_VIEW_TARGETS" in shell
    assert "render_team_research_ui" in shell
    assert "player_filter_tiles_v4" in shell
    assert "width=\"stretch\"" in shell
