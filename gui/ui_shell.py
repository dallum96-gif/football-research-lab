"""Quiet, text-led navigation shell for the Football Research Laboratory."""

import streamlit as st

from gui.navigation import SECTION_ORDER, navigation_by_section


ICONS = {
    "overview": "▦",
    "fixtures": "▣",
    "league-table": "☷",
    "players": "◯",
    "head-to-head": "⇄",
    "form": "⌁",
    "prediction": "∿",
    "data-quality": "✓",
    "provenance": "◇",
}


def render_workspace_sidebar(active_key):
    """Render compact, flush-left application navigation."""
    grouped = navigation_by_section()
    selected = active_key

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
            icon = ICONS.get(item.key, "·")
            label = f"{icon}  {item.label}"

            if st.sidebar.button(
                label,
                key=f"nav_{item.key}",
                use_container_width=True,
                type="secondary",
            ):
                selected = item.key
                st.session_state["frl_workspace"] = item.key
                st.rerun()

    return selected


def current_workspace(default="overview"):
    """Return the current workspace key."""
    return st.session_state.get("frl_workspace", default)
