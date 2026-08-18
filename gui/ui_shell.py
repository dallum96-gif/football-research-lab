"""Quiet, grouped navigation shell for the Football Research Laboratory."""

import html

import streamlit as st

from gui.navigation import HIDDEN_WORKSPACES, NAVIGATION, SECTION_ORDER, navigation_by_section


ICONS = {
    "overview": "home",
    "fixtures": "calendar_month",
    "league-table": "table_rows",
    "team-profile": "shield",
    "team-stats": "analytics",
    "player-profile": "person",
    "player-stats": "bar_chart",
    "prediction": "query_stats",
    "head-to-head": "swap_horiz",
    "teams": "shield",
    "players": "person",
    "analysis": "insights",
    "form": "trending_up",
    "data-quality": "verified",
    "provenance": "link",
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
            st.markdown(
                f"<div class='frl-home-card'><div class='frl-home-card-title'>{title}</div>"
                f"<div class='frl-home-card-copy'>{description}</div></div>",
                unsafe_allow_html=True,
            )
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
        section[data-testid="stSidebar"] * { box-sizing:border-box; }
        section[data-testid="stSidebar"] .block-container,
        section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] { font-family:"Source Sans",sans-serif !important; }
        .frl-sidebar-brand{display:block;width:100%;margin:0 0 1.05rem;padding:0;color:#fffaf0;text-align:left;font-family:"Source Sans",sans-serif;font-size:.67rem;font-weight:800;letter-spacing:.105em;line-height:1.2;text-transform:uppercase}
        .frl-sidebar-section{display:block;width:100%;margin:1.05rem 0 .35rem;padding:0;color:#8f8a7f;text-align:left;font-family:"Source Sans",sans-serif;font-size:.53rem;font-weight:800;letter-spacing:.145em;line-height:1.1;text-transform:uppercase}
        .frl-sidebar-section:first-of-type{margin-top:0}
        .frl-nav{display:block;width:100%;margin:0;padding:0}
        .frl-nav-item{display:flex;width:100%;height:1.72rem;align-items:center;gap:.52rem;margin:0;padding:.12rem .36rem;border-left:2px solid transparent;border-radius:0 5px 5px 0;background:transparent;color:#c9c6bc !important;text-decoration:none !important;font-family:"Source Sans",sans-serif;font-size:.73rem;font-weight:600;line-height:1;transition:background .12s ease,color .12s ease,border-color .12s ease}
        .frl-nav-item:hover{background:rgba(255,255,255,.055);color:#fffaf0 !important}
        .frl-nav-item.is-active{background:rgba(255,255,255,.065);border-left-color:#e85d3f;color:#f06d4e !important;font-weight:700}
        .frl-nav-icon{width:1.05rem;flex:0 0 1.05rem;display:inline-flex;align-items:center;justify-content:center;color:inherit;font-family:"Material Symbols Rounded","Material Symbols Outlined",sans-serif;font-size:17px;line-height:1;font-variation-settings:"FILL" 0,"wght" 520,"GRAD" 0,"opsz" 20}
        .frl-nav-label{display:block;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-align:left}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_nav_link(item, selected: str) -> None:
    label = html.escape(item.label)
    key = html.escape(item.key, quote=True)
    icon = html.escape(ICONS.get(item.key, "circle"), quote=True)
    active = " is-active" if selected == item.key else ""
    st.sidebar.markdown(
        f'<nav class="frl-nav"><a class="frl-nav-item{active}" href="?workspace={key}" aria-label="{label}">'
        f'<span class="frl-nav-icon">{icon}</span><span class="frl-nav-label">{label}</span></a></nav>',
        unsafe_allow_html=True,
    )


def render_workspace_sidebar(active_key):
    grouped = navigation_by_section()
    selected = current_workspace(active_key)
    _sidebar_navigation_css()
    st.sidebar.markdown("<div class='frl-sidebar-brand'>FOOTBALL RESEARCH LABORATORY</div>", unsafe_allow_html=True)

    for section in SECTION_ORDER:
        items = grouped[section]
        if not items:
            continue
        st.sidebar.markdown(f"<div class='frl-sidebar-section'>{html.escape(section)}</div>", unsafe_allow_html=True)
        for item in items:
            _render_nav_link(item, selected)

    if selected in TEAM_VIEW_TARGETS or selected == "teams":
        if selected in TEAM_VIEW_TARGETS:
            st.session_state["frl_team_view"] = TEAM_VIEW_TARGETS[selected]
        _render_teams_hub()
        st.stop()

    if selected in PLAYER_VIEW_TARGETS or selected == "players":
        if selected in PLAYER_VIEW_TARGETS:
            st.session_state["frl_player_view"] = PLAYER_VIEW_TARGETS[selected]
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
