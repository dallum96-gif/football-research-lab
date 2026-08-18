from __future__ import annotations

import html

import altair as alt
import streamlit as st

import query_api
from team_research_analytics import team_season_comparison


def _season_key(value: str) -> tuple[int, int]:
    try:
        left, right = value.split("-", 1)
        return int(left), int(right)
    except (TypeError, ValueError):
        return (0, 0)


def _num(value, digits: int = 3):
    try:
        return round(float(value), digits)
    except (TypeError, ValueError):
        return None


def _fmt(value, digits: int = 2, suffix: str = "") -> str:
    try:
        n = float(value)
    except (TypeError, ValueError):
        return "—"
    if digits == 0:
        return f"{int(round(n)):,}{suffix}"
    return f"{n:.{digits}f}{suffix}"


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


def _css() -> None:
    st.markdown(
        """
        <style>
        .frl-team7-hero{display:flex;justify-content:space-between;gap:1.2rem;align-items:end;margin-bottom:.95rem}
        .frl-team7-kicker{color:var(--frl-accent);font-size:.62rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase;margin-bottom:.38rem}
        .frl-team7-title{color:var(--frl-text);font-size:clamp(2.2rem,3.6vw,3.35rem);font-weight:800;letter-spacing:-.055em;line-height:.96;margin:0}
        .frl-team7-context{color:var(--frl-muted);font-size:.82rem;margin-top:.34rem}
        .frl-team7-rule{height:2px;background:var(--frl-text);margin:.9rem 0 1rem;opacity:.9}
        .frl-team7-label{color:var(--frl-accent);font-size:.62rem;font-weight:800;letter-spacing:.15em;text-transform:uppercase;margin:1.35rem 0 .58rem}
        .frl-team7-tile{min-height:6rem;padding:.9rem .9rem .78rem;border:1px solid var(--frl-border);border-radius:12px;background:var(--frl-surface);}
        .frl-team7-tile.accent{background:#f0d8cf;border-color:rgba(232,93,63,.18)}
        .frl-team7-tile.green{background:#e8edd4;border-color:rgba(154,170,66,.2)}
        .frl-team7-tile.warm{background:#eee7d8;border-color:rgba(198,138,53,.15)}
        .frl-team7-tile-label{color:var(--frl-muted-soft);font-size:.57rem;font-weight:800;letter-spacing:.11em;text-transform:uppercase}
        .frl-team7-tile-value{color:var(--frl-text);font-size:1.58rem;font-weight:820;line-height:1;margin-top:.36rem;letter-spacing:-.035em}
        .frl-team7-tile-copy{color:var(--frl-muted);font-size:.67rem;line-height:1.35;margin-top:.3rem}
        .frl-team7-pillrow{display:flex;gap:.35rem;flex-wrap:wrap}
        .frl-team7-pill{width:2rem;height:2rem;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:.65rem;font-weight:850;border:1px solid var(--frl-border);background:var(--frl-surface)}
        .frl-team7-pill.w{background:#e8edd4;border-color:rgba(154,170,66,.3);color:#66722a}
        .frl-team7-pill.d{background:#eee7d8;color:var(--frl-muted)}
        .frl-team7-pill.l{background:#f0d8cf;border-color:rgba(232,93,63,.2);color:#b8432a}
        .frl-team7-table{width:100%;border-top:1px solid var(--frl-border-strong)}
        .frl-team7-row{display:grid;grid-template-columns:1.05fr 1.2fr .8fr .8fr .9fr;gap:.6rem;align-items:center;padding:.58rem .05rem;border-bottom:1px solid var(--frl-border);font-size:.69rem}
        .frl-team7-row.head{color:var(--frl-muted-soft);font-size:.55rem;font-weight:800;letter-spacing:.09em;text-transform:uppercase}
        .frl-team7-row .main{color:var(--frl-text);font-weight:760}.frl-team7-row .muted{color:var(--frl-muted)}.frl-team7-row .right{text-align:right;color:var(--frl-text);font-weight:760}
        .frl-team7-note{color:var(--frl-muted-soft);font-size:.61rem;line-height:1.45;margin-top:.48rem}
        @media(max-width:900px){.frl-team7-hero{display:block}.frl-team7-row{grid-template-columns:1fr 1.15fr .72fr .72fr .8fr}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _tile(label: str, value: str, copy: str = "", tone: str = "") -> None:
    cls = f"frl-team7-tile {tone}".strip()
    st.markdown(
        f"<div class='{cls}'><div class='frl-team7-tile-label'>{html.escape(label)}</div>"
        f"<div class='frl-team7-tile-value'>{html.escape(value)}</div>"
        f"<div class='frl-team7-tile-copy'>{html.escape(copy)}</div></div>",
        unsafe_allow_html=True,
    )


def _metric(summary: dict, total_key: str) -> float | None:
    data = summary.get("summary", {})
    direct = data.get(total_key)
    if direct is not None:
        return _num(direct)
    return None


def _per_game(summary: dict, total_key: str) -> float | None:
    data = summary.get("summary", {})
    value = _num(data.get(total_key))
    played = _num(data.get("played"))
    return round(value / played, 3) if value is not None and played else None


def _position(season: str, team: str) -> int | None:
    rows = _league_table(season).get("teams", [])
    row = next((r for r in rows if r.get("team") == team), None)
    try:
        return int(row.get("position")) if row else None
    except (TypeError, ValueError):
        return None


def _history_chart(rows: list[dict], metric: str, title: str) -> None:
    values = []
    for row in rows:
        season = row.get("season")
        value = _num(row.get(metric))
        if season and value is not None:
            values.append({"season": season, "value": value})
    if not values:
        st.info(f"{title} is not available for this selection.")
        return
    order = [v["season"] for v in values]
    chart = (
        alt.Chart(alt.Data(values=values))
        .mark_line(point=alt.OverlayMarkDef(filled=True, size=70), strokeWidth=2.8)
        .encode(
            x=alt.X("season:N", title=None, sort=order, axis=alt.Axis(labelAngle=0, labelColor="#68645c", labelFontSize=11, domainColor="#c9c3b7", tickColor="#c9c3b7")),
            y=alt.Y("value:Q", title=None, scale=alt.Scale(zero=False, nice=True), axis=alt.Axis(labelColor="#68645c", labelFontSize=11, gridColor="#d9d3c8", gridOpacity=.55, domain=False)),
            tooltip=[alt.Tooltip("season:N", title="Season"), alt.Tooltip("value:Q", title=title, format=".2f")],
        ).properties(height=235, background="#fffdf8")
    )
    st.altair_chart(chart, width="stretch")


def _history_table(rows: list[dict]) -> None:
    body = [
        "<div class='frl-team7-table'>",
        "<div class='frl-team7-row head'><div>Season</div><div>Record</div><div>Points</div><div>PPG</div><div>GF / GA</div></div>",
    ]
    for row in reversed(rows):
        body.append(
            f"<div class='frl-team7-row'><div class='main'>{html.escape(str(row.get('season','')))}</div>"
            f"<div class='muted'>{row.get('wins',0)}W · {row.get('draws',0)}D · {row.get('losses',0)}L</div>"
            f"<div class='right'>{row.get('points','—')}</div><div class='right'>{_fmt(row.get('points_per_match'),2)}</div>"
            f"<div class='right'>{_fmt(row.get('goals_for_per_match'),2)} / {_fmt(row.get('goals_against_per_match'),2)}</div></div>"
        )
    body.append("</div>")
    st.markdown("".join(body), unsafe_allow_html=True)


def _form_row(form: dict) -> None:
    recent = form.get("windows", {}).get("5", {})
    results = recent.get("results", [])
    spans = []
    for r in results:
        cls = {"W":"w","D":"d","L":"l"}.get(r, "d")
        spans.append(f"<span class='frl-team7-pill {cls}'>{html.escape(str(r))}</span>")
    st.markdown(f"<div class='frl-team7-pillrow'>{''.join(spans) or '—'}</div>", unsafe_allow_html=True)


def _profile(team: str, season: str, summary: dict, form: dict, rows: list[dict]) -> None:
    data = summary.get("summary", {})
    position = _position(season, team)
    ppg = _per_game(summary, "points")
    gf = _per_game(summary, "goals_for")
    ga = _per_game(summary, "goals_against")
    gd = _metric(summary, "goal_difference")

    st.markdown("<div class='frl-team7-kicker'>Club profile</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-team7-title'>{html.escape(team)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-team7-context'>{season} · club history, identity and recent direction</div>", unsafe_allow_html=True)

    st.markdown("<div class='frl-team7-label'>This season</div>", unsafe_allow_html=True)
    cols = st.columns(5, gap="small")
    with cols[0]: _tile("Position", str(position or "—"), "league finish", "accent")
    with cols[1]: _tile("Points", _fmt(data.get("points"),0), season, "warm")
    with cols[2]: _tile("PPG", _fmt(ppg,2), "points per match", "green")
    with cols[3]: _tile("Goal difference", _fmt(gd,0, "+"), "season total")
    with cols[4]: _tile("GF / match", _fmt(gf,2), "goals scored", "accent")

    snap, history, momentum = st.tabs(["Snapshot", "History", "Momentum"])
    with snap:
        st.markdown("<div class='frl-team7-label'>The quick read</div>", unsafe_allow_html=True)
        cols = st.columns(4, gap="small")
        with cols[0]: _tile("Goals against", _fmt(ga,2), "per match", "warm")
        with cols[1]: _tile("Wins", str(data.get("wins",0)), season, "green")
        with cols[2]: _tile("Clean sheets", str(data.get("clean_sheets", "—")), season)
        with cols[3]: _tile("Played", str(data.get("played",0)), "completed matches")
        st.markdown("<div class='frl-team7-label'>Recent results</div>", unsafe_allow_html=True)
        _form_row(form)
        recent = form.get("windows", {}).get("5", {})
        rcols = st.columns(3, gap="small")
        with rcols[0]: _tile("Last 5 points", str(recent.get("points",0)), "recent return", "green")
        with rcols[1]: _tile("Scored", str(recent.get("goals_for",0)), "last five")
        with rcols[2]: _tile("Conceded", str(recent.get("goals_against",0)), "last five", "warm")
    with history:
        st.markdown("<div class='frl-team7-label'>Club performance journey</div>", unsafe_allow_html=True)
        history_range = st.radio("History range", ["Last 5", "Last 10"], horizontal=True, label_visibility="collapsed", key="frl_team7_profile_history")
        subset = rows[-5:] if history_range == "Last 5" else rows[-10:]
        _history_chart(subset, "points_per_match", "PPG")
        _history_table(subset)
        st.markdown("<div class='frl-team7-note'>PPG keeps different seasons directly comparable while the table preserves the underlying football story.</div>", unsafe_allow_html=True)
    with momentum:
        recent = form.get("windows", {}).get("5", {})
        longer = form.get("windows", {}).get("10", {})
        recent_ppg = (recent.get("points",0) / recent.get("matches",1)) if recent.get("matches") else None
        long_ppg = (longer.get("points",0) / longer.get("matches",1)) if longer.get("matches") else None
        delta = (recent_ppg - long_ppg) if recent_ppg is not None and long_ppg is not None else None
        cols = st.columns(3, gap="small")
        with cols[0]: _tile("Last 5 PPG", _fmt(recent_ppg,2), "recent momentum", "green")
        with cols[1]: _tile("Last 10 PPG", _fmt(long_ppg,2), "broader form")
        with cols[2]: _tile("Momentum", ("+" if (delta or 0) >= 0 else "") + _fmt(delta,2), "5 vs 10 match PPG", "accent" if (delta or 0) < 0 else "green")
        st.markdown("<div class='frl-team7-label'>Form at a glance</div>", unsafe_allow_html=True)
        _form_row(form)


def _stats(team: str, season: str, summary: dict, rows: list[dict]) -> None:
    data = summary.get("summary", {})
    ppg = _per_game(summary, "points")
    gf = _per_game(summary, "goals_for")
    ga = _per_game(summary, "goals_against")
    wins = int(data.get("wins",0) or 0)
    draws = int(data.get("draws",0) or 0)
    losses = int(data.get("losses",0) or 0)
    played = int(data.get("played",0) or 0)
    win_rate = wins / played * 100 if played else 0

    st.markdown("<div class='frl-team7-kicker'>Team intelligence</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-team7-title'>{html.escape(team)} · stats</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-team7-context'>{season} · team-level numbers, split into simple questions</div>", unsafe_allow_html=True)

    overview, attack, defence, results = st.tabs(["Overview", "Attack", "Defence", "Results"])
    with overview:
        cols = st.columns(4, gap="small")
        with cols[0]: _tile("PPG", _fmt(ppg,2), season, "accent")
        with cols[1]: _tile("GF / match", _fmt(gf,2), "attacking output", "green")
        with cols[2]: _tile("GA / match", _fmt(ga,2), "defensive output", "warm")
        with cols[3]: _tile("Win rate", _fmt(win_rate,0,"%"), season)
        st.markdown("<div class='frl-team7-label'>Season comparison</div>", unsafe_allow_html=True)
        recent = rows[-5:]
        _history_chart(recent, "points_per_match", "PPG")
        st.markdown("<div class='frl-team7-note'>A compact visual benchmark for the selected season against the recent club baseline.</div>", unsafe_allow_html=True)
    with attack:
        values = [r for r in rows if _num(r.get("goals_for_per_match")) is not None]
        avg = sum(r["goals_for_per_match"] for r in values)/len(values) if values else None
        best = max(values, key=lambda r: r["goals_for_per_match"], default={})
        cols = st.columns(4, gap="small")
        with cols[0]: _tile("Current", _fmt(gf,2), "goals / match", "accent")
        with cols[1]: _tile("History avg", _fmt(avg,2), "selected seasons")
        with cols[2]: _tile("Best", _fmt(best.get("goals_for_per_match"),2), str(best.get("season","")), "green")
        with cols[3]: _tile("Points", _fmt(data.get("points"),0), season)
        st.markdown("<div class='frl-team7-label'>Attack journey</div>", unsafe_allow_html=True)
        _history_chart(rows, "goals_for_per_match", "Goals per match")
    with defence:
        values = [r for r in rows if _num(r.get("goals_against_per_match")) is not None]
        avg = sum(r["goals_against_per_match"] for r in values)/len(values) if values else None
        best = min(values, key=lambda r: r["goals_against_per_match"], default={})
        cols = st.columns(4, gap="small")
        with cols[0]: _tile("Current", _fmt(ga,2), "goals conceded / match", "warm")
        with cols[1]: _tile("History avg", _fmt(avg,2), "selected seasons")
        with cols[2]: _tile("Best", _fmt(best.get("goals_against_per_match"),2), str(best.get("season","")), "green")
        with cols[3]: _tile("Clean sheets", str(data.get("clean_sheets","—")), season)
        st.markdown("<div class='frl-team7-label'>Defensive journey</div>", unsafe_allow_html=True)
        _history_chart(rows, "goals_against_per_match", "Goals conceded per match")
    with results:
        cols = st.columns(4, gap="small")
        with cols[0]: _tile("Wins", str(wins), season, "green")
        with cols[1]: _tile("Draws", str(draws), season)
        with cols[2]: _tile("Losses", str(losses), season, "warm")
        with cols[3]: _tile("Points", _fmt(data.get("points"),0), "current season", "accent")
        st.markdown("<div class='frl-team7-label'>Season record</div>", unsafe_allow_html=True)
        _history_table(rows)


def render_team_research_ui():
    _css()
    seasons = _seasons()
    if not seasons:
        st.error("No verified team seasons are available.")
        return
    season = st.selectbox("Season", seasons, index=0, key="frl_team7_season", label_visibility="visible")
    teams = [r.get("team") for r in _league_table(season).get("teams", []) if r.get("team")]
    team = st.selectbox("Team", teams, index=0, key="frl_team7_team", label_visibility="visible")
    if not team:
        return
    summary = _team_summary(season, team)
    form = _team_form(season, team)
    rows = list(_comparison(team, tuple(seasons[:10])).rows)
    view = st.session_state.get("frl_team_view", "Profile")
    hero_left, hero_right = st.columns([4.5, 1.7], gap="medium")
    with hero_left:
        st.markdown("<div class='frl-team7-kicker'>Football Research Laboratory</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='frl-team7-title'>{html.escape(team)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='frl-team7-context'>{season} · verified team identity</div>", unsafe_allow_html=True)
    with hero_right:
        st.markdown("<div style='text-align:right;color:var(--frl-muted-soft);font-size:.58rem;font-weight:800;letter-spacing:.11em;text-transform:uppercase;padding-top:.25rem;'>Browse</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:right;color:var(--frl-text);font-size:1.05rem;font-weight:800;margin-top:.2rem;'>{'Profile' if view == 'Profile' else 'Stats'}</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-team7-rule'></div>", unsafe_allow_html=True)
    if view == "Stats":
        _stats(team, season, summary, rows)
    else:
        _profile(team, season, summary, form, rows)
