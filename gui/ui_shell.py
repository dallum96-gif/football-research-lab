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
    st.markdown(
        "<div class='frl-context'>Player performance research across Premier League seasons</div>",
        unsafe_allow_html=True,
    )
    render_player_research_ui()


def _render_analysis_hub():
    st.markdown("<div class='frl-eyebrow'>Matchday Centre</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-entity-title'>Matchday Centre</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='frl-context'>Match-specific evidence, modelling and future analytical tools.</div>",
        unsafe_allow_html=True,
    )
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
    st.markdown(
        "<div class='frl-collage-section'>Coming into the same analytical layer</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Query, comparable matches, combined metrics, records and future mathematical/statistical models "
        "are designed to consume the same canonical graph and shared analytical services."
    )


def _render_sidebar_navigation(grouped, selected: str) -> None:
    st.sidebar.markdown(
        """
        <style>
        section[data-testid="stSidebar"] .block-container{font-family:"Source Sans",sans-serif!important}
        .frl-sidebar-shell{width:100%;box-sizing:border-box;color:#c9c6bc;font-family:"Source Sans",sans-serif}
        .frl-sidebar-brand{margin:0 0 24px;color:#fffaf0;font-size:11px;font-weight:800;letter-spacing:.105em;line-height:1.2;text-transform:uppercase}
        .frl-sidebar-section{margin:21px 0 8px;color:#8f8a7f;font-size:9px;font-weight:800;letter-spacing:.145em;line-height:1.15;text-align:left;text-transform:uppercase}
        .frl-sidebar-section:first-of-type{margin-top:0}
        section[data-testid="stSidebar"] .frl-nav-button{display:flex!important;justify-content:flex-start!important;text-align:left!important}
        section[data-testid="stSidebar"] .frl-nav-button button{display:flex!important;justify-content:flex-start!important;align-items:center!important;width:100%!important;min-height:29px!important;height:29px!important;margin:0!important;padding:4px 8px 4px 9px!important;border-left:2px solid transparent!important;border-radius:0 5px 5px 0!important;box-shadow:none!important;font-family:"Source Sans",sans-serif!important;font-size:13px!important;font-weight:600!important;line-height:1.1!important;text-align:left!important;transition:background .12s ease,color .12s ease,border-color .12s ease!important}
        section[data-testid="stSidebar"] .frl-nav-button button:hover{background:rgba(255,255,255,.055)!important;color:#fffaf0!important}
        section[data-testid="stSidebar"] .frl-nav-button-active button{background:rgba(255,255,255,.065)!important;border-left-color:#e85d3f!important;color:#f06d4e!important;font-weight:700!important}
        </style>
        <div class="frl-sidebar-shell">
          <div class="frl-sidebar-brand">FOOTBALL RESEARCH LABORATORY</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for section in SECTION_ORDER:
        items = grouped[section]
        if not items:
            continue

        st.sidebar.markdown(
            f'<div class="frl-sidebar-section">{html.escape(section)}</div>',
            unsafe_allow_html=True,
        )

        for item in items:
            icon = ICONS.get(item.key, "circle")
            label = f":material/{icon}: {item.label}"
            wrapper_class = "frl-nav-button frl-nav-button-active" if selected == item.key else "frl-nav-button"
            st.sidebar.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)
            if st.sidebar.button(
                label,
                key=f"frl_sidebar_nav_{item.key}",
                width="stretch",
                type="secondary",
            ):
                st.session_state["frl_workspace"] = item.key
                st.query_params["workspace"] = item.key
                st.rerun()
            st.sidebar.markdown("</div>", unsafe_allow_html=True)


def render_workspace_sidebar(active_key):
    grouped = navigation_by_section()
    selected = current_workspace(active_key)
    _render_sidebar_navigation(grouped, selected)

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
