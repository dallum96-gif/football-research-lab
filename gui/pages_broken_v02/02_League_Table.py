import pandas as pd
import streamlit as st

import query_api


@st.cache_data
def seasons():
    return query_api.list_seasons()


st.title("League Table")
st.caption(
    "Historical Premier League standings."
)

season_list = sorted(
    seasons(),
    reverse=True,
)

season = st.selectbox(
    "Season",
    season_list,
)

table = query_api.league_table(
    season=season
)

rows = table["teams"]

st.dataframe(
    pd.DataFrame(
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
            for row in rows
        ]
    ),
    width="stretch",
    hide_index=True,
)
