"""Quiet, text-led navigation shell for the Football Research Laboratory."""

import streamlit as st

from gui.navigation import SECTION_ORDER, navigation_by_section


ICONS = {
    "overview": ":material/home:",
    "fixtures": ":material/calendar_month:",
    "league-table": ":material/table_rows:",
    "players": ":material/person:",
    "head-to-head": ":material/swap_horiz:",
    "form": ":material/trending_up:",
    "prediction": ":material/query_stats:",
    "data-quality": ":material/verified:",
    "provenance": ":material/link:",
}

VALID_WORKSPACES = {
    "overview",
    "fixtures",
    "league-table",
    "players",
    "head-to-head",
    "form",
    "prediction",
    "data-quality",
    "provenance",
}


def current_workspace(default="overview"):
    """Return the current workspace, preferring the URL when present."""
    query_workspace = st.query_params.get("workspace")
    if query_workspace in VALID_WORKSPACES:
        return query_workspace
    return st.session_state.get("frl_workspace", default)


def render_workspace_sidebar(active_key):
    """Render compact, text-led application navigation."""
    grouped = navigation_by_section()
    selected = current_workspace(active_key)

    st.sidebar.markdown(
        "<div class='frl-sidebar-brand'>FOOTBALL RESEARCH LABORATORY</div>",
        unsafe_allow_html=True,
    )

    for section in SECTION_ORDER:
        items = grouped[section]
        if not items:
            continue

        st.sidebar.markdown(
            f"<div class='frl-sidebar-section'>{section}</div>",
            unsafe_allow_html=True,
        )

        for item in items:
            if st.sidebar.button(
                item.label,
                key=f"nav_{item.key}",
                icon=ICONS.get(item.key),
                use_container_width=True,
                type="secondary",
            ):
                st.session_state["frl_workspace"] = item.key
                st.query_params["workspace"] = item.key
                st.rerun()

    if selected == "head-to-head":
        from gui.head_to_head_ui import render_head_to_head
        render_head_to_head()
        st.stop()

    if selected == "players":
        from gui.player_filter_tiles_v2 import render_player_research_ui_tiles as render_player_research_ui
        st.markdown("<div class='frl-eyebrow'>Research</div>", unsafe_allow_html=True)
        st.markdown("<div class='frl-entity-title'>Players</div>", unsafe_allow_html=True)
        st.markdown("<div class='frl-context'>Player performance research across Premier League seasons</div>", unsafe_allow_html=True)
        render_player_research_ui()
        st.stop()

    if selected == "prediction":
        from gui.projection_lab_v2 import render_projection_lab
        render_projection_lab()
        st.stop()

    return selected
