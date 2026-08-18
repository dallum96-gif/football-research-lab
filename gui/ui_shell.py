"""Quiet, grouped navigation shell for the Football Research Laboratory."""

import streamlit as st

import query_api
from gui.navigation import HIDDEN_WORKSPACES, NAVIGATION, SECTION_ORDER, navigation_by_section


ICONS = {
    "overview": ":material/home:",
    "fixtures": ":material/calendar_month:",
    "league-table": ":material/table_rows:",
    "team-profile": ":material/shield:",
    "team-stats": ":material/analytics:",
    "player-profile": ":material/person:",
    "player-stats": ":material/bar_chart:",
    "prediction": ":material/query_stats:",
    "head-to-head": ":material/swap_horiz:",
    "teams": ":material/shield:",
    "players": ":material/person:",
    "analysis": ":material/insights:",
    "form": ":material/trending_up:",
    "data-quality": ":material/verified:",
    "provenance": ":material/link:",
}

PRIMARY_WORKSPACES = {item.key for item in NAVIGATION}
VALID_WORKSPACES = PRIMARY_WORKSPACES | set(HIDDEN_WORKSPACES)
TEAM_VIEW_TARGETS = {"team-profile": "Profile", "team-stats": "Stats"}
PLAYER_VIEW_TARGETS = {"player-profile": "Profile", "player-stats": "Stats"}


def current_workspace(default="overview"):
    query_workspace = st.query_params.get("workspace")
    if query_workspace in VALID_WORKSPACES:
        return query_workspace
    return st.session_state.get("frl_workspace", default)


def _render_teams_hub():
    from gui.team_research_ui import render_team_research_ui
    render_team_research_ui()


def _render_players_hub():
    from gui.player_filter_tiles_v4 import render_player_research_ui_tiles as render_player_research_ui
    st.markdown("<div class='frl-eyebrow'>Research</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-entity-title'>Players</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-context'>Player performance research across Premier League seasons</div>", unsafe_allow_html=True)
    render_player_research_ui()


def _render_analysis_hub():
    st.markdown("<div class='frl-eyebrow'>Matchday Centre</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-entity-title'>Matchday Centre</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-context'>Match-specific evidence, modelling and future analytical tools.</div>", unsafe_allow_html=True)
    tools = [
        ("Projection Lab", "Fixture context, projections and the route into prediction.", "prediction"),
        ("H2H / Stats Pack", "Compare two clubs through shared history and match-specific evidence.", "head-to-head"),
    ]
    cols = st.columns(2, gap="small")
    for col, (title, description, target) in zip(cols, tools):
        with col:
            st.markdown(f"<div class='frl-home-card'><div class='frl-home-card-title'>{title}</div><div class='frl-home-card-copy'>{description}</div></div>", unsafe_allow_html=True)
            if st.button("Open", key=f"analysis_open_{target}", type="tertiary", width="stretch"):
                st.session_state["frl_workspace"] = target
                st.query_params["workspace"] = target
                st.rerun()
    st.markdown("<div class='frl-collage-section'>Coming into the same analytical layer</div>", unsafe_allow_html=True)
    st.caption("Query, comparable matches, combined metrics, records and future mathematical/statistical models are designed to consume the same canonical graph and shared analytical services.")


def _sidebar_navigation_css() -> None:
    st.sidebar.markdown(
        """
        <style>
        section[data-testid="stSidebar"] *,
        section[data-testid="stSidebar"] button,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span { font-family:"Source Sans",sans-serif !important; }
        .frl-sidebar-brand{display:block!important;width:100%!important;box-sizing:border-box!important;color:#fffaf0!important;text-align:left!important;font-size:.66rem!important;font-weight:800!important;letter-spacing:.11em!important;line-height:1.25!important;text-transform:uppercase!important;margin:0 0 .88rem!important;padding:0!important}
        .frl-sidebar-section{display:block!important;width:100%!important;box-sizing:border-box!important;color:#8f8a7f!important;text-align:left!important;font-size:.53rem!important;font-weight:800!important;letter-spacing:.14em!important;line-height:1.15!important;text-transform:uppercase!important;margin:0!important;padding:0!important}
        section[data-testid="stSidebar"] .stMarkdown{width:100%!important;text-align:left!important;margin:0!important;padding:0!important}
        section[data-testid="stSidebar"] .stMarkdown>div{width:100%!important;text-align:left!important;margin:0!important;padding:0!important}
        section[data-testid="stSidebar"] .stMarkdown:has(.frl-sidebar-section){margin-bottom:.72rem!important}
        section[data-testid="stSidebar"] .stMarkdown:has(.frl-sidebar-brand){margin-bottom:1rem!important}
        section[data-testid="stSidebar"] .stButton{width:100%!important;margin:0!important;padding:0!important}
        section[data-testid="stSidebar"] .stButton>button{width:100%!important;min-height:1.54rem!important;height:1.54rem!important;margin:0!important;padding:.16rem .38rem!important;border:0!important;border-radius:5px!important;background:transparent!important;color:#c9c6bc!important;box-shadow:none!important;font-size:.73rem!important;font-weight:600!important;line-height:1!important;justify-content:flex-start!important;align-items:center!important;text-align:left!important}
        section[data-testid="stSidebar"] .stButton>button>div{display:flex!important;flex:1 1 auto!important;width:auto!important;height:100%!important;margin:0!important;padding:0!important;justify-content:flex-start!important;align-items:center!important;text-align:left!important}
        section[data-testid="stSidebar"] .stButton>button>div>div{display:flex!important;justify-content:flex-start!important;align-items:center!important;width:auto!important;max-width:none!important;text-align:left!important}
        section[data-testid="stSidebar"] .stButton>button p{width:auto!important;max-width:none!important;margin:0!important;padding:0!important;color:inherit!important;text-align:left!important;line-height:1!important;font-family:"Source Sans",sans-serif!important}
        section[data-testid="stSidebar"] .stButton>button span{color:inherit!important;text-align:left!important}
        section[data-testid="stSidebar"] .stButton>button:hover{color:#fffaf0!important;background:rgba(232,93,63,.10)!important}
        section[data-testid="stSidebar"] .stButton>button[kind="primary"]{background:rgba(255,255,255,.055)!important;color:#f06d4e!important;border-left:2px solid #e85d3f!important;border-radius:0 5px 5px 0!important}
        section[data-testid="stSidebar"] .stButton>button[kind="primary"]:hover{background:rgba(255,255,255,.08)!important}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _navigate(item_key: str) -> None:
    st.session_state["frl_workspace"] = item_key
    st.query_params["workspace"] = item_key
    if item_key in TEAM_VIEW_TARGETS:
        st.session_state["frl_team_view"] = TEAM_VIEW_TARGETS[item_key]
    elif item_key in PLAYER_VIEW_TARGETS:
        st.session_state["frl_player_view"] = PLAYER_VIEW_TARGETS[item_key]
    st.rerun()


def render_workspace_sidebar(active_key):
    grouped = navigation_by_section()
    selected = current_workspace(active_key)
    _sidebar_navigation_css()
    st.sidebar.markdown("<div class='frl-sidebar-brand'>FOOTBALL RESEARCH LABORATORY</div>", unsafe_allow_html=True)
    for section in SECTION_ORDER:
        items = grouped[section]
        if not items:
            continue
        st.sidebar.markdown(f"<div class='frl-sidebar-section'>{section}</div>", unsafe_allow_html=True)
        for item in items:
            if st.sidebar.button(item.label, key=f"nav_{item.key}", icon=ICONS.get(item.key), width="stretch", type="primary" if selected == item.key else "tertiary", help=item.description):
                _navigate(item.key)
    if selected in TEAM_VIEW_TARGETS or selected == "teams":
        if selected in TEAM_VIEW_TARGETS:
            st.session_state["frl_team_view"] = TEAM_VIEW_TARGETS[selected]
        _render_teams_hub(); st.stop()
    if selected in PLAYER_VIEW_TARGETS or selected == "players":
        if selected in PLAYER_VIEW_TARGETS:
            st.session_state["frl_player_view"] = PLAYER_VIEW_TARGETS[selected]
        _render_players_hub(); st.stop()
    if selected == "analysis":
        _render_analysis_hub(); st.stop()
    if selected == "head-to-head":
        from gui.head_to_head_ui import render_head_to_head
        render_head_to_head(); st.stop()
    if selected == "prediction":
        from gui.projection_lab_v2 import render_projection_lab
        render_projection_lab(); st.stop()
    return selected
