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


@st.cache_data
def get_league_table(season):
    return query_api.league_table(
        season=season
    )


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


def season_key(season):
    return int(season.split("-")[0])


def cycle_selection(state_key, options, direction):
    if not options:
        return

    current = st.session_state.get(
        state_key,
        options[0],
    )

    if current not in options:
        st.session_state[state_key] = options[0]
        return

    index = options.index(current)
    st.session_state[state_key] = options[
        (index + direction) % len(options)
    ]


st.title("Football Research Lab")
st.caption(
    "Premier League historical data and analysis"
)

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

table = get_league_table(season)

teams = sorted(
    [
        row["team"]
        for row in table["teams"]
    ],
    key=str.casefold,
)

with col2:
    team_search = st.text_input(
        "Find team",
        key="team_search",
        placeholder="Type a club name...",
    )

    filtered_teams = [
        name
        for name in teams
        if team_search.casefold()
        in name.casefold()
    ]

    if not filtered_teams:
        st.error(
            "No teams match that search."
        )
        st.stop()

    if (
        st.session_state.get("team_selector")
        not in filtered_teams
    ):
        st.session_state[
            "team_selector"
        ] = filtered_teams[0]

    team_nav = st.columns([1, 8, 1])

    with team_nav[0]:
        st.button(
            "▲",
            key="team_up",
            help="Previous team",
            on_click=cycle_selection,
            args=(
                "team_selector",
                filtered_teams,
                -1,
            ),
        )

    with team_nav[1]:
        team = st.selectbox(
            "Team",
            filtered_teams,
            key="team_selector",
        )

    with team_nav[2]:
        st.button(
            "▼",
            key="team_down",
            help="Next team",
            on_click=cycle_selection,
            args=(
                "team_selector",
                filtered_teams,
                1,
            ),
        )

summary = query_api.team_summary(
    season=season,
    team=team,
)

s = summary["summary"]

st.divider()

metric_cols = st.columns(5)

metric_cols[0].metric(
    "Points",
    s["points"],
)
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

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "League Table",
        "Fixture Explorer",
        "Season Comparison",
        "Head-to-Head",
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
    all_team_fixtures = get_fixtures(
        season=season,
        team=team,
    )

    opponent_names = sorted(
        {
            (
                row["away_team_name"]
                if row["home_team_name"] == team
                else row["home_team_name"]
            )
            for row in all_team_fixtures["results"]
        },
        key=str.casefold,
    )

    filter_cols = st.columns(3)

    with filter_cols[0]:
        opponent_choice = st.selectbox(
            "Opponent",
            ["All opponents"] + opponent_names,
        )

    with filter_cols[1]:
        venue_choice = st.selectbox(
            "Venue",
            ["All venues", "Home", "Away"],
        )

    with filter_cols[2]:
        result_choice = st.selectbox(
            "Result",
            ["All results", "W", "D", "L", "Unplayed"],
        )

    selected_opponent = (
        None
        if opponent_choice == "All opponents"
        else opponent_choice
    )

    selected_venue = {
        "All venues": None,
        "Home": "home",
        "Away": "away",
    }[venue_choice]

    selected_result = {
        "All results": None,
        "W": "W",
        "D": "D",
        "L": "L",
        "Unplayed": "UNPLAYED",
    }[result_choice]

    fixtures = get_fixtures(
        season=season,
        team=team,
        opponent=selected_opponent,
        venue=selected_venue,
        result=selected_result,
    )

    results = fixtures["results"]

    st.caption(
        f"{len(results)} fixture(s) match the selected filters"
    )

    fixture_rows = []

    for row in results:
        home = row["home_team_name"]
        away = row["away_team_name"]
        home_score = row["home_score"]
        away_score = row["away_score"]

        if home_score == "" or away_score == "":
            score = "—"
            result = "UNPLAYED"
        else:
            score = f"{home_score}-{away_score}"

            if home == team:
                home_score_i = int(home_score)
                away_score_i = int(away_score)

                result = (
                    "W"
                    if home_score_i > away_score_i
                    else "D"
                    if home_score_i == away_score_i
                    else "L"
                )
            else:
                away_score_i = int(away_score)
                home_score_i = int(home_score)

                result = (
                    "W"
                    if away_score_i > home_score_i
                    else "D"
                    if away_score_i == home_score_i
                    else "L"
                )

        opponent_name = (
            away
            if home == team
            else home
        )

        fixture_rows.append(
            {
                "Date": row["kickoff_time"][:10],
                "GW": row["gameweek"],
                "Venue": "Home" if home == team else "Away",
                "Opponent": opponent_name,
                "Score": score,
                "Result": result,
            }
        )

    fixture_df = pd.DataFrame(
        fixture_rows
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

    played_rows = {
        row["season"]: row
        for row in comparison["seasons"]
    }

    skipped_rows = {
        row["season"]: row
        for row in comparison.get(
            "skipped_seasons",
            []
        )
    }

    comparison_rows = []

    for requested_season in comparison[
        "requested_seasons"
    ]:
        if requested_season in played_rows:
            row = played_rows[
                requested_season
            ]

            historical_table = get_league_table(
                requested_season
            )

            position = next(
                (
                    table_row["position"]
                    for table_row in historical_table["teams"]
                    if table_row["team_id"] == row["team_id"]
                ),
                None,
            )

            comparison_rows.append(
                {
                    "Season": requested_season,
                    "Wins": row["wins"],
                    "Draws": row["draws"],
                    "Losses": row["losses"],
                    "GF": row["goals_for"],
                    "GA": row["goals_against"],
                    "GD": row["goal_difference"],
                    "Points": row["points"],
                    "Position": position,
                    "Status": "Premier League",
                }
            )

        elif requested_season in skipped_rows:
            comparison_rows.append(
                {
                    "Season": requested_season,
                    "Wins": None,
                    "Draws": None,
                    "Losses": None,
                    "GF": None,
                    "GA": None,
                    "GD": None,
                    "Points": 0,
                    "Position": 21,
                    "Status": "Not in Premier League",
                }
            )

    comparison_df = pd.DataFrame(
        comparison_rows
    )

    chart_df = comparison_df.set_index(
        "Season"
    )

    st.subheader("Points")
    st.line_chart(
        chart_df[["Points"]]
    )

    chart_cols = st.columns(2)

    with chart_cols[0]:
        st.subheader("Goal difference")
        st.line_chart(
            chart_df[["GD"]]
        )

    with chart_cols[1]:
        st.subheader("League position")
        st.caption(
            "1 = champions; 20 = bottom; 21 = not in the Premier League"
        )
        st.line_chart(
            chart_df[["Position"]]
        )

    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True,
    )

with tab4:
    st.subheader("Head-to-Head Explorer")

    h2h_cols = st.columns(2)

    with h2h_cols[0]:
        h2h_opponent_names = [
            name
            for name in teams
            if name != team
        ]

        h2h_opponent_search = st.text_input(
            "Find opponent",
            key="h2h_opponent_search",
            placeholder="Type a club name...",
        )

        filtered_h2h_opponents = [
            name
            for name in h2h_opponent_names
            if h2h_opponent_search.casefold()
            in name.casefold()
        ]

        if not filtered_h2h_opponents:
            st.error(
                "No opponents match that search."
            )
            st.stop()

        if (
            st.session_state.get("h2h_opponent")
            not in filtered_h2h_opponents
        ):
            st.session_state["h2h_opponent"] = (
                filtered_h2h_opponents[0]
            )

        h2h_nav = st.columns([1, 8, 1])

        with h2h_nav[0]:
            st.button(
                "▲",
                key="h2h_up",
                help="Previous opponent",
                on_click=cycle_selection,
                args=(
                    "h2h_opponent",
                    filtered_h2h_opponents,
                    -1,
                ),
            )

        with h2h_nav[1]:
            h2h_opponent = st.selectbox(
                "Opponent",
                filtered_h2h_opponents,
                key="h2h_opponent",
            )

        with h2h_nav[2]:
            st.button(
                "▼",
                key="h2h_down",
                help="Next opponent",
                on_click=cycle_selection,
                args=(
                    "h2h_opponent",
                    filtered_h2h_opponents,
                    1,
                ),
            )

    with h2h_cols[1]:
        h2h_seasons = st.multiselect(
            "Seasons",
            seasons,
            default=seasons,
            key="h2h_seasons",
        )

    if not h2h_seasons:
        st.info("Select at least one season.")
    else:
        h2h = query_api.head_to_head(
            team=team,
            opponent=h2h_opponent,
            seasons=h2h_seasons,
        )

        hs = h2h["summary"]
        h2h_metrics = st.columns(4)

        h2h_metrics[0].metric(
            f"{team} wins",
            hs["wins"],
        )
        h2h_metrics[1].metric(
            "Draws",
            hs["draws"],
        )
        h2h_metrics[2].metric(
            f"{h2h_opponent} wins",
            hs["losses"],
        )
        h2h_metrics[3].metric(
            "Matches",
            hs["matches"],
        )

        st.caption(
            f"Goals: {hs['goals_for']}-"
            f"{hs['goals_against']} "
            f"(GD {hs['goal_difference']:+d})"
        )

        if h2h.get("skipped_seasons"):
            skipped = ", ".join(
                row["season"]
                for row in h2h["skipped_seasons"]
            )
            st.info(
                "No Premier League meetings in: "
                + skipped
            )

        h2h_df = pd.DataFrame(
            [
                {
                    "Date": row["kickoff_time"][:10],
                    "Season": row["season"],
                    "GW": row["gameweek"],
                    "Fixture": (
                        f"{row['home_team_name']} "
                        f"{row['home_score']}-"
                        f"{row['away_score']} "
                        f"{row['away_team_name']}"
                    ),
                    "Result": row["team_result"],
                }
                for row in h2h["matches"]
            ]
        )

        st.dataframe(
            h2h_df,
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
