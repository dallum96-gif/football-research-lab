"""Browse-first fixture presentation layer.

The trusted fixture query contract remains in query_api. This module owns
presentation, filtering controls and navigation behaviour only.
"""

from datetime import datetime

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


def _display_date(value):
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.strftime("%d %b %Y")
    except (TypeError, ValueError):
        return str(value)[:10]


def _month_key(value):
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.strftime("%B %Y")
    except (TypeError, ValueError):
        return "Fixtures"


def _record(results, team):
    wins = draws = losses = unplayed = 0
    for row in results:
        result = _result_for_team(
            team,
            row["home_team_name"],
            row["away_team_name"],
            row["home_score"],
            row["away_score"],
        )
        wins += result == "W"
        draws += result == "D"
        losses += result == "L"
        unplayed += result == "UNPLAYED"
    return wins, draws, losses, unplayed


def render_fixture_explorer(season, team, get_fixtures):
    """Render the browse-first chronological fixture list for a chosen team."""
    all_results = get_fixtures(season=season, team=team)["results"]
    wins, draws, losses, unplayed = _record(all_results, team)

    record_parts = [
        f"{len(all_results)} matches",
        f"{wins} W",
        f"{draws} D",
        f"{losses} L",
    ]
    if unplayed:
        record_parts.append(f"{unplayed} unplayed")

    st.markdown(
        "<div class='frl-record-line'>"
        + " <span>·</span> ".join(record_parts)
        + "</div>",
        unsafe_allow_html=True,
    )

    opponent_names = sorted(
        {
            row["away_team_name"]
            if row["home_team_name"] == team
            else row["home_team_name"]
            for row in all_results
        },
        key=str.casefold,
    )

    selected_opponent = None
    selected_venue = None
    selected_result = None

    with st.expander("Filter fixtures", expanded=False):
        filter_cols = st.columns([2.2, 1.0, 1.0], gap="small")
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

    results = get_fixtures(
        season=season,
        team=team,
        opponent=selected_opponent,
        venue=selected_venue,
        result=selected_result,
    )["results"]

    if not results:
        st.markdown(
            "<div class='frl-empty-state'>No fixtures match the selected filters.</div>",
            unsafe_allow_html=True,
        )
        return

    if any(value is not None for value in (selected_opponent, selected_venue, selected_result)):
        filtered_wins, filtered_draws, filtered_losses, _ = _record(results, team)
        st.markdown(
            f"<div class='frl-filtered-line'>{len(results)} matches &nbsp;·&nbsp; "
            f"{filtered_wins} W &nbsp;·&nbsp; {filtered_draws} D &nbsp;·&nbsp; {filtered_losses} L</div>",
            unsafe_allow_html=True,
        )

    previous_month = None
    for row in results:
        month = _month_key(row["kickoff_time"])
        if month != previous_month:
            st.markdown(
                f"<div class='frl-month-heading'>{month}</div>",
                unsafe_allow_html=True,
            )
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
            previous_month = month

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
        score = (
            "—"
            if row["home_score"] in (None, "") or row["away_score"] in (None, "")
            else f"{row['home_score']}–{row['away_score']}"
        )
        result_class = _result_class(result)

        cols = st.columns([1.05, 3.1, 1.0, 0.95, 0.85], gap="small")
        cols[0].markdown(
            f"<div class='frl-meta'>{_display_date(row['kickoff_time'])}<br>"
            f"<span class='frl-meta-sub'>GW {row['gameweek']}</span></div>",
            unsafe_allow_html=True,
        )

        if cols[1].button(
            opponent,
            key=f"fixture_opponent_{row['fixture_id']}",
            width="stretch",
            type="secondary",
        ):
            st.query_params["fixture"] = f"{season}:{row['fixture_id']}"
            st.rerun()

        cols[2].markdown(f"<div class='frl-meta'>{venue}</div>", unsafe_allow_html=True)
        cols[3].markdown(f"<div class='frl-score'>{score}</div>", unsafe_allow_html=True)
        cols[4].markdown(
            f"<div class='frl-result {result_class}'>{result}</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='frl-fixture-row-rule'></div>", unsafe_allow_html=True)
