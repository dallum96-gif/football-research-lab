from datetime import datetime
from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import query_api
from gui.fixture_explorer import render_fixture_explorer
from gui.theme import apply_theme, render_brand_header
from gui.ui_shell import current_workspace, render_workspace_sidebar


st.set_page_config(
    page_title="Football Research Laboratory",
    page_icon="⚽",
    layout="wide",
)

apply_theme()


def season_key(season):
    try:
        return int(str(season).split("-")[0])
    except (TypeError, ValueError):
        return 0


@st.cache_data
def get_seasons():
    return sorted(
        query_api.list_seasons(),
        key=season_key,
        reverse=True,
    )


@st.cache_data
def get_league_table(season):
    return query_api.league_table(season=season)


@st.cache_data
def get_fixtures(
    season,
    team,
    opponent=None,
    venue=None,
    result=None,
):
    return query_api.fixtures(
        season=season,
        team=team,
        opponent=opponent,
        venue=venue,
        result=result,
        limit=100,
    )


def render_overview():
    st.markdown("### Football research, not just football dashboards")
    st.write(
        "Explore the historical Premier League evidence base, inspect individual "
        "fixtures, and progressively move from observation into research and modelling."
    )

    st.markdown("#### Start with a question")

    cols = st.columns(3)

    with cols[0]:
        st.markdown("**Fixtures**")
        st.caption("Explore canonical fixtures and inspect match-level evidence.")
        if st.button("Open Fixtures", use_container_width=True, key="overview_fixtures"):
            st.session_state["frl_workspace"] = "fixtures"
            st.rerun()

    with cols[1]:
        st.markdown("**Teams**")
        st.caption("Compare league performance across the seasons in the research base.")
        if st.button("Open Teams", use_container_width=True, key="overview_teams"):
            st.session_state["frl_workspace"] = "teams"
            st.rerun()

    with cols[2]:
        st.markdown("**Players**")
        st.caption("Search the available historical player research data.")
        if st.button("Open Players", use_container_width=True, key="overview_players"):
            st.session_state["frl_workspace"] = "players"
            st.rerun()

    st.divider()

    st.markdown("#### Laboratory principles")

    principle_cols = st.columns(3)
    principle_cols[0].metric("Historical seasons", len(get_seasons()))
    principle_cols[1].metric("Canonical fixture records", "3,800")
    principle_cols[2].metric("Research gate", "26/26")

    st.caption(
        "The interface is being redesigned around the same trusted research contracts; "
        "the UI is allowed to change, but the evidence underneath it is not."
    )


def render_teams():
    seasons = get_seasons()
    season = st.selectbox(
        "Season",
        seasons,
        key="redesign_team_season",
    )

    table = get_league_table(season)

    st.markdown("### Teams")
    st.caption("League performance from the canonical fixture layer.")

    st.dataframe(
        [
            {
                "Pos": row["position"],
                "Team": row["team"],
                "P": row["played"],
                "W": row["wins"],
                "D": row["draws"],
                "L": row["losses"],
                "GF": row["goals_for"],
                "GA": row["goals_against"],
                "GD": row["goal_difference"],
                "Pts": row["points"],
            }
            for row in table["teams"]
        ],
        width="stretch",
        hide_index=True,
    )


def render_players_placeholder():
    st.markdown("### Players")
    st.caption("Player Research is the next workspace being migrated into the new interface.")
    st.info(
        "The existing player-research contract remains intact. This redesign is intentionally "
        "being migrated workspace-by-workspace rather than rewritten in one large change."
    )


def render_placeholder(title, description):
    st.markdown(f"### {title}")
    st.caption(description)
    st.info("This workspace is queued for migration into the new research interface.")


render_brand_header()

workspace = render_workspace_sidebar(current_workspace())

if workspace == "overview":
    render_overview()
elif workspace == "fixtures":
    seasons = get_seasons()
    season = st.selectbox(
        "Season",
        seasons,
        key="redesign_fixture_season",
    )
    table = get_league_table(season)
    teams = sorted(
        [row["team"] for row in table["teams"]],
        key=str.casefold,
    )
    team = st.selectbox(
        "Team",
        teams,
        key="redesign_fixture_team",
    )
    render_fixture_explorer(
        season=season,
        team=team,
        get_fixtures=get_fixtures,
    )
elif workspace == "teams":
    render_teams()
elif workspace == "players":
    render_players_placeholder()
elif workspace == "head-to-head":
    render_placeholder(
        "Head-to-Head",
        "Compare clubs across shared Premier League history.",
    )
elif workspace == "form":
    render_placeholder(
        "Form & Streaks",
        "Inspect recent form, match ranges and current streaks.",
    )
elif workspace == "prediction":
    render_placeholder(
        "Prediction Lab",
        "Explore the current experimental prediction models.",
    )
elif workspace == "data-quality":
    render_placeholder(
        "Data Quality",
        "Inspect completeness and research controls.",
    )
elif workspace == "provenance":
    render_placeholder(
        "Provenance",
        "Inspect source and lineage information behind research outputs.",
    )
else:
    st.error(f"Unknown workspace: {workspace}")
