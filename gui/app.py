from pathlib import Path
import sys

import streamlit as st
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import query_api


st.set_page_config(
    page_title="Football Research Lab",
    page_icon="⚽",
    layout="wide",
)


@st.cache_data
def get_seasons():
    return query_api.list_seasons()


def season_key(season):
    return int(season.split("-")[0])


st.title("Football Research Lab")
st.caption("Premier League historical data and analysis")

seasons = sorted(
    get_seasons(),
    key=season_key,
    reverse=True,
)

if not seasons:
    st.error("No seasons available.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    season = st.selectbox(
        "Season",
        seasons,
    )

table = query_api.league_table(
    season=season
)

teams = [
    row["team"]
    for row in table["teams"]
]

with col2:
    team = st.selectbox(
        "Team",
        teams,
    )

summary = query_api.team_summary(
    season=season,
    team=team,
)

s = summary["summary"]

st.divider()

metric_cols = st.columns(5)

metric_cols[0].metric("Points", s["points"])
metric_cols[1].metric(
    "Record",
    f"{s['wins']}W {s['draws']}D {s['losses']}L",
)
metric_cols[2].metric(
    "Goals",
    f"{s['goals_for']}-{s['goals_against']}",
)
metric_cols[3].metric(
    "Goal Difference",
    f"{s['goal_difference']:+d}",
)
metric_cols[4].metric(
    "Played",
    f"{s['played']}/{s['matches_in_schedule']}",
)

if summary["data_quality"]["status"] != "COMPLETE":
    st.warning(
        "This season contains incomplete fixture data."
    )

tab1, tab2, tab3 = st.tabs(
    [
        "League Table",
        "Fixtures",
        "Season Comparison",
    ]
)

with tab1:
    df = pd.DataFrame(
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
        ]
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

with tab2:
    fixtures = query_api.fixtures(
        season=season,
        team=team,
        limit=100,
    )

    fixture_df = pd.DataFrame(
        [
            {
                "Date": row["kickoff_time"][:10],
                "Gameweek": row["gameweek"],
                "Home": row["home_team_name"],
                "Score": (
                    f"{row['home_score']}-"
                    f"{row['away_score']}"
                ),
                "Away": row["away_team_name"],
            }
            for row in fixtures["results"]
        ]
    )

    st.dataframe(
        fixture_df,
        use_container_width=True,
        hide_index=True,
    )

with tab3:
    comparison = query_api.team_compare(
        team=team,
        seasons=seasons,
    )

    comparison_df = pd.DataFrame(
        [
            {
                "Season": row["season"],
                "Wins": row["wins"],
                "Draws": row["draws"],
                "Losses": row["losses"],
                "GF": row["goals_for"],
                "GA": row["goals_against"],
                "GD": row["goal_difference"],
                "Points": row["points"],
            }
            for row in comparison["seasons"]
        ]
    ).sort_values("Season")

    st.line_chart(
        comparison_df.set_index("Season")[["Points"]]
    )

    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True,
    )

with st.expander("Data provenance"):
    st.write(
        {
            "Query version": summary["query_version"],
            "Fixture source": summary["source_file"],
            "Identity source": summary["identity_source_file"],
        }
    )
