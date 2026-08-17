from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_redesign_python_files_compile():
    targets = [ROOT / "gui", ROOT / "poisson_model.py", ROOT / "player_research.py"]
    failures: list[str] = []

    for target in targets:
        paths = [target] if target.is_file() else list(target.rglob("*.py"))
        for path in paths:
            try:
                ast.parse(path.read_text(encoding="utf-8-sig"))
            except SyntaxError as exc:
                failures.append(f"{path}: {exc}")

    assert not failures, "\n".join(failures)


def _nav_items():
    navigation = (ROOT / "gui" / "navigation.py").read_text(encoding="utf-8-sig")
    tree = ast.parse(navigation)

    items: list[tuple[str, str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "NavigationItem":
            if len(node.args) >= 3 and all(isinstance(arg, ast.Constant) for arg in node.args[:3]):
                items.append((str(node.args[0].value), str(node.args[1].value), str(node.args[2].value)))
    return items


def test_navigation_contains_exact_primary_workspaces():
    items = _nav_items()
    assert [(key, label) for key, label, _ in items] == [
        ("overview", "Home"),
        ("fixtures", "Fixtures & Results"),
        ("league-table", "League Table"),
        ("teams", "Teams"),
        ("players", "Players"),
        ("analysis", "Analysis"),
    ]
    assert all(section == "Primary" for _, _, section in items)


def test_navigation_keys_are_unique():
    items = _nav_items()
    keys = [key for key, _, _ in items]
    assert keys
    assert len(keys) == len(set(keys))


def test_projection_lab_is_available_under_analysis():
    shell = (ROOT / "gui" / "ui_shell.py").read_text(encoding="utf-8-sig")
    assert 'selected == "analysis"' in shell
    assert '"prediction"' in shell
    assert "render_projection_lab" in shell


def test_all_primary_workspaces_are_routable():
    shell = (ROOT / "gui" / "ui_shell.py").read_text(encoding="utf-8-sig")
    routes = {
        "teams": "_render_teams_hub",
        "analysis": "_render_analysis_hub",
        "players": "render_player_research_ui",
    }

    for workspace, renderer in routes.items():
        assert f'selected == "{workspace}"' in shell
        assert renderer in shell

    app = (ROOT / "gui" / "app_redesign.py").read_text(encoding="utf-8-sig")
    for workspace in ("overview", "fixtures", "league-table"):
        assert f'workspace == "{workspace}"' in app


def test_team_research_view_contract():
    team_ui = (ROOT / "gui" / "team_research_ui.py").read_text(encoding="utf-8-sig")
    shell = (ROOT / "gui" / "ui_shell.py").read_text(encoding="utf-8-sig")

    assert "render_team_research_ui" in team_ui
    assert "Team Profile" in team_ui or "Team view" in team_ui
    assert '"Profile"' in team_ui
    assert '"Stats"' in team_ui
    assert "query_api.team_summary" in team_ui
    assert "query_api.team_compare" in team_ui
    assert "query_api.team_form" in team_ui
    assert "query_api.fixtures" in team_ui
    assert "fixtures_master_corrected.csv" not in team_ui
    assert 'font-family:"Source Sans"' not in team_ui
    assert "background:var(--frl-surface)" in team_ui
    assert 'selected == "teams"' in shell
    assert "render_team_research_ui" in shell


def test_hidden_contextual_workspaces_remain_compatible():
    navigation = (ROOT / "gui" / "navigation.py").read_text(encoding="utf-8-sig")
    for key in ("head-to-head", "form", "prediction", "data-quality", "provenance"):
        assert key in navigation
    assert "HIDDEN_WORKSPACES" in navigation


def test_player_filter_tile_design_boundary():
    renderer_paths = [
        ROOT / "gui" / "player_filter_tiles_v2.py",
        ROOT / "gui" / "player_filter_tiles_v3.py",
        ROOT / "gui" / "player_filter_tiles_v4.py",
    ]
    renderer_text = "\n".join(
        path.read_text(encoding="utf-8-sig")
        for path in renderer_paths
        if path.exists()
    )
    shell = (ROOT / "gui" / "ui_shell.py").read_text(encoding="utf-8-sig")

    assert "def render_player_research_ui_tiles" in renderer_text
    assert "st.popover(" not in renderer_text
    assert "background:transparent" in renderer_text
    assert "var(--frl-accent)" in renderer_text
    assert 'font-family:"Source Sans"' in renderer_text
    assert "player_research_player_match" in renderer_text
    assert "player_match_passes" in renderer_text
    assert "player_match_accurate_passes" in renderer_text
    assert "player_match_key_passes" in renderer_text
    assert "player_match_big_chances_created" in renderer_text
    assert "player_filter_tiles_v4" in shell


def test_player_filter_tiles_v4_is_art_directed_and_light():
    renderer = (ROOT / "gui" / "player_filter_tiles_v4.py").read_text(encoding="utf-8-sig")
    assert "Build a shortlist" in renderer
    assert "Stats, thresholds & combinations" in renderer
    assert 'content:"＋"' in renderer
    assert "opacity:0" in renderer
    assert "[data-baseweb=\"menu\"]" in renderer
    assert "background:var(--frl-surface)" in renderer
