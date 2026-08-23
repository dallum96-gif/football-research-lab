from __future__ import annotations

import streamlit as st

# V8 is a single visual consolidation layer over the working prototype.
# It deliberately leaves the existing Fixtures page untouched.

st.markdown(
    """
    <style>
    /* ================================================================
       1. COMPACT ANALYTICAL LAYOUT
       ================================================================ */
    .analysis-wrap {
        max-width: 860px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    .viz-grid {
        grid-template-columns: repeat(2, 300px) !important;
        justify-content: center !important;
        max-width: 620px !important;
        margin: 0 auto !important;
        gap: 12px !important;
    }
    .viz-card {
        width: 300px !important;
        max-width: 300px !important;
        box-sizing: border-box !important;
    }
    .stat-grid {
        grid-template-columns: repeat(4, 140px) !important;
        justify-content: center !important;
        max-width: 590px !important;
        margin: 12px auto !important;
        gap: 10px !important;
    }
    .stat-card {
        min-height: 78px !important;
        padding: .72rem .78rem !important;
    }

    /* ================================================================
       2. GOALS BECOME THE MATCH STORY
       ================================================================ */
    .goal-event {
        margin: 7px 0 !important;
        padding: 11px 12px !important;
        border: 1px solid rgba(232,93,63,.30) !important;
        border-left: 4px solid var(--frl-accent) !important;
        border-radius: 12px !important;
        background: rgba(232,93,63,.07) !important;
        box-shadow: 0 5px 18px rgba(24,23,20,.045) !important;
    }
    .goal-event .event-icon {
        width: 30px !important;
        height: 30px !important;
        background: rgba(154,170,66,.18) !important;
        border-color: rgba(154,170,66,.36) !important;
        font-size: .78rem !important;
    }
    .goal-event .event-main {
        font-size: .84rem !important;
        font-weight: 900 !important;
    }
    .goal-score {
        font-size: .74rem !important;
        font-weight: 950 !important;
        color: var(--frl-accent) !important;
    }

    /* ================================================================
       3. LINEUP: CORRECT FOOTBALL LEFT/RIGHT ORIENTATION
       First four divs in the pitch are pitch markings; player tokens then
       begin at div #5. This mirrors the lateral player positions only.
       ================================================================ */
    .pitch .player-token:nth-of-type(6)  { left: 88% !important; }
    .pitch .player-token:nth-of-type(7)  { left: 62% !important; }
    .pitch .player-token:nth-of-type(8)  { left: 38% !important; }
    .pitch .player-token:nth-of-type(9)  { left: 12% !important; }
    .pitch .player-token:nth-of-type(12) { left: 85% !important; }
    .pitch .player-token:nth-of-type(13) { left: 50% !important; }
    .pitch .player-token:nth-of-type(14) { left: 15% !important; }

    /* Liverpool attacking trio has the same viewer-side convention. */
    .pitch .player-token:nth-of-type(12) { left: 84% !important; }
    .pitch .player-token:nth-of-type(14) { left: 16% !important; }

    /* ================================================================
       4. LINEUP TAB CONTRAST
       ================================================================ */
    [data-baseweb="tab-list"] {
        justify-content: center !important;
    }
    [data-baseweb="tab"] {
        color: var(--frl-text) !important;
        opacity: 1 !important;
    }
    [data-baseweb="tab"] *,
    [data-baseweb="tab"] p,
    [data-baseweb="tab"] span,
    [data-baseweb="tab"] div {
        color: var(--frl-text) !important;
        opacity: 1 !important;
    }
    [data-baseweb="tab"][aria-selected="true"],
    [data-baseweb="tab"][aria-selected="true"] * {
        color: var(--frl-text) !important;
    }

    /* ================================================================
       5. SLEEK CATEGORY-STYLE NAVIGATION SUPPORT
       Keeps the visual language ready for the next analytical layer.
       ================================================================ */
    .analysis-wrap .section-kicker {
        margin-bottom: .35rem !important;
    }

    @media (max-width: 900px) {
        .viz-grid {
            grid-template-columns: minmax(260px, 300px) !important;
            max-width: 320px !important;
        }
        .viz-card {
            width: 300px !important;
            max-width: 300px !important;
        }
        .stat-grid {
            grid-template-columns: repeat(2, 140px) !important;
            max-width: 290px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Import after the override so the existing prototype renders with this layer.
import gui.fixture_result_prototype_v6  # noqa: F401,E402
