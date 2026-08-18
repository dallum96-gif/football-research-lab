from __future__ import annotations

import html

import altair as alt
import streamlit as st

import gui.team_research_ui_v7 as base
from team_research_stats import team_season_stats_by_name


def _fmt(value, digits: int = 2, suffix: str = "") -> str:
    try:
        n = float(value)
    except (TypeError, ValueError):
        return "—"
    if digits == 0:
        return f"{int(round(n)):,}{suffix}"
    return f"{n:.{digits}f}{suffix}"


def _bar_chart(items: list[tuple[str, float | None]], title: str) -> None:
    values = [
        {"metric": label, "value": float(value)}
        for label, value in items
        if value is not None
    ]
    if not values:
        st.info(f"{title} is not available for this season.")
        return
    chart = (
        alt.Chart(alt.Data(values=values))
        .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
        .encode(
            x=alt.X("metric:N", title=None, axis=alt.Axis(labelAngle=0, labelColor="#68645c", labelFontSize=10, domain=False, tickColor="transparent")),
            y=alt.Y("value:Q", title=None, scale=alt.Scale(zero=True, nice=True), axis=alt.Axis(labelColor="#68645c", labelFontSize=10, gridColor="#d9d3c8", gridOpacity=.45, domain=False)),
            tooltip=[alt.Tooltip("metric:N", title="Metric"), alt.Tooltip("value:Q", title=title, format=".1f")],
        )
        .properties(height=190, background="#fffdf8")
    )
    st.altair_chart(chart, width="stretch")


def _stats(team: str, season: str, summary: dict, rows: list[dict]) -> None:
    data = summary.get("summary", {})
    ppg = base._per_game(summary, "points")
    gf = base._per_game(summary, "goals_for")
    ga = base._per_game(summary, "goals_against")
    wins = int(data.get("wins", 0) or 0)
    draws = int(data.get("draws", 0) or 0)
    losses = int(data.get("losses", 0) or 0)
    played = int(data.get("played", 0) or 0)
    win_rate = wins / played * 100 if played else 0

    match_stats = team_season_stats_by_name(season, team)

    st.markdown("<div class='frl-team7-kicker'>Team intelligence</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-team7-title'>{html.escape(team)} · stats</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-team7-context'>{season} · team-level numbers, split into simple questions</div>", unsafe_allow_html=True)

    overview, attack, defence, results = st.tabs(["Overview", "Attack", "Defence", "Results"])

    with overview:
        cols = st.columns(4, gap="small")
        with cols[0]: base._tile("PPG", _fmt(ppg, 2), season, "accent")
        with cols[1]: base._tile("GF / match", _fmt(gf, 2), "attacking output", "green")
        with cols[2]: base._tile("GA / match", _fmt(ga, 2), "defensive output", "warm")
        with cols[3]: base._tile("Win rate", _fmt(win_rate, 0, "%"), season)

        st.markdown("<div class='frl-team7-label'>How they play</div>", unsafe_allow_html=True)
        if match_stats.get("status") == "AVAILABLE":
            cols = st.columns(5, gap="small")
            with cols[0]: base._tile("Possession", _fmt(match_stats.get("Possession_per_match"), 1, "%"), "average share", "accent")
            with cols[1]: base._tile("Shots", _fmt(match_stats.get("Shots_per_match"), 1), "per match", "green")
            with cols[2]: base._tile("On target", _fmt(match_stats.get("Shots on target_per_match"), 1), "per match")
            with cols[3]: base._tile("xG", _fmt(match_stats.get("Expected goals_per_match"), 2), "expected goals / match", "warm")
            with cols[4]: base._tile("Pass accuracy", _fmt((match_stats.get("pass_accuracy") or 0) * 100, 1, "%"), "completed / attempted", "accent")

            st.markdown("<div class='frl-team7-label'>Statistical fingerprint</div>", unsafe_allow_html=True)
            _bar_chart(
                [
                    ("Shots", match_stats.get("Shots_per_match")),
                    ("On target", match_stats.get("Shots on target_per_match")),
                    ("Corners", match_stats.get("Corners_per_match")),
                    ("Big chances", match_stats.get("Big chances created_per_match")),
                ],
                "Per match",
            )
        else:
            st.info("Packaged match statistics are not available for this team/season yet.")

        st.markdown("<div class='frl-team7-label'>Recent season benchmark</div>", unsafe_allow_html=True)
        base._history_chart(rows[-5:], "points_per_match", "PPG")

    with attack:
        if match_stats.get("status") != "AVAILABLE":
            st.info("Attack statistics are not available for this team/season yet.")
            return
        xg = match_stats.get("Expected goals_per_match")
        xa = match_stats.get("Expected assists_per_match")
        shots = match_stats.get("Shots_per_match")
        sot = match_stats.get("Shots on target_per_match")
        big_created = match_stats.get("Big chances created_per_match")
        big_missed = match_stats.get("Big chances missed_per_match")
        corners = match_stats.get("Corners_per_match")
        conversion = match_stats.get("goals_per_shot")

        cols = st.columns(5, gap="small")
        with cols[0]: base._tile("xG", _fmt(xg, 2), "per match", "accent")
        with cols[1]: base._tile("Shots", _fmt(shots, 1), "per match", "green")
        with cols[2]: base._tile("On target", _fmt(sot, 1), "per match")
        with cols[3]: base._tile("Big chances", _fmt(big_created, 1), "created / match", "warm")
        with cols[4]: base._tile("Conversion", _fmt((conversion or 0) * 100, 1, "%"), "goals per shot", "accent")

        st.markdown("<div class='frl-team7-label'>Chance creation</div>", unsafe_allow_html=True)
        _bar_chart(
            [("xG", xg), ("Shots", shots), ("On target", sot), ("Corners", corners)],
            "Attack output",
        )

        c1, c2, c3 = st.columns(3, gap="small")
        with c1: base._tile("xA", _fmt(xa, 2), "expected assists / match")
        with c2: base._tile("Big chances missed", _fmt(big_missed, 1), "per match", "warm")
        with c3: base._tile("xG vs goals", _fmt(match_stats.get("xg_overperformance"), 2), "season difference", "green" if (match_stats.get("xg_overperformance") or 0) >= 0 else "accent")

    with defence:
        if match_stats.get("status") != "AVAILABLE":
            st.info("Defensive statistics are not available for this team/season yet.")
            return
        cols = st.columns(5, gap="small")
        with cols[0]: base._tile("GA / match", _fmt(ga, 2), "scoreline output", "warm")
        with cols[1]: base._tile("Tackles", _fmt(match_stats.get("Tackles_per_match"), 1), "per match", "green")
        with cols[2]: base._tile("Interceptions", _fmt(match_stats.get("Interceptions_per_match"), 1), "per match")
        with cols[3]: base._tile("Clearances", _fmt(match_stats.get("Clearances_per_match"), 1), "per match", "warm")
        with cols[4]: base._tile("Clean sheets", str(int(match_stats.get("clean_sheets", data.get("clean_sheets", 0)) or 0)), season, "accent")

        st.markdown("<div class='frl-team7-label'>Defensive activity</div>", unsafe_allow_html=True)
        _bar_chart(
            [("Tackles", match_stats.get("Tackles_per_match")), ("Interceptions", match_stats.get("Interceptions_per_match")), ("Clearances", match_stats.get("Clearances_per_match")), ("Blocks", match_stats.get("Blocked shots_per_match"))],
            "Defensive actions",
        )

        c1, c2, c3 = st.columns(3, gap="small")
        with c1: base._tile("Fouls committed", _fmt(match_stats.get("Fouls conceded_per_match"), 1), "per match")
        with c2: base._tile("Yellow cards", _fmt(match_stats.get("Yellow cards_per_match"), 1), "per match", "warm")
        with c3: base._tile("Red cards", _fmt(match_stats.get("Red cards_per_match"), 2), "per match", "accent")

    with results:
        cols = st.columns(4, gap="small")
        with cols[0]: base._tile("Wins", str(wins), season, "green")
        with cols[1]: base._tile("Draws", str(draws), season)
        with cols[2]: base._tile("Losses", str(losses), season, "warm")
        with cols[3]: base._tile("Points", _fmt(data.get("points"), 0), "current season", "accent")

        if match_stats.get("status") == "AVAILABLE":
            st.markdown("<div class='frl-team7-label'>Results + efficiency</div>", unsafe_allow_html=True)
            cols = st.columns(4, gap="small")
            with cols[0]: base._tile("Clean-sheet rate", _fmt((match_stats.get("clean_sheet_rate") or 0) * 100, 1, "%"), "of matches", "green")
            with cols[1]: base._tile("Failed to score", _fmt((match_stats.get("failed_to_score_rate") or 0) * 100, 1, "%"), "of matches", "warm")
            with cols[2]: base._tile("Home matches", str(int(match_stats.get("home_matches", 0))), season)
            with cols[3]: base._tile("Away matches", str(int(match_stats.get("away_matches", 0))), season)

        st.markdown("<div class='frl-team7-label'>Season record</div>", unsafe_allow_html=True)
        base._history_table(rows)


def render_team_research_ui():
    base._stats = _stats
    return base.render_team_research_ui()
