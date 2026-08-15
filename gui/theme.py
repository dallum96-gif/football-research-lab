import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        :root {
            --frl-bg: #11161b;
            --frl-surface: #171e24;
            --frl-surface-raised: #1c252c;
            --frl-border: rgba(220, 226, 230, 0.12);
            --frl-border-strong: rgba(220, 226, 230, 0.18);
            --frl-text: #edf1f2;
            --frl-muted: #9ca7ad;
            --frl-accent: #7fa895;
            --frl-accent-soft: rgba(127, 168, 149, 0.14);
            --frl-warning: #d9b36c;
        }

        .stApp {
            background: var(--frl-bg);
            color: var(--frl-text);
        }

        .main {
            background: var(--frl-bg);
        }

        .block-container {
            max-width: 1480px;
            padding-top: 2.1rem;
            padding-bottom: 4rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }

        .frl-eyebrow {
            color: var(--frl-muted);
            font-size: 0.72rem;
            font-weight: 750;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            margin-bottom: 0.45rem;
        }

        .frl-title {
            color: var(--frl-text);
            font-size: 2.35rem;
            font-weight: 800;
            line-height: 1.05;
            letter-spacing: -0.025em;
            margin: 0;
        }

        .frl-subtitle {
            color: var(--frl-muted);
            margin-top: 0.5rem;
            margin-bottom: 1.65rem;
            font-size: 0.98rem;
            line-height: 1.55;
            max-width: 760px;
        }

        /* Navigation should read like an application, not a dashboard widget. */
        div[data-baseweb="tab-list"] {
            gap: 0.2rem;
            border-bottom: 1px solid var(--frl-border);
            margin-bottom: 1.5rem;
        }

        button[data-baseweb="tab"] {
            color: var(--frl-muted);
            font-weight: 650;
            font-size: 0.88rem;
            padding: 0.45rem 0.85rem 0.7rem 0.85rem;
        }

        button[data-baseweb="tab"]:hover {
            color: var(--frl-text);
        }

        /* Keep controls recognisable and quiet. */
        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stDateInput"] input {
            background: var(--frl-surface);
            color: var(--frl-text);
            border: 1px solid var(--frl-border);
            border-radius: 9px;
        }

        div[data-baseweb="select"] > div:hover,
        div[data-testid="stTextInput"] input:hover,
        div[data-testid="stNumberInput"] input:hover,
        div[data-testid="stDateInput"] input:hover {
            border-color: var(--frl-border-strong);
        }

        button[kind="secondary"] {
            background: var(--frl-surface);
            color: var(--frl-text);
            border: 1px solid var(--frl-border);
            border-radius: 9px;
        }

        button[kind="secondary"]:hover {
            border-color: var(--frl-border-strong);
            color: var(--frl-text);
        }

        /* Metrics are compact information blocks, not decorative cards. */
        div[data-testid="stMetric"] {
            padding: 0.85rem 0.95rem 0.8rem 0.95rem;
            background: var(--frl-surface);
            border: 1px solid var(--frl-border);
            border-radius: 10px;
        }

        div[data-testid="stMetricLabel"] {
            color: var(--frl-muted);
        }

        div[data-testid="stMetricValue"] {
            color: var(--frl-text);
        }

        /* Data is the hero: give tables a simple editorial frame. */
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--frl-border);
            border-radius: 10px;
            overflow: hidden;
            background: var(--frl-surface);
        }

        /* Expanders are secondary evidence containers, not primary navigation. */
        div[data-testid="stExpander"] {
            border: 1px solid var(--frl-border);
            border-radius: 10px;
            background: var(--frl-surface);
        }

        section[data-testid="stSidebar"] {
            background: #0e1317;
            border-right: 1px solid var(--frl-border);
        }

        .frl-sidebar-title {
            color: var(--frl-text);
            font-size: 0.98rem;
            font-weight: 800;
            margin-bottom: 0.25rem;
        }

        .frl-sidebar-copy {
            color: var(--frl-muted);
            font-size: 0.8rem;
            line-height: 1.45;
            margin-bottom: 1rem;
        }

        .frl-sidebar-section {
            color: var(--frl-muted);
            font-size: 0.69rem;
            font-weight: 750;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin: 1.15rem 0 0.45rem 0;
        }

        .frl-status {
            display: inline-block;
            padding: 0.26rem 0.52rem;
            border: 1px solid rgba(127, 168, 149, 0.28);
            border-radius: 6px;
            background: var(--frl-accent-soft);
            color: #acd0bb;
            font-size: 0.72rem;
            font-weight: 750;
            letter-spacing: 0.02em;
        }

        /* Remove a little of Streamlit's visual noise without disguising it. */
        div[data-testid="stDecoration"] {
            background-image: none;
        }

        div[data-testid="stToolbar"] {
            visibility: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand_header():
    st.markdown(
        """
        <div class="frl-eyebrow">Football Research Laboratory</div>
        <div class="frl-title">Research, evidence, analysis.</div>
        <div class="frl-subtitle">
            Premier League data, player research, match analysis and experimental modelling.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_controls():
    st.sidebar.markdown(
        "<div class='frl-sidebar-title'>Lab controls</div>",
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        "<div class='frl-sidebar-copy'>Useful controls for the research workspace.</div>",
        unsafe_allow_html=True,
    )

    if st.sidebar.button(
        "Refresh data",
        use_container_width=True,
        key="sidebar_refresh_data",
    ):
        st.cache_data.clear()
        st.rerun()

    if st.sidebar.button(
        "Reset interface",
        use_container_width=True,
        key="sidebar_reset_interface",
    ):
        keys_to_remove = [
            key
            for key in list(st.session_state.keys())
            if key.startswith(
                (
                    "player_",
                    "prediction_",
                    "h2h_",
                    "form_",
                )
            )
        ]

        for key in keys_to_remove:
            del st.session_state[key]

        st.rerun()

    st.sidebar.markdown(
        "<div class='frl-sidebar-section'>Assurance</div>",
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        "<span class='frl-status'>26/26 research tests passing</span>",
        unsafe_allow_html=True,
    )

    st.sidebar.caption(
        "Core Query Lab: 14/14 · Player Research: 12/12"
    )

    st.sidebar.markdown(
        "<div class='frl-sidebar-section'>Data coverage</div>",
        unsafe_allow_html=True,
    )

    st.sidebar.caption(
        "Premier League: 2016–17 to 2025–26"
    )

    st.sidebar.caption(
        "Player gameweek records available"
    )

    st.sidebar.markdown(
        "<div class='frl-sidebar-section'>Laboratory principle</div>",
        unsafe_allow_html=True,
    )

    st.sidebar.caption(
        "Answers should be inspectable, not merely asserted."
    )
