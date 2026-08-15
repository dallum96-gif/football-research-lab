import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        :root {
            --frl-bg: #0e141a;
            --frl-surface: #151c22;
            --frl-surface-raised: #192128;
            --frl-border: rgba(222, 228, 232, 0.08);
            --frl-border-strong: rgba(222, 228, 232, 0.15);
            --frl-text: #eef1f1;
            --frl-muted: #8f9aa1;
            --frl-muted-soft: #737f86;
            --frl-accent: #759b8c;
            --frl-accent-bright: #9fc2b3;
            --frl-negative: #c58f8f;
            --frl-warning: #b7a47c;

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

        section[data-testid="stSidebar"] {
            width: 190px !important;
            min-width: 190px !important;
            max-width: 190px !important;
            background: #0a1015;
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
            padding: 0 !important;
            margin: 0 !important;
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
            color: #748087;
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
            font-size: 0.62rem;
            font-weight: 750;
            letter-spacing: 0.15em;
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

        .frl-entity-title {
            color: var(--frl-text);
            font-size: 2.05rem;
            font-weight: 760;
            letter-spacing: -0.025em;
            line-height: 1.04;
            margin: 0;
        }

        .frl-context {
            color: var(--frl-muted);
            font-size: 0.84rem;
            margin-top: 0.28rem;
        }

        .frl-record-line {
            color: var(--frl-muted);
            font-size: 0.8rem;
            margin: 0.75rem 0 1rem;
            padding-bottom: 0.72rem;
            border-bottom: 1px solid var(--frl-border);
        }

        .frl-record-line span { color: var(--frl-muted-soft); }

        .frl-filtered-line {
            color: var(--frl-muted);
            font-size: 0.76rem;
            margin: 0.25rem 0 0.7rem;
        }

        .frl-empty-state {
            color: var(--frl-muted);
            padding: 1rem 0;
            border-top: 1px solid var(--frl-border);
            border-bottom: 1px solid var(--frl-border);
            font-size: 0.82rem;
        }

        .frl-month-heading {
            color: var(--frl-text);
            font-size: 0.68rem;
            font-weight: 760;
            letter-spacing: 0.13em;
            text-transform: uppercase;
            margin: 1.35rem 0 0.32rem;
        }

        div[data-testid="stExpander"] {
            border: 0 !important;
            border-top: 1px solid var(--frl-border) !important;
            border-bottom: 1px solid var(--frl-border) !important;
            border-radius: 0 !important;
            background: transparent !important;
            margin: 0.1rem 0 0.7rem !important;
        }

        div[data-testid="stExpander"] summary {
            color: var(--frl-muted) !important;
            font-size: 0.72rem !important;
            font-weight: 650 !important;
        }

        div[data-testid="stExpander"] summary:hover {
            color: var(--frl-text) !important;
        }

        div[data-baseweb="select"] > div {
            background: rgba(21, 28, 34, 0.78) !important;
            color: var(--frl-text) !important;
            border: 1px solid rgba(222, 228, 232, 0.07) !important;
            border-radius: 5px !important;
            min-height: 2.05rem !important;
            box-shadow: none !important;
        }

        div[data-baseweb="select"] > div:hover,
        div[data-baseweb="select"] > div:focus-within {
            background: rgba(25, 33, 40, 0.92) !important;
            border-color: rgba(117, 155, 140, 0.42) !important;
            box-shadow: none !important;
        }

        div[data-baseweb="popover"],
        div[data-baseweb="menu"] {
            background: var(--frl-surface-raised) !important;
        }

        div[data-baseweb="menu"] li:hover {
            background: rgba(117, 155, 140, 0.08) !important;
        }

        .frl-fixture-header {
            display: grid;
            grid-template-columns: 1.1fr 3.25fr 0.95fr 0.9fr 0.72fr;
            column-gap: 1rem;
            color: var(--frl-muted-soft);
            font-size: 0.61rem;
            font-weight: 750;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            padding: 0.35rem 0.18rem 0.48rem;
            border-bottom: 1px solid var(--frl-border-strong);
        }

        .frl-fixture-row-rule {
            height: 1px;
            background: var(--frl-border);
            margin: 0.05rem 0;
        }

        .frl-meta {
            color: var(--frl-muted);
            font-size: 0.75rem;
            line-height: 1.3;
        }

        .frl-meta-sub {
            color: var(--frl-muted-soft);
            font-size: 0.67rem;
        }

        .frl-score {
            color: var(--frl-text);
            font-weight: 760;
            font-size: 0.92rem;
        }

        .frl-result {
            font-size: 0.71rem;
            font-weight: 750;
            letter-spacing: 0.05em;
        }

        .frl-result-win { color: var(--frl-accent-bright); }
        .frl-result-draw { color: var(--frl-muted); }
        .frl-result-loss { color: var(--frl-negative); }
        .frl-result-unplayed { color: var(--frl-warning); }

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

        /* Overview / landing page */
        .frl-home-title {
            color: var(--frl-text);
            max-width: 840px;
            font-size: clamp(2.25rem, 4vw, 3.65rem);
            font-weight: 760;
            line-height: 0.98;
            letter-spacing: -0.045em;
            margin: 0;
        }

        .frl-home-subtitle {
            max-width: 660px;
            color: var(--frl-muted);
            font-size: 0.92rem;
            line-height: 1.55;
            margin-top: 0.9rem;
        }

        .frl-home-stat {
            border-top: 1px solid var(--frl-border);
            padding-top: 0.7rem;
        }

        .frl-home-stat span {
            display: block;
            color: var(--frl-text);
            font-size: 1.45rem;
            font-weight: 720;
            letter-spacing: -0.02em;
            line-height: 1;
        }

        .frl-home-stat small {
            display: block;
            margin-top: 0.28rem;
            color: var(--frl-muted-soft);
            font-size: 0.66rem;
            text-transform: uppercase;
            letter-spacing: 0.11em;
        }

        .frl-home-rule {
            height: 1px;
            background: var(--frl-border);
            margin: 2.1rem 0 1rem;
        }

        .frl-home-section-label {
            color: var(--frl-muted-soft);
            font-size: 0.62rem;
            font-weight: 750;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            margin-bottom: 0.65rem;
        }

        .frl-home-card {
            min-height: 7.5rem;
            padding: 1rem 0.1rem 0.75rem;
            border-top: 1px solid var(--frl-border);
            border-bottom: 1px solid var(--frl-border);
        }

        .frl-home-card-title {
            color: var(--frl-text);
            font-size: 1.02rem;
            font-weight: 700;
        }

        .frl-home-card-copy {
            max-width: 250px;
            margin-top: 0.42rem;
            color: var(--frl-muted);
            font-size: 0.78rem;
            line-height: 1.45;
        }

        .frl-home-section-spaced { margin-top: 2.1rem; }

        .frl-home-principles {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem 1.3rem;
            color: var(--frl-muted);
            font-size: 0.74rem;
        }

        .frl-home-principles span::before {
            content: "";
            display: inline-block;
            width: 4px;
            height: 4px;
            margin: 0 0.45rem 0.15rem 0;
            border-radius: 50%;
            background: var(--frl-accent);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand_header():
    st.markdown("<div class='frl-masthead'>Football Research Laboratory</div>", unsafe_allow_html=True)


def render_sidebar_controls():
    return None
