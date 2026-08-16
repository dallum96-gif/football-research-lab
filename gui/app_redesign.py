from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import query_api

from gui.fixture_explorer import render_fixture_explorer
from gui.fixture_position_sparkline import render_last_five_position_sparkline
from gui.ui_shell import current_workspace, render_workspace_sidebar
from gui.theme import apply_theme, render_brand_header
from gui.player_research_ui import render_player_research_ui


st.set_page_config(
    page_title="Football Research Lab",
    page_icon="âš½",
    layout="wide",
    initial_sidebar_state="locked",
)

apply_theme()


def render_fixture_detail(detail):
    fixture = detail["fixture"]
    stats = detail["stats"]

    home = fixture["home_team_name"]
    away = fixture["away_team_name"]

    home_score = fixture["home_score"] if fixture["home_score"] not in (None, "") else "-"
    away_score = fixture["away_score"] if fixture["away_score"] not in (None, "") else "-"

    home_core = stats["home"]["core"]
    away_core = stats["away"]["core"]

    def display_value(values, label):
        raw = values.get(label)
        if raw in (None, ""):
            return "-"
        try:
            n = float(raw)
            return str(int(n)) if n.is_integer() else f"{n:.1f}"
        except (TypeError, ValueError):
            return str(raw)

    def numeric_value(values, label):
        try:
            return float(values.get(label))
        except (TypeError, ValueError):
            return 0.0

    categories = {
        "Attacking": ["Shots", "Shots on target", "Shots off target", "Blocked shots", "Corners"],
        "Possession": ["Possession", "Passes", "Accurate passes", "Crosses"],
        "Defending": [
            "Tackles", "Tackles won", "Interceptions", "Interceptions won",
            "Clearances", "Effective clearances", "Offsides"
        ],
        "Discipline": ["Fouls won", "Fouls conceded", "Yellow cards", "Red cards"],
    }

    summary_metrics = [
        ("Possession", "Possession"),
        ("Shots", "Shots"),
        ("On target", "Shots on target"),
        ("Corners", "Corners"),
        ("Passes", "Passes"),
        ("Fouls", "Fouls conceded"),
    ]

    # ------------------------------------------------------------
    # MATCH HEADER
    # ------------------------------------------------------------

    st.markdown(
        f"<div style='text-align:center;color:var(--frl-muted-soft);"
        f"font-size:.62rem;font-weight:800;letter-spacing:.14em;"
        f"text-transform:uppercase;'>{fixture['season']} · GW {fixture['gameweek']}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='text-align:center;color:var(--frl-muted);"
        f"font-size:.72rem;margin-top:.18rem;'>{fixture['kickoff_time'][:10]}</div>",
        unsafe_allow_html=True,
    )

    kit_colours = {
        "Manchester United": "#DA291C",
        "Arsenal": "#EF0107",
        "Liverpool": "#C8102E",
        "Manchester City": "#6CABDD",
        "Chelsea": "#034694",
        "Tottenham Hotspur": "#132257",
        "Newcastle United": "#241F20",
        "Aston Villa": "#670E36",
        "West Ham United": "#7A263A",
        "Everton": "#003399",
        "Crystal Palace": "#1B458F",
        "Brighton & Hove Albion": "#0057B8",
        "Nottingham Forest": "#E53233",
        "Fulham": "#111111",
        "Brentford": "#E30613",
        "Bournemouth": "#DA291C",
        "Wolverhampton Wanderers": "#FDB913",
        "Burnley": "#6C1D45",
        "Leeds United": "#FFCD00",
        "Sunderland": "#EB172B",
    }

    def kit_markup(team, side):
        colour = kit_colours.get(team, "#6f7b84")
        alignment = "justify-content:flex-end;" if side == "home" else "justify-content:flex-start;"
        return (
            f"<div style='display:flex;align-items:center;gap:.58rem;"
            f"{alignment}'>"
            f"<span style='display:inline-block;width:26px;height:28px;"
            f"background:{colour};"
            f"clip-path:polygon(22% 0,38% 0,44% 12%,56% 12%,62% 0,"
            f"78% 0,100% 25%,84% 39%,76% 28%,76% 100%,24% 100%,"
            f"24% 28%,16% 39%,0 25%);'></span>"
            f"<span style='color:var(--frl-text);font-size:1.35rem;"
            f"font-weight:820;line-height:1.05;'>{team}</span>"
            f"</div>"
        )

    score_cols = st.columns([1.2, 0.8, 1.2], gap="small", vertical_alignment="center")

    with score_cols[0]:
        st.markdown(
            kit_markup(home, "home"),
            unsafe_allow_html=True,
        )

    with score_cols[1]:
        st.markdown(
            f"<div style='text-align:center;color:var(--frl-text);"
            f"font-size:3rem;font-weight:850;line-height:1;'>"
            f"{home_score}&ndash;{away_score}</div>",
            unsafe_allow_html=True,
        )

    with score_cols[2]:
        st.markdown(
            kit_markup(away, "away"),
            unsafe_allow_html=True,
        )

    if st.button("Back to Fixture Explorer", key="fixture_back_detail", type="tertiary"):
        st.query_params.pop("fixture", None)
        st.rerun()

    if fixture.get("data_corrected") == "true":
        st.info(
            "This fixture contains a verified historical data correction. "
            "The analytical view uses the corrected kickoff and result."
        )

    if stats["status"] != "AVAILABLE":
        st.warning("Historical match statistics are not available for this fixture.")
        return

    # ------------------------------------------------------------
    # MATCH AT A GLANCE
    # ------------------------------------------------------------

    st.markdown(
        "<div style='margin-top:1.15rem;color:var(--frl-accent);"
        "font-size:.60rem;font-weight:820;letter-spacing:.14em;"
        "text-transform:uppercase;'>Match at a glance</div>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        cols = st.columns(6, gap="small")

        for col, (label, key) in zip(cols, summary_metrics):
            with col:
                st.caption(label)

                st.markdown(
                    f"<div style='color:var(--frl-secondary);font-size:.66rem;"
                    f"font-weight:800;'>{home}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div style='color:var(--frl-text);font-size:1.08rem;"
                    f"font-weight:850;line-height:1;'>{display_value(home_core, key)}</div>",
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"<div style='color:var(--frl-accent);font-size:.66rem;"
                    f"font-weight:800;margin-top:.28rem;'>{away}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div style='color:var(--frl-text);font-size:1.08rem;"
                    f"font-weight:850;line-height:1;'>{display_value(away_core, key)}</div>",
                    unsafe_allow_html=True,
                )

    # ------------------------------------------------------------
    # DETAILED STATS
    # ------------------------------------------------------------

    st.markdown(
        "<div style='margin-top:1.35rem;color:var(--frl-accent);"
        "font-size:.60rem;font-weight:820;letter-spacing:.14em;"
        "text-transform:uppercase;'>Investigate the match</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='color:var(--frl-text);font-size:1.15rem;"
        "font-weight:820;margin:.15rem 0 .2rem;'>Match statistics</div>",
        unsafe_allow_html=True,
    )

    st.caption("View by category")

    category_key = f"fixture_stat_category_{fixture['fixture_id']}"
    selected_category = st.session_state.get(category_key, "Attacking")

    category_cols = st.columns(4, gap="small")

    for col, category_name in zip(category_cols, categories):
        with col:
            active = selected_category == category_name

            if st.button(
                category_name,
                key=f"fixture_category_{fixture['fixture_id']}_{category_name}",
                type="primary" if active else "secondary",
                width="stretch",
            ):
                st.session_state[category_key] = category_name
                st.rerun()

    labels = [
        label
        for label in categories[selected_category]
        if label in home_core or label in away_core
    ]

    with st.container(border=True):
        header = st.columns([1.5, 1, 1], gap="small")

        header[0].markdown(
            "<div style='color:var(--frl-muted-soft);font-size:.56rem;"
            "font-weight:820;letter-spacing:.10em;text-transform:uppercase;'>"
            "Statistic</div>",
            unsafe_allow_html=True,
        )
        header[1].markdown(
            f"<div style='text-align:right;color:var(--frl-secondary);"
            f"font-size:.56rem;font-weight:820;letter-spacing:.08em;"
            f"text-transform:uppercase;'>{home}</div>",
            unsafe_allow_html=True,
        )
        header[2].markdown(
            f"<div style='text-align:right;color:var(--frl-accent);"
            f"font-size:.56rem;font-weight:820;letter-spacing:.08em;"
            f"text-transform:uppercase;'>{away}</div>",
            unsafe_allow_html=True,
        )

        st.divider()

        for label in labels:
            hv = numeric_value(home_core, label)
            av = numeric_value(away_core, label)

            home_colour = "#3f7f52" if hv > av else "var(--frl-text)"
            away_colour = "#e85d3f" if av > hv else "var(--frl-text)"

            row = st.columns([1.5, 1, 1], gap="small")

            with row[0]:
                st.markdown(
                    f"<div style='color:var(--frl-text);font-size:.73rem;"
                    f"font-weight:720;padding:.28rem 0;'>{label}</div>",
                    unsafe_allow_html=True,
                )

            with row[1]:
                st.markdown(
                    f"<div style='text-align:right;color:{home_colour};"
                    f"font-size:.82rem;font-weight:850;padding:.28rem 0;'>"
                    f"{display_value(home_core, label)}</div>",
                    unsafe_allow_html=True,
                )

            with row[2]:
                st.markdown(
                    f"<div style='text-align:right;color:{away_colour};"
                    f"font-size:.82rem;font-weight:850;padding:.28rem 0;'>"
                    f"{display_value(away_core, label)}</div>",
                    unsafe_allow_html=True,
                )

            st.markdown(
                "<div style='height:1px;background:var(--frl-border);'></div>",
                unsafe_allow_html=True,
            )

    with st.expander("Additional statistics", expanded=False):
        with st.container(border=True):
            optional = stats["home"]["optional"]

            for label in optional:
                row = st.columns([1.5, 1, 1], gap="small")

                with row[0]:
                    st.markdown(
                        f"<div style='color:var(--frl-text);font-size:.70rem;"
                        f"font-weight:700;padding:.22rem 0;'>{label}</div>",
                        unsafe_allow_html=True,
                    )

                with row[1]:
                    st.markdown(
                        f"<div style='text-align:right;color:var(--frl-text);"
                        f"font-size:.76rem;font-weight:780;'>"
                        f"{display_value(stats['home']['optional'], label)}</div>",
                        unsafe_allow_html=True,
                    )

                with row[2]:
                    st.markdown(
                        f"<div style='text-align:right;color:var(--frl-text);"
                        f"font-size:.76rem;font-weight:780;'>"
                        f"{display_value(stats['away']['optional'], label)}</div>",
                        unsafe_allow_html=True,
                    )

    with st.expander("Data provenance", expanded=False):
        st.write(
            {
                "Canonical fixture ID": fixture["fixture_id"],
                "PL source match ID": stats["source_match_id"],
                "Canonical fixture source": detail["provenance"]["canonical_source"],
                "Identity source": detail["provenance"]["identity_source"],
                "Correction source": detail["provenance"]["correction_source"],
            }
        )

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
def get_head_to_head(team, opponent, seasons):
    return query_api.head_to_head(
        team=team,
        opponent=opponent,
        seasons=seasons,
    )


@st.cache_data
def get_team_form(season, team):
    return query_api.team_form(
        season=season,
        team=team,
    )


@st.cache_data
def get_fixtures(
    season,
    team,
    opponent=None,
    venue=None,
    result=None,
    limit=100,
):
    return query_api.fixtures(
        season=season,
        team=team,
        opponent=opponent,
        venue=venue,
        result=result,
        limit=limit,
    )


render_workspace_sidebar(current_workspace())
render_brand_header()
fixture_token = st.query_params.get("fixture")

if fixture_token:
    try:
        fixture_season, fixture_id = fixture_token.split(":", 1)

        detail = query_api.fixture_detail(
            season=fixture_season,
            fixture_id=fixture_id,
        )

        if st.button(
            "â† Back to Fixture Explorer",
            key="fixture_back_route",
        ):
            del st.query_params["fixture"]
            st.rerun()

        st.divider()
        render_fixture_detail(detail)
        st.stop()

    except Exception as exc:
        st.error(f"Unable to open fixture: {exc}")
        st.stop()

workspace = current_workspace()

if workspace == "overview":
    seasons = sorted(get_seasons(), key=season_key, reverse=True)
    overview_season = "2025-26" if "2025-26" in seasons else (seasons[0] if seasons else "")
    table = get_league_table(overview_season) if overview_season else {"teams": []}
    teams = table.get("teams", [])

    top_scorers = []
    top_red_cards = []
    top_saves = []
    top_own_goals = []
    for metric, target in (("goals", "top_scorers"), ("red_cards", "top_red_cards"), ("saves", "top_saves"), ("own_goals", "top_own_goals")):
        try:
            rows = get_top_players(overview_season, metric, 5).get("results", []) if overview_season else []
        except Exception:
            rows = []
        if target == "top_scorers":
            top_scorers = rows
        elif target == "top_red_cards":
            top_red_cards = rows
        elif target == "top_saves":
            top_saves = rows
        else:
            top_own_goals = rows

    best_points = sorted(teams, key=lambda row: row.get("points", 0), reverse=True)[:6]
    most_saves = top_saves[0] if top_saves else {}
    most_points = max(teams, key=lambda row: row.get("points", 0), default={})
    most_red = top_red_cards[0] if top_red_cards else {}
    most_own_goal = top_own_goals[0] if top_own_goals else {}

    def stat_value(item):
        value = item.get("value", "-")
        try:
            number = float(value)
            return str(int(number)) if number.is_integer() else f"{number:.1f}"
        except (TypeError, ValueError):
            return "-"

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
        .frl-points-card { padding:1rem 1rem 0.85rem; border:1px solid var(--frl-border); border-radius:14px; background:var(--frl-surface); }
        .frl-points-title { color:var(--frl-text); font-size:1.05rem; font-weight:800; }
        .frl-points-note { margin-top:0.22rem; color:var(--frl-muted-soft); font-size:0.68rem; }
        .frl-points-row { display:grid; grid-template-columns:1.65rem minmax(120px, 1fr) 2.3rem; gap:0.55rem; align-items:center; padding:0.58rem 0; border-bottom:1px solid var(--frl-border); }
        .frl-points-row:last-child { border-bottom:0; }
        .frl-points-rank { color:var(--frl-muted-soft); font-size:0.60rem; font-weight:800; }
        .frl-points-team { min-width:0; color:var(--frl-text); font-size:0.72rem; font-weight:720; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
        .frl-points-track { height:0.42rem; margin-top:0.24rem; overflow:hidden; border-radius:999px; background:var(--frl-surface-raised); }
        .frl-points-fill { height:100%; border-radius:999px; background:var(--frl-accent); }
        .frl-points-value { color:var(--frl-text); font-size:0.76rem; font-weight:800; text-align:right; }
        .frl-mini-caption { margin-top:0.55rem; color:var(--frl-muted-soft); font-size:0.65rem; }
        .frl-collage-footer { margin-top:1rem; color:var(--frl-muted-soft); font-size:0.67rem; }
        @media (max-width: 900px) { .frl-fact-row { grid-template-columns:1fr; } .frl-points-row { grid-template-columns:1.4rem minmax(90px, 1fr) 2.1rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='frl-collage-kicker'>A little place to get lost in football</div>", unsafe_allow_html=True)
    st.markdown("<div class='frl-collage-title'>The beautiful game,<br>with receipts.</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='frl-collage-sub'>A playful snapshot of the lab using the 2025/26 Premier League season. Some useful, some gloriously unnecessary.</div>",
        unsafe_allow_html=True,
    )

    fact_cols = st.columns(3, gap="small")
    fact_cards = [
        ("Most saves", stat_value(most_saves), most_saves.get("player", "No recorded data"), True),
        ("Most red cards", stat_value(most_red), most_red.get("player", "No recorded data"), False),
        ("Most own goals", stat_value(most_own_goal), most_own_goal.get("player", "No recorded data"), False),
    ]
    for col, (label, value, copy, accent) in zip(fact_cols, fact_cards):
        with col:
            cls = "frl-fact frl-fact-accent" if accent else "frl-fact"
            st.markdown(
                f"<div class='{cls}'><div class='frl-fact-label'>{label}</div><div class='frl-fact-value'>{value}</div><div class='frl-fact-copy'>{copy} · {overview_season}</div></div>",
                unsafe_allow_html=True,
            )

    left, right = st.columns([1.15, 0.85], gap="medium")
    with left:
        st.markdown("<div class='frl-collage-section'>Points at a glance</div>", unsafe_allow_html=True)
        if best_points:
            max_points = max(row.get("points", 0) for row in best_points) or 1
            rows_html = []
            for rank, row in enumerate(best_points, start=1):
                points = row.get("points", 0)
                width = max(8, round((points / max_points) * 100))
                rows_html.append(
                    f"<div class='frl-points-row'><div class='frl-points-rank'>{rank:02d}</div><div><div class='frl-points-team'>{row.get('team', '-')}</div><div class='frl-points-track'><div class='frl-points-fill' style='width:{width}%;'></div></div></div><div class='frl-points-value'>{points}</div></div>"
                )
            st.markdown(
                "<div class='frl-points-card'>"
                "<div class='frl-points-title'>League table, at a glance</div>"
                f"<div class='frl-points-note'>{overview_season}</div>"
                + "".join(rows_html)
                + "</div>",
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
            f"<div class='frl-player-card-note'>{overview_season}</div>"
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
        render_last_five_position_sparkline(season, team, get_fixtures)
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
    seasons = sorted(
        get_seasons(),
        key=season_key,
        reverse=True,
    )

    st.markdown(
        "<div class='frl-eyebrow'>Explore</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='frl-entity-title'>League Table</div>",
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------
    # Table view
    # ------------------------------------------------------------

    view_key = "league_table_view"
    selected_view = st.session_state.get(
        view_key,
        "Current season",
    )

    st.markdown(
        "<div style='margin-top:.55rem;color:var(--frl-muted-soft);"
        "font-size:.56rem;font-weight:820;letter-spacing:.12em;"
        "text-transform:uppercase;'>Table view</div>",
        unsafe_allow_html=True,
    )

    view_cols = st.columns(3, gap="small")

    for col, option in zip(
        view_cols,
        ["Current season", "Historical season", "Custom range"],
    ):
        with col:
            if st.button(
                option,
                key=f"league_table_view_{option}",
                width="stretch",
                type=(
                    "primary"
                    if selected_view == option
                    else "secondary"
                ),
            ):
                st.session_state[view_key] = option
                st.rerun()

    if not seasons:
        st.error("No seasons available.")
        st.stop()

    if selected_view == "Current season":
        season = (
            "2025-26"
            if "2025-26" in seasons
            else seasons[0]
        )
        comparison_seasons = [season]

    elif selected_view == "Historical season":
        historical = [
            value
            for value in seasons
            if value != "2025-26"
        ]

        options = historical or seasons

        season = st.selectbox(
            "Historical season",
            options,
            index=(
                options.index("2024-25")
                if "2024-25" in options
                else 0
            ),
            key="league_table_historical_season",
        )

        comparison_seasons = [season]

    else:
        range_cols = st.columns(2, gap="small")

        with range_cols[0]:
            start_season = st.selectbox(
                "From",
                seasons,
                key="league_table_range_start",
            )

        valid_end = [
            value
            for value in seasons
            if season_key(value) >= season_key(start_season)
        ]

        with range_cols[1]:
            end_season = st.selectbox(
                "To",
                valid_end,
                key="league_table_range_end",
            )

        comparison_seasons = [
            value
            for value in seasons
            if (
                season_key(start_season)
                <= season_key(value)
                <= season_key(end_season)
            )
        ]

        season = end_season

    # ------------------------------------------------------------
    # Venue
    # ------------------------------------------------------------

    venue_key = "league_table_venue"
    selected_venue = st.session_state.get(
        venue_key,
        "Overall",
    )

    st.markdown(
        "<div style='margin-top:.85rem;color:var(--frl-muted-soft);"
        "font-size:.56rem;font-weight:820;letter-spacing:.12em;"
        "text-transform:uppercase;'>Venue</div>",
        unsafe_allow_html=True,
    )

    venue_cols = st.columns(3, gap="small")

    for col, option in zip(
        venue_cols,
        ["Overall", "Home", "Away"],
    ):
        with col:
            if st.button(
                option,
                key=f"league_table_venue_{option}",
                width="stretch",
                type=(
                    "primary"
                    if selected_venue == option
                    else "secondary"
                ),
            ):
                st.session_state[venue_key] = option
                st.rerun()

    # ------------------------------------------------------------
    # Data source for the existing renderer
    # ------------------------------------------------------------

    def aggregate_league_rows(selected_seasons, venue):
        totals = {}

        for season_value in selected_seasons:
            payload = get_fixtures(
                season=season_value,
                team=None,
                limit=5000,
            )

            for fixture in payload.get("results", []):
                home = fixture["home_team_name"]
                away = fixture["away_team_name"]

                if venue == "Home":
                    sides = [
                        (
                            home,
                            fixture.get("home_score"),
                            fixture.get("away_score"),
                        )
                    ]
                elif venue == "Away":
                    sides = [
                        (
                            away,
                            fixture.get("away_score"),
                            fixture.get("home_score"),
                        )
                    ]
                else:
                    sides = [
                        (
                            home,
                            fixture.get("home_score"),
                            fixture.get("away_score"),
                        ),
                        (
                            away,
                            fixture.get("away_score"),
                            fixture.get("home_score"),
                        ),
                    ]

                for team_name, gf_raw, ga_raw in sides:
                    if team_name not in totals:
                        totals[team_name] = {
                            "team": team_name,
                            "played": 0,
                            "wins": 0,
                            "draws": 0,
                            "losses": 0,
                            "goals_for": 0,
                            "goals_against": 0,
                            "points": 0,
                        }

                    if gf_raw in (None, "") or ga_raw in (None, ""):
                        continue

                    gf = int(gf_raw)
                    ga = int(ga_raw)

                    item = totals[team_name]
                    item["played"] += 1
                    item["goals_for"] += gf
                    item["goals_against"] += ga

                    if gf > ga:
                        item["wins"] += 1
                        item["points"] += 3
                    elif gf == ga:
                        item["draws"] += 1
                        item["points"] += 1
                    else:
                        item["losses"] += 1

        rows = list(totals.values())

        for row in rows:
            row["goal_difference"] = (
                row["goals_for"]
                - row["goals_against"]
            )

        rows.sort(
            key=lambda row: (
                -row["points"],
                -row["goal_difference"],
                -row["goals_for"],
                row["team"].casefold(),
            )
        )

        for position, row in enumerate(rows, start=1):
            row["position"] = position

        return rows

    if (
        len(comparison_seasons) == 1
        and selected_venue == "Overall"
    ):
        table = get_league_table(season)
    else:
        table = {
            "teams": aggregate_league_rows(
                comparison_seasons,
                selected_venue,
            )
        }

    league_rows = table.get("teams", [])

    st.markdown(
        f"<div class='frl-context'>Premier League · {season} · "
        f"{selected_venue}</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
        .frl-league-card {
            margin-top: 1.15rem;
            padding: 0.95rem 1rem 0.55rem;
            border: 1px solid var(--frl-border);
            border-radius: 14px;
            background: var(--frl-surface);
        }
        .frl-league-header {
            display: grid;
            grid-template-columns: 2.5rem minmax(170px, 1fr) repeat(9, 3.2rem);
            gap: 0.25rem;
            align-items: center;
            padding: 0 0 0.55rem;
            border-bottom: 1px solid var(--frl-border-strong);
            color: var(--frl-muted-soft);
            font-size: 0.57rem;
            font-weight: 800;
            letter-spacing: 0.09em;
            text-transform: uppercase;
        }
        .frl-league-header div:not(:nth-child(2)) { text-align: center; }

        .frl-league-row {
            display: grid;
            grid-template-columns: 2.5rem minmax(170px, 1fr) repeat(9, 3.2rem);
            gap: 0.25rem;
            align-items: center;
            min-height: 2.65rem;
            border-bottom: 1px solid var(--frl-border);
            color: var(--frl-text);
            font-size: 0.73rem;
        }
        .frl-league-row:last-child { border-bottom: 0; }

        .frl-league-pos {
            color: var(--frl-muted-soft);
            font-size: 0.68rem;
            font-weight: 800;
            text-align: center;
        }

        .frl-league-team {
            min-width: 0;
            font-weight: 760;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .frl-league-num {
            color: var(--frl-muted);
            text-align: center;
            font-variant-numeric: tabular-nums;
        }

        .frl-league-points {
            color: var(--frl-text);
            font-weight: 850;
            text-align: center;
            font-variant-numeric: tabular-nums;
        }

        .frl-zone-title { border-left: 3px solid var(--frl-secondary); }
        .frl-zone-europe { border-left: 3px solid var(--frl-accent); }
        .frl-zone-relegation { border-left: 3px solid var(--frl-negative); }

        .frl-league-legend {
            display: flex;
            flex-wrap: wrap;
            gap: 0.8rem 1.25rem;
            margin-top: 0.8rem;
            color: var(--frl-muted-soft);
            font-size: 0.63rem;
        }
        .frl-league-legend span::before {
            content: "";
            display: inline-block;
            width: 6px;
            height: 6px;
            margin-right: 0.35rem;
            border-radius: 50%;
            background: var(--frl-muted-soft);
        }
        .frl-league-legend .title::before { background: var(--frl-secondary); }
        .frl-league-legend .europe::before { background: var(--frl-accent); }
        .frl-league-legend .relegation::before { background: var(--frl-negative); }

        @media (max-width: 1000px) {
            .frl-league-card { overflow-x: auto; }
            .frl-league-header,
            .frl-league-row {
                min-width: 660px;
                grid-template-columns: 2.3rem minmax(150px, 1fr) repeat(9, 2.7rem);
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='frl-league-card'>"
        "<div class='frl-league-header'>"
        "<div>Pos</div>"
        "<div>Club</div>"
        "<div>P</div>"
        "<div>W</div>"
        "<div>D</div>"
        "<div>L</div>"
        "<div>GF</div>"
        "<div>GA</div>"
        "<div>GD</div>"
        "<div>Pts</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    row_html = []

    for row in league_rows:
        pos = int(row.get("position", 0) or 0)

        if pos == 1:
            zone_class = "frl-zone-title"
        elif pos <= 6:
            zone_class = "frl-zone-europe"
        elif pos >= max(1, len(league_rows) - 2):
            zone_class = "frl-zone-relegation"
        else:
            zone_class = ""

        row_html.append(
            f"<div class='frl-league-row {zone_class}'>"
            f"<div class='frl-league-pos'>{row.get('position', '—')}</div>"
            f"<div class='frl-league-team'>{row.get('team', '—')}</div>"
            f"<div class='frl-league-num'>{row.get('played', '—')}</div>"
            f"<div class='frl-league-num'>{row.get('wins', '—')}</div>"
            f"<div class='frl-league-num'>{row.get('draws', '—')}</div>"
            f"<div class='frl-league-num'>{row.get('losses', '—')}</div>"
            f"<div class='frl-league-num'>{row.get('goals_for', '—')}</div>"
            f"<div class='frl-league-num'>{row.get('goals_against', '—')}</div>"
            f"<div class='frl-league-num'>{row.get('goal_difference', '—')}</div>"
            f"<div class='frl-league-points'>{row.get('points', '—')}</div>"
            f"</div>"
        )

    st.markdown(
        "".join(row_html) +
        "<div class='frl-league-legend'>"
        "<span class='title'>Champions</span>"
        "<span class='europe'>European places</span>"
        "<span class='relegation'>Relegation zone</span>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

elif workspace == "form":
    seasons = sorted(
        get_seasons(),
        key=season_key,
        reverse=True,
    )

    season = st.selectbox(
        "Season",
        seasons,
        key="form_season",
    ) if seasons else ""

    table = (
        get_league_table(season)
        if season
        else {"teams": []}
    )

    teams = sorted(
        [row["team"] for row in table.get("teams", [])],
        key=str.casefold,
    )

    team = st.selectbox(
        "Team",
        teams,
        key="form_team",
    ) if teams else ""

    st.markdown(
        "<div class='frl-eyebrow'>Explore</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='frl-entity-title'>Form & Streaks</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='frl-context'>{team} · {season}</div>",
        unsafe_allow_html=True,
    )

    form = (
        get_team_form(season, team)
        if season and team
        else {"matches": []}
    )

    matches = form.get("matches", [])

    completed = [
        row for row in matches
        if row.get("home_score") not in (None, "")
        and row.get("away_score") not in (None, "")
    ]

    if not completed:
        st.info(
            "No completed matches are available for this team and season."
        )
    else:
        recent = completed[-10:]

        def form_result(row):
            return (
                row.get("team_result")
                or row.get("result")
                or "-"
            )

        wins = sum(
            1 for row in recent
            if form_result(row) == "W"
        )
        draws = sum(
            1 for row in recent
            if form_result(row) == "D"
        )
        losses = sum(
            1 for row in recent
            if form_result(row) == "L"
        )

        metric_cols = st.columns(4, gap="small")

        metric_cols[0].metric(
            "Last 10",
            len(recent),
        )
        metric_cols[1].metric(
            "Wins",
            wins,
        )
        metric_cols[2].metric(
            "Draws",
            draws,
        )
        metric_cols[3].metric(
            "Losses",
            losses,
        )

        st.markdown(
            "<div style='margin-top:1.25rem;color:var(--frl-accent);"
            "font-size:.60rem;font-weight:820;letter-spacing:.14em;"
            "text-transform:uppercase;'>Recent form</div>",
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            form_cols = st.columns(
                len(recent),
                gap="small",
            )

            for col, row in zip(form_cols, recent):
                result = form_result(row)

                colour = (
                    "#3f7f52"
                    if result == "W"
                    else "#e85d3f"
                    if result == "L"
                    else "#9a7b2f"
                )

                with col:
                    st.markdown(
                        f"<div style='text-align:center;"
                        f"color:var(--frl-muted-soft);font-size:.53rem;"
                        f"font-weight:800;'>GW {row.get('gameweek', '-')}</div>",
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        f"<div style='text-align:center;margin-top:.24rem;"
                        f"padding:.30rem 0;border-radius:7px;"
                        f"background:{colour};color:white;"
                        f"font-size:.86rem;font-weight:850;'>{result}</div>",
                        unsafe_allow_html=True,
                    )

        # Current streaks
        results = [
            form_result(row)
            for row in completed
        ]

        current_result = (
            results[-1]
            if results
            else "-"
        )

        current_result_streak = 0
        for result in reversed(results):
            if result == current_result:
                current_result_streak += 1
            else:
                break

        current_unbeaten = 0
        for result in reversed(results):
            if result in {"W", "D"}:
                current_unbeaten += 1
            else:
                break

        def longest(values, target):
            best = 0
            current = 0

            for value in values:
                if value == target:
                    current += 1
                    best = max(best, current)
                else:
                    current = 0

            return best

        unbeaten_values = [
            "U" if result in {"W", "D"} else "N"
            for result in results
        ]

        streak_cols = st.columns(2, gap="medium")

        with streak_cols[0]:
            st.markdown(
                "<div style='margin-top:1.25rem;color:var(--frl-accent);"
                "font-size:.60rem;font-weight:820;letter-spacing:.14em;"
                "text-transform:uppercase;'>Current streaks</div>",
                unsafe_allow_html=True,
            )

            with st.container(border=True):
                current_rows = [
                    ("Result streak", current_result_streak, current_result),
                    ("Unbeaten", current_unbeaten, "W/D"),
                ]

                for label, amount, suffix in current_rows:
                    cols = st.columns([1.7, .55, .55], gap="small")

                    cols[0].markdown(
                        f"<div style='color:var(--frl-text);font-size:.70rem;"
                        f"font-weight:720;padding:.26rem 0;'>{label}</div>",
                        unsafe_allow_html=True,
                    )
                    cols[1].markdown(
                        f"<div style='text-align:right;color:var(--frl-text);"
                        f"font-size:.95rem;font-weight:850;padding:.26rem 0;'>"
                        f"{amount}</div>",
                        unsafe_allow_html=True,
                    )
                    cols[2].markdown(
                        f"<div style='text-align:right;color:var(--frl-accent);"
                        f"font-size:.60rem;font-weight:820;padding:.26rem 0;'>"
                        f"{suffix}</div>",
                        unsafe_allow_html=True,
                    )

        with streak_cols[1]:
            st.markdown(
                "<div style='margin-top:1.25rem;color:var(--frl-accent);"
                "font-size:.60rem;font-weight:820;letter-spacing:.14em;"
                "text-transform:uppercase;'>Best runs</div>",
                unsafe_allow_html=True,
            )

            with st.container(border=True):
                best_rows = [
                    ("Win streak", longest(results, "W")),
                    ("Unbeaten", longest(unbeaten_values, "U")),
                    ("Loss streak", longest(results, "L")),
                ]

                for label, amount in best_rows:
                    cols = st.columns([1.8, .7], gap="small")

                    cols[0].markdown(
                        f"<div style='color:var(--frl-text);font-size:.70rem;"
                        f"font-weight:720;padding:.26rem 0;'>{label}</div>",
                        unsafe_allow_html=True,
                    )
                    cols[1].markdown(
                        f"<div style='text-align:right;color:var(--frl-text);"
                        f"font-size:.95rem;font-weight:850;padding:.26rem 0;'>"
                        f"{amount}</div>",
                        unsafe_allow_html=True,
                    )

        st.markdown(
            "<div style='margin-top:1.25rem;color:var(--frl-accent);"
            "font-size:.60rem;font-weight:820;letter-spacing:.14em;"
            "text-transform:uppercase;'>Match history</div>",
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            for row in reversed(completed):
                result = form_result(row)

                colour = (
                    "#3f7f52"
                    if result == "W"
                    else "#e85d3f"
                    if result == "L"
                    else "#9a7b2f"
                )

                cols = st.columns(
                    [.65, 2.2, .9, 2.2, .7],
                    gap="small",
                )

                cols[0].markdown(
                    f"<div style='color:var(--frl-muted-soft);"
                    f"font-size:.62rem;font-weight:800;padding:.24rem 0;'>"
                    f"GW {row.get('gameweek', '-')}</div>",
                    unsafe_allow_html=True,
                )

                cols[1].markdown(
                    f"<div style='text-align:right;color:var(--frl-text);"
                    f"font-size:.72rem;font-weight:720;padding:.24rem 0;'>"
                    f"{row.get('home_team_name', '')}</div>",
                    unsafe_allow_html=True,
                )

                cols[2].markdown(
                    f"<div style='text-align:center;color:var(--frl-text);"
                    f"font-size:.80rem;font-weight:850;padding:.24rem 0;'>"
                    f"{row.get('home_score', '-')}–{row.get('away_score', '-')}</div>",
                    unsafe_allow_html=True,
                )

                cols[3].markdown(
                    f"<div style='color:var(--frl-text);font-size:.72rem;"
                    f"font-weight:720;padding:.24rem 0;'>"
                    f"{row.get('away_team_name', '')}</div>",
                    unsafe_allow_html=True,
                )

                cols[4].markdown(
                    f"<div style='text-align:right;color:{colour};"
                    f"font-size:.75rem;font-weight:850;padding:.24rem 0;'>"
                    f"{result}</div>",
                    unsafe_allow_html=True,
                )

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



