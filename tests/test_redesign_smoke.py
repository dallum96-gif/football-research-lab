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

    keys: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "NavigationItem":
            if node.args and isinstance(node.args[0], ast.Constant):
                keys.append(str(node.args[0].value))
    return keys


def test_navigation_keys_are_unique():
    keys = _nav_items()
    assert keys
    assert len(keys) == len(set(keys))


def test_projection_lab_is_in_analysis_navigation():
    navigation = (ROOT / "gui" / "navigation.py").read_text(encoding="utf-8-sig")
    assert 'NavigationItem("prediction", "Projection Lab", "Analysis"' in navigation
    assert '"Modelling"' not in navigation.split("SECTION_ORDER", 1)[1].split("FUTURE_WORKSPACES", 1)[0]


def test_all_primary_workspaces_are_routable():
    shell = (ROOT / "gui" / "ui_shell.py").read_text(encoding="utf-8-sig")
    routes = {
        "head-to-head": "render_head_to_head",
        "players": "render_player_research_ui",
        "prediction": "render_projection_lab",
    }

    for workspace, renderer in routes.items():
        assert f'selected == "{workspace}"' in shell
        assert renderer in shell

    app = (ROOT / "gui" / "app_redesign.py").read_text(encoding="utf-8-sig")
    for workspace in ("fixtures", "league-table", "form"):
        assert f'workspace == "{workspace}"' in app


def test_player_filter_tile_design_boundary():
    renderer = (ROOT / "gui" / "player_filter_tiles_v2.py").read_text(encoding="utf-8-sig")
    shell = (ROOT / "gui" / "ui_shell.py").read_text(encoding="utf-8-sig")

    assert "def render_player_research_ui_tiles" in renderer
    assert "st.popover(" not in renderer
    assert "background:transparent" in renderer
    assert "var(--frl-accent)" in renderer
    assert 'font-family:"Source Sans"' in renderer
    assert "player_research_player_match" in renderer
    assert "player_match_passes" in renderer
    assert "player_match_accurate_passes" in renderer
    assert "player_match_key_passes" in renderer
    assert "player_match_big_chances_created" in renderer
    assert "player_filter_tiles_v2" in shell
