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


def _sidebar_navigation_html(grouped, selected: str) -> str:
    parts = [
        """
        <style>
        section[data-testid="stSidebar"] .block-container{font-family:"Source Sans",sans-serif!important}
        .frl-sidebar-shell{width:100%;box-sizing:border-box;color:#c9c6bc;font-family:"Source Sans",sans-serif}
        .frl-sidebar-brand{margin:0 0 24px;color:#fffaf0;font-size:11px;font-weight:800;letter-spacing:.105em;line-height:1.2;text-transform:uppercase}
        .frl-sidebar-section{margin:21px 0 8px;color:#8f8a7f;font-size:9px;font-weight:800;letter-spacing:.145em;line-height:1.15;text-align:left;text-transform:uppercase}
        .frl-sidebar-section:first-of-type{margin-top:0}
        .frl-sidebar-links{display:flex;flex-direction:column;gap:3px;width:100%}
        .frl-sidebar-link{display:flex;width:100%;height:29px;box-sizing:border-box;align-items:center;gap:9px;margin:0;padding:4px 8px 4px 9px;border-left:2px solid transparent;border-radius:0 5px 5px 0;background:transparent;color:#c9c6bc!important;text-decoration:none!important;font-family:"Source Sans",sans-serif;font-size:13px;font-weight:600;line-height:1.1;transition:background .12s ease,color .12s ease,border-color .12s ease}
        .frl-sidebar-link:hover{background:rgba(255,255,255,.055);color:#fffaf0!important}
        .frl-sidebar-link.is-active{background:rgba(255,255,255,.065);border-left-color:#e85d3f;color:#f06d4e!important;font-weight:700}
        .frl-sidebar-icon{width:18px;flex:0 0 18px;display:inline-flex;align-items:center;justify-content:center;color:inherit;font-family:"Material Symbols Rounded","Material Symbols Outlined",sans-serif;font-size:18px;line-height:1;font-variation-settings:"FILL" 0,"wght" 520,"GRAD" 0,"opsz" 20}
        .frl-sidebar-label{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:left}
        </style>
        <div class="frl-sidebar-shell">
          <div class="frl-sidebar-brand">FOOTBALL RESEARCH LABORATORY</div>
        """
    ]
    for section in SECTION_ORDER:
        items = grouped[section]
        if not items:
            continue
        parts.append(f'<div class="frl-sidebar-section">{html.escape(section)}</div>')
        parts.append('<div class="frl-sidebar-links">')
        for item in items:
            label = html.escape(item.label)
            key = html.escape(item.key, quote=True)
            icon = html.escape(ICONS.get(item.key, "circle"), quote=True)
            active = " is-active" if selected == item.key else ""
            parts.append(
                f'<a class="frl-sidebar-link{active}" href="?workspace={key}" aria-label="{label}">'
                f'<span class="frl-sidebar-icon">{icon}</span>'
                f'<span class="frl-sidebar-label">{label}</span>'
                "</a>"
            )
        parts.append("</div>")
    parts.append("</div>")
    return "".join(parts)


def render_workspace_sidebar(active_key):
    grouped = navigation_by_section()
    selected = current_workspace(active_key)
    st.sidebar.markdown(_sidebar_navigation_html(grouped, selected), unsafe_allow_html=True)

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
