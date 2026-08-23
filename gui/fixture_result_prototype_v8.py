from __future__ import annotations

import gui.fixture_result_prototype_v6  # noqa: F401,E402
import streamlit as st

# V8 is the single visual consolidation layer over the working prototype.
# The existing Fixtures page remains untouched.

st.markdown(
    """
    <style>
    /* Compact analytical layout: small editorial modules, never full-width dashboard panels. */
    .analysis-wrap { max-width: 860px !important; margin-left: auto !important; margin-right: auto !important; }
    .viz-grid { grid-template-columns: repeat(2, 300px) !important; justify-content: center !important; max-width: 620px !important; margin: 0 auto !important; gap: 12px !important; }
    .viz-card { width: 300px !important; max-width: 300px !important; box-sizing: border-box !important; }
    .stat-grid { grid-template-columns: repeat(4, 140px) !important; justify-content: center !important; max-width: 590px !important; margin: 12px auto !important; gap: 10px !important; }
    .stat-card { min-height: 78px !important; padding: .72rem .78rem !important; }

    /* Goals are the story: more visual weight than cards/subs without becoming gaudy. */
    .goal-event { margin: 7px 0 !important; padding: 11px 12px !important; border: 1px solid rgba(232,93,63,.30) !important; border-left: 4px solid var(--frl-accent) !important; border-radius: 12px !important; background: rgba(232,93,63,.07) !important; box-shadow: 0 5px 18px rgba(24,23,20,.045) !important; }
    .goal-event .event-icon { width: 30px !important; height: 30px !important; background: rgba(154,170,66,.18) !important; border-color: rgba(154,170,66,.36) !important; font-size: .78rem !important; }
    .goal-event .event-main { font-size: .84rem !important; font-weight: 900 !important; }
    .goal-score { font-size: .74rem !important; font-weight: 950 !important; color: var(--frl-accent) !important; }

    /* Correct football-facing left/right orientation. Player token 1 starts at div 5. */
    .pitch .player-token:nth-of-type(6) { left: 88% !important; }
    .pitch .player-token:nth-of-type(7) { left: 62% !important; }
    .pitch .player-token:nth-of-type(8) { left: 38% !important; }
    .pitch .player-token:nth-of-type(9) { left: 12% !important; }
    .pitch .player-token:nth-of-type(12) { left: 84% !important; }
    .pitch .player-token:nth-of-type(14) { left: 16% !important; }

    /* Lineup tabs: readable inactive and active labels on the warm light theme. */
    [data-baseweb="tab-list"] { justify-content: center !important; }
    [data-baseweb="tab"], [data-baseweb="tab"] *, [data-baseweb="tab"] p, [data-baseweb="tab"] span, [data-baseweb="tab"] div,
    [data-baseweb="tab"][aria-selected="true"], [data-baseweb="tab"][aria-selected="true"] * { color: var(--frl-text) !important; opacity: 1 !important; }

    /* Keep the analytical space visually compact. */
    .analysis-wrap .section-kicker { margin-bottom: .35rem !important; }

    @media (max-width: 900px) {
        .viz-grid { grid-template-columns: minmax(260px, 300px) !important; max-width: 320px !important; }
        .viz-card { width: 300px !important; max-width: 300px !important; }
        .stat-grid { grid-template-columns: repeat(2, 140px) !important; max-width: 290px !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)
