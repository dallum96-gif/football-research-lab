from __future__ import annotations

import streamlit as st

import query_api
from frl_analytical import team_fixtures
from frl_visualisations import team_goals_trend


def _season_key(value: str) -> tuple[int, int]:
    try:
        left, right = value.split("-", 1)
        return int(left), int(right)
    except (TypeError, ValueError):
        return (0, 0)


def _fmt(value) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "—"


@st.cache_data(show_spinner=False)
def _seasons() -> list[str]:
    return sorted(query_api.list_seasons(), key=_season_key, reverse=True)


@st.cache_data(show_spinner=False)
def _league_table(season: str) -> dict:
    return query_api.league_table(season)


@st.cache_data(show_spinner=False)
def _team_summary(season: str, team: str) -> dict:
    return query_api.team_summary(season=season, team=team)


@st.cache_data(show_spinner=False)
def _team_form(season: str, team: str) -> dict:
    return query_api.team_form(season=season, team=team)


@st.cache_data(show_spinner=False)
def _team_fixtures_visual(season: str, team: str):
    return team_fixtures(season=season, team=team, limit=100)


@st.cache_data(show_spinner=False)
def _team_fixtures_display(season: str, team: str) -> dict:
    return query_api.fixtures(season=season, team=team, limit=100)


def _css() -> None:
    st.markdown(
        """
        <style>
        .frl-team-kicker{color:var(--frl-accent);font-size:.62rem;font-weight:800;letter-spacing:.15em;text-transform:uppercase;margin-bottom:.35rem}
        .frl-team-title{color:var(--frl-text);font-size:2.05rem;font-weight:800;line-height:1.04;letter-spacing:-.035em;margin:0}
        .frl-team-note{color:var(--frl-muted);font-size:.82rem;margin-top:.28rem}
        .frl-team-section{color:var(--frl-muted-soft);font-size:.61rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;margin:1.2rem 0 .42rem}
        .frl-team-record{color:var(--frl-muted);font-size:.76rem;margin:.72rem 0 1rem;padding:.72rem 0;border-top:1px solid var(--frl-border);border-bottom:1px solid var(--frl-border)}
        .frl-team-record strong{color:var(--frl-text);font-weight:780}
        .frl-team-form{display:flex;gap:.35rem;margin:.2rem 0 .6rem}
        .frl-team-form span{min-width:1.8rem;height:1.8rem;border:1px solid var(--frl-border);border-radius:5px;display:flex;align-items:center;justify-content:center;color:var(--frl-muted);font-size:.62rem;font-weight:800}
        .frl-team-form .win{color:var(--frl-secondary);border-color:rgba(154,170,66,.45)}
        .frl-team-form .draw{color:var(--frl-muted);}
        .frl-team-form .loss{color:var(--frl-negative);border-color:rgba(232,93,63,.35)}
        .frl-team-row{display:grid;grid-template-columns:4rem minmax(0,1fr) 4.5rem 3rem;gap:.5rem;align-items:center;padding:.55rem 0;border-bottom:1px solid var(--frl-border)}
        .frl-team-row:last-child{border-bottom:0}
        .frl-team-row-muted{color:var(--frl-muted-soft);font-size:.58rem}
        .frl-team-row-main{color:var(--frl-text);font-size:.68rem;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
        .frl-team-row-meta{color:var(--frl-muted);font-size:.6rem;text-align:right}
        .frl-team-row-accent{color:var(--frl-text);font-size:.66rem;font-weight:800;text-align:right}
        @media(max-width:900px){.frl-team-row{grid-template-columns:3.2rem minmax(0,1fr) 4rem 2.8rem}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _profile(summary: dict, form: dict, fixtures: dict, season: str, team: str) -> None:
    data = summary.get("summary", {})
    recent = form.get("windows", {}).get("5", {})
    streaks = form.get("streaks", {})

    st.markdown("<div class='frl-team-section'>Season snapshot</div>", unsafe_allow_html=True)
    record = (
        f"<strong>{_fmt(data.get('played'))}</strong> played · "
        f"<strong>{_fmt(data.get('wins'))}</strong> wins · "
        f"<strong>{_fmt(data.get('points'))}</strong> points · "
        f"<strong>{_fmt(data.get('goals_for'))}–{_fmt(data.get('goals_against'))}</strong> goals · "
        f"<strong>{_fmt(data.get('goal_difference')):+}</strong> GD"
    )
    st.markdown(f"<div class='frl-team-record'>{record}</div>", unsafe_allow_html=True)

    st.markdown("<div class='frl-team-section'>Goals trend</div>", unsafe_allow_html=True)
    st.caption("Goals scored and conceded by fixture. Hover a point for the opponent, result and fixture evidence.")
    trend_result = _team_fixtures_visual(season, team)
    st.altair_chart(team_goals_trend(trend_result), width="stretch")

    left, right = st.columns(2, gap="medium")
    with left:
        st.markdown("<div class='frl-team-section'>Recent form</div>", unsafe_allow_html=True)
        spans = []
        for result in recent.get("results", []):
            result_class = {"W": "win", "D": "draw", "L": "loss"}.get(result, "")
            spans.append(f"<span class='{result_class}'>{result}</span>")
        pills = "".join(spans) or '<span>—</span>'
        st.markdown(f"<div class='frl-team-form'>{pills}</div>", unsafe_allow_html=True)
        st.caption(
            f"{recent.get('points', 0)} pts · {recent.get('goals_for', 0)} scored · {recent.get('goals_against', 0)} conceded"
        )

    with right:
        st.markdown("<div class='frl-team-section'>Current runs</div>", unsafe_allow_html=True)
        for label, value in [
            ("Wins", streaks.get("current_win_streak", 0)),
            ("Unbeaten", streaks.get("current_unbeaten_streak", 0)),
            ("Clean sheets", streaks.get("current_clean_sheet_streak", 0)),
            ("Scoring", streaks.get("current_scoring_streak", 0)),
        ]:
            st.markdown(
                f"<div class='frl-team-row'><div class='frl-team-row-muted'>run</div><div class='frl-team-row-main'>{label}</div><div class='frl-team-row-meta'>current</div><div class='frl-team-row-accent'>{_fmt(value)}</div></div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div class='frl-team-section'>Recent fixtures</div>", unsafe_allow_html=True)
    recent_rows = list(fixtures.get("results", []))[-5:]
    if not recent_rows:
        st.markdown("<div class='frl-empty-state'>No fixture history is available for this scope.</div>", unsafe_allow_html=True)
        return

    for row in reversed(recent_rows):
        home = row.get("home_team_name", "Home")
        away = row.get("away_team_name", "Away")
        score = "—"
        if row.get("home_score") not in (None, "") and row.get("away_score") not in (None, ""):
            score = f"{row['home_score']}–{row['away_score']}"
        st.markdown(
            f"<div class='frl-team-row'><div class='frl-team-row-muted'>{row.get('gameweek','')}</div><div class='frl-team-row-main'>{home} <span style='color:var(--frl-muted-soft)'>v</span> {away}</div><div class='frl-team-row-meta'>{str(row.get('kickoff_time',''))[:10]}</div><div class='frl-team-row-accent'>{score}</div></div>",
            unsafe_allow_html=True,
        )


def _stats(comparison: dict) -> None:
    rows = comparison.get("seasons", [])
    if not rows:
        st.info("No verified season records are available for this team in the selected range.")
        return

    latest = rows[-1]
    st.markdown("<div class='frl-team-section'>Research snapshot</div>", unsafe_allow_html=True)
    record = (
        f"<strong>{_fmt(latest.get('points'))}</strong> latest points · "
        f"<strong>{int(latest.get('goal_difference', 0)):+d}</strong> latest GD · "
        f"<strong>{_fmt(latest.get('wins'))}</strong> latest wins · "
        f"<strong>{len(rows)}</strong> seasons found"
    )
    st.markdown(f"<div class='frl-team-record'>{record}</div>", unsafe_allow_html=True)

    st.markdown("<div class='frl-team-section'>Season comparison</div>", unsafe_allow_html=True)
    header = "<div class='frl-team-row'><div class='frl-team-row-muted'>Season</div><div class='frl-team-row-main'>Record</div><div class='frl-team-row-meta'>GD</div><div class='frl-team-row-accent'>Pts</div></div>"
    body = "".join(
        f"<div class='frl-team-row'><div class='frl-team-row-muted'>{row.get('season','')}</div><div class='frl-team-row-main'>{row.get('wins',0)}W · {row.get('draws',0)}D · {row.get('losses',0)}L · {row.get('played',0)} played</div><div class='frl-team-row-meta'>{int(row.get('goal_difference',0)):+d}</div><div class='frl-team-row-accent'>{row.get('points',0)}</div></div>"
        for row in rows
    )
    st.markdown(f"<div>{header}{body}</div>", unsafe_allow_html=True)
    if comparison.get("skipped_seasons"):
        st.caption("Some requested seasons are omitted because the verified team identity was not present in those seasons.")


def render_team_research_ui() -> None:
    _css()
    seasons = _seasons()
    if not seasons:
        st.error("No verified team seasons are available.")
        return

    season = st.selectbox("Season", seasons, index=0, key="frl_team_season")
    table = _league_table(season).get("teams", [])
    teams = [row.get("team") for row in table if row.get("team")]
    if not teams:
        st.info("No teams are available for this season.")
        return

    team = st.selectbox("Team", teams, index=0, key="frl_selected_team")
    st.markdown("<div class='frl-team-kicker'>Team research</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-team-title'>{team}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-team-note'>{season} · verified team identity · football research context</div>", unsafe_allow_html=True)

    view = st.segmented_control("Team view", ["Profile", "Stats"], default="Profile", key="frl_team_view", label_visibility="collapsed")
    if view == "Profile":
        _profile(
            _team_summary(season, team),
            _team_form(season, team),
            _team_fixtures_display(season, team),
            season,
            team,
        )
        return

    selected = st.multiselect("Seasons", seasons, default=seasons[: min(4, len(seasons))], key="frl_team_stats_seasons") or [season]
    selected = sorted(selected, key=_season_key)
    _stats(query_api.team_compare(team=team, seasons=selected))
