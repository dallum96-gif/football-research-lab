from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "gui" / "team_research_ui_v3.py"
SHELL = ROOT / "gui" / "ui_shell.py"


def test_team_research_v3_surface_contract():
    text = UI.read_text(encoding="utf-8-sig")
    assert "def render_team_research_ui" in text
    assert '"Season story"' in text
    assert '"Team snapshot"' in text
    assert '"Attack"' in text
    assert '"Defence"' in text
    assert '"Results"' in text


def test_team_research_v3_profile_chart_is_robust():
    text = UI.read_text(encoding="utf-8-sig")
    assert "def _profile_chart" in text
    assert "datetime.fromisoformat" in text
    assert "background=FRL_SURFACE" in text


def test_sidebar_routes_to_team_research_v3():
    text = SHELL.read_text(encoding="utf-8-sig")
    assert "gui.team_research_ui_v3" in text
    assert "render_team_research_ui" in text
