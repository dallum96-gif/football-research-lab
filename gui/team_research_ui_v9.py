from __future__ import annotations

import streamlit as st

import gui.team_research_ui_v8 as base


def _css() -> None:
    base._css()
    st.markdown(
        """
        <style>
        .frl-team9-browse-note{
            color:var(--frl-muted-soft);
            font-size:.56rem;
            font-weight:820;
            letter-spacing:.11em;
            text-transform:uppercase;
            margin:.05rem 0 .18rem;
        }
        div[data-testid="stSelectbox"]{
            margin-top:0;
            margin-bottom:.38rem;
        }
        div[data-testid="stSelectbox"] label{
            display:none;
        }
        div[data-testid="stSelectbox"] [data-baseweb="select"] > div{
            min-height:2.05rem;
            border:1px solid var(--frl-border);
            border-radius:8px;
            background:transparent;
            box-shadow:none;
        }
        div[data-testid="stSelectbox"] [data-baseweb="select"] [role="button"]{
            color:var(--frl-text);
            font-size:.70rem;
            font-weight:720;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='frl-team9-browse-note'>Browse team research</div>",
        unsafe_allow_html=True,
    )


def render_team_research_ui():
    base._css = _css
    return base.render_team_research_ui()
