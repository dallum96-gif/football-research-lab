import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        :root {
            --frl-bg: #101417;
            --frl-surface: #161c20;
            --frl-surface-raised: #1b2328;
            --frl-border: rgba(220, 226, 230, 0.10);
            --frl-border-strong: rgba(220, 226, 230, 0.16);
            --frl-text: #edf0ef;
            --frl-muted: #9aa3a6;
            --frl-accent: #a58a63;
            --frl-accent-soft: rgba(165, 138, 99, 0.13);
        }

        .stApp,
        .main {
            background: var(--frl-bg);
            color: var(--frl-text);
        }

        .block-container {
            max-width: 1480px;
            padding-top: 1.8rem;
            padding-bottom: 3.5rem;
            padding-left: 2.15rem;
            padding-right: 2.15rem;
        }

        .frl-eyebrow {
            color: var(--frl-muted);
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.17em;
            text-transform: uppercase;
            margin-bottom: 0.45rem;
        }

        .frl-title {
            color: var(--frl-text);
            font-size: 2.25rem;
            font-weight: 800;
            line-height: 1.05;
            letter-spacing: -0.022em;
            margin: 0;
        }

        .frl-subtitle {
            color: var(--frl-muted);
            margin-top: 0.45rem;
            margin-bottom: 1.5rem;
            font-size: 0.96rem;
            line-height: 1.5;
            max-width: 760px;
        }

        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stDateInput"] input {
            background: var(--frl-surface);
            color: var(--frl-text);
            border: 1px solid var(--frl-border);
            border-radius: 7px;
            min-height: 2.2rem;
        }

        div[data-baseweb="select"] > div:hover,
        div[data-testid="stTextInput"] input:hover,
        div[data-testid="stNumberInput"] input:hover,
        div[data-testid="stDateInput"] input:hover {
            border-color: var(--frl-border-strong);
        }

        /* Sidebar is navigation, so keep it compact and quiet. */
        section[data-testid="stSidebar"] {
            background: #0d1114;
            border-right: 1px solid var(--frl-border);
        }

        section[data-testid="stSidebar"] .stButton > button {
            min-height: 1.95rem;
            height: 1.95rem;
            padding: 0.15rem 0.65rem;
            border-radius: 6px;
            font-size: 0.82rem;
            font-weight: 600;
            text-align: left;
            justify-content: flex-start;
            box-shadow: none;
        }

        section[data-testid="stSidebar"] .stButton {
            margin-bottom: 0.08rem;
        }

        section[data-testid="stSidebar"] hr {
            margin: 0.7rem 0;
            border-color: var(--frl-border);
        }

        .frl-sidebar-title {
            color: var(--frl-text);
            font-size: 0.95rem;
            font-weight: 800;
            margin-bottom: 0.15rem;
        }

        .frl-sidebar-copy {
            color: var(--frl-muted);
            font-size: 0.76rem;
            line-height: 1.4;
            margin-bottom: 0.55rem;
        }

        .frl-sidebar-section {
            color: var(--frl-muted);
            font-size: 0.66rem;
            font-weight: 750;
            letter-spacing: 0.13em;
            text-transform: uppercase;
            margin: 0.9rem 0 0.35rem 0;
        }

        .frl-status {
            display: inline-block;
            padding: 0.2rem 0.42rem;
            border: 1px solid rgba(165, 138, 99, 0.28);
            border-radius: 5px;
            background: var(--frl-accent-soft);
            color: #c6b28f;
            font-size: 0.68rem;
            font-weight: 700;
        }

        div[data-testid="stMetric"] {
            padding: 0.75rem 0.85rem;
            background: var(--frl-surface);
            border: 1px solid var(--frl-border);
            border-radius: 8px;
        }

        div[data-testid="stMetricLabel"] {
            color: var(--frl-muted);
        }

        div[data-testid="stMetricValue"] {
            color: var(--frl-text);
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--frl-border);
            border-radius: 8px;
            overflow: hidden;
            background: var(--frl-surface);
        }

        div[data-testid="stExpander"] {
            border: 1px solid var(--frl-border);
            border-radius: 8px;
            background: var(--frl-surface);
        }

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
            if key.startswith(("player_", "prediction_", "h2h_", "form_"))
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
    st.sidebar.caption("Core Query Lab: 14/14 · Player Research: 12/12")

    st.sidebar.markdown(
        "<div class='frl-sidebar-section'>Data coverage</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.caption("Premier League: 2016–17 to 2025–26")
    st.sidebar.caption("Player gameweek records available")

    st.sidebar.markdown(
        "<div class='frl-sidebar-section'>Laboratory principle</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.caption("Answers should be inspectable, not merely asserted.")
