"""Fixture Explorer presentation layer.

The trusted fixture query contract remains in query_api/query_lab.  This module
owns only the Streamlit presentation and navigation behaviour for the fixture
explorer so the UI can evolve without changing fixture semantics.
"""

import pandas as pd
import streamlit as st


def render_fixture_explorer(
    season,
    team,
    get_fixtures,
):
    """Render the fixture explorer for a selected season and team."""
    st.markdown("## Fixture Explorer")
    st.caption(
        "Explore the canonical fixture record and open any match for its detailed evidence."
    )

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
            key="fixture_explorer_opponent",
        )

    with filter_cols[1]:
        venue_choice = st.selectbox(
            "Venue",
            ["All venues", "Home", "Away"],
            key="fixture_explorer_venue",
        )

    with filter_cols[2]:
        result_choice = st.selectbox(
            "Result",
            ["All results", "W", "D", "L", "Unplayed"],
            key="fixture_explorer_result",
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

    if not results:
        st.info("No fixtures match the selected filters.")
        return

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

        fixture_rows.append(
            {
                "_fixture_id": row["fixture_id"],
                "Date": row["kickoff_time"][:10],
                "GW": row["gameweek"],
                "Venue": "Home" if home == team else "Away",
                "Opponent": away if home == team else home,
                "Score": score,
                "Result": result,
            }
        )

    header_cols = st.columns(
        [1.25, 0.65, 0.8, 2.0, 0.9, 0.8]
    )

    for col, header in zip(
        header_cols,
        ("Date", "GW", "Venue", "Opponent", "Score", "Result"),
    ):
        col.markdown(f"**{header}**")

    st.divider()

    for row in fixture_rows:
        cols = st.columns(
            [1.25, 0.65, 0.8, 2.0, 0.9, 0.8]
        )

        cols[0].write(row["Date"])
        cols[1].write(row["GW"])
        cols[2].write(row["Venue"])

        if cols[3].button(
            row["Opponent"],
            key=f"fixture_opponent_{row['_fixture_id']}",
            use_container_width=True,
        ):
            st.query_params["fixture"] = (
                f"{season}:{row['_fixture_id']}"
            )
            st.rerun()

        cols[4].write(row["Score"])
        cols[5].write(row["Result"])
