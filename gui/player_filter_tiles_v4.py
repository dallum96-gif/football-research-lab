"""FRL Players tile presentation v4.

Adds the art-directed Advanced tile treatment without changing the
underlying player research or verified Player-Match data contracts.
"""
from __future__ import annotations

import streamlit as st

from gui.player_filter_tiles_v3 import render_player_research_ui_tiles as _render_v3


def _advanced_tile_style() -> None:
    st.markdown(
        """
        <style>
        /* Advanced is an editorial tile action, not a form toggle. */
        [data-testid="stToggle"] input {
            position:absolute !important;
            opacity:0 !important;
            width:1px !important;
            height:1px !important;
        }

        [data-testid="stToggle"] label {
            position:relative !important;
            display:flex !important;
            align-items:flex-start !important;
            gap:.34rem !important;
            width:100% !important;
            min-height:2.05rem !important;
            padding:.08rem 0 !important;
            cursor:pointer !important;
            color:var(--frl-text) !important;
            font-family:"Source Sans",sans-serif !important;
            font-size:.72rem !important;
            font-weight:790 !important;
            letter-spacing:.01em !important;
        }

        [data-testid="stToggle"] label::before {
            content:"＋";
            flex:0 0 auto;
            color:var(--frl-accent);
            font-family:"Source Sans",sans-serif;
            font-size:1rem;
            font-weight:820;
            line-height:.9;
            margin-top:.02rem;
        }

        [data-testid="stToggle"] label::after {
            content:"Explore stats, thresholds & combinations";
            position:absolute;
            left:1.18rem;
            top:1rem;
            color:var(--frl-muted);
            font-family:"Source Sans",sans-serif;
            font-size:.57rem;
            font-weight:560;
            line-height:1.15;
            white-space:nowrap;
        }

        [data-testid="stToggle"] label > div {
            display:none !important;
        }

        [data-testid="stToggle"] label:hover {
            color:var(--frl-accent) !important;
        }

        [data-testid="stToggle"]:has(input:checked) label {
            color:var(--frl-text) !important;
        }

        [data-testid="stToggle"]:has(input:checked) label::before {
            content:"✓";
            color:var(--frl-accent);
        }

        /* Keep all selector/query surfaces light. */
        [data-baseweb="menu"],
        [data-baseweb="popover"],
        [role="listbox"],
        [data-testid="stSelectboxVirtualDropdown"] {
            background:var(--frl-surface) !important;
            color:var(--frl-text) !important;
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
    _render_v3()
