"""Quiet, text-led navigation shell for the Football Research Laboratory."""

import streamlit as st

import query_api
from gui.navigation import HIDDEN_WORKSPACES, SECTION_ORDER, navigation_by_section


ICONS = {
    "overview": ":material/home:",
    "fixtures": ":material/calendar_month:",
    "league-table": ":material/table_rows:",
    "teams": ":material/shield:",
    "players": ":material/person:",
    "analysis": ":material/insights:",
    "head-to-head": ":material/swap_horiz:",
    "prediction": ":material/query_stats:",
    "form": ":material/trending_up:",
    "data-quality": ":material/verified:",
    "provenance": ":material/link:",
}

PRIMARY_WORKSPACES = {
    "overview",
    "fixtures",
    "league-table",
    "teams",
    "players",
    "analysis",
}

# Hidden/deep-link workspaces remain valid so existing internal links and future
# contextual relationships are not destroyed when the sidebar becomes smaller.
VALID_WORKSPACES = PRIMARY_WORKSPACES | set(HIDDEN_WORKSPACES)


def current_workspace(default="overview"):
    """Return the current workspace, preferring the URL when present."""
    query_workspace = st.query_params.get("workspace")
    if query_workspace in VALID_WORKSPACES:
        return query_workspace
    return st.session_state.get("frl_workspace", default)


def _render_teams_hub():
    seasons = sorted(
        query_api.available_seasons(),
        key=lambda value: (int(value[:4]), int(value[5:])),
        reverse=True,
    )
    season = seasons[0] if seasons else None

    st.markdown("<div class='frl-eyebrow'>Research</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-entity-title'>Teams</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='frl-context'>Club profiles, team statistics and connected fixture research.</div>",
        unsafe_allow_html=True,
    )

    if not season:
        st.info("Team research is not available yet.")
        return

    season = st.selectbox("Season", seasons, index=0, key="frl_team_hub_season")
    rows = query_api.league_table(season).get("teams", [])

    st.markdown("<div class='frl-collage-section'>Choose a club</div>", unsafe_allow_html=True)
    cols = st.columns(3, gap="small")
    for index, row in enumerate(rows):
        team = row.get("team", "Unknown team")
        with cols[index % 3]:
            st.markdown(
                f"<div class='frl-home-card'><div class='frl-home-card-title'>{team}</div>"
                f"<div class='frl-home-card-copy'>{row.get('points', 0)} pts · {row.get('played', 0)} played · "
                f"{row.get('wins', 0)}W {row.get('draws', 0)}D {row.get('losses', 0)}L</div></div>",
                unsafe_allow_html=True,
            )
            if st.button("Open fixtures", key=f"team_hub_{season}_{team}", type="tertiary", width="stretch"):
                st.session_state["redesign_fixture_season_header"] = season
                st.session_state["redesign_fixture_team_header"] = team
                st.session_state["frl_workspace"] = "fixtures"
                st.query_params["workspace"] = "fixtures"
                st.rerun()

    st.caption("Team Profile and Team Stats will sit behind these canonical team identities as those views are built.")


def _render_analysis_hub():
    st.markdown("<div class='frl-eyebrow'>Analysis</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-entity-title'>Analysis</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='frl-context'>One analytical workspace for Matchday, modelling and future research tools.</div>",
        unsafe_allow_html=True,
    )

    tools = [
        (
            "Matchday Centre",
            "Fixture context, Stat Pack and the route into prediction.",
            "prediction",
        ),
        (
            "Head-to-Head",
            "Compare two clubs through their shared Premier League history.",
            "head-to-head",
        ),
    ]

    cols = st.columns(2, gap="small")
    for col, (title, description, target) in zip(cols, tools):
        with col:
            st.markdown(
                f"<div class='frl-home-card'><div class='frl-home-card-title'>{title}</div>"
                f"<div class='frl-home-card-copy'>{description}</div></div>",
                unsafe_allow_html=True,
            )
            if st.button("Open", key=f"analysis_open_{target}", type="tertiary", width="stretch"):
                st.session_state["frl_workspace"] = target
                st.query_params["workspace"] = target
                st.rerun()

    st.markdown(
        "<div class='frl-collage-section'>Coming into the same analytical layer</div>",
        unsafe_allow_html=True,
    )
    st.caption("Query, comparable matches, combined metrics, records and future mathematical/statistical models are designed to consume the same canonical graph and shared analytical services.")


def render_workspace_sidebar(active_key):
    """Render compact, text-led primary navigation and contextual workspaces."""
    grouped = navigation_by_section()
    selected = current_workspace(active_key)

    st.sidebar.markdown(
        "<div class='frl-sidebar-brand'>FOOTBALL RESEARCH LABORATORY</div>",
        unsafe_allow_html=True,
    )

    for section in SECTION_ORDER:
        items = grouped[section]
        if not items:
            continue

        for item in items:
            if st.sidebar.button(
                item.label,
                key=f"nav_{item.key}",
                icon=ICONS.get(item.key),
                use_container_width=True,
                type="secondary",
            ):
                st.session_state["frl_workspace"] = item.key
                st.query_params["workspace"] = item.key
                st.rerun()

    if selected == "teams":
        _render_teams_hub()
        st.stop()

    if selected == "analysis":
        _render_analysis_hub()
        st.stop()

    if selected == "head-to-head":
        from gui.head_to_head_ui import render_head_to_head
        render_head_to_head()
        st.stop()

    if selected == "players":
        from gui.player_filter_tiles_v4 import render_player_research_ui_tiles as render_player_research_ui
        st.markdown("<div class='frl-eyebrow'>Research</div>", unsafe_allow_html=True)
        st.markdown("<div class='frl-entity-title'>Players</div>", unsafe_allow_html=True)
        st.markdown("<div class='frl-context'>Player performance research across Premier League seasons</div>", unsafe_allow_html=True)
        render_player_research_ui()
        st.stop()

    if selected == "prediction":
        from gui.projection_lab_v2 import render_projection_lab
        render_projection_lab()
        st.stop()

    return selected
