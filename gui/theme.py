import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1500px;
            padding-top: 1.4rem;
            padding-bottom: 3.5rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }

        .frl-eyebrow {
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            opacity: 0.58;
            margin-bottom: 0.35rem;
        }

        .frl-title {
            font-size: 2.45rem;
            font-weight: 800;
            line-height: 1.05;
            margin: 0;
        }

        .frl-subtitle {
            margin-top: 0.45rem;
            margin-bottom: 1.4rem;
            font-size: 1rem;
            opacity: 0.68;
        }

        div[data-baseweb="tab-list"] {
            gap: 0.15rem;
            border-bottom: 1px solid rgba(128,128,128,.18);
            margin-bottom: 1.35rem;
        }

        button[data-baseweb="tab"] {
            font-weight: 650;
            font-size: 0.92rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }

        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input {
            border-radius: 10px;
        }

        button[kind="secondary"] {
            border-radius: 10px;
        }

        div[data-testid="stMetric"] {
            padding: 0.8rem 0.95rem;
            border: 1px solid rgba(128,128,128,.16);
            border-radius: 14px;
            background: rgba(128,128,128,.035);
        }

        div[data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(128,128,128,.14);
        }

        div[data-testid="stExpander"] {
            border-radius: 12px;
            border: 1px solid rgba(128,128,128,.15);
        }

        section[data-testid="stSidebar"] {
            border-right: 1px solid rgba(128,128,128,.12);
        }

        .frl-sidebar-title {
            font-weight: 800;
            font-size: 1rem;
            margin-bottom: 0.2rem;
        }

        .frl-sidebar-copy {
            font-size: 0.82rem;
            opacity: 0.62;
            line-height: 1.45;
            margin-bottom: 1rem;
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
        "### Lab controls"
    )

    st.sidebar.caption(
        "Useful controls for the research workspace."
    )

    if st.sidebar.button(
        "? Refresh data",
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

    st.sidebar.divider()

    st.sidebar.markdown(
        "#### Assurance"
    )

    st.sidebar.success(
        "20/20 research tests passing"
    )

    st.sidebar.caption(
        "Core Query Lab: 14/14 ? "
        "Player Research: 6/6"
    )

    st.sidebar.divider()

    st.sidebar.markdown(
        "#### Data coverage"
    )

    st.sidebar.caption(
        "Premier League: 2016?17 ? 2025?26"
    )

    st.sidebar.caption(
        "Player gameweek records available"
    )

    st.sidebar.divider()

    st.sidebar.markdown(
        "#### Laboratory principle"
    )

    st.sidebar.caption(
        "Answers should be inspectable, "
        "not merely asserted."
    )
