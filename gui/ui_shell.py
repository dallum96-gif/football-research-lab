from __future__ import annotations

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
TEAM_VIEW_TARGETS = {"team-profile", "team-stats"}
PLAYER_VIEW_TARGETS = {"player-profile", "player-stats"}


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
        .frl-sidebar-brand{color:var(--frl-text);font-size:.68rem;font-weight:850;letter-spacing:.14em;line-height:1.3;margin:.15rem 0 1.1rem}
        .frl-sidebar-section{color:var(--frl-muted-soft);font-size:.54rem;font-weight:850;letter-spacing:.16em;text-transform:uppercase;margin:.95rem 0 .24rem;padding-top:.12rem}
        [data-testid="stSidebar"] .stButton{margin:0 !important}
        [data-testid="stSidebar"] .stButton > button{justify-content:flex-start !important;text-align:left !important;border-radius:5px !important;border:1px solid transparent !important;min-height:2rem !important;padding:.18rem .5rem !important;font-size:.72rem !important;font-weight:650 !important;box-shadow:none !important}
        [data-testid="stSidebar"] .stButton > button > div{justify-content:flex-start !important;width:100% !important}
        [data-testid="stSidebar"] .stButton > button p{text-align:left !important;width:100% !important;margin:0 !important}
        [data-testid="stSidebar"] .stButton > button:hover{background:var(--frl-surface) !important;border-color:var(--frl-border) !important}
        [data-testid="stSidebar"] .stButton > button[kind="primary"]{background:var(--frl-surface) !important;color:var(--frl-accent) !important;border-color:var(--frl-border) !important}
        [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover{background:var(--frl-surface) !important}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _navigate(item_key: str) -> None:
    st.session_state["frl_workspace"] = item_key
    st.query_params["workspace"] = item_key
    st.session_state.pop(f"frl_team_view_{item_key}", None)
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
            if st.sidebar.button(
                item.label,
                key=f"nav_{item.key}",
                icon=ICONS.get(item.key),
                width="stretch",
                type="primary" if selected == item.key else "tertiary",
                help=item.description,
            ):
                _navigate(item.key)

    if selected in TEAM_VIEW_TARGETS or selected == "teams":
        _render_teams_hub()
        st.stop()
    if selected in PLAYER_VIEW_TARGETS or selected == "players":
        _render_players_hub()
        st.stop()
    if selected == "analysis":
        _render_analysis_hub()
        st.stop()
    if selected == "head-to-head":
        from gui.head_to_head_ui import render_head_to_head
        render_head_to_head()
        st.stop()
    if selected == "prediction":
        from gui.projection_lab_v2 import render_projection_lab
        render_projection_lab()
        st.stop()

    return selected
