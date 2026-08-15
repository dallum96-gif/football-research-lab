import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        :root {
            --frl-bg: #0f151b;
            --frl-surface: #151d24;
            --frl-surface-raised: #192229;
            --frl-border: rgba(222, 228, 232, 0.09);
            --frl-border-strong: rgba(222, 228, 232, 0.16);
            --frl-text: #edf1f2;
            --frl-muted: #98a4aa;
            --frl-accent: #739b8c;
            --frl-accent-bright: #9fc2b3;
        }

        .stApp,
        .main {
            background: var(--frl-bg);
            color: var(--frl-text);
        }

        .block-container {
            max-width: 1500px;
            padding-top: 1.35rem;
            padding-bottom: 3.5rem;
            padding-left: 2.1rem;
            padding-right: 2.1rem;
        }

        .frl-eyebrow {
            color: var(--frl-muted);
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.17em;
            text-transform: uppercase;
            margin-bottom: 0.3rem;
        }

        .frl-title {
            color: var(--frl-text);
            font-size: 1.95rem;
            font-weight: 780;
            line-height: 1.08;
            letter-spacing: -0.018em;
            margin: 0;
        }

        .frl-subtitle {
            color: var(--frl-muted);
            margin-top: 0.35rem;
            margin-bottom: 1.2rem;
            font-size: 0.92rem;
            line-height: 1.45;
            max-width: 760px;
        }

        .frl-entity-title {
            color: var(--frl-text);
            font-size: 2rem;
            font-weight: 760;
            letter-spacing: -0.02em;
            line-height: 1.08;
            margin: 0;
        }

        .frl-context {
            color: var(--frl-muted);
            font-size: 0.88rem;
            margin-top: 0.24rem;
            margin-bottom: 1rem;
        }

        .frl-count-line {
            color: var(--frl-muted);
            font-size: 0.82rem;
            margin: 0.7rem 0 0.55rem 0;
        }

        .frl-fixture-header {
            display: grid;
            grid-template-columns: 1fr 3.2fr 1fr 1fr 0.9fr;
            column-gap: 1rem;
            color: var(--frl-muted);
            font-size: 0.66rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 0.35rem 0.35rem 0.45rem 0.35rem;
            border-bottom: 1px solid var(--frl-border);
        }

        .frl-meta {
            color: var(--frl-muted);
            font-size: 0.78rem;
        }

        .frl-score {
            color: var(--frl-text);
            font-weight: 760;
            font-size: 0.92rem;
        }

        .frl-result {
            font-size: 0.75rem;
            font-weight: 700;
        }

        .frl-result-win { color: var(--frl-accent-bright); }
        .frl-result-draw { color: var(--frl-muted); }
        .frl-result-loss { color: #c58f8f; }
        .frl-result-unplayed { color: #b7a47c; }

        /* Quiet, professional navigation rail. */
        section[data-testid="stSidebar"] {
            background: #0c1217;
            border-right: 1px solid var(--frl-border);
        }

        section[data-testid="stSidebar"] .block-container {
            padding: 1.1rem 0.8rem 1.5rem 0.8rem;
        }

        .frl-sidebar-brand {
            color: var(--frl-text);
            font-size: 0.7rem;
            font-weight: 760;
            letter-spacing: 0.14em;
            line-height: 1.35;
            text-transform: uppercase;
            margin: 0 0 1rem 0;
        }

        .frl-sidebar-section {
            color: #718087;
            font-size: 0.6rem;
            font-weight: 750;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            margin: 0.95rem 0 0.18rem 0.2rem;
        }

        section[data-testid="stSidebar"] .stButton {
            margin: 0;
        }

        section[data-testid="stSidebar"] .stButton > button {
            min-height: 1.55rem;
            height: 1.55rem;
            padding: 0.02rem 0.35rem;
            margin: 0;
            border: 0;
            border-radius: 4px;
            background: transparent;
            color: #aab4b9;
            box-shadow: none;
            font-size: 0.78rem;
            font-weight: 600;
            justify-content: flex-start;
            text-align: left;
            white-space: nowrap;
        }

        section[data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(255,255,255,0.025);
            color: var(--frl-text);
        }

        section[data-testid="stSidebar"] .stButton > button:focus:not(:active) {
            border-color: transparent;
            box-shadow: none;
        }

        /* Compact selects used by the research workspaces. */
        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stDateInput"] input {
            background: var(--frl-surface);
            color: var(--frl-text);
            border: 1px solid var(--frl-border);
            border-radius: 6px;
            min-height: 2rem;
        }

        div[data-baseweb="select"] > div:hover,
        div[data-testid="stTextInput"] input:hover,
        div[data-testid="stNumberInput"] input:hover,
        div[data-testid="stDateInput"] input:hover {
            border-color: var(--frl-border-strong);
        }

        .stButton > button {
            color: var(--frl-text);
            border-color: var(--frl-border);
            background: transparent;
            border-radius: 6px;
        }

        .stButton > button:hover {
            border-color: var(--frl-border-strong);
            background: rgba(255,255,255,0.018);
        }

        div[data-testid="stMetric"] {
            padding: 0.65rem 0.78rem;
            background: transparent;
            border-top: 1px solid var(--frl-border);
            border-bottom: 1px solid var(--frl-border);
            border-left: 0;
            border-right: 0;
            border-radius: 0;
        }

        div[data-testid="stMetricLabel"] { color: var(--frl-muted); }
        div[data-testid="stMetricValue"] { color: var(--frl-text); }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--frl-border);
            border-radius: 7px;
            overflow: hidden;
            background: var(--frl-surface);
        }

        div[data-testid="stExpander"] {
            border: 1px solid var(--frl-border);
            border-radius: 7px;
            background: var(--frl-surface);
        }

        div[data-testid="stDecoration"] { background-image: none; }
        div[data-testid="stToolbar"] { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand_header():
    st.markdown(
        """
        <div class="frl-eyebrow">Football Research Laboratory</div>
        <div class="frl-title">Research, evidence, analysis.</div>
        <div class="frl-subtitle">Premier League data, player research, match analysis and experimental modelling.</div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_controls():
    return None
