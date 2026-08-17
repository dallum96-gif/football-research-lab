"""Team Profile and Team Stats workspace.

Presentation-only layer over the trusted team/query contracts.
"""
from __future__ import annotations

from typing import Any

import streamlit as st

import query_api


def _season_key(value: str) -> tuple[int, int]:
    try:
        start, end = value.split("-", 1)
        return int(start), int(end)
    except ValueError:
        return 0, 0


def _fmt_int(value: Any) -> str:
    if value in (None, ""):
        return "—"
    try:
        return f"{int(float(value)):,}"
    except (TypeError, ValueError):
        return str(value)


def _fmt_decimal(value: Any, decimals: int = 2) -> str:
    if value in (None, ""):
        return "—"
    try:
        return f"{float(value):.{decimals}f}"
    except (TypeError, ValueError):
        return str(value)


def _record_cards(summary: dict[str, Any]) -> None:
    data = summary.get("summary", {})
    cards = [
        ("Position", _fmt_int(summary.get("position") or summary.get("league_position"))),
        ("Points", _fmt_int(data.get("points"))),
        ("Record", f"{data.get('wins', 0)}W {data.get('draws', 0)}D {data.get('losses', 0)}L"),
        ("Goal difference", _fmt_int(data.get("goal_difference"))),
    ]

    cols = st.columns(4, gap="small")
    for col, (label, value) in zip(cols, cards):
        with col:
            st.markdown(
                "<div class='frl-team-stat-card'>"
                f"<div class='frl-team-stat-label'>{label}</div>"
                f"<div class='frl-team-stat-value'>{value}</div>"
                "</div>",
                unsafe_allow_html=True,
            )


def _render_profile(season: str, team: str) -> None:
    summary = query_api.team_summary(season=season, team=team)
    form = query_api.team_form(season=season, team=team)
    fixtures = query_api.fixtures(season=season, team=team, limit=12)

    st.markdown("<div class='frl-eyebrow'>Team Profile</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-team-title'>{summary.get('team', team)}</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='frl-context'>{season} · canonical team identity · {summary.get('persistent_team_code') or '—'}</div>",
        unsafe_allow_html=True,
    )

    _record_cards(summary)

    window_5 = form.get("windows", {}).get("5", {})
    results = window_5.get("results", [])
    form_line = "  ".join(results) if results else "No completed matches"

    st.markdown("<div class='frl-team-section'>Recent form</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='frl-team-form-strip'>"
        f"<div class='frl-team-form-label'>Last 5</div>"
        f"<div class='frl-team-form-results'>{form_line}</div>"
        f"<div class='frl-team-form-meta'>{window_5.get('points', 0)} pts · {window_5.get('goals_for', 0)} GF · {window_5.get('goals_against', 0)} GA</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    streaks = form.get("streaks", {})
    streak_cards = [
        ("Unbeaten", streaks.get("current_unbeaten_streak", 0)),
        ("Wins", streaks.get("current_win_streak", 0)),
        ("Scoring", streaks.get("current_scoring_streak", 0)),
        ("Clean sheets", streaks.get("current_clean_sheet_streak", 0)),
    ]
    cols = st.columns(4, gap="small")
    for col, (label, value) in zip(cols, streak_cards):
        with col:
            st.markdown(
                "<div class='frl-team-mini-card'>"
                f"<div class='frl-team-mini-label'>{label}</div>"
                f"<div class='frl-team-mini-value'>{_fmt_int(value)}</div>"
                "</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div class='frl-team-section'>Recent fixtures</div>", unsafe_allow_html=True)
    rows = fixtures.get("results", [])[-8:]
    rows = list(reversed(rows))
    if not rows:
        st.caption("No fixture records available for this season.")
        return

    for row in rows:
        home = row.get("home_team_name", "Home")
        away = row.get("away_team_name", "Away")
        hs = row.get("home_score", "—") or "—"
        aws = row.get("away_score", "—") or "—"
        kickoff = str(row.get("kickoff_time", ""))[:10]
        opponent = away if home == team else home
        venue = "H" if home == team else "A"
        result = "—"
        if hs != "—" and aws != "—":
            if home == team:
                result = "W" if int(hs) > int(aws) else "D" if int(hs) == int(aws) else "L"
            else:
                result = "W" if int(aws) > int(hs) else "D" if int(aws) == int(hs) else "L"
        st.markdown(
            "<div class='frl-team-fixture-row'>"
            f"<div class='frl-team-fixture-date'>{kickoff}</div>"
            f"<div class='frl-team-fixture-venue'>{venue}</div>"
            f"<div class='frl-team-fixture-opponent'>{opponent}</div>"
            f"<div class='frl-team-fixture-score'>{hs}–{aws}</div>"
            f"<div class='frl-team-fixture-result frl-result-{result.lower()}'>{result}</div>"
            "</div>",
            unsafe_allow_html=True,
        )


def _render_stats(season: str, team: str) -> None:
    seasons = sorted(query_api.available_seasons(), key=_season_key)

    st.markdown("<div class='frl-eyebrow'>Team Stats</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-team-title'>{team}</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='frl-context'>Season and multi-season performance research from the canonical team layer.</div>",
        unsafe_allow_html=True,
    )

    start_index = max(0, len(seasons) - 5)
    start = st.selectbox("From", seasons, index=start_index, key="frl_team_stats_start")
    end_options = [value for value in seasons if _season_key(value) >= _season_key(start)]
    end = st.selectbox("To", end_options, index=len(end_options) - 1, key="frl_team_stats_end")

    requested = [value for value in seasons if _season_key(start) <= _season_key(value) <= _season_key(end)]
    comparison = query_api.team_compare(team=team, seasons=requested)

    st.markdown("<div class='frl-team-section'>Season record</div>", unsafe_allow_html=True)

    season_rows = comparison.get("seasons", [])
    if not season_rows:
        st.info("No verified team seasons exist in the selected range.")
        return

    table_rows = []
    for row in season_rows:
        table_rows.append(
            {
                "Season": row.get("season"),
                "Pos": row.get("position", "—"),
                "Played": row.get("played", "—"),
                "W": row.get("wins", 0),
                "D": row.get("draws", 0),
                "L": row.get("losses", 0),
                "GF": row.get("goals_for", 0),
                "GA": row.get("goals_against", 0),
                "GD": row.get("goal_difference", 0),
                "Pts": row.get("points", 0),
            }
        )

    import pandas as pd
    st.dataframe(
        pd.DataFrame(table_rows),
        hide_index=True,
        use_container_width=True,
    )

    st.markdown("<div class='frl-team-section'>Research notes</div>", unsafe_allow_html=True)
    skipped = comparison.get("skipped_seasons", [])
    if skipped:
        st.caption("The selected range includes seasons where the club was not in the Premier League; those seasons are retained as explicit exclusions rather than treated as missing data.")
    else:
        st.caption("Every selected season resolved to the same verified persistent club identity.")

    totals = {
        "Seasons represented": len(season_rows),
        "Total points": sum(int(row.get("points", 0)) for row in season_rows),
        "Goals for": sum(int(row.get("goals_for", 0)) for row in season_rows),
        "Goals against": sum(int(row.get("goals_against", 0)) for row in season_rows),
    }
    cols = st.columns(4, gap="small")
    for col, (label, value) in zip(cols, totals.items()):
        with col:
            st.markdown(
                "<div class='frl-team-mini-card'>"
                f"<div class='frl-team-mini-label'>{label}</div>"
                f"<div class='frl-team-mini-value'>{_fmt_int(value)}</div>"
                "</div>",
                unsafe_allow_html=True,
            )


def render_team_workspace() -> None:
    seasons = sorted(query_api.available_seasons(), key=_season_key, reverse=True)
    if not seasons:
        st.error("No team seasons are available.")
        return

    season = st.selectbox("Season", seasons, index=0, key="frl_team_workspace_season")
    league = query_api.league_table(season)
    teams = [row.get("team") for row in league.get("teams", []) if row.get("team")]
    if not teams:
        st.error("No verified teams are available for this season.")
        return

    selected = st.session_state.get("frl_team_workspace_team", teams[0])
    if selected not in teams:
        selected = teams[0]

    selected = st.selectbox("Team", teams, index=teams.index(selected), key="frl_team_workspace_team")

    st.markdown(
        """
        <style>
        .frl-team-title { color:var(--frl-text); font-size:clamp(2rem,3.7vw,3.25rem); font-weight:820; line-height:.95; letter-spacing:-.05em; margin-top:.15rem; }
        .frl-team-stat-card { min-height:88px; padding:.78rem .85rem; border:1px solid var(--frl-border); border-radius:12px; background:transparent; }
        .frl-team-stat-label,.frl-team-mini-label { color:var(--frl-muted-soft); font-size:.57rem; font-weight:800; letter-spacing:.11em; text-transform:uppercase; }
        .frl-team-stat-value { margin-top:.34rem; color:var(--frl-text); font-size:1.32rem; font-weight:820; letter-spacing:-.03em; }
        .frl-team-section { margin-top:1.15rem; margin-bottom:.48rem; color:var(--frl-accent); font-size:.61rem; font-weight:820; letter-spacing:.14em; text-transform:uppercase; }
        .frl-team-form-strip { display:grid; grid-template-columns:80px 1fr auto; gap:.75rem; align-items:center; padding:.8rem .9rem; border-top:1px solid var(--frl-border); border-bottom:1px solid var(--frl-border); }
        .frl-team-form-label { color:var(--frl-muted-soft); font-size:.56rem; font-weight:800; letter-spacing:.10em; text-transform:uppercase; }
        .frl-team-form-results { color:var(--frl-text); font-size:.86rem; font-weight:760; letter-spacing:.04em; }
        .frl-team-form-meta { color:var(--frl-muted); font-size:.66rem; }
        .frl-team-mini-card { padding:.72rem .78rem; border:1px solid var(--frl-border); border-radius:10px; background:transparent; }
        .frl-team-mini-value { margin-top:.24rem; color:var(--frl-text); font-size:1.02rem; font-weight:800; }
        .frl-team-fixture-row { display:grid; grid-template-columns:76px 28px minmax(120px,1fr) 68px 36px; gap:.55rem; align-items:center; padding:.63rem 0; border-bottom:1px solid var(--frl-border); }
        .frl-team-fixture-date,.frl-team-fixture-venue { color:var(--frl-muted-soft); font-size:.62rem; }
        .frl-team-fixture-opponent { color:var(--frl-text); font-size:.76rem; font-weight:720; }
        .frl-team-fixture-score { color:var(--frl-text); font-size:.74rem; font-weight:800; text-align:right; }
        .frl-team-fixture-result { font-size:.62rem; font-weight:850; text-align:right; }
        .frl-result-w { color:#3f7b55; } .frl-result-d { color:var(--frl-muted); } .frl-result-l { color:var(--frl-accent); }
        @media (max-width: 900px) { .frl-team-form-strip { grid-template-columns:1fr; gap:.2rem; } .frl-team-fixture-row { grid-template-columns:62px 24px 1fr 58px 28px; } }
        </style>
        """,
        unsafe_allow_html=True,
    )

    view = st.radio("Team view", ["Profile", "Stats"], horizontal=True, key="frl_team_workspace_view")
    if view == "Profile":
        _render_profile(season, selected)
    else:
        _render_stats(season, selected)
