"""Team Profile and Team Stats presentation for the FRL.

Presentation only: all football calculations come from query_api.
"""
from __future__ import annotations

import streamlit as st

import query_api


def _season_key(value: str) -> tuple[int, int]:
    try:
        left, right = value.split("-", 1)
        return int(left), int(right)
    except (TypeError, ValueError):
        return (0, 0)


def _fmt_int(value) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "—"


def _fmt_pct(value) -> str:
    try:
        return f"{float(value):.0f}%"
    except (TypeError, ValueError):
        return "—"


def _team_css() -> None:
    st.markdown(
        """
        <style>
        .frl-team-kicker { color:var(--frl-accent); font-size:.58rem; font-weight:820; letter-spacing:.16em; text-transform:uppercase; }
        .frl-team-title { margin-top:.22rem; color:var(--frl-text); font-family:"Source Sans",sans-serif; font-size:clamp(2rem,4vw,3.25rem); font-weight:820; line-height:.95; letter-spacing:-.045em; }
        .frl-team-note { margin-top:.42rem; color:var(--frl-muted); font-size:.78rem; line-height:1.35; }
        .frl-team-switch { margin:.9rem 0 1.05rem; border-bottom:1px solid var(--frl-border); padding-bottom:.35rem; }
        .frl-team-stat-grid { display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:.55rem; margin:1rem 0 1.1rem; }
        .frl-team-stat { min-height:78px; padding:.72rem .78rem; border:1px solid var(--frl-border); border-radius:12px; background:transparent; }
        .frl-team-stat-label { color:var(--frl-muted-soft); font-size:.52rem; font-weight:820; letter-spacing:.11em; text-transform:uppercase; }
        .frl-team-stat-value { margin-top:.32rem; color:var(--frl-text); font-size:1.28rem; font-weight:820; letter-spacing:-.035em; }
        .frl-team-stat-accent .frl-team-stat-value { color:var(--frl-accent); }
        .frl-team-section { margin-top:1.1rem; color:var(--frl-accent); font-size:.58rem; font-weight:820; letter-spacing:.15em; text-transform:uppercase; }
        .frl-team-card { padding:.78rem .85rem; border:1px solid var(--frl-border); border-radius:12px; background:var(--frl-surface); }
        .frl-team-card-title { color:var(--frl-text); font-size:.86rem; font-weight:780; }
        .frl-team-card-copy { margin-top:.2rem; color:var(--frl-muted); font-size:.67rem; line-height:1.4; }
        .frl-form-strip { display:flex; gap:.28rem; flex-wrap:wrap; margin-top:.5rem; }
        .frl-form-pill { width:1.8rem; height:1.8rem; display:flex; align-items:center; justify-content:center; border:1px solid var(--frl-border); border-radius:7px; color:var(--frl-text); background:transparent; font-size:.62rem; font-weight:820; }
        .frl-form-pill-win { border-color:rgba(232,93,63,.34); color:var(--frl-accent); }
        .frl-team-row { display:grid; grid-template-columns:2.8rem minmax(0,1fr) 5.2rem 3.8rem; gap:.6rem; align-items:center; padding:.62rem 0; border-bottom:1px solid var(--frl-border); }
        .frl-team-row:last-child { border-bottom:0; }
        .frl-team-row-rank { color:var(--frl-muted-soft); font-size:.58rem; font-weight:820; }
        .frl-team-row-name { color:var(--frl-text); font-size:.7rem; font-weight:720; min-width:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
        .frl-team-row-meta { color:var(--frl-muted); font-size:.62rem; text-align:right; }
        .frl-team-row-points { color:var(--frl-accent); font-size:.7rem; font-weight:820; text-align:right; }
        @media (max-width: 900px) { .frl-team-stat-grid { grid-template-columns:repeat(3,minmax(0,1fr)); } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _profile(team: str, season: str, summary: dict, form: dict, fixtures: dict) -> None:
    s = summary.get("summary", {})
    streaks = form.get("streaks", {})
    window = form.get("windows", {}).get("5", {})

    st.markdown("<div class='frl-team-section'>Season snapshot</div>", unsafe_allow_html=True)
    stats = [
        ("Played", _fmt_int(s.get("played")), False),
        ("Wins", _fmt_int(s.get("wins")), False),
        ("Points", _fmt_int(s.get("points")), True),
        ("Goals for", _fmt_int(s.get("goals_for")), False),
        ("Goals against", _fmt_int(s.get("goals_against")), False),
        ("Goal difference", _fmt_int(s.get("goal_difference")), False),
    ]
    cards = "".join(
        f"<div class='frl-team-stat{' frl-team-stat-accent' if accent else ''}'><div class='frl-team-stat-label'>{label}</div><div class='frl-team-stat-value'>{value}</div></div>"
        for label, value, accent in stats
    )
    st.markdown(f"<div class='frl-team-stat-grid'>{cards}</div>", unsafe_allow_html=True)

    left, right = st.columns([1.05, .95], gap="medium")
    with left:
        st.markdown("<div class='frl-team-section'>Recent form</div>", unsafe_allow_html=True)
        results = window.get("results", [])
        pills = "".join(
            f"<span class='frl-form-pill{' frl-form-pill-win' if result == 'W' else ''}'>{result}</span>"
            for result in results
        )
        st.markdown(
            f"<div class='frl-team-card'><div class='frl-team-card-title'>Last five</div><div class='frl-form-strip'>{pills or '<span class=\"frl-team-card-copy\">No completed fixtures</span>'}</div><div class='frl-team-card-copy'>{window.get('points', 0)} points · {window.get('goals_for', 0)} scored · {window.get('goals_against', 0)} conceded</div></div>",
            unsafe_allow_html=True,
        )
    with right:
        st.markdown("<div class='frl-team-section'>Current runs</div>", unsafe_allow_html=True)
        streak_items = [
            ("Wins", streaks.get("current_win_streak", 0)),
            ("Unbeaten", streaks.get("current_unbeaten_streak", 0)),
            ("Clean sheets", streaks.get("current_clean_sheet_streak", 0)),
            ("Scoring", streaks.get("current_scoring_streak", 0)),
        ]
        rows = "".join(
            f"<div class='frl-team-row'><div class='frl-team-row-rank'>•</div><div class='frl-team-row-name'>{label}</div><div class='frl-team-row-meta'>current</div><div class='frl-team-row-points'>{value}</div></div>"
            for label, value in streak_items
        )
        st.markdown(f"<div class='frl-team-card'>{rows}</div>", unsafe_allow_html=True)

    st.markdown("<div class='frl-team-section'>Recent fixtures</div>", unsafe_allow_html=True)
    recent = fixtures.get("results", [])[-5:]
    if recent:
        for row in reversed(recent):
            home = row.get("home_team_name", "Home")
            away = row.get("away_team_name", "Away")
            score = f"{row.get('home_score')}–{row.get('away_score')}" if row.get("home_score") not in (None, "") and row.get("away_score") not in (None, "") else "—"
            st.markdown(
                f"<div class='frl-team-row'><div class='frl-team-row-rank'>{row.get('gameweek','')}</div><div class='frl-team-row-name'>{home} <span style='color:var(--frl-muted-soft)'>v</span> {away}</div><div class='frl-team-row-meta'>{row.get('kickoff_time','')[:10]}</div><div class='frl-team-row-points'>{score}</div></div>",
                unsafe_allow_html=True,
            )
    else:
        st.caption("No fixture history is available for this scope.")


def _stats(team: str, seasons: list[str], comparison: dict) -> None:
    rows = comparison.get("seasons", [])
    st.markdown("<div class='frl-team-section'>Season comparison</div>", unsafe_allow_html=True)
    if not rows:
        st.info("No verified season records are available for this team in the selected range.")
        return

    latest = rows[-1]
    cols = st.columns(4, gap="small")
    for col, (label, value) in zip(
        cols,
        [
            ("Latest points", latest.get("points", 0)),
            ("Latest GD", latest.get("goal_difference", 0)),
            ("Latest wins", latest.get("wins", 0)),
            ("Seasons found", len(rows)),
        ],
    ):
        with col:
            st.markdown(
                f"<div class='frl-team-stat'><div class='frl-team-stat-label'>{label}</div><div class='frl-team-stat-value'>{value}</div></div>",
                unsafe_allow_html=True,
            )

    header = "".join(
        "<div class='frl-team-row'><div class='frl-team-row-rank'>Season</div><div class='frl-team-row-name'>Record</div><div class='frl-team-row-meta'>GD</div><div class='frl-team-row-points'>Pts</div></div>"
    )
    body = "".join(
        f"<div class='frl-team-row'><div class='frl-team-row-rank'>{row.get('season','')}</div><div class='frl-team-row-name'>{row.get('wins',0)}W · {row.get('draws',0)}D · {row.get('losses',0)}L · {row.get('played',0)} played</div><div class='frl-team-row-meta'>{row.get('goal_difference',0):+d}</div><div class='frl-team-row-points'>{row.get('points',0)}</div></div>"
        for row in rows
    )
    st.markdown(f"<div class='frl-team-card'>{header}{body}</div>", unsafe_allow_html=True)

    skipped = comparison.get("skipped_seasons", [])
    if skipped:
        st.caption("Some requested seasons are intentionally omitted because the verified team identity was not present in those seasons.")


def render_team_research_ui() -> None:
    _team_css()
    seasons = sorted(query_api.available_seasons(), key=_season_key, reverse=True)
    if not seasons:
        st.error("No verified team seasons are available.")
        return

    current_season = st.session_state.get("frl_team_season", seasons[0])
    if current_season not in seasons:
        current_season = seasons[0]
    season = st.selectbox("Season", seasons, index=seasons.index(current_season), key="frl_team_season")

    rows = query_api.league_table(season).get("teams", [])
    teams = [row.get("team", "") for row in rows if row.get("team")]
    current_team = st.session_state.get("frl_selected_team", teams[0] if teams else "")
    if current_team not in teams and teams:
        current_team = teams[0]
    team = st.selectbox("Team", teams, index=teams.index(current_team) if current_team in teams else 0, key="frl_selected_team")

    st.markdown("<div class='frl-team-kicker'>Team research</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-team-title'>{team}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-team-note'>{season} · canonical team identity · research context</div>", unsafe_allow_html=True)

    view = st.segmented_control(
        "Team view",
        ["Profile", "Stats"],
        default=st.session_state.get("frl_team_view", "Profile"),
        key="frl_team_view",
    )

    if view == "Profile":
        summary = query_api.team_summary(season=season, team=team)
        form = query_api.team_form(season=season, team=team)
        fixtures = query_api.fixtures(season=season, team=team, limit=100)
        _profile(team, season, summary, form, fixtures)
        return

    compare_seasons = st.multiselect(
        "Seasons",
        seasons,
        default=seasons[: min(4, len(seasons))],
        key="frl_team_stats_seasons",
    ) or [season]
    compare_seasons = sorted(compare_seasons, key=_season_key)
    comparison = query_api.team_compare(team=team, seasons=compare_seasons)
    _stats(team, compare_seasons, comparison)
