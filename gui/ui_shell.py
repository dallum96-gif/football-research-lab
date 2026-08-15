"""Reusable presentation shell for the Football Research Laboratory.

This module deliberately knows about navigation metadata only. Individual
workspaces remain responsible for their own trusted query/API contracts.
"""

import streamlit as st

from gui.navigation import SECTION_ORDER, navigation_by_section


def render_workspace_sidebar(active_key):
    """Render the Lab navigation and return the requested workspace key."""
    grouped = navigation_by_section()

    st.sidebar.markdown("### Football Research Lab")
    st.sidebar.caption("Research, evidence, analysis.")
    st.sidebar.divider()

    selected = active_key

    for section in SECTION_ORDER:
        items = grouped[section]
        if not items:
            continue

        st.sidebar.markdown(f"**{section}**")

        for item in items:
            if st.sidebar.button(
                item.label,
                key=f"nav_{item.key}",
                use_container_width=True,
                type=(
                    "primary"
                    if item.key == active_key
                    else "secondary"
                ),
            ):
                selected = item.key
                st.session_state["frl_workspace"] = item.key
                st.rerun()

    st.sidebar.divider()
    st.sidebar.caption(
        "Answers should be inspectable, not merely asserted."
    )

    return selected


def current_workspace(default="overview"):
    """Return the current workspace without coupling callers to widget state."""
    return st.session_state.get(
        "frl_workspace",
        default,
    )
