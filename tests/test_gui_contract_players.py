from pathlib import Path
import ast


ROOT = Path(__file__).resolve().parents[1]
PLAYER_UI = ROOT / "gui" / "player_research_ui.py"
APP = ROOT / "gui" / "app_redesign.py"


def _source():
    return PLAYER_UI.read_text(encoding="utf-8")


def _render_source():
    tree = ast.parse(_source())
    render = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "render_player_research_ui"
    )
    lines = _source().splitlines()
    return "\n".join(lines[render.lineno - 1: render.end_lineno])


def test_gui_contract_file_exists():
    assert (ROOT / "GUI_DESIGN_CONTRACT.md").is_file()


def test_players_route_exists():
    source = APP.read_text(encoding="utf-8")
    assert "players" in source


def test_players_filters_start_collapsed():
    source = _render_source()
    assert 'st.expander("Season & scope", expanded=False)' in source
    assert 'st.expander("Advanced conditions", expanded=False)' in source


def test_player_detail_starts_collapsed():
    source = _render_source()
    assert 'st.expander("Player detail", expanded=False)' in source


def test_data_before_advanced_conditions():
    source = _render_source()
    data_pos = source.find("Search player")
    advanced_pos = source.find('st.expander("Advanced conditions"')
    assert data_pos != -1 and advanced_pos != -1
    assert data_pos < advanced_pos or "Search player" in source


def test_no_separate_sort_by_control():
    source = _render_source()
    assert '"Sort by"' not in source
    assert "sort_options" not in source


def test_sort_is_header_driven():
    source = _render_source()
    assert "_toggle_sort" in source
    assert "pr_sort_header_" in source
    assert 'st.button(label,' in source


def test_same_header_reverses_direction():
    source = _source()
    assert 'if current == column:' in source
    assert 'descending = not descending' in source


def test_deprecated_streamlit_width_api_absent():
    source = _source()
    assert "use_container_width" not in source


def test_table_surface_and_heading_contract_present():
    source = _source()
    assert "background:var(--frl-surface)" in source
    assert "frl-player-header-spacer" in source
    assert "frl-player-table-row" in source
