"""Fixture Explorer presentation layer.

The trusted fixture query contract remains in query_api/query_lab. This module
owns only presentation and navigation behaviour for the explorer.
"""

import streamlit as st


def render_fixture_explorer(season, team, get_fixtures):
    st.markdown("## Fixture Explorer")
    st.caption("Browse the selected team's canonical fixture record and open any match for detailed evidence.")

    filter_cols = st.columns([1.8, 1.0, 1.0, 0.9])

    all_team_fixtures = get_fixtures(season=season, team=team)
    opponent_names = sorted(
        {
            row["away_team_name"] if row["home_team_name"] == team else row["home_team_name"]
            for row in all_team_fixtures["results"]
        },
        key=str.casefold,
    )

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

    with filter_cols[3]:
        st.markdown("&nbsp;", unsafe_allow_html=True)
        clear_filters = st.button("Clear", key="fixture_explorer_clear")

    if clear_filters:
        for key in (
            "fixture_explorer_opponent",
            "fixture_explorer_venue",
            "fixture_explorer_result",
        ):
            st.session_state.pop(key, None)
        st.rerun()

    selected_opponent = None if opponent_choice == "All opponents" else opponent_choice
    selected_venue = {"All venues": None, "Home": "home", "Away": "away"}[venue_choice]
    selected_result = {"All results": None, "W": "W", "D": "D", "L": "L", "Unplayed": "UNPLAYED"}[result_choice]

    fixtures = get_fixtures(
        season=season,
        team=team,
        opponent=selected_opponent,
        venue=selected_venue,
        result=selected_result,
    )
    results = fixtures["results"]

    st.markdown(
        f"**{len(results)}** fixtures · {team} · {season}",
    )

    if not results:
        st.info("No fixtures match the selected filters.")
        return

    st.markdown("<div class='frl-fixture-table-head'>Date&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;GW&nbsp;&nbsp;&nbsp;&nbsp;Venue&nbsp;&nbsp;&nbsp;&nbsp;Opponent&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Score&nbsp;&nbsp;&nbsp;&nbsp;Result</div>", unsafe_allow_html=True)

    for row in results:
        home = row["home_team_name"]
        away = row["away_team_name"]
        home_score = row["home_score"]
        away_score = row["away_score"]

        if home_score == "" or away_score == "":
            score = "—"
            result = "UNPLAYED"
        elif home == team:
            score = f"{home_score}-{away_score}"
            h, a = int(home_score), int(away_score)
            result = "W" if h > a else "D" if h == a else "L"
        else:
            score = f"{home_score}-{away_score}"
            h, a = int(home_score), int(away_score)
            result = "W" if a > h else "D" if a == h else "L"

        cols = st.columns([1.15, 0.5, 0.65, 2.2, 0.75, 0.7])
        cols[0].caption(row["kickoff_time"][:10])
        cols[1].caption(row["gameweek"])
        cols[2].caption("Home" if home == team else "Away")

        if cols[3].button(
            away if home == team else home,
            key=f"fixture_opponent_{row['fixture_id']}",
            use_container_width=True,
        ):
            st.query_params["fixture"] = f"{season}:{row['fixture_id']}"
            st.rerun()

        cols[4].caption(score)
        cols[5].caption(result)
