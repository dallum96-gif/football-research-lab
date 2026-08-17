from __future__ import annotations

import streamlit as st

import query_api


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


def _css() -> None:
    st.markdown(
        """
        <style>
        .frl-team-kicker{color:var(--frl-accent);font-size:.58rem;font-weight:800;letter-spacing:.15em;text-transform:uppercase;margin-bottom:.3rem}
        .frl-team-title{color:var(--frl-text);font-size:clamp(2rem,3.8vw,3rem);font-weight:800;line-height:1;letter-spacing:-.045em;margin:0}
        .frl-team-note{color:var(--frl-muted);font-size:.78rem;margin-top:.35rem}
        .frl-team-section{color:var(--frl-accent);font-size:.58rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;margin:1rem 0 .45rem}
        .frl-team-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:.5rem}
        .frl-team-stat{background:var(--frl-surface);border:1px solid var(--frl-border);border-radius:7px;padding:.65rem .7rem}
        .frl-team-stat-label{color:var(--frl-muted-soft);font-size:.52rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase}
        .frl-team-stat-value{color:var(--frl-text);font-size:1.22rem;font-weight:800;margin-top:.25rem}
        .frl-team-stat-accent .frl-team-stat-value{color:var(--frl-accent)}
        .frl-team-card{background:var(--frl-surface);border:1px solid var(--frl-border);border-radius:7px;padding:.75rem}
        .frl-team-card-title{color:var(--frl-text);font-size:.82rem;font-weight:760}
        .frl-team-card-copy{color:var(--frl-muted);font-size:.65rem;margin-top:.2rem}
        .frl-team-form{display:flex;gap:.25rem;margin-top:.45rem}
        .frl-team-form span{width:1.75rem;height:1.75rem;border:1px solid var(--frl-border);border-radius:6px;display:flex;align-items:center;justify-content:center;color:var(--frl-text);font-size:.6rem;font-weight:800}
        .frl-team-form .win{color:var(--frl-accent);border-color:rgba(232,93,63,.35)}
        .frl-team-row{display:grid;grid-template-columns:4rem minmax(0,1fr) 4.5rem 3rem;gap:.5rem;align-items:center;padding:.55rem 0;border-bottom:1px solid var(--frl-border)}
        .frl-team-row:last-child{border-bottom:0}
        .frl-team-row-muted{color:var(--frl-muted-soft);font-size:.58rem}
        .frl-team-row-main{color:var(--frl-text);font-size:.68rem;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
        .frl-team-row-meta{color:var(--frl-muted);font-size:.6rem;text-align:right}
        .frl-team-row-accent{color:var(--frl-accent);font-size:.66rem;font-weight:800;text-align:right}
        @media(max-width:900px){.frl-team-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _profile(summary: dict, form: dict, fixtures: dict) -> None:
    data = summary.get("summary", {})
    recent = form.get("windows", {}).get("5", {})
    streaks = form.get("streaks", {})

    st.markdown("<div class='frl-team-section'>Season snapshot</div>", unsafe_allow_html=True)
    items = [
        ("Played", data.get("played"), False),
        ("Wins", data.get("wins"), False),
        ("Points", data.get("points"), True),
        ("Goals for", data.get("goals_for"), False),
        ("Goals against", data.get("goals_against"), False),
        ("Goal difference", data.get("goal_difference"), False),
    ]
    cards = "".join(
        f"<div class='frl-team-stat{' frl-team-stat-accent' if accent else ''}'><div class='frl-team-stat-label'>{label}</div><div class='frl-team-stat-value'>{_fmt(value)}</div></div>"
        for label, value, accent in items
    )
    st.markdown(f"<div class='frl-team-grid'>{cards}</div>", unsafe_allow_html=True)

    left, right = st.columns(2, gap="medium")
    with left:
        st.markdown("<div class='frl-team-section'>Recent form</div>", unsafe_allow_html=True)
        pills = "".join(
            f"<span class='{'win' if result == 'W' else ''}'>{result}</span>"
            for result in recent.get("results", [])
        )
        form_content = pills or '<span class="frl-team-card-copy">—</span>'
        st.markdown(
            f"<div class='frl-team-card'><div class='frl-team-card-title'>Last five</div><div class='frl-team-form'>{form_content}</div><div class='frl-team-card-copy'>{recent.get('points',0)} pts · {recent.get('goals_for',0)} scored · {recent.get('goals_against',0)} conceded</div></div>",
            unsafe_allow_html=True,
        )
    with right:
        st.markdown("<div class='frl-team-section'>Current runs</div>", unsafe_allow_html=True)
        rows = "".join(
            f"<div class='frl-team-row'><div class='frl-team-row-muted'>run</div><div class='frl-team-row-main'>{label}</div><div class='frl-team-row-meta'>current</div><div class='frl-team-row-accent'>{value}</div></div>"
            for label, value in [
                ("Wins", streaks.get("current_win_streak", 0)),
                ("Unbeaten", streaks.get("current_unbeaten_streak", 0)),
                ("Clean sheets", streaks.get("current_clean_sheet_streak", 0)),
                ("Scoring", streaks.get("current_scoring_streak", 0)),
            ]
        )
        st.markdown(f"<div class='frl-team-card'>{rows}</div>", unsafe_allow_html=True)

    st.markdown("<div class='frl-team-section'>Recent fixtures</div>", unsafe_allow_html=True)
    recent_rows = list(fixtures.get("results", []))[-5:]
    if not recent_rows:
        st.caption("No fixture history is available for this scope.")
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
    items = [
        ("Latest points", latest.get("points"), True),
        ("Latest GD", latest.get("goal_difference"), False),
        ("Latest wins", latest.get("wins"), False),
        ("Seasons found", len(rows), False),
    ]
    cols = st.columns(4, gap="small")
    for col, (label, value, accent) in zip(cols, items):
        with col:
            st.markdown(
                f"<div class='frl-team-stat{' frl-team-stat-accent' if accent else ''}'><div class='frl-team-stat-label'>{label}</div><div class='frl-team-stat-value'>{_fmt(value)}</div></div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div class='frl-team-section'>Season comparison</div>", unsafe_allow_html=True)
    header = "<div class='frl-team-row'><div class='frl-team-row-muted'>Season</div><div class='frl-team-row-main'>Record</div><div class='frl-team-row-meta'>GD</div><div class='frl-team-row-accent'>Pts</div></div>"
    body = "".join(
        f"<div class='frl-team-row'><div class='frl-team-row-muted'>{row.get('season','')}</div><div class='frl-team-row-main'>{row.get('wins',0)}W · {row.get('draws',0)}D · {row.get('losses',0)}L · {row.get('played',0)} played</div><div class='frl-team-row-meta'>{int(row.get('goal_difference',0)):+d}</div><div class='frl-team-row-accent'>{row.get('points',0)}</div></div>"
        for row in rows
    )
    st.markdown(f"<div class='frl-team-card'>{header}{body}</div>", unsafe_allow_html=True)
    if comparison.get("skipped_seasons"):
        st.caption("Some requested seasons are omitted because the verified team identity was not present in those seasons.")


def render_team_research_ui() -> None:
    _css()
    seasons = sorted(query_api.available_seasons(), key=_season_key, reverse=True)
    if not seasons:
        st.error("No verified team seasons are available.")
        return

    season = st.selectbox("Season", seasons, index=0, key="frl_team_season")
    table = query_api.league_table(season).get("teams", [])
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
            query_api.team_summary(season=season, team=team),
            query_api.team_form(season=season, team=team),
            query_api.fixtures(season=season, team=team, limit=100),
        )
        return

    selected = st.multiselect("Seasons", seasons, default=seasons[: min(4, len(seasons))], key="frl_team_stats_seasons") or [season]
    selected = sorted(selected, key=_season_key)
    _stats(query_api.team_compare(team=team, seasons=selected))
