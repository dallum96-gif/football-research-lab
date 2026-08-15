"""Compact navigation shell for the Football Research Laboratory UI."""

import streamlit as st

from gui.navigation import SECTION_ORDER, navigation_by_section


def render_workspace_sidebar(active_key):
    """Render compact, left-aligned workspace navigation."""
    grouped = navigation_by_section()
    selected = active_key

    st.sidebar.markdown(
        "<div class='frl-sidebar-brand'>Football Research Lab</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        "<div class='frl-sidebar-rule'></div>",
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
                use_container_width=True,
                type="primary" if item.key == active_key else "secondary",
            ):
                selected = item.key
                st.session_state["frl_workspace"] = item.key
                st.rerun()

    st.sidebar.markdown(
        "<div class='frl-sidebar-rule'></div>",
        unsafe_allow_html=True,
    )
    st.sidebar.caption("Answers should be inspectable, not merely asserted.")

    return selected


def current_workspace(default="overview"):
    """Return the current workspace key."""
    return st.session_state.get("frl_workspace", default)
