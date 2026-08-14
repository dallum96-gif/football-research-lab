from pathlib import Path
from datetime import date, datetime
import sys

import streamlit as st
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import query_api
import poisson_model
import kelly_analysis


st.set_page_config(
    page_title="Football Research Lab",
    page_icon="⚽",
    layout="wide",
)

st.markdown(
    """
    <style>
    .form-pill {
        display: inline-block;
        min-width: 34px;
        padding: 6px 10px;
        margin: 3px 4px 3px 0;
        border: 1px solid rgba(128,128,128,.25);
        border-radius: 999px;
        text-align: center;
        font-weight: 700;
        font-size: .9rem;
    }
    .form-range {
        color: rgba(128,128,128,.9);
        font-size: .9rem;
        margin-bottom: .35rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
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


@st.cache_data
def get_team_form(season, team):
    return query_api.team_form(
        season=season,
        team=team,
    )




def render_fixture_detail(detail):
    fixture = detail["fixture"]
    stats = detail["stats"]

    home = fixture["home_team_name"]
    away = fixture["away_team_name"]

    home_score = fixture["home_score"] or "—"
    away_score = fixture["away_score"] or "—"

    st.markdown(
        f"<div style='text-align:center;'>"
        f"<div style='font-size:.9rem; opacity:.7;'>"
        f"{fixture['season']} · GW {fixture['gameweek']}"
        f"</div>"
        f"<div style='font-size:1rem; opacity:.8; margin-top:.25rem;'>"
        f"{fixture['kickoff_time'][:10]}"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<div style='text-align:center; margin:1rem 0 1.5rem 0;'>"
        f"<div style='font-size:1.55rem; font-weight:700;'>"
        f"{home}"
        f"</div>"
        f"<div style='font-size:3rem; font-weight:800; line-height:1.1; margin:.35rem 0;'>"
        f"{home_score}–{away_score}"
        f"</div>"
        f"<div style='font-size:1.55rem; font-weight:700;'>"
        f"{away}"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    if fixture.get("data_corrected") == "true":
        st.info(
            "This fixture contains a verified historical data correction. "
            "The analytical view uses the corrected kickoff and result."
        )

    if stats["status"] != "AVAILABLE":
        st.warning(
            "Historical match statistics are not available for this fixture."
        )
        return

    home_core = stats["home"]["core"]
    away_core = stats["away"]["core"]

    def stat_value(values, label):
        value = values.get(label)
        return 0 if value is None else value

    def render_group(title, labels):
        st.markdown(
            f"#### {title}"
        )

        rows = [
            {
                "Statistic": label,
                home: stat_value(home_core, label),
                away: stat_value(away_core, label),
            }
            for label in labels
            if label in home_core
        ]

        st.dataframe(
            pd.DataFrame(rows),
            width="stretch",
            hide_index=True,
        )

    render_group(
        "Attacking",
        [
            "Shots",
            "Shots on target",
            "Shots off target",
            "Blocked shots",
            "Corners",
        ],
    )

    render_group(
        "Possession & passing",
        [
            "Possession",
            "Passes",
            "Accurate passes",
            "Crosses",
        ],
    )

    render_group(
        "Defending",
        [
            "Tackles",
            "Tackles won",
            "Interceptions",
            "Interceptions won",
            "Clearances",
            "Effective clearances",
            "Offsides",
        ],
    )

    render_group(
        "Discipline",
        [
            "Fouls won",
            "Fouls conceded",
            "Yellow cards",
            "Red cards",
        ],
    )

    home_optional = stats["home"]["optional"]
    away_optional = stats["away"]["optional"]

    optional_rows = []

    for label in home_optional:
        optional_rows.append(
            {
                "Statistic": label,
                home: (
                    0
                    if home_optional[label] is None
                    else home_optional[label]
                ),
                away: (
                    0
                    if away_optional[label] is None
                    else away_optional[label]
                ),
            }
        )

    with st.expander(
        "Additional statistics",
        expanded=False,
    ):
        st.dataframe(
            pd.DataFrame(optional_rows),
            width="stretch",
            hide_index=True,
        )

        st.caption(
            "Zero is displayed where the source provides no "
            "value for this fixture statistic."
        )

    with st.expander(
        "Data provenance",
        expanded=False,
    ):
        st.write(
            {
                "Canonical fixture ID":
                    fixture["fixture_id"],
                "PL source match ID":
                    stats["source_match_id"],
                "Canonical fixture source":
                    detail["provenance"]["canonical_source"],
                "Identity source":
                    detail["provenance"]["identity_source"],
                "Correction source":
                    detail["provenance"]["correction_source"],
            }
        )


def render_prediction_lab():
    st.subheader(
        "Prediction Lab"
    )

    st.caption(
        "Poisson V0.1 — exploratory model based exclusively "
        "on 2025/26 score data. Not yet out-of-sample validated."
    )

    teams = poisson_model.PREMIER_LEAGUE_2026_27

    st.markdown("#### Match")

    home_col, away_col = st.columns(2)

    with home_col:
        home_team = st.selectbox(
            "Home team",
            teams,
            index=teams.index("Arsenal"),
            key="prediction_home_team",
        )

    away_options = [
        team
        for team in teams
        if team != home_team
    ]

    default_away = (
        away_options.index("Manchester United")
        if "Manchester United" in away_options
        else 0
    )

    with away_col:
        away_team = st.selectbox(
            "Away team",
            away_options,
            index=default_away,
            key="prediction_away_team",
        )

    prediction = poisson_model.poisson_prediction(
        home_team,
        away_team,
    )

    expected_home = prediction[
        "expected_goals"
    ]["home"]

    expected_away = prediction[
        "expected_goals"
    ]["away"]

    metric_cols = st.columns(2)

    metric_cols[0].metric(
        f"{home_team} expected goals",
        f"{expected_home:.2f}",
    )

    metric_cols[1].metric(
        f"{away_team} expected goals",
        f"{expected_away:.2f}",
    )

    probabilities = prediction[
        "probabilities"
    ]

    fair = prediction[
        "fair_odds"
    ]

    result_rows = [
        {
            "Outcome": "Home win",
            "Model probability":
                f"{probabilities['home_win'] * 100:.1f}%",
            "Fair odds":
                f"{fair['home_win']:.2f}",
        },
        {
            "Outcome": "Draw",
            "Model probability":
                f"{probabilities['draw'] * 100:.1f}%",
            "Fair odds":
                f"{fair['draw']:.2f}",
        },
        {
            "Outcome": "Away win",
            "Model probability":
                f"{probabilities['away_win'] * 100:.1f}%",
            "Fair odds":
                f"{fair['away_win']:.2f}",
        },
        {
            "Outcome": "Over 2.5",
            "Model probability":
                f"{probabilities['over_2_5'] * 100:.1f}%",
            "Fair odds":
                f"{1 / probabilities['over_2_5']:.2f}",
        },
        {
            "Outcome": "BTTS",
            "Model probability":
                f"{probabilities['btts'] * 100:.1f}%",
            "Fair odds":
                f"{1 / probabilities['btts']:.2f}",
        },
    ]

    st.markdown("#### Model output")

    st.dataframe(
        pd.DataFrame(result_rows),
        width="stretch",
        hide_index=True,
    )

    most_likely = prediction[
        "most_likely_score"
    ]

    st.caption(
        "Most likely score: "
        f"{most_likely['home']}–"
        f"{most_likely['away']} "
        f"({most_likely['probability'] * 100:.1f}%)"
    )

    if (
        home_team in poisson_model.PROMOTED_TEAMS
        or away_team in poisson_model.PROMOTED_TEAMS
    ):
        st.info(
            "Promoted-team treatment: "
            + prediction["promotion_method"]
        )

    st.divider()

    st.markdown("#### Bookmaker comparison")

    st.caption(
        "Enter decimal 1X2 odds to compare the market "
        "with the model."
    )

    odds_home, odds_draw, odds_away = st.columns(3)

    with odds_home:
        home_odds = st.number_input(
            "Home odds",
            min_value=1.01,
            value=2.00,
            step=0.01,
            key="prediction_home_odds",
        )

    with odds_draw:
        draw_odds = st.number_input(
            "Draw odds",
            min_value=1.01,
            value=3.50,
            step=0.01,
            key="prediction_draw_odds",
        )

    with odds_away:
        away_odds = st.number_input(
            "Away odds",
            min_value=1.01,
            value=4.00,
            step=0.01,
            key="prediction_away_odds",
        )

    comparison = (
        poisson_model.compare_bookmaker_odds(
            prediction,
            home_odds,
            draw_odds,
            away_odds,
        )
    )

    labels = {
        "home_win": "Home win",
        "draw": "Draw",
        "away_win": "Away win",
    }

    comparison_rows = []

    for key in (
        "home_win",
        "draw",
        "away_win",
    ):
        comparison_rows.append(
            {
                "Outcome": labels[key],
                "Model":
                    f"{probabilities[key] * 100:.1f}%",
                "Market":
                    f"{comparison['market_probability'][key] * 100:.1f}%",
                "Edge":
                    f"{comparison['probability_edge'][key] * 100:+.1f}pp",
                "Fair odds":
                    f"{fair[key]:.2f}",
                "Bookmaker odds":
                    f"{comparison['bookmaker_odds'][key]:.2f}",
                "EV":
                    f"{comparison['expected_value'][key] * 100:+.1f}%",
            }
        )

    st.dataframe(
        pd.DataFrame(comparison_rows),
        width="stretch",
        hide_index=True,
    )

    st.caption(
        "Market overround: "
        f"{(comparison['overround'] - 1) * 100:.2f}%"
    )

    st.divider()

    st.markdown("#### Kelly staking analysis")

    bankroll = st.number_input(
        "Optional bankroll",
        min_value=0.0,
        value=1000.0,
        step=50.0,
        key="prediction_bankroll",
    )

    kelly_rows = []

    for key in (
        "home_win",
        "draw",
        "away_win",
    ):
        analysis = (
            kelly_analysis.kelly_analysis(
                probabilities[key],
                comparison["bookmaker_odds"][key],
                bankroll,
            )
        )

        kelly_rows.append(
            {
                "Outcome": labels[key],
                "Full Kelly":
                    f"{analysis['full_kelly'] * 100:.2f}%",
                "Half Kelly":
                    f"{analysis['half_kelly'] * 100:.2f}%",
                "Quarter Kelly":
                    f"{analysis['quarter_kelly'] * 100:.2f}%",
                "Full Kelly £":
                    f"£{analysis['stakes']['full_kelly']:.2f}",
                "Half Kelly £":
                    f"£{analysis['stakes']['half_kelly']:.2f}",
                "Quarter Kelly £":
                    f"£{analysis['stakes']['quarter_kelly']:.2f}",
            }
        )

    st.dataframe(
        pd.DataFrame(kelly_rows),
        width="stretch",
        hide_index=True,
    )

    st.warning(
        "Kelly figures are mathematical outputs based on "
        "the model probability. Poisson V0.1 is exploratory "
        "and has not yet been validated out of sample. "
        "The Laboratory does not make a betting recommendation."
    )

def season_key(season):
    return int(season.split("-")[0])


def kickoff_date(row):
    return datetime.fromisoformat(
        row["kickoff_time"].replace("Z", "+00:00")
    ).date()


def gameweek_number(row):
    try:
        return int(row["gameweek"])
    except (TypeError, ValueError):
        return None


def result_pills(results):
    if not results:
        return "<span class='form-range'>No completed matches in this range.</span>"

    pills = []
    for result in results:
        pills.append(
            f"<span class='form-pill'>{result}</span>"
        )
    return "".join(pills)


st.title("Football Research Lab")
st.caption(
    "Premier League historical data and analysis"
)

fixture_token = st.query_params.get("fixture")

if fixture_token:
    try:
        fixture_season, fixture_id = fixture_token.split(":", 1)

        detail = query_api.fixture_detail(
            season=fixture_season,
            fixture_id=fixture_id,
        )

        if st.button(
            "← Back to Fixture Explorer",
            key="fixture_back",
        ):
            del st.query_params["fixture"]
            st.rerun()

        st.divider()

        render_fixture_detail(detail)

        st.stop()

    except Exception as exc:
        st.error(
            f"Unable to open fixture: {exc}"
        )
        st.stop()



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

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "League Table",
        "Fixture Explorer",
        "Season Comparison",
        "Head-to-Head",
        "Form & Streaks",
        "Prediction Lab",
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
        width='stretch',
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
                "_fixture_id": row["fixture_id"],
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

    header_cols = st.columns(
        [1.2, 0.7, 0.8, 1.8, 0.9, 0.8]
    )

    headers = [
        "Date",
        "GW",
        "Venue",
        "Opponent",
        "Score",
        "Result",
    ]

    for col, header in zip(
        header_cols,
        headers,
    ):
        col.markdown(
            f"**{header}**"
        )

    st.divider()

    for row in fixture_rows:
        cols = st.columns(
            [1.2, 0.7, 0.8, 1.8, 0.9, 0.8]
        )

        cols[0].write(row["Date"])
        cols[1].write(row["GW"])
        cols[2].write(row["Venue"])

        if cols[3].button(
            row["Opponent"],
            key=(
                "fixture_opponent_"
                f"{row['_fixture_id']}"
            ),
            use_container_width=True,
        ):
            st.query_params["fixture"] = (
                f"{season}:{row['_fixture_id']}"
            )
            st.rerun()

        cols[4].write(row["Score"])
        cols[5].write(row["Result"])

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
        width='stretch',
        hide_index=True,
    )

with tab4:
    st.subheader("Head-to-Head Explorer")

    h2h_cols = st.columns(2)

    with h2h_cols[0]:
        h2h_opponent_names = sorted(
            [
                name
                for name in teams
                if name != team
            ],
            key=str.casefold,
        )

        h2h_opponent = st.selectbox(
            "Opponent",
            h2h_opponent_names,
            key="h2h_opponent",
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
            width='stretch',
            hide_index=True,
        )

with tab5:
    st.subheader("Form & Streaks")
    st.caption(
        "Explore completed league form by matchday or calendar date."
    )

    form = get_team_form(
        season=season,
        team=team,
    )
    completed = form["matches"]

    if not completed:
        st.info("No completed matches are available for this team and season.")
    else:
        max_gameweek = max(
            gameweek_number(row)
            for row in completed
            if gameweek_number(row) is not None
        )
        min_date = min(kickoff_date(row) for row in completed)
        max_date = max(kickoff_date(row) for row in completed)

        filter_mode = st.radio(
            "Filter range",
            ["Matchdays", "Dates"],
            horizontal=True,
            label_visibility="collapsed",
        )

        if filter_mode == "Matchdays":
            range_cols = st.columns(2)
            with range_cols[0]:
                start_gw = st.number_input(
                    "From matchday",
                    min_value=1,
                    max_value=max_gameweek,
                    value=1,
                    step=1,
                )
            with range_cols[1]:
                end_gw = st.number_input(
                    "To matchday",
                    min_value=1,
                    max_value=max_gameweek,
                    value=max_gameweek,
                    step=1,
                )

            if start_gw > end_gw:
                start_gw, end_gw = end_gw, start_gw

            filtered = [
                row
                for row in completed
                if (
                    gameweek_number(row) is not None
                    and start_gw <= gameweek_number(row) <= end_gw
                )
            ]

            range_label = (
                f"GW {start_gw}–{end_gw}"
            )

        else:
            range_cols = st.columns(2)
            with range_cols[0]:
                start_date = st.date_input(
                    "From date",
                    value=min_date,
                    min_value=min_date,
                    max_value=max_date,
                )
            with range_cols[1]:
                end_date = st.date_input(
                    "To date",
                    value=max_date,
                    min_value=min_date,
                    max_value=max_date,
                )

            if start_date > end_date:
                start_date, end_date = end_date, start_date

            filtered = [
                row
                for row in completed
                if start_date <= kickoff_date(row) <= end_date
            ]

            range_label = (
                f"{start_date.strftime('%d %b %Y')} – "
                f"{end_date.strftime('%d %b %Y')}"
            )

        if filtered:
            filtered = sorted(
                filtered,
                key=lambda row: row["kickoff_time"],
            )

            points = sum(row["points"] for row in filtered)
            goals_for = sum(row["goals_for"] for row in filtered)
            goals_against = sum(row["goals_against"] for row in filtered)
            wins = sum(row["result"] == "W" for row in filtered)
            draws = sum(row["result"] == "D" for row in filtered)
            losses = sum(row["result"] == "L" for row in filtered)

            first_date = kickoff_date(filtered[0])
            last_date = kickoff_date(filtered[-1])
            first_gw = gameweek_number(filtered[0])
            last_gw = gameweek_number(filtered[-1])

            st.markdown(
                f"**{team}** · {range_label}  "
                f"  \n"
                f"{len(filtered)} matches · "
                f"GW {first_gw}–{last_gw} · "
                f"{first_date.strftime('%d %b')}–{last_date.strftime('%d %b %Y')}"
            )

            form_metrics = st.columns(5)
            form_metrics[0].metric("Points", points)
            form_metrics[1].metric("Record", f"{wins}W {draws}D {losses}L")
            form_metrics[2].metric("Goals for", goals_for)
            form_metrics[3].metric("Goals against", goals_against)
            form_metrics[4].metric("Goal difference", f"{goals_for - goals_against:+d}")

            st.markdown("**Results**")
            st.markdown(
                result_pills([row["result"] for row in filtered]),
                unsafe_allow_html=True,
            )

            st.markdown("**Matches**")
            form_rows = []
            for row in filtered:
                form_rows.append(
                    {
                        "Date": kickoff_date(row).strftime("%d %b %Y"),
                        "GW": row["gameweek"],
                        "Fixture": (
                            f"{row['home_team_name']} "
                            f"{row['home_score']}-{row['away_score']} "
                            f"{row['away_team_name']}"
                        ),
                        "Result": row["result"],
                        "Pts": row["points"],
                    }
                )

            st.dataframe(
                pd.DataFrame(form_rows),
                width="stretch",
                hide_index=True,
            )
        else:
            st.info("No completed matches fall inside the selected range.")

        st.divider()
        st.markdown("**Season streaks**")
        streak_cols = st.columns(5)
        streaks = form["streaks"]
        streak_cols[0].metric("Win streak", streaks["current_win_streak"])
        streak_cols[1].metric("Unbeaten", streaks["current_unbeaten_streak"])
        streak_cols[2].metric("Loss streak", streaks["current_loss_streak"])
        streak_cols[3].metric("Clean sheets", streaks["current_clean_sheet_streak"])
        streak_cols[4].metric("Scoring", streaks["current_scoring_streak"])

with st.expander("Data provenance"):
    st.write(
        {
            "Query version": summary["query_version"],
            "Fixture source": summary["source_file"],
            "Identity source": summary["identity_source_file"],
        }
    )


with tab6:
    render_prediction_lab()
