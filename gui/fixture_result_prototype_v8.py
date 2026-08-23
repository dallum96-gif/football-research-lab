from __future__ import annotations

from pathlib import Path
import runpy

import streamlit as st

# V8 intentionally executes the working V6 prototype by file path rather than
# importing it as a Python package. This keeps direct `streamlit run` execution
# reliable from the repository root and leaves the existing Fixtures page untouched.
BASE = Path(__file__).with_name("fixture_result_prototype_v6.py")
runpy.run_path(str(BASE), run_name="__main__")

# Final visual consolidation layer: compact analytical modules and readable tabs.
st.markdown(
    """
    <style>
    /* Keep the analytical area centred and deliberately compact. */
    .analysis-wrap { max-width: 860px !important; margin: 0 auto !important; }
    .viz-grid { grid-template-columns: repeat(2, 300px) !important; justify-content: center !important; max-width: 620px !important; margin: 12px auto !important; gap: 12px !important; }
    .viz-card { width: 300px !important; max-width: 300px !important; box-sizing: border-box !important; }
    .stat-grid { grid-template-columns: repeat(4, 140px) !important; justify-content: center !important; max-width: 590px !important; margin: 12px auto !important; gap: 10px !important; }
    .stat-card { min-height: 78px !important; padding: .72rem .78rem !important; }

    /* Goals should read as moments, not ordinary timeline rows. */
    .goal-event { margin: 7px 0 !important; padding: 11px 12px !important; border: 1px solid rgba(232,93,63,.30) !important; border-left: 4px solid var(--frl-accent) !important; border-radius: 12px !important; background: rgba(232,93,63,.07) !important; box-shadow: 0 5px 18px rgba(24,23,20,.045) !important; }
    .goal-event .event-icon { width: 30px !important; height: 30px !important; background: rgba(154,170,66,.18) !important; border-color: rgba(154,170,66,.36) !important; font-size: .78rem !important; }
    .goal-event .event-main { font-size: .84rem !important; font-weight: 900 !important; }
    .goal-score { font-size: .74rem !important; font-weight: 950 !important; color: var(--frl-accent) !important; }

    /* Correct football-facing left/right orientation of full-back and wide-player tokens. */
    .pitch .player-token:nth-of-type(6) { left: 88% !important; }
    .pitch .player-token:nth-of-type(7) { left: 62% !important; }
    .pitch .player-token:nth-of-type(8) { left: 38% !important; }
    .pitch .player-token:nth-of-type(9) { left: 12% !important; }
    .pitch .player-token:nth-of-type(12) { left: 84% !important; }
    .pitch .player-token:nth-of-type(14) { left: 16% !important; }

    /* Streamlit tab labels stay dark/readable on the light FRL theme. */
    [data-baseweb="tab-list"] { justify-content: center !important; }
    [data-baseweb="tab"],
    [data-baseweb="tab"] *,
    [data-baseweb="tab"] p,
    [data-baseweb="tab"] span,
    [data-baseweb="tab"] div,
    [data-baseweb="tab"][aria-selected="true"],
    [data-baseweb="tab"][aria-selected="true"] * {
        color: var(--frl-text) !important;
        opacity: 1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
