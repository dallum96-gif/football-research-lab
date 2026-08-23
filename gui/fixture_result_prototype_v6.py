from __future__ import annotations

# V6 is a visual patch over the stable V5 prototype.
# Keep V5 as the rendered source; append CSS overrides only so the experiment
# stays disposable and the underlying fixture experience remains unchanged.
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import gui.fixture_result_prototype_v5  # noqa: F401,E402

st.markdown(
    """
    <style>
    /* Keep analytical modules deliberately small and centred. */
    .analysis-wrap {
        max-width: 860px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    .viz-grid {
        grid-template-columns: 320px 320px !important;
        justify-content: center !important;
        max-width: 680px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    .viz-card {
        width: 320px !important;
        max-width: 320px !important;
    }
    .stat-grid {
        grid-template-columns: repeat(4, 150px) !important;
        justify-content: center !important;
        max-width: 660px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* Streamlit tabs: always use FRL readable text, including the inactive tab. */
    [data-baseweb="tablist"] {
        justify-content: center !important;
    }
    [data-baseweb="tab"] {
        color: var(--frl-text) !important;
    }
    [data-baseweb="tab"] * {
        color: var(--frl-text) !important;
    }
    [data-baseweb="tab"][aria-selected="true"] {
        color: var(--frl-text) !important;
    }
    [data-baseweb="tab"][aria-selected="true"] * {
        color: var(--frl-text) !important;
    }

    @media (max-width: 900px) {
        .viz-grid {
            grid-template-columns: minmax(260px, 1fr) !important;
            max-width: 340px !important;
        }
        .viz-card {
            width: 100% !important;
            max-width: 340px !important;
        }
        .stat-grid {
            grid-template-columns: repeat(2, 150px) !important;
            max-width: 320px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)
