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


def render_workspace_sidebar(active_key):
    """Render compact, clearly separated application navigation."""
    grouped = navigation_by_section()
    selected = active_key

    st.sidebar.markdown(
        "<div class='frl-sidebar-brand'>FOOTBALL RESEARCH LABORATORY</div>",
        unsafe_allow_html=True,
    )

    visible_sections = [section for section in SECTION_ORDER if grouped[section]]

    for section_index, section in enumerate(visible_sections):
        items = grouped[section]

        st.sidebar.markdown(
            f"<div class='frl-sidebar-section'>{section}</div>",
            unsafe_allow_html=True,
        )

        # A real DOM spacer between the category heading and the first
        # Streamlit button prevents the two from visually colliding.
        st.sidebar.markdown(
            "<div class='frl-sidebar-heading-gap' aria-hidden='true'></div>",
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
                selected = item.key
                st.session_state["frl_workspace"] = item.key
                st.rerun()

        if section_index < len(visible_sections) - 1:
            st.sidebar.markdown(
                "<div class='frl-sidebar-section-gap' aria-hidden='true'></div>",
                unsafe_allow_html=True,
            )

    return selected


def current_workspace(default="overview"):
    """Return the current workspace key."""
    return st.session_state.get("frl_workspace", default)
