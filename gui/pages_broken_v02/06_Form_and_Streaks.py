import pandas as pd
import streamlit as st

import query_api


@st.cache_data
def season_list():
    return query_api.list_seasons()


st.title("Form & Streaks")
st.caption(
    "Explore completed league form and current streaks."
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

form = query_api.team_form(
    season=season,
    team=team,
)

st.subheader("Current streaks")

streaks = form["streaks"]

cols = st.columns(5)

cols[0].metric(
    "Wins",
    streaks["current_win_streak"],
)

cols[1].metric(
    "Unbeaten",
    streaks["current_unbeaten_streak"],
)

cols[2].metric(
    "Losses",
    streaks["current_loss_streak"],
)

cols[3].metric(
    "Clean sheets",
    streaks["current_clean_sheet_streak"],
)

cols[4].metric(
    "Scoring",
    streaks["current_scoring_streak"],
)

st.subheader("Recent form")

form_rows = form.get(
    "matches",
    form.get(
        "fixtures",
        [],
    ),
)

st.dataframe(
    pd.DataFrame(
        form_rows
    ),
    width="stretch",
    hide_index=True,
)

with st.expander(
    "Form payload",
    expanded=False,
):
    st.json(form)
