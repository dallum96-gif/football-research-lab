from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_team_view_uses_one_shot_navigation_handoff():
    ui = (ROOT / "gui" / "team_research_ui.py").read_text(encoding="utf-8-sig")
    shell = (ROOT / "gui" / "ui_shell.py").read_text(encoding="utf-8-sig")

    assert 'st.session_state.pop("_frl_team_view_target", "Profile")' in ui
    assert 'key="frl_team_view"' in ui
    assert 'st.session_state["frl_team_view"]' not in shell
    assert 'st.session_state.pop("frl_team_view", None)' in shell


def test_sidebar_buttons_are_left_aligned():
    shell = (ROOT / "gui" / "ui_shell.py").read_text(encoding="utf-8-sig")

    assert 'justify-content:flex-start !important;width:100% !important' in shell
    assert 'text-align:left !important;width:100% !important' in shell


def test_team_stats_uses_performance_map():
    ui = (ROOT / "gui" / "team_research_ui.py").read_text(encoding="utf-8-sig")
    visualisations = (ROOT / "frl_team_visualisations.py").read_text(encoding="utf-8-sig")

    assert "team_season_performance_map" in ui
    assert "Season performance map" in ui
    assert "def team_season_performance_map" in visualisations
