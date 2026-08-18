from __future__ import annotations

import streamlit as st

import query_api
from team_research_analytics import team_performance_profile, team_season_comparison
from frl_team_visualisations import team_performance_trajectory, team_season_performance_map


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
def _team_fixtures_display(season: str, team: str) -> dict:
    return query_api.fixtures(season=season, team=team, limit=100)


@st.cache_data(show_spinner=False)
def _team_profile(season: str, team: str):
    return team_performance_profile(season=season, team=team, rolling_window=5)


@st.cache_data(show_spinner=False)
def _team_comparison(team: str, seasons: list[str]):
    return team_season_comparison(team=team, seasons=seasons)


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
        .frl-team-findings{color:var(--frl-muted);font-size:.78rem;line-height:1.5;margin:.15rem 0 .6rem}
        .frl-team-findings strong{color:var(--frl-text);font-weight:780}
        .frl-team-form{display:flex;gap:.35rem;margin:.2rem 0 .6rem}
        .frl-team-form span{min-width:1.8rem;height:1.8rem;border:1px solid var(--frl-border);border-radius:5px;display:flex;align-items:center;justify-content:center;color:var(--frl-muted);font-size:.62rem;font-weight:800}
        .frl-team-form .win{color:var(--frl-secondary);border-color:rgba(154,170,66,.45)}
        .frl-team-form .draw{color:var(--frl-muted)}
        .frl-team-form .loss{color:var(--frl-negative);border-color:rgba(232,93,63,.35)}
        .frl-team-row{display:grid;grid-template-columns:5rem minmax(0,1fr) 5rem 4rem;gap:.5rem;align-items:center;padding:.55rem 0;border-bottom:1px solid var(--frl-border)}
        .frl-team-row:hover{background:var(--frl-surface)}
        .frl-team-row:last-child{border-bottom:0}
        .frl-team-row-muted{color:var(--frl-muted-soft);font-size:.58rem}
        .frl-team-row-main{color:var(--frl-text);font-size:.68rem;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
        .frl-team-row-meta{color:var(--frl-muted);font-size:.6rem;text-align:right}
        .frl-team-row-accent{color:var(--frl-text);font-size:.66rem;font-weight:800;text-align:right}
        .frl-team-table-head{color:var(--frl-muted-soft);font-size:.56rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;padding:.4rem 0;border-bottom:1px solid var(--frl-border)}
        .frl-team-method{color:var(--frl-muted-soft);font-size:.58rem;line-height:1.45;margin-top:.45rem}
        @media(max-width:900px){.frl-team-row{grid-template-columns:3.8rem minmax(0,1fr) 4.5rem 3.4rem}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_venue_splits(profile) -> None:
    venue_rows = profile.population.get("venue_splits", [])
    if not venue_rows:
        return

    st.markdown("<div class='frl-team-section'>Home / away split</div>", unsafe_allow_html=True)
    st.caption("Same season, same fixture population; venue is defined from the selected team's home/away status.")
    header = "<div class='frl-team-row frl-team-table-head'><div>Venue</div><div>Record</div><div>PPG</div><div>GF / GA</div></div>"
    body = ""
    for row in venue_rows:
        body += (
            f"<div class='frl-team-row'>"
            f"<div class='frl-team-row-muted'>{row['label']}</div>"
            f"<div class='frl-team-row-main'>{row['wins']}W · {row['matches'] - row['wins']} non-wins · {row['win_rate'] * 100:.0f}% win rate</div>"
            f"<div class='frl-team-row-meta'>{_fmt_float(row['ppg'])}</div>"
            f"<div class='frl-team-row-accent'>{_fmt_float(row['goals_per_match'])} / {_fmt_float(row['goals_against_per_match'])}</div>"
            f"</div>"
        )
    st.markdown(header + body, unsafe_allow_html=True)


def _render_phases(profile) -> None:
    phase_rows = profile.population.get("phase_splits", [])
    if not phase_rows:
        return

    st.markdown("<div class='frl-team-section'>Season phases</div>", unsafe_allow_html=True)
    st.caption("The completed season is divided into three chronological thirds by fixture count.")
    header = "<div class='frl-team-row frl-team-table-head'><div>Phase</div><div>Record</div><div>PPG</div><div>GF / GA</div></div>"
    body = ""
    for row in phase_rows:
        if row["matches"] == 0:
            continue
        body += (
            f"<div class='frl-team-row'>"
            f"<div class='frl-team-row-muted'>{row['label']}</div>"
            f"<div class='frl-team-row-main'>{row['matches']} matches · {row['wins']} wins</div>"
            f"<div class='frl-team-row-meta'>{_fmt_float(row['ppg'])}</div>"
            f"<div class='frl-team-row-accent'>{_fmt_float(row['goals_per_match'])} / {_fmt_float(row['goals_against_per_match'])}</div>"
            f"</div>"
        )
    st.markdown(header + body, unsafe_allow_html=True)


def _render_findings(profile) -> None:
    overall = profile.population.get("overall", {})
    venue = profile.population.get("venue_splits", [])
    phases = [row for row in profile.population.get("phase_splits", []) if row.get("matches", 0)]

    best_phase = max(phases, key=lambda row: row.get("ppg", -1), default=None)
    home = next((row for row in venue if row.get("label") == "Home"), None)
    away = next((row for row in venue if row.get("label") == "Away"), None)

    finding_bits = [
        f"<strong>{_fmt_float(overall.get('ppg'))}</strong> points per match overall",
        f"<strong>{overall.get('clean_sheet_rate', 0) * 100:.0f}%</strong> clean-sheet rate",
        f"<strong>{overall.get('failed_to_score_rate', 0) * 100:.0f}%</strong> failed-to-score rate",
    ]
    if best_phase:
        finding_bits.append(
            f"best phase: <strong>{best_phase['label']}</strong> at <strong>{_fmt_float(best_phase['ppg'])} PPG</strong>"
        )
    if home and away:
        finding_bits.append(
            f"home/away PPG gap: <strong>{_fmt_float(home['ppg'] - away['ppg'])}</strong>"
        )

    st.markdown(
        "<div class='frl-team-findings'>" + " · ".join(finding_bits) + "</div>",
        unsafe_allow_html=True,
    )


def _render_recent_form(form: dict) -> None:
    recent = form.get("windows", {}).get("5", {})
    st.markdown("<div class='frl-team-section'>Recent form</div>", unsafe_allow_html=True)
    spans = []
    for result in recent.get("results", []):
        result_class = {"W": "win", "D": "draw", "L": "loss"}.get(result, "")
        spans.append(f"<span class='{result_class}'>{result}</span>")
    pills = "".join(spans) or "<span>—</span>"
    st.markdown(f"<div class='frl-team-form'>{pills}</div>", unsafe_allow_html=True)
    st.caption(
        f"{recent.get('points', 0)} pts · {recent.get('goals_for', 0)} scored · {recent.get('goals_against', 0)} conceded"
    )


def _render_recent_fixtures(fixtures: dict) -> None:
    st.markdown("<div class='frl-team-section'>Recent fixtures</div>", unsafe_allow_html=True)
    rows = list(fixtures.get("results", []))[-5:]
    if not rows:
        st.info("No fixture history is available for this scope.")
        return

    for row in reversed(rows):
        home = row.get("home_team_name", "Home")
        away = row.get("away_team_name", "Away")
        score = "—"
        if row.get("home_score") not in (None, "") and row.get("away_score") not in (None, ""):
            score = f"{row['home_score']}–{row['away_score']}"
        st.markdown(
            f"<div class='frl-team-row'>"
            f"<div class='frl-team-row-muted'>GW {row.get('gameweek','—')}</div>"
            f"<div class='frl-team-row-main'>{home} <span style='color:var(--frl-muted-soft)'>v</span> {away}</div>"
            f"<div class='frl-team-row-meta'>{str(row.get('kickoff_time',''))[:10]}</div>"
            f"<div class='frl-team-row-accent'>{score}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )


def _profile(summary: dict, form: dict, fixtures: dict, profile) -> None:
    data = summary.get("summary", {})

    st.markdown("<div class='frl-team-section'>Season snapshot</div>", unsafe_allow_html=True)
    record = (
        f"<strong>{_fmt(data.get('played'))}</strong> played · "
        f"<strong>{_fmt(data.get('wins'))}</strong> wins · "
        f"<strong>{_fmt(data.get('points'))}</strong> points · "
        f"<strong>{_fmt(data.get('goals_for'))}–{_fmt(data.get('goals_against'))}</strong> goals · "
        f"<strong>{_fmt_signed(data.get('goal_difference'))}</strong> GD"
    )
    st.markdown(f"<div class='frl-team-record'>{record}</div>", unsafe_allow_html=True)
    _render_findings(profile)

    st.markdown("<div class='frl-team-section'>Performance trajectory</div>", unsafe_allow_html=True)
    st.caption("Rolling five-match PPG shows short-term momentum against the cumulative season baseline.")
    st.altair_chart(team_performance_trajectory(profile), width="stretch")

    left, right = st.columns(2, gap="medium")
    with left:
        _render_venue_splits(profile)
    with right:
        _render_recent_form(form)

    _render_phases(profile)
    _render_recent_fixtures(fixtures)

    st.markdown(
        "<div class='frl-team-method'>"
        f"Coverage: {profile.population.get('completed_matches', 0)} completed fixtures. "
        f"Rolling window: {profile.population.get('rolling_window', 5)} matches. "
        "Metrics are derived from the canonical fixture result and inherit its provenance."
        "</div>",
        unsafe_allow_html=True,
    )


def _stats(comparison) -> None:
    rows = comparison.rows
    if not rows:
        st.info("No verified season records are available for this team in the selected range.")
        return

    signals = comparison.population.get("signals", {})
    st.markdown("<div class='frl-team-section'>Season performance map</div>", unsafe_allow_html=True)
    st.caption("Each point is a season: move right for more scoring and down for fewer goals conceded. Point size and colour show points per match; the line connects seasons chronologically.")
    st.altair_chart(team_season_performance_map(comparison), width="stretch")

    header = "<div class='frl-team-row frl-team-table-head'><div>Season</div><div>Record</div><div>PPG</div><div>GF / GA</div></div>"
    body = ""
    for row in rows:
        body += (
            f"<div class='frl-team-row'>"
            f"<div class='frl-team-row-muted'>{row.get('season','')}</div>"
            f"<div class='frl-team-row-main'>{row.get('wins',0)}W · {row.get('draws',0)}D · {row.get('losses',0)}L · {row.get('played',0)} played</div>"
            f"<div class='frl-team-row-meta'>{_fmt_float(row.get('points_per_match'))}</div>"
            f"<div class='frl-team-row-accent'>{_fmt_float(row.get('goals_for_per_match'))} / {_fmt_float(row.get('goals_against_per_match'))}</div>"
            f"</div>"
        )
    st.markdown(header + body, unsafe_allow_html=True)

    best_ppg = signals.get("best_ppg")
    best_attack = signals.get("best_attack")
    best_defence = signals.get("best_defence")
    if best_ppg or best_attack or best_defence:
        bits = []
        if best_ppg:
            bits.append(f"best PPG: <strong>{best_ppg['season']}</strong> ({_fmt_float(best_ppg['points_per_match'])})")
        if best_attack:
            bits.append(f"best attack: <strong>{best_attack['season']}</strong> ({_fmt_float(best_attack['goals_for_per_match'])} GF/match)")
        if best_defence:
            bits.append(f"best defence: <strong>{best_defence['season']}</strong> ({_fmt_float(best_defence['goals_against_per_match'])} GA/match)")
        st.markdown("<div class='frl-team-findings'>" + " · ".join(bits) + "</div>", unsafe_allow_html=True)

    if comparison.population.get("skipped_seasons"):
        st.caption("Some requested seasons are omitted because verified persistent club identity was not present in those seasons.")


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
    st.markdown(f"<div class='frl-team-note'>{season} · verified team identity · research workspace</div>", unsafe_allow_html=True)

    default_view = st.session_state.pop("_frl_team_view_target", "Profile")
    view = st.segmented_control(
        "Team view",
        ["Profile", "Stats"],
        default=default_view,
        key="frl_team_view",
        label_visibility="collapsed",
    )
    if view == "Profile":
        _profile(
            _team_summary(season, team),
            _team_form(season, team),
            _team_fixtures_display(season, team),
            _team_profile(season, team),
        )
        return

    selected = st.multiselect(
        "Seasons",
        seasons,
        default=seasons[: min(6, len(seasons))],
        key="frl_team_stats_seasons",
    ) or [season]
    selected = sorted(selected, key=_season_key)
    _stats(_team_comparison(team, selected))
