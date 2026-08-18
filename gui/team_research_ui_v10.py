from __future__ import annotations

import html
import streamlit as st

import gui.team_research_ui_v8 as base


def _render_browse_controls(season: str, team: str, seasons: list[str], teams: list[str]) -> tuple[str, str]:
    st.markdown(
        "<div style='margin-top:.55rem;color:var(--frl-muted-soft);font-size:.56rem;font-weight:820;letter-spacing:.11em;text-transform:uppercase;'>Browse team research</div>",
        unsafe_allow_html=True,
    )
    cols = st.columns([1.0, 2.0], gap="small")
    with cols[0]:
        selected_season = st.selectbox(
            "Season",
            seasons,
            index=seasons.index(season) if season in seasons else 0,
            key="frl_team10_season",
            label_visibility="collapsed",
        )
    with cols[1]:
        selected_team = st.selectbox(
            "Team",
            teams,
            index=teams.index(team) if team in teams else 0,
            key="frl_team10_team",
            label_visibility="collapsed",
        )
    return selected_season, selected_team


def render_team_research_ui() -> None:
    base._css()
    seasons = base._seasons()
    if not seasons:
        st.error("No verified team seasons are available.")
        return

    stored_season = st.session_state.get("frl_team10_season", seasons[0])
    season = stored_season if stored_season in seasons else seasons[0]
    teams = [r.get("team") for r in base._league_table(season).get("teams", []) if r.get("team")]
    if not teams:
        st.error("No verified teams are available for this season.")
        return

    stored_team = st.session_state.get("frl_team10_team", teams[0])
    team = stored_team if stored_team in teams else teams[0]

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
    selected_season, selected_team = _render_browse_controls(season, team, seasons, teams)

    if selected_season != season:
        st.session_state["frl_team10_season"] = selected_season
        st.session_state.pop("frl_team10_team", None)
        st.rerun()
    if selected_team != team:
        st.session_state["frl_team10_team"] = selected_team
        st.rerun()

    summary = base._team_summary(season, team)
    form = base._team_form(season, team)
    rows = list(base._comparison(team, tuple(seasons[:10])).rows)
    if view == "Stats":
        base._stats(team, season, summary, rows)
    else:
        base._profile(team, season, summary, form, rows)
