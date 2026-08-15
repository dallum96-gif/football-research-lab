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
def get_top_players(season, metric, limit=5):
    return query_api.top_players(season=season, metric=metric, limit=limit)


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
    seasons = sorted(get_seasons(), key=season_key, reverse=True)
    latest_season = seasons[-1] if seasons else ""
    table = get_league_table(latest_season) if latest_season else {"teams": []}
    teams = table.get("teams", [])

    top_scorers = []
    try:
        top_scorers = get_top_players(latest_season, "goals", 5).get("results", []) if latest_season else []
    except Exception:
        top_scorers = []

    best_points = sorted(teams, key=lambda row: row.get("points", 0), reverse=True)[:6]
    most_goals = max(teams, key=lambda row: row.get("goals_for", 0), default={})
    biggest_gd = max(teams, key=lambda row: row.get("goal_difference", 0), default={})
    most_points = max(teams, key=lambda row: row.get("points", 0), default={})

    st.markdown(
        """
        <style>
        .frl-collage-kicker { color:var(--frl-accent); font-size:0.62rem; font-weight:800; letter-spacing:0.16em; text-transform:uppercase; margin-bottom:0.62rem; }
        .frl-collage-title { max-width:820px; color:var(--frl-text); font-size:clamp(2.45rem,4.3vw,4.1rem); font-weight:800; line-height:0.93; letter-spacing:-0.055em; }
        .frl-collage-sub { max-width:640px; margin-top:0.9rem; color:var(--frl-muted); font-size:0.94rem; line-height:1.5; }
        .frl-fact-row { display:grid; grid-template-columns:repeat(3,1fr); gap:0.7rem; margin-top:1.3rem; }
        .frl-fact { min-height:110px; padding:0.95rem 1rem 0.85rem; border:1px solid var(--frl-border); border-radius:12px; background:var(--frl-surface); }
        .frl-fact-accent { background:#f0d8cf; border-color:rgba(232,93,63,0.14); }
        .frl-fact-label { color:var(--frl-muted-soft); font-size:0.58rem; font-weight:800; letter-spacing:0.11em; text-transform:uppercase; }
        .frl-fact-value { margin-top:0.42rem; color:var(--frl-text); font-size:1.55rem; font-weight:800; line-height:1; letter-spacing:-0.03em; }
        .frl-fact-copy { margin-top:0.27rem; color:var(--frl-muted); font-size:0.70rem; line-height:1.35; }
        .frl-collage-section { margin-top:1.55rem; color:var(--frl-accent); font-size:0.62rem; font-weight:800; letter-spacing:0.15em; text-transform:uppercase; }
        .frl-player-card { padding:1rem 1rem 0.85rem; border:1px solid var(--frl-border); border-radius:14px; background:var(--frl-surface); }
        .frl-player-card-title { color:var(--frl-text); font-size:1.05rem; font-weight:800; }
        .frl-player-card-note { margin-top:0.22rem; color:var(--frl-muted-soft); font-size:0.68rem; }
        .frl-player-row { display:flex; align-items:center; gap:0.7rem; padding:0.68rem 0; border-bottom:1px solid var(--frl-border); }
        .frl-player-row:last-child { border-bottom:0; }
        .frl-player-rank { flex:0 0 auto; width:1.55rem; height:1.55rem; display:flex; align-items:center; justify-content:center; border-radius:50%; background:var(--frl-surface-raised); color:var(--frl-muted); font-size:0.62rem; font-weight:800; }
        .frl-player-name { flex:1; color:var(--frl-text); font-size:0.78rem; font-weight:720; }
        .frl-player-value { color:var(--frl-accent); font-size:0.85rem; font-weight:800; }
        .frl-mini-caption { margin-top:0.55rem; color:var(--frl-muted-soft); font-size:0.65rem; }
        .frl-collage-footer { margin-top:1rem; color:var(--frl-muted-soft); font-size:0.67rem; }
        @media (max-width: 900px) { .frl-fact-row { grid-template-columns:1fr; } }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='frl-collage-kicker'>A little place to get lost in football</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-collage-title'>The beautiful game,<br>with receipts.</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='frl-collage-sub'>Live football facts from the lab, pulled from the latest dataset: {latest_season or 'the current collection'}. Some useful, some gloriously unnecessary.</div>",
        unsafe_allow_html=True,
    )

    fact_cols = st.columns(3, gap="small")
    fact_cards = [
        ("Most goals", str(most_goals.get("goals_for", "—")), most_goals.get("team", "Latest season"), True),
        ("Biggest goal difference", str(biggest_gd.get("goal_difference", "—")), biggest_gd.get("team", "Latest season"), False),
        ("Most points", str(most_points.get("points", "—")), most_points.get("team", "Latest season"), False),
    ]
    for col, (label, value, copy, accent) in zip(fact_cols, fact_cards):
        with col:
            cls = "frl-fact frl-fact-accent" if accent else "frl-fact"
            st.markdown(
                f"<div class='{cls}'><div class='frl-fact-label'>{label}</div><div class='frl-fact-value'>{value}</div><div class='frl-fact-copy'>{copy} · {latest_season}</div></div>",
                unsafe_allow_html=True,
            )

    left, right = st.columns([1.15, 0.85], gap="medium")
    with left:
        st.markdown("<div class='frl-collage-section'>Points race</div>", unsafe_allow_html=True)
        if best_points:
            points_df = pd.DataFrame({
                "Team": [row.get("team", "") for row in best_points],
                "Points": [row.get("points", 0) for row in best_points],
            }).set_index("Team")
            st.bar_chart(points_df, y="Points", height=235, use_container_width=True)
            st.markdown(
                f"<div class='frl-mini-caption'>Top six by points in {latest_season}.</div>",
                unsafe_allow_html=True,
            )

    with right:
        st.markdown("<div class='frl-collage-section'>Who was putting them away?</div>", unsafe_allow_html=True)
        rows_html = []
        for item in top_scorers:
            value = item.get("value", 0)
            formatted = str(int(value)) if float(value).is_integer() else f"{value:.1f}"
            rows_html.append(
                f"<div class='frl-player-row'><span class='frl-player-rank'>{item.get('rank', ''):02d}</span><span class='frl-player-name'>{item.get('player', '')}</span><span class='frl-player-value'>{formatted}</span></div>"
            )
        st.markdown(
            "<div class='frl-player-card'>"
            "<div class='frl-player-card-title'>Top scorers</div>"
            f"<div class='frl-player-card-note'>{latest_season}</div>"
            + "".join(rows_html)
            + "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='frl-collage-section'>Choose your rabbit hole</div>", unsafe_allow_html=True)
    action_cols = st.columns(3, gap="medium")
    actions = [
        ("Fixtures", "Browse a team's history.", "fixtures"),
        ("Players", "Find someone ridiculous.", "players"),
        ("League table", "See how it actually finished.", "league-table"),
    ]
    for col, (title, description, target) in zip(action_cols, actions):
        with col:
            st.markdown(
                f"<div class='frl-home-card'><div class='frl-home-card-title'>{title}</div><div class='frl-home-card-copy'>{description}</div></div>",
                unsafe_allow_html=True,
            )
            if st.button("Open", key=f"overview_open_{target}", type="tertiary", width="stretch"):
                st.query_params["workspace"] = target
                st.rerun()

    st.markdown(
        "<div class='frl-collage-footer'>Placeholder homepage for now. The proper landing page can be designed once the research tools are finished.</div>",
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
