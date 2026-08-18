import pandas as pd
import streamlit as st

import query_api


@st.cache_data
def season_list():
    return query_api.list_seasons()


st.title("Fixture Explorer")
st.caption(
    "Search historical fixtures by season, team and result."
)

seasons = sorted(
    season_list(),
    reverse=True,
)

season = st.selectbox(
    "Season",
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

opponent = st.selectbox(
    "Opponent",
    ["Any opponent"] + teams,
)

venue = st.selectbox(
    "Venue",
    ["Any venue", "Home", "Away"],
)

result = st.selectbox(
    "Result",
    [
        "Any result",
        "Win",
        "Draw",
        "Loss",
    ],
)

data = query_api.fixtures(
    season=season,
    team=team,
    opponent=(
        None
        if opponent == "Any opponent"
        else opponent
    ),
    venue=(
        None
        if venue == "Any venue"
        else venue
    ),
    result=(
        None
        if result == "Any result"
        else result
    ),
    limit=100,
)

fixture_rows = (
    data["fixtures"]
    if isinstance(data, dict)
    and "fixtures" in data
    else data
)

st.caption(
    f"{len(fixture_rows)} fixture(s)"
)

st.dataframe(
    pd.DataFrame(
        fixture_rows
    ),
    width="stretch",
    hide_index=True,
)
