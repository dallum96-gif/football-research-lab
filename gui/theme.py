import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        :root {
            --frl-bg: #0e141a;
            --frl-surface: #151c22;
            --frl-surface-raised: #192129;
            --frl-border: rgba(222, 228, 232, 0.08);
            --frl-border-strong: rgba(222, 228, 232, 0.15);
            --frl-text: #eef1f1;
            --frl-muted: #8f9aa1;
            --frl-accent: #759b8c;
            --frl-accent-soft: rgba(117, 155, 140, 0.11);
        }

        .stApp,
        .main {
            background: var(--frl-bg);
            color: var(--frl-text);
        }

        .block-container {
            max-width: 1500px;
            padding-top: 1.25rem;
            padding-bottom: 3rem;
            padding-left: 1.5rem;
            padding-right: 1.5rem;
        }

        /* Narrow, quiet navigation rail. */
        section[data-testid="stSidebar"] {
            width: 190px !important;
            min-width: 190px !important;
            max-width: 190px !important;
            background: #0a1015;
            border-right: 1px solid var(--frl-border);
        }

        section[data-testid="stSidebar"] > div:first-child {
            padding: 0.9rem 0.45rem 1.1rem 0.45rem;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            padding-left: 0 !important;
            padding-right: 0 !important;
        }

        section[data-testid="stSidebar"] .stButton,
        section[data-testid="stSidebar"] .stButton > div {
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        section[data-testid="stSidebar"] .stButton > button {
            width: 100% !important;
            min-height: 1.52rem;
            height: 1.52rem;
            padding: 0.02rem 0.2rem !important;
            margin: 0 !important;
            border: 0 !important;
            border-radius: 3px;
            background: transparent !important;
            color: #c4cdd1 !important;
            box-shadow: none !important;
            font-size: 0.75rem;
            font-weight: 560;
            justify-content: flex-start !important;
            text-align: left !important;
            align-items: center !important;
        }

        section[data-testid="stSidebar"] .stButton > button > div,
        section[data-testid="stSidebar"] .stButton > button p {
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            justify-content: flex-start !important;
            text-align: left !important;
        }

        section[data-testid="stSidebar"] .stButton > button:hover {
            color: var(--frl-text) !important;
            background: rgba(255,255,255,0.025) !important;
        }

        section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
            color: #dce9e3 !important;
            background: var(--frl-accent-soft) !important;
        }

        section[data-testid="stSidebar"] hr {
            margin: 0.48rem 0;
            border-color: var(--frl-border);
        }

        .frl-sidebar-brand {
            color: var(--frl-text);
            font-size: 0.68rem;
            font-weight: 760;
            letter-spacing: 0.1em;
            line-height: 1.25;
            text-transform: uppercase;
            margin: 0 0 0.7rem 0.1rem;
        }

        .frl-sidebar-section {
            color: #748087;
            font-size: 0.56rem;
            font-weight: 760;
            letter-spacing: 0.13em;
            text-transform: uppercase;
            margin: 0.72rem 0 0.15rem 0.1rem;
        }

        .frl-eyebrow {
            color: var(--frl-muted);
            font-size: 0.66rem;
            font-weight: 700;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }

        .frl-title {
            color: var(--frl-text);
            font-size: 1.95rem;
            font-weight: 780;
            line-height: 1.06;
            letter-spacing: -0.02em;
            margin: 0;
        }

        .frl-subtitle {
            color: var(--frl-muted);
            margin-top: 0.3rem;
            margin-bottom: 1.05rem;
            font-size: 0.9rem;
            line-height: 1.42;
            max-width: 730px;
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
            font-size: 0.86rem;
            margin-top: 0.22rem;
            margin-bottom: 0.9rem;
        }

        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stDateInput"] input {
            background: var(--frl-surface);
            color: var(--frl-text);
            border: 1px solid var(--frl-border);
            border-radius: 6px;
            min-height: 1.95rem;
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
            padding: 0.58rem 0.7rem;
            background: transparent;
            border-top: 1px solid var(--frl-border);
            border-bottom: 1px solid var(--frl-border);
            border-left: 0;
            border-right: 0;
            border-radius: 0;
        }

        div[data-testid="stMetricLabel"] { color: var(--frl-muted); }
        div[data-testid="stMetricValue"] { color: var(--frl-text); }
        div[data-testid="stDataFrame"] { border: 1px solid var(--frl-border); border-radius: 7px; overflow: hidden; background: var(--frl-surface); }
        div[data-testid="stExpander"] { border: 1px solid var(--frl-border); border-radius: 7px; background: var(--frl-surface); }
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
