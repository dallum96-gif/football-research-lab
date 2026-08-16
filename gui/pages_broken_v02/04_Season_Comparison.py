import pandas as pd
import streamlit as st

import query_api


@st.cache_data
def season_list():
    return query_api.list_seasons()


st.title("Season Comparison")
st.caption(
    "Compare a team's historical season performance."
)

seasons = sorted(
    season_list(),
    reverse=True,
)

season = st.selectbox(
    "Reference season",
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

team = st.selectbox(
    "Team",
    teams,
)

comparison = query_api.team_compare(
    team=team,
)

st.json(comparison)
