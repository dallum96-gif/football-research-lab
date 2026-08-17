"""FRL Players tile presentation v4.

Art-directed Advanced tile action layered over the verified v3 renderer.
The underlying player research and Player-Match contracts are unchanged.
"""
from __future__ import annotations

import streamlit as st

from gui.player_filter_tiles_v3 import render_player_research_ui_tiles as _render_v3


def _advanced_tile_style() -> None:
    st.markdown(
        """
        <style>
        /* Advanced is an editorial tile action, not a form control. */
        [data-testid="stToggle"] {
            display:none !important;
        }

        .frl-advanced-action {
            margin:.04rem 0 0;
        }

        .frl-advanced-action button {
            width:100% !important;
            min-height:2.15rem !important;
            height:2.15rem !important;
            padding:.08rem 0 !important;
            border:0 !important;
            border-radius:0 !important;
            background:transparent !important;
            color:var(--frl-text) !important;
            box-shadow:none !important;
            font-family:"Source Sans",sans-serif !important;
            font-size:.74rem !important;
            font-weight:790 !important;
            letter-spacing:.01em !important;
            text-align:left !important;
        }

        .frl-advanced-action button:hover,
        .frl-advanced-action button:focus-visible {
            color:var(--frl-accent) !important;
            background:rgba(232,93,63,.035) !important;
            box-shadow:none !important;
        }

        .frl-advanced-action button::first-letter {
            color:var(--frl-accent) !important;
        }

        .frl-advanced-note {
            color:var(--frl-muted) !important;
            font-family:"Source Sans",sans-serif !important;
            font-size:.57rem !important;
            line-height:1.2 !important;
            margin:.02rem 0 0 !important;
        }

        /* Keep every query surface light and on-brand. */
        [data-baseweb="menu"],
        [data-baseweb="popover"],
        [role="listbox"],
        [data-testid="stSelectboxVirtualDropdown"] {
            background:var(--frl-surface) !important;
            color:var(--frl-text) !important;
            border-color:var(--frl-border) !important;
        }

        [data-baseweb="menu"] li,
        [role="option"] {
            background:transparent !important;
            color:var(--frl-text) !important;
            font-family:"Source Sans",sans-serif !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_player_research_ui_tiles() -> None:
    _advanced_tile_style()

    original_toggle = st.toggle

    def _editorial_toggle(label, value=False, key=None, **kwargs):
        state_key = key or "frl_advanced"
        current = bool(st.session_state.get(state_key, value))

        with st.container(key="frl_advanced_action"):
            action_label = "✓ Advanced active" if current else "＋ Build a shortlist"
            clicked = st.button(
                action_label,
                key=f"{state_key}_editorial_button",
                use_container_width=True,
            )
            st.markdown(
                "<div class='frl-advanced-note'>"
                "Stats, thresholds & combinations"
                "</div>",
                unsafe_allow_html=True,
            )

        if clicked:
            st.session_state[state_key] = not current
            st.rerun()

        return current

    st.toggle = _editorial_toggle
    try:
        _render_v3()
    finally:
        st.toggle = original_toggle
