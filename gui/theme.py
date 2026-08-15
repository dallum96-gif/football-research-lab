import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        :root {
            --frl-bg: #111a24;
            --frl-surface: #182331;
            --frl-surface-raised: #1c2938;
            --frl-border: rgba(242, 237, 225, 0.10);
            --frl-border-strong: rgba(242, 237, 225, 0.17);
            --frl-text: #f1eee6;
            --frl-muted: #9aa4ad;
            --frl-muted-soft: #737f89;
            --frl-accent: #789c8c;
            --frl-accent-bright: #a8c8ba;
            --frl-negative: #c28f8f;
            --frl-warning: #c0aa79;

            /* Shared layout rhythm */
            --frl-top-inset: 1.35rem;
            --frl-side-inset: 0.9rem;
            --frl-content-inset: 1.55rem;
            --frl-section-gap: 1.25rem;
        }

        .stApp,
        .main {
            background: var(--frl-bg);
            color: var(--frl-text);
        }

        .block-container {
            max-width: 1500px;
            padding-top: var(--frl-top-inset);
            padding-bottom: 3rem;
            padding-left: var(--frl-content-inset);
            padding-right: var(--frl-content-inset);
        }

        header[data-testid="stHeader"] {
            height: 0 !important;
            min-height: 0 !important;
            background: transparent !important;
        }

        /* Fixed navigation rail: its top rhythm intentionally matches the main canvas. */
        section[data-testid="stSidebar"] {
            width: 190px !important;
            min-width: 190px !important;
            max-width: 190px !important;
            background: #0c141d;
            border-right: 1px solid var(--frl-border);
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        section[data-testid="stSidebar"] > div:first-child {
            padding-top: var(--frl-top-inset) !important;
            padding-right: var(--frl-side-inset);
            padding-bottom: 1.1rem;
            padding-left: var(--frl-side-inset);
            margin-top: 0 !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
            padding-top: 0 !important;
            margin-top: 0 !important;
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
            color: #cbd3d7 !important;
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
            background: rgba(241, 238, 230, 0.035) !important;
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
            margin: 0 0 0.8rem var(--frl-side-inset);
        }

        .frl-sidebar-section {
            color: #7a858f;
            font-size: 0.56rem;
            font-weight: 760;
            letter-spacing: 0.13em;
            text-transform: uppercase;
            margin: 0.82rem 0 0.15rem var(--frl-side-inset);
        }

        .frl-masthead {
            color: var(--frl-text);
            font-size: 0.72rem;
            font-weight: 760;
            letter-spacing: 0.12em;
            line-height: 1;
            text-transform: uppercase;
            margin: 0 0 var(--frl-section-gap) 0;
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

        .frl-record-line {
            color: var(--frl-muted);
            font-size: 0.8rem;
            margin: 0.25rem 0 1rem 0;
            padding-bottom: 0.7rem;
            border-bottom: 1px solid var(--frl-border);
        }

        .frl-record-line strong {
            color: var(--frl-text);
            font-weight: 700;
        }

        .frl-fixture-header {
            display: grid;
            grid-template-columns: 1.05fr 3.1fr 1fr 0.95fr 0.85fr;
            column-gap: 1rem;
            color: var(--frl-muted);
            font-size: 0.64rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 0.32rem 0.18rem 0.42rem 0.18rem;
            border-bottom: 1px solid var(--frl-border-strong);
        }

        .frl-fixture-row-rule {
            height: 1px;
            background: var(--frl-border);
            margin: 0.08rem 0;
        }

        .frl-meta {
            color: var(--frl-muted);
            font-size: 0.76rem;
            line-height: 1.35;
        }

        .frl-meta-sub {
            color: var(--frl-muted-soft);
            font-size: 0.69rem;
        }

        .frl-score {
            color: var(--frl-text);
            font-weight: 760;
            font-size: 0.93rem;
        }

        .frl-result {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.04em;
        }

        .frl-result-win { color: var(--frl-accent-bright); }
        .frl-result-draw { color: var(--frl-muted); }
        .frl-result-loss { color: var(--frl-negative); }
        .frl-result-unplayed { color: var(--frl-warning); }

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
            background: rgba(241, 238, 230, 0.02);
        }

        .frl-fixture-header + div .stButton > button {
            min-height: 1.95rem;
            height: 1.95rem;
            padding: 0 !important;
            border: 0 !important;
            justify-content: flex-start !important;
            text-align: left !important;
            font-size: 0.91rem;
            font-weight: 680;
            color: var(--frl-text);
            background: transparent !important;
        }

        .frl-fixture-header + div .stButton > button:hover {
            color: var(--frl-accent-bright);
            background: transparent !important;
        }

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
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand_header():
    st.markdown(
        """
        <div class="frl-masthead">Football Research Laboratory</div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_controls():
    return None
