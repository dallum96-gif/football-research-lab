

def test_team_research_view_contract():
    team_ui = (ROOT / "gui" / "team_research_ui.py").read_text(encoding="utf-8-sig")
    shell = (ROOT / "gui" / "ui_shell.py").read_text(encoding="utf-8-sig")

    assert "render_team_research_ui" in team_ui
    assert "Team Profile" in team_ui or "Team view" in team_ui
    assert '"Profile"' in team_ui
    assert '"Stats"' in team_ui
    assert "query_api.team_summary" in team_ui
    assert "team_season_comparison" in team_ui or "query_api.team_compare" in team_ui
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
