import pandas as pd
import streamlit as st

import query_api


@st.cache_data
def season_list():
    return query_api.list_seasons()


st.title("Head-to-Head")
st.caption(
    "Explore the historical record between two teams."
)

seasons = sorted(
    season_list(),
    reverse=True,
)

season = st.selectbox(
    "Starting season",
    seasons,
)

table = query_api.league_table(
    season=season
)

teams = sorted(
    [
        row["team"]
        for row in table["teams"]
    ],
    key=str.casefold,
)

col1, col2 = st.columns(2)

with col1:
    team = st.selectbox(
        "Team",
        teams,
        key="h2h_team",
    )

with col2:
    opponent = st.selectbox(
        "Opponent",
        teams,
        key="h2h_opponent",
    )

if team == opponent:
    st.info(
        "Choose two different teams."
    )
else:
    data = query_api.head_to_head(
        team=team,
        opponent=opponent,
    )

    st.json(data)
