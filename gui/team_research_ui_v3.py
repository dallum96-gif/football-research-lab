from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import altair as alt
import streamlit as st

import query_api
from team_research_analytics import team_performance_profile

FRL_SURFACE = "#fffdf8"
FRL_BORDER = "#d9d4c8"
FRL_GRID = "#dfdbd1"
FRL_TEXT = "#171714"
FRL_MUTED = "#68645c"
FRL_SOFT = "#9a968d"
FRL_ACCENT = "#e85d3f"
FRL_GREEN = "#9aaa42"


def _season_key(value: str) -> tuple[int, int]:
    try:
        a, b = value.split("-", 1)
        return int(a), int(b)
    except (TypeError, ValueError):
        return (0, 0)


def _num(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _fmt(value: Any, digits: int = 2) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "—"


def _fmt_int(value: Any) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "—"


def _fmt_signed(value: Any) -> str:
    try:
        return f"{int(value):+,}"
    except (TypeError, ValueError):
        return "—"


@st.cache_data(show_spinner=False)
def _seasons():
    return sorted(query_api.list_seasons(), key=_season_key, reverse=True)


@st.cache_data(show_spinner=False)
def _league_table(season: str):
    return query_api.league_table(season=season)


@st.cache_data(show_spinner=False)
def _summary(season: str, team: str):
    return query_api.team_summary(season=season, team=team)


@st.cache_data(show_spinner=False)
def _fixtures(season: str, team: str):
    return query_api.fixtures(season=season, team=team, limit=100)


@st.cache_data(show_spinner=False)
def _profile(season: str, team: str):
    return team_performance_profile(season=season, team=team, rolling_window=5)


def _css():
    st.markdown(
        """
        <style>
        .frl-team-kicker{color:var(--frl-accent);font-size:.60rem;font-weight:850;letter-spacing:.16em;text-transform:uppercase;margin-bottom:.34rem}
        .frl-team-title{color:var(--frl-text);font-size:2.15rem;font-weight:820;line-height:1.02;letter-spacing:-.04em;margin:0}
        .frl-team-context{color:var(--frl-muted);font-size:.76rem;margin-top:.24rem}
        .frl-team-headline{color:var(--frl-text);font-size:1.02rem;line-height:1.42;font-weight:620;margin:.85rem 0 1rem;max-width:66rem}
        .frl-team-headline strong{color:var(--frl-accent);font-weight:820}
        .frl-team-metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));border-top:1px solid var(--frl-border);border-bottom:1px solid var(--frl-border);margin:.85rem 0 1rem}
        .frl-team-metric{padding:.72rem .78rem .70rem 0;border-right:1px solid var(--frl-border)}
        .frl-team-metric:last-child{border-right:0}
        .frl-team-metric-label{color:var(--frl-soft);font-size:.51rem;font-weight:820;letter-spacing:.11em;text-transform:uppercase}
        .frl-team-metric-value{color:var(--frl-text);font-size:1.18rem;font-weight:800;margin-top:.10rem}
        .frl-team-metric-sub{color:var(--frl-muted);font-size:.56rem;margin-top:.06rem}
        .frl-team-toolbar-label{color:var(--frl-soft);font-size:.55rem;font-weight:820;letter-spacing:.10em;text-transform:uppercase;margin:.85rem 0 .24rem}
        .frl-team-tab button{background:transparent!important;border:0!important;border-bottom:2px solid transparent!important;border-radius:0!important;color:var(--frl-muted)!important;min-height:1.9rem!important;padding:.05rem .16rem!important;font-size:.66rem!important;font-weight:780!important;box-shadow:none!important}
        .frl-team-tab.active button{color:var(--frl-text)!important;border-bottom-color:var(--frl-accent)!important}
        .frl-team-tab button:hover{color:var(--frl-text)!important;background:transparent!important}
        .frl-team-section{color:var(--frl-soft);font-size:.56rem;font-weight:820;letter-spacing:.12em;text-transform:uppercase;margin:1.15rem 0 .42rem}
        .frl-team-table{border-top:1px solid var(--frl-border);border-bottom:1px solid var(--frl-border)}
        .frl-team-row{display:grid;grid-template-columns:8rem minmax(0,1fr) 5.5rem;gap:.8rem;align-items:center;padding:.58rem 0;border-bottom:1px solid var(--frl-border)}
        .frl-team-row:last-child{border-bottom:0}
        .frl-team-label{color:var(--frl-text);font-size:.70rem;font-weight:720}
        .frl-team-desc{color:var(--frl-muted);font-size:.59rem}
        .frl-team-value{text-align:right;color:var(--frl-text);font-size:.78rem;font-weight:820}
        .frl-team-form{display:flex;gap:.30rem;flex-wrap:wrap;margin:.28rem 0 .35rem}
        .frl-form-pill{min-width:1.9rem;height:1.9rem;padding:0 .40rem;border:1px solid var(--frl-border);border-radius:3px;display:flex;align-items:center;justify-content:center;font-size:.60rem;font-weight:850;color:var(--frl-muted)}
        .frl-form-pill.win{color:var(--frl-green);border-color:rgba(154,170,66,.48)}
        .frl-form-pill.loss{color:var(--frl-accent);border-color:rgba(232,93,63,.40)}
        @media(max-width:900px){.frl-team-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _tabs(label: str, options: list[str], key: str, default: str) -> str:
    st.markdown(f"<div class='frl-team-toolbar-label'>{label}</div>", unsafe_allow_html=True)
    current = st.session_state.get(key, default)
    cols = st.columns(len(options), gap="small")
    for col, option in zip(cols, options):
        with col:
            active = current == option
            st.markdown(f"<div class='frl-team-tab{' active' if active else ''}'>", unsafe_allow_html=True)
            if st.button(option, key=f"{key}_{option}", width="stretch", type="tertiary"):
                st.session_state[key] = option
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    return current


def _cards(summary: dict):
    s = summary.get("summary", {})
    played = max(_num(s.get("played")), 1)
    cells = [
        ("POINTS", _fmt_int(s.get("points")), f"{_fmt(_num(s.get('points')) / played)} PPG"),
        ("RECORD", f"{_fmt_int(s.get('wins'))}–{_fmt_int(s.get('draws'))}–{_fmt_int(s.get('losses'))}", f"{_fmt_int(s.get('played'))} played"),
        ("GOALS", f"{_fmt_int(s.get('goals_for'))}–{_fmt_int(s.get('goals_against'))}", "for / against"),
        ("GOAL DIFF", _fmt_signed(s.get("goal_difference")), "season total"),
    ]
    html = "<div class='frl-team-metrics'>" + "".join(
        f"<div class='frl-team-metric'><div class='frl-team-metric-label'>{a}</div><div class='frl-team-metric-value'>{b}</div><div class='frl-team-metric-sub'>{c}</div></div>"
        for a, b, c in cells
    ) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


def _profile_chart(profile, metric: str):
    values = []
    for i, row in enumerate(profile.rows, 1):
        raw = row.get("kickoff_time")
        try:
            dt = raw if isinstance(raw, datetime) else datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            dt = dt.astimezone(timezone.utc)
        except (TypeError, ValueError):
            continue
        if metric == "PPG":
            value, baseline, label = row.get("rolling_ppg"), row.get("cumulative_ppg"), "Rolling PPG"
        elif metric == "Attack":
            value, baseline, label = row.get("rolling_goals_for_per_match"), _num(row.get("goals_for")) / i, "Goals scored / match"
        else:
            value, baseline, label = row.get("rolling_goals_against_per_match"), _num(row.get("goals_against")) / i, "Goals conceded / match"
        if value is None:
            continue
        values.append({"date": dt, "value": float(value), "baseline": float(baseline), "opponent": row.get("opponent"), "result": row.get("result"), "match": i, "label": label})
    if not values:
        raise ValueError("No completed fixture values are available for the profile chart.")
    base = alt.Chart(alt.Data(values=values)).encode(
        x=alt.X("date:T", title=None, axis=alt.Axis(format="%b", tickCount=8, labelPadding=7)),
        y=alt.Y("value:Q", title=None, scale=alt.Scale(zero=False, nice=True)),
        tooltip=[alt.Tooltip("date:T", title="Date", format="%d %b %Y"), alt.Tooltip("opponent:N", title="Opponent"), alt.Tooltip("result:N", title="Result"), alt.Tooltip("value:Q", title="Trend", format=".2f"), alt.Tooltip("baseline:Q", title="Season baseline", format=".2f"), alt.Tooltip("match:Q", title="Match")],
    )
    chart = alt.layer(
        base.mark_line(color=FRL_SOFT, strokeDash=[5, 5], strokeWidth=1.0).encode(y=alt.Y("baseline:Q")),
        base.mark_line(color=FRL_ACCENT, strokeWidth=2.5),
        base.mark_point(color=FRL_ACCENT, filled=True, size=50, stroke=FRL_SURFACE, strokeWidth=1.3),
    ).properties(height=320, background=FRL_SURFACE, padding={"left": 4, "right": 12, "top": 8, "bottom": 4})
    return chart.configure_view(stroke=FRL_BORDER, strokeWidth=1).configure_axis(labelColor=FRL_MUTED, domainColor=FRL_BORDER, tickColor=FRL_BORDER, gridColor=FRL_GRID, gridOpacity=.55, labelFont="Arial", titleFont="Arial", labelFontSize=11)


def _profile_view(profile, summary, fixtures):
    _cards(summary)
    rows = list(profile.rows)
    overall = profile.population.get("overall", {})
    latest = _num(rows[-1].get("rolling_ppg")) if rows else 0
    headline = f"Latest five-match form: <strong>{_fmt(latest)} PPG</strong> · season baseline {_fmt(overall.get('ppg'))}."
    st.markdown(f"<div class='frl-team-headline'>{headline}</div>", unsafe_allow_html=True)
    metric = _tabs("Season story", ["PPG", "Attack", "Defence"], "frl_team_profile_metric_v3", "PPG")
    st.markdown("<div class='frl-team-section'>Trend through the season</div>", unsafe_allow_html=True)
    try:
        st.altair_chart(_profile_chart(profile, metric), width="stretch")
    except ValueError as exc:
        st.warning(str(exc))
    window = _tabs("Recent matches", ["5", "10"], "frl_team_recent_v3", "5")
    n = 10 if window == "10" else 5
    recent = list(fixtures.get("results", []))[-n:]
    team = summary.get("team") or summary.get("canonical_name") or ""
    pills = []
    for row in reversed(recent):
        if row.get("home_score") in (None, "") or row.get("away_score") in (None, ""):
            result = "—"; klass = ""
        elif team and row.get("home_team_name") == team:
            result = "W" if _num(row.get("home_score")) > _num(row.get("away_score")) else "L" if _num(row.get("home_score")) < _num(row.get("away_score")) else "D"; klass = result.lower()
        elif team and row.get("away_team_name") == team:
            result = "W" if _num(row.get("away_score")) > _num(row.get("home_score")) else "L" if _num(row.get("away_score")) < _num(row.get("home_score")) else "D"; klass = result.lower()
        else:
            result = "•"; klass = ""
        pills.append(f"<span class='frl-form-pill {klass}'>{result}</span>")
    st.markdown("<div class='frl-team-form'>" + "".join(pills) + "</div>", unsafe_allow_html=True)


def _stats_view(profile, summary):
    tab = _tabs("Team snapshot", ["Overview", "Attack", "Defence", "Results"], "frl_team_stats_tab_v3", "Overview")
    _cards(summary)
    o = profile.population.get("overall", {})
    if tab in {"Overview", "Results"}:
        rows = [("Points per match", _fmt(o.get("ppg")), "season average"), ("Win rate", _fmt(_num(o.get("win_rate"))*100, 1)+"%", "matches won"), ("Points", _fmt_int(o.get("points")), "season total"), ("Record", f"{_fmt_int(o.get('wins'))}–{_fmt_int(o.get('matches', 0)-o.get('wins', 0))}", "wins / non-wins")]
    elif tab == "Attack":
        rows = [("Goals scored / match", _fmt(o.get("goals_per_match")), "season scoring rate"), ("Goals scored", _fmt_int(o.get("goals_for")), "season total"), ("Failed to score", _fmt(_num(o.get("failed_to_score_rate"))*100,1)+"%", "share of matches"), ("Goal difference / match", _fmt(o.get("goal_difference_per_match")), "net output")]
    else:
        rows = [("Goals conceded / match", _fmt(o.get("goals_against_per_match")), "season defensive rate"), ("Clean sheet rate", _fmt(_num(o.get("clean_sheet_rate"))*100,1)+"%", "share of matches"), ("Goals conceded", _fmt_int(o.get("goals_against")), "season total"), ("Failed to score rate", _fmt(_num(o.get("failed_to_score_rate"))*100,1)+"%", "matches without a goal")]
    st.markdown("<div class='frl-team-section'>Snapshot</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-team-table'>" + "".join(f"<div class='frl-team-row'><div class='frl-team-label'>{a}</div><div class='frl-team-desc'>{c}</div><div class='frl-team-value'>{b}</div></div>" for a,b,c in rows) + "</div>", unsafe_allow_html=True)
    context = _tabs("Context", ["Home / Away", "Season phases"], "frl_team_stats_context_v3", "Home / Away")
    splits = profile.population.get("venue_splits", []) if context == "Home / Away" else profile.population.get("phase_splits", [])
    st.markdown("<div class='frl-team-section'>Context</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-team-table'>" + "".join(f"<div class='frl-team-row'><div class='frl-team-label'>{r.get('label')}</div><div class='frl-team-desc'>{r.get('matches')} matches · {r.get('wins')} wins</div><div class='frl-team-value'>{_fmt(r.get('ppg'))} PPG</div></div>" for r in splits if r.get('matches')) + "</div>", unsafe_allow_html=True)


def render_team_research_ui():
    _css()
    seasons = _seasons()
    if not seasons:
        st.error("No verified team seasons are available.")
        return
    route = "Stats" if st.query_params.get("workspace") == "team-stats" else "Profile"
    season = st.selectbox("Season", seasons, index=0, key=f"frl_team_season_v3_{route}")
    teams = [r.get("team") for r in _league_table(season).get("teams", []) if r.get("team")]
    if not teams:
        st.info("No teams are available for this season.")
        return
    team = st.selectbox("Team", teams, index=0, key=f"frl_selected_team_v3_{route}")
    st.markdown("<div class='frl-team-kicker'>Team research</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-team-title'>{team}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-team-context'>{season} · verified team identity · {route.lower()} workspace</div>", unsafe_allow_html=True)
    profile = _profile(season, team)
    summary = _summary(season, team)
    if route == "Stats":
        _stats_view(profile, summary)
    else:
        _profile_view(profile, summary, _fixtures(season, team))
