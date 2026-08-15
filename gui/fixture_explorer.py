"""Editorial Fixture Explorer presentation layer."""

import streamlit as st


def _result_for_team(team, home, away, home_score, away_score):
    if home_score in (None, "") or away_score in (None, ""):
        return "UNPLAYED"

    home_score = int(home_score)
    away_score = int(away_score)

    if home == team:
        return "W" if home_score > away_score else "D" if home_score == away_score else "L"

    return "W" if away_score > home_score else "D" if away_score == home_score else "L"


def _result_class(result):
    return {
        "W": "frl-result-win",
        "D": "frl-result-draw",
        "L": "frl-result-loss",
        "UNPLAYED": "frl-result-unplayed",
    }.get(result, "frl-result-draw")


def render_fixture_explorer(season, team, get_fixtures):
    st.markdown(
        "<div class='frl-eyebrow'>Fixtures</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='frl-entity-title'>{team}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='frl-context'>Premier League · {season}</div>",
        unsafe_allow_html=True,
    )

    all_team_fixtures = get_fixtures(season=season, team=team)
    opponent_names = sorted(
        {
            row["away_team_name"] if row["home_team_name"] == team else row["home_team_name"]
            for row in all_team_fixtures["results"]
        },
        key=str.casefold,
    )

    filter_cols = st.columns([2.0, 1.0, 1.0], gap="small")

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

    selected_opponent = None if opponent_choice == "All opponents" else opponent_choice
    selected_venue = {"All venues": None, "Home": "home", "Away": "away"}[venue_choice]
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

    st.markdown(
        f"<div class='frl-count-line'>{len(results)} matches</div>",
        unsafe_allow_html=True,
    )

    if not results:
        st.info("No fixtures match the selected filters.")
        return

    st.markdown(
        """
        <div class="frl-fixture-header">
            <div>Date</div>
            <div>Opponent</div>
            <div>Venue</div>
            <div>Score</div>
            <div>Result</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for row in results:
        home = row["home_team_name"]
        away = row["away_team_name"]
        opponent = away if home == team else home
        venue = "Home" if home == team else "Away"
        result = _result_for_team(
            team,
            home,
            away,
            row["home_score"],
            row["away_score"],
        )

        if row["home_score"] in (None, "") or row["away_score"] in (None, ""):
            score = "—"
        else:
            score = f"{row['home_score']}-{row['away_score']}"

        date = str(row["kickoff_time"])[:10]
        result_class = _result_class(result)

        cols = st.columns([1.0, 3.2, 1.0, 1.0, 0.9], gap="small")
        cols[0].markdown(
            f"<div class='frl-meta'>{date}<br>GW {row['gameweek']}</div>",
            unsafe_allow_html=True,
        )

        if cols[1].button(
            opponent,
            key=f"fixture_opponent_{row['fixture_id']}",
            use_container_width=True,
        ):
            st.query_params["fixture"] = f"{season}:{row['fixture_id']}"
            st.rerun()

        cols[2].markdown(
            f"<div class='frl-meta'>{venue}</div>",
            unsafe_allow_html=True,
        )
        cols[3].markdown(
            f"<div class='frl-score'>{score}</div>",
            unsafe_allow_html=True,
        )
        cols[4].markdown(
            f"<div class='frl-result {result_class}'>{result}</div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div class='frl-fixture-row-rule'></div>", unsafe_allow_html=True)
