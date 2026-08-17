from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_team_workspace_uses_canonical_query_boundary():
    ui = (ROOT / "gui" / "team_research_ui.py").read_text(encoding="utf-8-sig")
    assert "query_api.team_summary" in ui
    assert "query_api.team_compare" in ui
    assert "query_api.team_form" in ui
    assert "query_api.fixtures" in ui
    assert "fixtures_master_corrected.csv" not in ui
    assert "query_lab" not in ui


def test_team_workspace_has_profile_and_stats_views():
    ui = (ROOT / "gui" / "team_research_ui.py").read_text(encoding="utf-8-sig")
    assert '"Profile"' in ui
    assert '"Stats"' in ui
    assert "Season snapshot" in ui
    assert "Season comparison" in ui


def test_team_workspace_preserves_shared_visual_language():
    ui = (ROOT / "gui" / "team_research_ui.py").read_text(encoding="utf-8-sig")
    assert "var(--frl-bg)" not in ui
    assert "var(--frl-surface)" in ui
    assert "var(--frl-border)" in ui
    assert "var(--frl-accent)" in ui
    assert 'font-family:"Source Sans"' not in ui
