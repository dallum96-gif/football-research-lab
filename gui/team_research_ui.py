from __future__ import annotations

import streamlit as st

import query_api
from frl_team_visualisations import team_performance_trajectory, team_season_trend
from team_research_analytics import team_performance_profile, team_season_comparison


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


def _fmt_float(value, digits: int = 2) -> str:
    if value is None:
        return "—"
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "—"


def _fmt_signed(value) -> str:
    try:
        return f"{int(value):+,}"
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
def _team_fixtures(season: str, team: str) -> dict:
    return query_api.fixtures(season=season, team=team, limit=100)


@st.cache_data(show_spinner=False)
def _team_profile(season: str, team: str, rolling_window: int):
    return team_performance_profile(season=season, team=team, rolling_window=rolling_window)


@st.cache_data(show_spinner=False)
def _team_comparison(team: str, seasons: list[str]):
    return team_season_comparison(team=team, seasons=seasons)


def _css() -> None:
    st.markdown(
        """
        <style>
        .frl-team-kicker{color:var(--frl-accent);font-size:.61rem;font-weight:850;letter-spacing:.16em;text-transform:uppercase;margin-bottom:.35rem}
        .frl-team-title{color:var(--frl-text);font-size:2.05rem;font-weight:820;line-height:1.04;letter-spacing:-.035em;margin:0}
        .frl-team-context{color:var(--frl-muted);font-size:.8rem;margin-top:.28rem}
        .frl-team-insight{color:var(--frl-text);font-size:1.05rem;line-height:1.35;font-weight:620;margin:.9rem 0 1rem;max-width:58rem}
        .frl-team-insight span{color:var(--frl-accent)}
        .frl-team-method{color:var(--frl-muted-soft);font-size:.58rem;line-height:1.45;margin-top:.55rem}
        .frl-team-metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));border-top:1px solid var(--frl-border);border-bottom:1px solid var(--frl-border);margin:1rem 0 1.15rem}
        .frl-team-metric{padding:.75rem .75rem .72rem 0;border-right:1px solid var(--frl-border)}
        .frl-team-metric:last-child{border-right:0}
        .frl-team-metric-label{color:var(--frl-muted-soft);font-size:.54rem;font-weight:820;letter-spacing:.09em;text-transform:uppercase}
        .frl-team-metric-value{color:var(--frl-text);font-size:1.08rem;font-weight:780;margin-top:.12rem}
        .frl-team-metric-sub{color:var(--frl-muted);font-size:.57rem;margin-top:.08rem}
        .frl-team-section{color:var(--frl-muted-soft);font-size:.59rem;font-weight:820;letter-spacing:.12em;text-transform:uppercase;margin:1.2rem 0 .42rem}
        .frl-team-form{display:flex;gap:.34rem;margin:.25rem 0 .38rem;flex-wrap:wrap}
        .frl-team-form-pill{min-width:2rem;height:2rem;padding:0 .46rem;border:1px solid var(--frl-border);border-radius:4px;display:flex;align-items:center;justify-content:center;color:var(--frl-muted);font-size:.62rem;font-weight:850}
        .frl-team-form-pill.win{color:var(--frl-secondary);border-color:rgba(154,170,66,.45)}
        .frl-team-form-pill.loss{color:var(--frl-negative);border-color:rgba(232,93,63,.35)}
        .frl-team-form-pill.draw{color:var(--frl-muted)}
        .frl-team-row{display:grid;grid-template-columns:5rem minmax(0,1fr) 5rem 4rem;gap:.5rem;align-items:center;padding:.56rem 0;border-bottom:1px solid var(--frl-border)}
        .frl-team-row:last-child{border-bottom:0}
        .frl-team-muted{color:var(--frl-muted-soft);font-size:.58rem}
        .frl-team-main{color:var(--frl-text);font-size:.68rem;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
        .frl-team-meta{color:var(--frl-muted);font-size:.6rem;text-align:right}
        .frl-team-accent{color:var(--frl-text);font-size:.66rem;font-weight:800;text-align:right}
        .frl-team-table-head{color:var(--frl-muted-soft);font-size:.54rem;font-weight:820;letter-spacing:.08em;text-transform:uppercase;padding:.42rem 0;border-bottom:1px solid var(--frl-border)}
        .frl-team-switch-note{color:var(--frl-muted);font-size:.66rem;margin-top:.2rem}
        @media(max-width:900px){.frl-team-metrics{grid-template-columns:repeat(2,minmax(0,1fr));}.frl-team-metric:nth-child(2){border-right:0}.frl-team-row{grid-template-columns:3.8rem minmax(0,1fr) 4.5rem 3.4rem}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _route_view() -> str:
    return "Stats" if st.query_params.get("workspace") == "team-stats" else "Profile"


def _headline_profile(profile) -> str:
    overall = profile.population.get("overall", {})
    phases = [row for row in profile.population.get("phase_splits", []) if row.get("matches")]
    venue = profile.population.get("venue_splits", [])
    rows = list(profile.rows)
    if not rows:
        return "No completed fixtures are available for this research scope."

    rolling_now = rows[-1].get("rolling_ppg")
    rolling_start = rows[min(4, len(rows) - 1)].get("rolling_ppg")
    phase_best = max(phases, key=lambda row: row.get("ppg", -1), default=None)
    home = next((row for row in venue if row.get("label") == "Home"), None)
    away = next((row for row in venue if row.get("label") == "Away"), None)

    if rolling_now is not None and rolling_start is not None and rolling_now - rolling_start >= 0.2:
        first = f"The season finished with momentum: the rolling five-match rate rose from {_fmt_float(rolling_start)} to {_fmt_float(rolling_now)} PPG."
    elif rolling_now is not None and rolling_start is not None and rolling_start - rolling_now >= 0.2:
        first = f"The season tailed off: the rolling five-match rate fell from {_fmt_float(rolling_start)} to {_fmt_float(rolling_now)} PPG."
    else:
        first = f"The season stayed relatively stable at {_fmt_float(overall.get('ppg'))} PPG overall."

    if phase_best:
        second = f" Best phase: {phase_best['label'].lower()} at {_fmt_float(phase_best['ppg'])} PPG."
    elif home and away:
        second = f" Home advantage: {_fmt_float(home['ppg'] - away['ppg'])} PPG."
    else:
        second = ""
    return first + second


def _headline_stats(comparison) -> str:
    rows = list(comparison.rows)
    if not rows:
        return "No verified season records are available for this comparison."
    rows.sort(key=lambda row: row["season"])
    latest = rows[-1]
    mean = sum(float(row["points_per_match"]) for row in rows if row.get("points_per_match") is not None) / len(rows)
    delta = float(latest["points_per_match"]) - mean
    direction = "above" if delta >= 0 else "below"
    attack = _fmt_float(latest.get("goals_for_per_match"))
    defence = _fmt_float(latest.get("goals_against_per_match"))
    return f"{latest['season']} sits <span>{_fmt_float(latest['points_per_match'])} PPG</span>, {abs(delta):.2f} {direction} the selected-period average, with {attack} scored and {defence} conceded per match."


def _metric_options_profile() -> tuple[str, ...]:
    return ("Form", "Attack", "Defence")


def _profile_metric(value: str) -> str:
    return {"Form": "form", "Attack": "attack", "Defence": "defence"}[value]


def _stats_metric(value: str) -> str:
    return {"Performance": "ppg", "Attack": "attack", "Defence": "defence"}[value]


def _render_metrics(summary: dict) -> None:
    data = summary.get("summary", {})
    record = f"{_fmt(data.get('wins'))}–{_fmt(data.get('draws'))}–{_fmt(data.get('losses'))}"
    cells = [
        ("POINTS", _fmt(data.get("points")), "season total"),
        ("RECORD", record, f"{_fmt(data.get('played'))} played"),
        ("GOALS", f"{_fmt(data.get('goals_for'))}–{_fmt(data.get('goals_against'))}", "for / against"),
        ("GD", _fmt_signed(data.get("goal_difference")), "goal difference"),
    ]
    html = "<div class='frl-team-metrics'>"
    for label, value, sub in cells:
        html += f"<div class='frl-team-metric'><div class='frl-team-metric-label'>{label}</div><div class='frl-team-metric-value'>{value}</div><div class='frl-team-metric-sub'>{sub}</div></div>"
    st.markdown(html + "</div>", unsafe_allow_html=True)


def _render_recent_form(form: dict, window: int) -> None:
    recent = form.get("windows", {}).get(str(window), {})
    st.markdown("<div class='frl-team-section'>Recent form</div>", unsafe_allow_html=True)
    pills = []
    for result in recent.get("results", []):
        klass = {"W": "win", "D": "draw", "L": "loss"}.get(result, "draw")
        pills.append(f"<span class='frl-team-form-pill {klass}'>{result}</span>")
    st.markdown("<div class='frl-team-form'>" + "".join(pills) + "</div>", unsafe_allow_html=True)
    st.caption(f"{recent.get('points', 0)} points · {recent.get('goals_for', 0)} scored · {recent.get('goals_against', 0)} conceded")


def _render_fixture_strip(fixtures: dict, window: int) -> None:
    rows = list(fixtures.get("results", []))[-window:]
    if not rows:
        return
    st.markdown("<div class='frl-team-section'>Latest fixtures</div>", unsafe_allow_html=True)
    header = "<div class='frl-team-row frl-team-table-head'><div>GW</div><div>Fixture</div><div>Date</div><div>Score</div></div>"
    body = ""
    for row in reversed(rows):
        home = row.get("home_team_name", "Home")
        away = row.get("away_team_name", "Away")
        score = "—" if row.get("home_score") in (None, "") or row.get("away_score") in (None, "") else f"{row['home_score']}–{row['away_score']}"
        body += f"<div class='frl-team-row'><div class='frl-team-muted'>GW {row.get('gameweek','—')}</div><div class='frl-team-main'>{home} <span style='color:var(--frl-muted-soft)'>v</span> {away}</div><div class='frl-team-meta'>{str(row.get('kickoff_time',''))[:10]}</div><div class='frl-team-accent'>{score}</div></div>"
    st.markdown(header + body, unsafe_allow_html=True)


def _render_profile_splits(profile) -> None:
    tab = st.segmented_control("Browse splits", ["Home / Away", "Season phases"], default="Home / Away", key="frl_team_profile_split", label_visibility="collapsed")
    st.markdown("<div class='frl-team-switch-note'>One compact view at a time — switch when you want to compare the shape of the season.</div>", unsafe_allow_html=True)
    rows = profile.population.get("venue_splits", []) if tab == "Home / Away" else profile.population.get("phase_splits", [])
    if not rows:
        return
    header = "<div class='frl-team-row frl-team-table-head'><div>Split</div><div>Record</div><div>PPG</div><div>GF / GA</div></div>"
    body = ""
    for row in rows:
        if not row.get("matches"):
            continue
        if tab == "Home / Away":
            record = f"{row.get('wins', 0)}W · {row.get('matches', 0) - row.get('wins', 0)} non-wins"
        else:
            record = f"{row.get('matches', 0)} matches · {row.get('wins', 0)} wins"
        body += f"<div class='frl-team-row'><div class='frl-team-muted'>{row.get('label','')}</div><div class='frl-team-main'>{record}</div><div class='frl-team-meta'>{_fmt_float(row.get('ppg'))}</div><div class='frl-team-accent'>{_fmt_float(row.get('goals_per_match'))} / {_fmt_float(row.get('goals_against_per_match'))}</div></div>"
    st.markdown(header + body, unsafe_allow_html=True)


def _profile(summary: dict, form: dict, fixtures: dict, profile) -> None:
    _render_metrics(summary)
    st.markdown(f"<div class='frl-team-insight'>{_headline_profile(profile)}</div>", unsafe_allow_html=True)

    left, right = st.columns([1.05, 1], gap="medium")
    with left:
        trend = st.segmented_control("Trend", list(_metric_options_profile()), default="Form", key="frl_profile_trend", label_visibility="visible")
    with right:
        window = st.segmented_control("Recent window", [5, 10], default=5, key="frl_profile_window", label_visibility="visible")

    st.markdown("<div class='frl-team-section'>Season trend</div>", unsafe_allow_html=True)
    st.altair_chart(team_performance_trajectory(profile, metric=_profile_metric(trend or "Form")), width="stretch")

    with st.container():
        _render_recent_form(form, int(window or 5))
        _render_profile_splits(profile)
        _render_fixture_strip(fixtures, min(int(window or 5), 10))

    st.markdown(
        f"<div class='frl-team-method'>Profile covers {profile.population.get('completed_matches', 0)} completed fixtures. The trend uses a rolling window against the season baseline and inherits the canonical fixture provenance.</div>",
        unsafe_allow_html=True,
    )


def _stats(comparison, scope_label: str) -> None:
    if not comparison.rows:
        st.info("No verified season records are available for this team in the selected range.")
        return

    metric = st.segmented_control("Trend", ["Performance", "Attack", "Defence"], default="Performance", key=f"frl_stats_metric_{scope_label}", label_visibility="visible")
    st.markdown(f"<div class='frl-team-insight'>{_headline_stats(comparison)}</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-team-section'>Historical trend</div>", unsafe_allow_html=True)
    st.altair_chart(team_season_trend(comparison, metric=_stats_metric(metric or "Performance")), width="stretch")

    signals = comparison.population.get("signals", {})
    best_ppg = signals.get("best_ppg")
    best_attack = signals.get("best_attack")
    best_defence = signals.get("best_defence")
    bits = []
    if best_ppg:
        bits.append(f"Best PPG <strong>{best_ppg['season']}</strong> · {_fmt_float(best_ppg['points_per_match'])}")
    if best_attack:
        bits.append(f"Best attack <strong>{best_attack['season']}</strong> · {_fmt_float(best_attack['goals_for_per_match'])} GF/match")
    if best_defence:
        bits.append(f"Best defence <strong>{best_defence['season']}</strong> · {_fmt_float(best_defence['goals_against_per_match'])} GA/match")
    if bits:
        st.markdown("<div class='frl-team-switch-note'>" + " · ".join(bits) + "</div>", unsafe_allow_html=True)

    st.markdown("<div class='frl-team-section'>Season ledger</div>", unsafe_allow_html=True)
    header = "<div class='frl-team-row frl-team-table-head'><div>Season</div><div>Record</div><div>PPG</div><div>GF / GA</div></div>"
    body = ""
    for row in comparison.rows:
        body += f"<div class='frl-team-row'><div class='frl-team-muted'>{row.get('season','')}</div><div class='frl-team-main'>{row.get('wins',0)}W · {row.get('draws',0)}D · {row.get('losses',0)}L · {row.get('played',0)} played</div><div class='frl-team-meta'>{_fmt_float(row.get('points_per_match'))}</div><div class='frl-team-accent'>{_fmt_float(row.get('goals_for_per_match'))} / {_fmt_float(row.get('goals_against_per_match'))}</div></div>"
    st.markdown(header + body, unsafe_allow_html=True)
    if comparison.population.get("skipped_seasons"):
        st.caption("Some requested seasons are omitted because verified persistent club identity was not present in those seasons.")


def render_team_research_ui() -> None:
    _css()
    seasons = _seasons()
    if not seasons:
        st.error("No verified team seasons are available.")
        return

    route = _route_view()
    season = st.selectbox("Season", seasons, index=0, key=f"frl_team_season_{route}")
    teams = [row.get("team") for row in _league_table(season).get("teams", []) if row.get("team")]
    if not teams:
        st.info("No teams are available for this season.")
        return
    team = st.selectbox("Team", teams, index=0, key=f"frl_selected_team_{route}")

    st.markdown("<div class='frl-team-kicker'>Team research</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-team-title'>{team}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-team-context'>{season} · verified team identity · {route.lower()} workspace</div>", unsafe_allow_html=True)

    view_key = f"frl_team_view_{route.lower()}"
    view = st.segmented_control("View", ["Profile", "Stats"], default=route, key=view_key, label_visibility="collapsed") or route
    if view == "Profile":
        profile = _team_profile(season, team, 5)
        _profile(_team_summary(season, team), _team_form(season, team), _team_fixtures(season, team), profile)
        return

    scope = st.segmented_control("Compare", ["Last 5", "Last 10", "Custom"], default="Last 5", key=f"frl_team_stats_scope_{team}", label_visibility="visible")
    if scope == "Last 10":
        selected = seasons[:10]
    elif scope == "Custom":
        selected = st.multiselect("Seasons", seasons, default=seasons[:5], key=f"frl_team_stats_custom_{team}") or seasons[:5]
    else:
        selected = seasons[:5]
    selected = sorted(selected, key=_season_key)
    _stats(_team_comparison(team, selected), f"{team}-{scope}")
