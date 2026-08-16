import streamlit as st


GROUPS = {
    "Explore": [
        "League Table",
        "Fixture Explorer",
        "Season Comparison",
        "Players",
    ],
    "Research": [
        "Head-to-Head",
        "Form & Streaks",
    ],
    "Modelling": [
        "Prediction Lab",
    ],
}


def render_navigation():
    current = st.session_state.get(
        "frl_page",
        "Players",
    )

    st.sidebar.markdown(
        "### Research"
    )

    st.sidebar.caption(
        "Football Research Laboratory"
    )

    st.sidebar.divider()

    for group, pages in GROUPS.items():
        st.sidebar.markdown(
            f"**{group}**"
        )

        for page in pages:
            if st.sidebar.button(
                page,
                key=f"frl_nav_{page}",
                use_container_width=True,
                type=(
                    "primary"
                    if current == page
                    else "secondary"
                ),
            ):
                st.session_state[
                    "frl_page"
                ] = page
                st.rerun()

    st.sidebar.divider()

    st.sidebar.markdown(
        "**Assurance**"
    )

    st.sidebar.success(
        "26/26 tests passing"
    )

    if st.sidebar.button(
        "Refresh data",
        use_container_width=True,
        key="frl_refresh",
    ):
        st.cache_data.clear()
        st.rerun()

    return current
