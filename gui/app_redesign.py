from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import query_api

from gui.fixture_explorer import render_fixture_explorer
from gui.ui_shell import current_workspace, render_workspace_sidebar
from gui.theme import apply_theme, render_brand_header


st.set_page_config(
    page_title="Football Research Lab",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="locked",
)

apply_theme()


def season_key(season):
    return int(season.split("-")[0])


@st.cache_data
def get_seasons():
    return query_api.list_seasons()


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


render_workspace_sidebar(current_workspace())
render_brand_header()
workspace = current_workspace()

if workspace == "overview":
    st.markdown("<div class='frl-title'>Research, evidence, analysis.</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='frl-subtitle'>Premier League data, player research, match analysis and experimental modelling.</div>",
        unsafe_allow_html=True,
    )

    cols = st.columns(3)
    cols[0].metric("Premier League seasons", len(get_seasons()))
    cols[1].metric("Fixtures in canonical master", "3,800")
    cols[2].metric("Research assurance", "26 / 26")

    st.divider()
    st.markdown("### Start exploring")
    st.caption(
        "The redesign is being migrated workspace-by-workspace. Fixtures and the League Table are the first live views."
    )

elif workspace == "fixtures":
    seasons = sorted(get_seasons(), key=season_key, reverse=True)

    context_cols = st.columns([1, 1], gap="small")
    with context_cols[0]:
        season = st.selectbox("Season", seasons, key="redesign_fixture_season")

    table = get_league_table(season)
    teams = sorted([row["team"] for row in table["teams"]], key=str.casefold)

    with context_cols[1]:
        team = st.selectbox("Team", teams, key="redesign_fixture_team")

    st.divider()
    render_fixture_explorer(
        season=season,
        team=team,
        get_fixtures=get_fixtures,
    )

elif workspace == "league-table":
    seasons = sorted(get_seasons(), key=season_key, reverse=True)
    season = st.selectbox("Season", seasons, key="redesign_league_table_season")
    table = get_league_table(season)

    st.markdown("<div class='frl-eyebrow'>Explore</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-entity-title'>League Table</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-context'>Premier League · {season}</div>", unsafe_allow_html=True)

    rows = [
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
    ]

    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

else:
    item_labels = {
        "players": "Players",
        "head-to-head": "Head-to-Head",
        "form": "Form & Streaks",
        "prediction": "Prediction Lab",
        "data-quality": "Data Quality",
        "provenance": "Provenance",
    }
    label = item_labels.get(workspace, workspace.replace("-", " ").title())
    st.markdown(f"<div class='frl-eyebrow'>{label}</div>", unsafe_allow_html=True)
    st.info(
        "This workspace is intentionally held outside the preview until its existing behaviour has been migrated without changing the trusted contracts."
    )
