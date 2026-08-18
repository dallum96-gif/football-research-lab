from __future__ import annotations

import html

import altair as alt
import streamlit as st

import query_api
from team_research_analytics import team_performance_profile, team_season_comparison


def _season_key(value: str) -> tuple[int, int]:
    try:
        left, right = value.split("-", 1)
        return int(left), int(right)
    except (TypeError, ValueError):
        return (0, 0)


def _num(value, digits: int = 2):
    try:
        return round(float(value), digits)
    except (TypeError, ValueError):
        return None


def _fmt(value, digits: int = 2, signed: bool = False) -> str:
    try:
        n = float(value)
    except (TypeError, ValueError):
        return "—"
    if digits == 0:
        return f"{int(round(n)):+,}" if signed else f"{int(round(n)):,}"
    return f"{n:+.{digits}f}" if signed else f"{n:.{digits}f}"


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
def _comparison(team: str, seasons: tuple[str, ...]):
    return team_season_comparison(team=team, seasons=list(seasons))


@st.cache_data(show_spinner=False)
def _profile(season: str, team: str):
    return team_performance_profile(season=season, team=team, rolling_window=5)


def _css() -> None:
    st.markdown(
        """
        <style>
        .frl-team-v5-kicker{color:var(--frl-accent);font-size:.62rem;font-weight:800;letter-spacing:.15em;text-transform:uppercase;margin-bottom:.35rem}
        .frl-team-v5-title{color:var(--frl-text);font-size:2.35rem;font-weight:800;letter-spacing:-.045em;line-height:1.0;margin:0}
        .frl-team-v5-context{color:var(--frl-muted);font-size:.84rem;margin-top:.3rem}
        .frl-team-v5-rule{height:2px;background:var(--frl-text);margin:1.55rem 0 .95rem;opacity:.92}
        .frl-team-v5-label{color:var(--frl-accent);font-size:.62rem;font-weight:800;letter-spacing:.15em;text-transform:uppercase;margin-bottom:.58rem}
        .frl-team-v5-tile{border-top:2px solid var(--frl-text);border-bottom:1px solid var(--frl-border);padding:.86rem .05rem .74rem;min-height:5.8rem}
        .frl-team-v5-tile-label{color:var(--frl-muted-soft);font-size:.59rem;font-weight:800;letter-spacing:.11em;text-transform:uppercase}
        .frl-team-v5-tile-value{color:var(--frl-text);font-size:1.45rem;font-weight:800;letter-spacing:-.025em;line-height:1;margin-top:.35rem}
        .frl-team-v5-tile-copy{color:var(--frl-muted);font-size:.69rem;line-height:1.35;margin-top:.34rem}
        .frl-team-v5-table{width:100%;border-top:1px solid var(--frl-border-strong)}
        .frl-team-v5-row{display:grid;grid-template-columns:1.05fr 1.2fr .8fr .85fr .8fr;gap:.55rem;align-items:center;padding:.56rem .05rem;border-bottom:1px solid var(--frl-border);font-size:.69rem}
        .frl-team-v5-row.head{color:var(--frl-muted-soft);font-size:.56rem;font-weight:800;letter-spacing:.09em;text-transform:uppercase}
        .frl-team-v5-row .main{color:var(--frl-text);font-weight:700}
        .frl-team-v5-row .muted{color:var(--frl-muted)}
        .frl-team-v5-row .right{text-align:right;color:var(--frl-text);font-weight:760}
        .frl-team-v5-note{color:var(--frl-muted-soft);font-size:.61rem;line-height:1.45;margin-top:.55rem}
        @media(max-width:900px){.frl-team-v5-row{grid-template-columns:1fr 1.25fr .72fr .8fr .75fr}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _tile(label: str, value: str, copy: str = "") -> None:
    st.markdown(
        f"<div class='frl-team-v5-tile'><div class='frl-team-v5-tile-label'>{html.escape(label)}</div>"
        f"<div class='frl-team-v5-tile-value'>{html.escape(value)}</div>"
        f"<div class='frl-team-v5-tile-copy'>{html.escape(copy)}</div></div>",
        unsafe_allow_html=True,
    )


def _season_chart(rows: list[dict]) -> None:
    if not rows:
        st.info("No verified historical seasons are available for this team.")
        return

    values = []
    for row in rows:
        season = row.get("season")
        ppg = _num(row.get("points_per_match"), 3)
        if season and ppg is not None:
            values.append({"season": season, "ppg": ppg})
    if not values:
        st.info("PPG history is not available for this selection.")
        return

    chart = (
        alt.Chart(alt.Data(values=values))
        .mark_line(point=alt.OverlayMarkDef(filled=True, size=56), strokeWidth=2.5)
        .encode(
            x=alt.X("season:N", title=None, sort=[v["season"] for v in values], axis=alt.Axis(labelAngle=0, labelColor="#68645c", labelFontSize=11, domainColor="#c9c3b7", tickColor="#c9c3b7")),
            y=alt.Y("ppg:Q", title="PPG", scale=alt.Scale(zero=False, nice=True), axis=alt.Axis(labelColor="#68645c", labelFontSize=11, gridColor="#d9d3c8", gridOpacity=.6, domain=False)),
            tooltip=[alt.Tooltip("season:N", title="Season"), alt.Tooltip("ppg:Q", title="PPG", format=".2f")],
        )
        .properties(height=255, background="#fffdf8")
    )
    st.altair_chart(chart, width="stretch")


def _history_table(rows: list[dict]) -> None:
    body = [
        "<div class='frl-team-v5-table'>",
        "<div class='frl-team-v5-row head'><div>Season</div><div>Record</div><div>Points</div><div>PPG</div><div>GF / GA</div></div>",
    ]
    for row in reversed(rows):
        body.append(
            f"<div class='frl-team-v5-row'>"
            f"<div class='main'>{html.escape(str(row.get('season','')))}</div>"
            f"<div class='muted'>{row.get('wins',0)}W · {row.get('draws',0)}D · {row.get('losses',0)}L</div>"
            f"<div class='right'>{row.get('points','—')}</div>"
            f"<div class='right'>{_fmt(row.get('points_per_match'),2)}</div>"
            f"<div class='right'>{_fmt(row.get('goals_for_per_match'),2)} / {_fmt(row.get('goals_against_per_match'),2)}</div>"
            f"</div>"
        )
    body.append("</div>")
    st.markdown("".join(body), unsafe_allow_html=True)


def _profile_page(team: str, season: str, summary: dict, form: dict) -> None:
    comparison = _comparison(team, tuple(_seasons()[:10]))
    rows = list(comparison.rows)
    current = summary.get("summary", {})

    st.markdown("<div class='frl-team-v5-label'>Club profile</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-team-v5-title'>{html.escape(team)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-team-v5-context'>Historical performance, recent direction and the shape of the club across seasons.</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-team-v5-rule'></div>", unsafe_allow_html=True)

    season_cols = st.columns(4, gap="small")
    with season_cols[0]: _tile("Points", _fmt(current.get("points"),0), season)
    with season_cols[1]: _tile("PPG", _fmt(current.get("points_per_match"),2), season)
    with season_cols[2]: _tile("Goals / match", _fmt(current.get("goals_for_per_match"),2), season)
    with season_cols[3]: _tile("Goals against", _fmt(current.get("goals_against_per_match"),2), season)

    st.markdown("<div class='frl-team-v5-label' style='margin-top:1.65rem'>Historical arc</div>", unsafe_allow_html=True)
    tab5, tab10 = st.tabs(["Last 5", "Last 10"])
    for tab, window in ((tab5,5),(tab10,10)):
        with tab:
            subset = rows[-window:]
            st.caption(f"Points-per-match journey across the last {window} completed seasons.")
            _season_chart(subset)
            _history_table(subset)

    recent = form.get("windows", {}).get("5", {})
    st.markdown("<div class='frl-team-v5-label' style='margin-top:1.65rem'>Recent direction</div>", unsafe_allow_html=True)
    cols = st.columns(3, gap="small")
    with cols[0]: _tile("Last 5", str(recent.get("points",0)), "points won")
    with cols[1]: _tile("Goals", str(recent.get("goals_for",0)), "scored in last five")
    with cols[2]: _tile("Conceded", str(recent.get("goals_against",0)), "in last five")


def _stats_page(team: str, season: str, summary: dict) -> None:
    current = summary.get("summary", {})
    comparison = _comparison(team, tuple(_seasons()[:10]))
    rows = list(comparison.rows)
    if not rows:
        st.info("No verified season records are available for this team.")
        return

    st.markdown("<div class='frl-team-v5-label'>Team intelligence</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-team-v5-title'>{html.escape(team)} · stats</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-team-v5-context'>A compact statistical snapshot of the team. Switch perspective instead of building a dashboard.</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-team-v5-rule'></div>", unsafe_allow_html=True)

    overview, attack, defence, results = st.tabs(["Overview", "Attack", "Defence", "Results"])

    with overview:
        cols = st.columns(4, gap="small")
        with cols[0]: _tile("PPG", _fmt(current.get("points_per_match"),2), season)
        with cols[1]: _tile("Points", _fmt(current.get("points"),0), season)
        with cols[2]: _tile("GF / match", _fmt(current.get("goals_for_per_match"),2), season)
        with cols[3]: _tile("GA / match", _fmt(current.get("goals_against_per_match"),2), season)
        st.markdown("<div class='frl-team-v5-label' style='margin-top:1.45rem'>Across selected history</div>", unsafe_allow_html=True)
        avg_ppg = sum(_num(r.get("points_per_match"),3) or 0 for r in rows) / len(rows)
        best_ppg = max(rows, key=lambda r: _num(r.get("points_per_match"),3) or -1)
        consistency = sum(1 for r in rows if (_num(r.get("points_per_match"),3) or 0) >= 2.0)
        cols = st.columns(3, gap="small")
        with cols[0]: _tile("10-season avg", _fmt(avg_ppg,2), "PPG")
        with cols[1]: _tile("Best season", _fmt(best_ppg.get("points_per_match"),2), str(best_ppg.get("season","")))
        with cols[2]: _tile("2.0+ PPG", str(consistency), f"of {len(rows)} seasons")

    with attack:
        best = max(rows, key=lambda r: _num(r.get("goals_for_per_match"),3) or -1)
        avg = sum(_num(r.get("goals_for_per_match"),3) or 0 for r in rows) / len(rows)
        cols = st.columns(3, gap="small")
        with cols[0]: _tile("Current", _fmt(current.get("goals_for_per_match"),2), "goals per match")
        with cols[1]: _tile("10-season avg", _fmt(avg,2), "goals per match")
        with cols[2]: _tile("Best attack", _fmt(best.get("goals_for_per_match"),2), str(best.get("season","")))
        st.markdown("<div class='frl-team-v5-label' style='margin-top:1.45rem'>Attack history</div>", unsafe_allow_html=True)
        _history_table(rows)

    with defence:
        best = min(rows, key=lambda r: _num(r.get("goals_against_per_match"),3) if _num(r.get("goals_against_per_match"),3) is not None else 999)
        avg = sum(_num(r.get("goals_against_per_match"),3) or 0 for r in rows) / len(rows)
        cols = st.columns(3, gap="small")
        with cols[0]: _tile("Current", _fmt(current.get("goals_against_per_match"),2), "goals conceded per match")
        with cols[1]: _tile("10-season avg", _fmt(avg,2), "goals conceded per match")
        with cols[2]: _tile("Best defence", _fmt(best.get("goals_against_per_match"),2), str(best.get("season","")))
        st.markdown("<div class='frl-team-v5-label' style='margin-top:1.45rem'>Defensive history</div>", unsafe_allow_html=True)
        _history_table(rows)

    with results:
        wins = int(float(current.get("wins",0) or 0))
        draws = int(float(current.get("draws",0) or 0))
        losses = int(float(current.get("losses",0) or 0))
        played = int(float(current.get("played",0) or 0))
        win_rate = wins / played if played else None
        cols = st.columns(4, gap="small")
        with cols[0]: _tile("Wins", str(wins), season)
        with cols[1]: _tile("Draws", str(draws), season)
        with cols[2]: _tile("Losses", str(losses), season)
        with cols[3]: _tile("Win rate", _fmt((win_rate or 0)*100,0)+"%", season)
        st.markdown("<div class='frl-team-v5-label' style='margin-top:1.45rem'>Season record</div>", unsafe_allow_html=True)
        _history_table(rows)


def render_team_research_ui():
    _css()
    seasons = _seasons()
    if not seasons:
        st.error("No verified team seasons are available.")
        return

    top_cols = st.columns([1.05, 2.2], gap="small")
    with top_cols[0]:
        season = st.selectbox("Season", seasons, index=0, key="frl_team_v5_season")
    table = _league_table(season).get("teams", [])
    teams = [row.get("team") for row in table if row.get("team")]
    if not teams:
        st.info("No teams are available for this season.")
        return
    with top_cols[1]:
        team = st.selectbox("Team", teams, index=0, key="frl_team_v5_team")

    st.markdown("<div class='frl-team-v5-kicker'>Team research</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-team-v5-title'>{html.escape(team)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-team-v5-context'>{season} · verified team identity · research workspace</div>", unsafe_allow_html=True)

    view = st.radio("Workspace", ["Profile", "Stats"], horizontal=True, label_visibility="collapsed", key="frl_team_v5_view")
    summary = _team_summary(season, team)
    if view == "Profile":
        _profile_page(team, season, summary, _team_form(season, team))
    else:
        _stats_page(team, season, summary)
