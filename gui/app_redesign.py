from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import query_api

from gui.fixture_explorer import render_fixture_explorer
from gui.ui_shell import current_workspace, render_workspace_sidebar
from gui.theme import apply_theme, render_brand_header


st.set_page_config(
    page_title="Football Research Lab",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="locked",
)

apply_theme()


def season_key(season):
    return int(season.split("-")[0])


@st.cache_data
def get_seasons():
    return query_api.list_seasons()


@st.cache_data
def get_league_table(season):
    return query_api.league_table(season=season)


@st.cache_data
def get_fixtures(
    season,
    team,
    opponent=None,
    venue=None,
    result=None,
):
    return query_api.fixtures(
        season=season,
        team=team,
        opponent=opponent,
        venue=venue,
        result=result,
        limit=100,
    )


render_workspace_sidebar(current_workspace())
render_brand_header()
workspace = current_workspace()

if workspace == "overview":
    st.markdown("<div class='frl-eyebrow'>Football Research Laboratory</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-home-title'>The football database for asking better questions.</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='frl-home-subtitle'>Premier League history, players, fixtures and research tools — built around persistent identity, provenance and tested data.</div>",
        unsafe_allow_html=True,
    )

    stats = st.columns(4, gap="small")
    stats[0].markdown("<div class='frl-home-stat'><span>10</span><small>seasons</small></div>", unsafe_allow_html=True)
    stats[1].markdown("<div class='frl-home-stat'><span>3,800</span><small>fixtures</small></div>", unsafe_allow_html=True)
    stats[2].markdown("<div class='frl-home-stat'><span>26 / 26</span><small>assurance tests</small></div>", unsafe_allow_html=True)
    stats[3].markdown("<div class='frl-home-stat'><span>2016–26</span><small>coverage</small></div>", unsafe_allow_html=True)

    st.markdown("<div class='frl-home-rule'></div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-home-section-label'>Explore</div>", unsafe_allow_html=True)

    explore_cols = st.columns(3, gap="medium")
    cards = [
        ("Fixtures", "Browse a team's Premier League history.", "fixtures"),
        ("League Table", "See how the competition finished.", "league-table"),
        ("Players", "Find players and investigate their history.", "players"),
    ]
    for col, (title, description, target) in zip(explore_cols, cards):
        with col:
            st.markdown(
                f"<div class='frl-home-card'><div class='frl-home-card-title'>{title}</div><div class='frl-home-card-copy'>{description}</div></div>",
                unsafe_allow_html=True,
            )
            if st.button("Open", key=f"overview_open_{target}", type="tertiary", width="stretch"):
                st.query_params["workspace"] = target
                st.rerun()

    st.markdown("<div class='frl-home-section-label frl-home-section-spaced'>Built for research</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='frl-home-principles'><span>Persistent football identity</span><span>Provenance</span><span>Invariant testing</span><span>Temporal integrity</span></div>",
        unsafe_allow_html=True,
    )

elif workspace == "fixtures":
    seasons = sorted(get_seasons(), key=season_key, reverse=True)
    default_season = seasons[0] if seasons else ""
    season = st.session_state.get("redesign_fixture_season_header", default_season)
    if season not in seasons:
        season = default_season

    table = get_league_table(season)
    teams = sorted([row["team"] for row in table["teams"]], key=str.casefold)
    default_team = teams[0] if teams else ""
    team = st.session_state.get("redesign_fixture_team_header", default_team)
    if team not in teams:
        team = default_team

    header_left, header_team, header_season = st.columns([5.4, 1.7, 1.25], gap="small", vertical_alignment="bottom")
    with header_left:
        st.markdown("<div class='frl-eyebrow'>Fixtures</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='frl-entity-title'>{team}</div>", unsafe_allow_html=True)
        st.markdown("<div class='frl-context'>Premier League</div>", unsafe_allow_html=True)
    with header_team:
        st.markdown(
            """
            <style>
            .frl-team-selector-marker + div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
                background: #171714 !important;
                border-color: #171714 !important;
                color: #fffaf0 !important;
                -webkit-text-fill-color: #fffaf0 !important;
                box-shadow: none !important;
            }
            .frl-team-selector-marker + div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover,
            .frl-team-selector-marker + div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
                background: #171714 !important;
                border-color: #e85d3f !important;
                color: #fffaf0 !important;
                -webkit-text-fill-color: #fffaf0 !important;
                box-shadow: 0 0 0 2px rgba(232,93,63,0.12) !important;
            }
            .frl-team-selector-marker + div[data-testid="stSelectbox"] div[data-baseweb="select"] svg {
                color: #fffaf0 !important;
                fill: #fffaf0 !important;
            }
            .frl-team-selector-marker + div[data-testid="stSelectbox"] div[data-baseweb="select"] input {
                color: #fffaf0 !important;
                -webkit-text-fill-color: #fffaf0 !important;
            }
            </style>
            <div class='frl-team-selector-marker' aria-hidden='true'></div>
            """,
            unsafe_allow_html=True,
        )
        team = st.selectbox(
            "Team",
            teams,
            index=teams.index(team) if team in teams else 0,
            key="redesign_fixture_team_header",
            label_visibility="collapsed",
        ) if teams else ""
    with header_season:
        season = st.selectbox(
            "Season",
            seasons,
            index=seasons.index(season) if season in seasons else 0,
            key="redesign_fixture_season_header",
            label_visibility="collapsed",
        ) if seasons else ""

    if season != default_season:
        table = get_league_table(season)
        teams = sorted([row["team"] for row in table["teams"]], key=str.casefold)
        if team not in teams:
            team = teams[0] if teams else ""

    render_fixture_explorer(
        season=season,
        team=team,
        get_fixtures=get_fixtures,
    )

elif workspace == "league-table":
    seasons = sorted(get_seasons(), key=season_key, reverse=True)
    season = st.selectbox("Season", seasons, key="redesign_league_table_season")
    table = get_league_table(season)

    st.markdown("<div class='frl-eyebrow'>Explore</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-entity-title'>League Table</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-context'>Premier League · {season}</div>", unsafe_allow_html=True)

    rows = [
        {
            "Pos": row["position"],
            "Team": row["team"],
            "P": row["played"],
            "W": row["wins"],
            "D": row["draws"],
            "L": row["losses"],
            "GF": row["goals_for"],
            "GA": row["goals_against"],
            "GD": row["goal_difference"],
            "Pts": row["points"],
        }
        for row in table["teams"]
    ]

    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

else:
    item_labels = {
        "players": "Players",
        "head-to-head": "Head-to-Head",
        "form": "Form & Streaks",
        "prediction": "Prediction",
        "data-quality": "Data Quality",
        "provenance": "Provenance",
    }
    label = item_labels.get(workspace, workspace.replace("-", " ").title())
    st.markdown("<div class='frl-eyebrow'>Explore</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='frl-entity-title'>{label}</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-context'>Research workspace</div>", unsafe_allow_html=True)
