from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

import player_research


FILTER_OPTIONS = {
    "Minutes": ("minutes", "int"),
    "Starts": ("starts", "int"),
    "Goals": ("goals", "int"),
    "Assists": ("assists", "int"),
    "Clean sheets": ("clean_sheets", "int"),
    "Saves": ("saves", "int"),
    "Tackles": ("tackles", "int"),
    "Recoveries": ("recoveries", "int"),
    "BPS": ("bps", "int"),
    "Bonus": ("bonus", "int"),
    "FPL points": ("points", "int"),
    "xG": ("xg", "float"),
    "xA": ("xa", "float"),
    "xGI": ("xgi", "float"),
    "Goals / 90": ("goals_per_90", "float"),
    "Assists / 90": ("assists_per_90", "float"),
    "xG / 90": ("xg_per_90", "float"),
    "xA / 90": ("xa_per_90", "float"),
    "xGI / 90": ("xgi_per_90", "float"),
    "BPS / 90": ("bps_per_90", "float"),
}

OPERATORS = [
    "At least",
    "At most",
    "Greater than",
    "Less than",
    "Equals",
]


def fmt(value, decimals=2):
    if value is None:
        return "—"
    if decimals == 0:
        return f"{int(round(value)):,}"
    return f"{value:.{decimals}f}"


def _player_css():
    st.markdown(
        """
        <style>
        .frl-player-hero {
            margin-top: .9rem;
            padding: 1.1rem 1.15rem 1rem;
            border: 1px solid var(--frl-border);
            border-radius: 14px;
            background: var(--frl-surface);
        }
        .frl-player-hero-kicker {
            color: var(--frl-accent);
            font-size: .57rem;
            font-weight: 820;
            letter-spacing: .14em;
            text-transform: uppercase;
        }
        .frl-player-hero-title {
            margin-top: .38rem;
            color: var(--frl-text);
            font-size: clamp(1.55rem, 2.7vw, 2.15rem);
            font-weight: 840;
            letter-spacing: -.04em;
            line-height: 1.03;
        }
        .frl-player-hero-note {
            margin-top: .35rem;
            color: var(--frl-muted);
            font-size: .71rem;
            line-height: 1.35;
        }
        .frl-player-card {
            padding: .88rem .95rem;
            border: 1px solid var(--frl-border);
            border-radius: 12px;
            background: var(--frl-surface);
        }
        .frl-player-card-label {
            color: var(--frl-muted-soft);
            font-size: .55rem;
            font-weight: 820;
            letter-spacing: .11em;
            text-transform: uppercase;
        }
        .frl-player-card-value {
            margin-top: .23rem;
            color: var(--frl-text);
            font-size: 1.45rem;
            font-weight: 850;
            letter-spacing: -.03em;
        }
        .frl-player-card-note {
            margin-top: .12rem;
            color: var(--frl-muted);
            font-size: .63rem;
        }
        .frl-player-section {
            margin-top: 1.1rem;
            margin-bottom: .42rem;
            color: var(--frl-accent);
            font-size: .60rem;
            font-weight: 820;
            letter-spacing: .14em;
            text-transform: uppercase;
        }
        .frl-player-note {
            color: var(--frl-muted-soft);
            font-size: .67rem;
            line-height: 1.35;
        }
        .frl-player-result-note {
            color: var(--frl-muted);
            font-size: .70rem;
            margin-top: .28rem;
        }
        .frl-player-detail-title {
            color: var(--frl-text);
            font-size: 1.35rem;
            font-weight: 830;
            letter-spacing: -.03em;
        }
        .frl-player-detail-note {
            margin-top: .2rem;
            color: var(--frl-muted);
            font-size: .68rem;
        }
        div[data-testid="stRadio"] label,
        div[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
            color: var(--frl-text) !important;
        }
        div[data-testid="stNumberInput"] label,
        div[data-testid="stTextInput"] label,
        div[data-testid="stSelectbox"] label {
            color: var(--frl-muted-soft) !important;
            font-size: .56rem !important;
            font-weight: 820 !important;
            letter-spacing: .10em !important;
            text-transform: uppercase !important;
        }
        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input {
            background: var(--frl-surface-raised) !important;
            color: var(--frl-text) !important;
            border: 1px solid var(--frl-border) !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }
        div[data-baseweb="select"] * {
            color: var(--frl-text) !important;
        }
        div[data-baseweb="select"] > div:hover,
        div[data-baseweb="select"] > div:focus-within,
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stNumberInput"] input:focus {
            border-color: var(--frl-accent) !important;
            box-shadow: 0 0 0 2px rgba(232,93,63,.09) !important;
        }
        div[data-baseweb="popover"],
        div[data-baseweb="menu"] {
            background: var(--frl-surface) !important;
            border-color: var(--frl-border) !important;
        }
        div[data-baseweb="menu"] li {
            color: var(--frl-text) !important;
        }
        div[data-baseweb="menu"] li:hover {
            background: rgba(232,93,63,.08) !important;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--frl-border) !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            background: var(--frl-surface) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_player_research_ui():
    _player_css()

    st.markdown(
        "<div class='frl-player-hero'>"
        "<div class='frl-player-hero-kicker'>Research</div>"
        "<div class='frl-player-hero-title'>Find the players worth investigating.</div>"
        "<div class='frl-player-hero-note'>Search, filter and compare Premier League player performance across seasons without leaving the lab.</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='frl-player-section'>Research scope</div>",
        unsafe_allow_html=True,
    )

    seasons = list(player_research.available_seasons())
    if not seasons:
        st.error("No player data available.")
        return

    mode = st.radio(
        "Time range",
        ["Single season", "Multiple seasons"],
        horizontal=True,
        key="pr_mode",
    )

    if mode == "Single season":
        season = st.selectbox(
            "Season",
            seasons,
            index=len(seasons) - 1,
            key="pr_single_season",
        )
        selected_seasons = [season]
        with st.spinner("Loading players…"):
            players = list(player_research.season_players(season))
    else:
        scope_cols = st.columns(2, gap="medium")
        with scope_cols[0]:
            start_season = st.selectbox(
                "From",
                seasons,
                index=max(0, len(seasons) - 5),
                key="pr_start_season",
            )
        with scope_cols[1]:
            end_season = st.selectbox(
                "To",
                seasons,
                index=len(seasons) - 1,
                key="pr_end_season",
            )

        low = min(seasons.index(start_season), seasons.index(end_season))
        high = max(seasons.index(start_season), seasons.index(end_season))
        selected_seasons = seasons[low:high + 1]

        with st.spinner(f"Loading {len(selected_seasons)} seasons…"):
            players = list(
                player_research.multi_season_players(
                    selected_seasons[0],
                    selected_seasons[-1],
                )
            )

    scope_label = (
        f"{selected_seasons[0]} → {selected_seasons[-1]}"
        if len(selected_seasons) > 1
        else selected_seasons[0]
    )

    st.markdown(
        "<div class='frl-player-section'>Scope at a glance</div>",
        unsafe_allow_html=True,
    )

    scope_cards = st.columns(3, gap="small")
    scope_items = [
        ("Seasons", len(selected_seasons), scope_label),
        ("Players", len(players), "available in this scope"),
        ("Positions", len({p['position'] for p in players if p['position']}), "represented"),
    ]
    for col, (label, value, note) in zip(scope_cards, scope_items):
        with col:
            st.markdown(
                f"<div class='frl-player-card'><div class='frl-player-card-label'>{label}</div>"
                f"<div class='frl-player-card-value'>{value:,}</div>"
                f"<div class='frl-player-card-note'>{note}</div></div>",
                unsafe_allow_html=True,
            )

    st.markdown(
        "<div class='frl-player-section'>Find players</div>",
        unsafe_allow_html=True,
    )

    search = st.text_input(
        "Player",
        placeholder="Search by player name…",
        key="pr_search",
    )

    filter_cols = st.columns(3, gap="medium")

    positions = sorted(
        {player["position"] for player in players if player["position"]}
    )
    clubs = sorted(
        {club for player in players for club in player["clubs"]},
        key=str.casefold,
    )

    with filter_cols[0]:
        position = st.selectbox(
            "Position",
            ["All positions"] + positions,
            key="pr_position",
        )

    with filter_cols[1]:
        club = st.selectbox(
            "Club",
            ["All clubs"] + clubs,
            key="pr_club",
        )

    max_minutes = int(
        max((player["minutes"] for player in players), default=0)
    )

    with filter_cols[2]:
        minimum_minutes = st.number_input(
            "Minimum minutes",
            min_value=0,
            max_value=max_minutes,
            value=0,
            step=90,
            format="%d",
            key="pr_min_minutes",
        )

    if mode == "Multiple seasons":
        minimum_seasons = st.number_input(
            "Minimum seasons played",
            min_value=1,
            max_value=len(selected_seasons),
            value=1,
            step=1,
            format="%d",
            key="pr_min_seasons",
        )
    else:
        minimum_seasons = 0

    st.markdown(
        "<div class='frl-player-section'>Conditions</div>",
        unsafe_allow_html=True,
    )

    condition_count = st.selectbox(
        "Number of conditions",
        [0, 1, 2, 3],
        key="pr_condition_count",
    )

    filters = []

    for index in range(condition_count):
        metric_col, operator_col, value_col = st.columns(
            [2.2, 1.4, 1.0],
            gap="small",
        )

        with metric_col:
            metric_label = st.selectbox(
                "Statistic",
                list(FILTER_OPTIONS.keys()),
                key=f"pr_condition_metric_{index}",
            )

        metric, value_type = FILTER_OPTIONS[metric_label]

        with operator_col:
            operator = st.selectbox(
                "Condition",
                OPERATORS,
                key=f"pr_condition_operator_{index}",
            )

        with value_col:
            if value_type == "int":
                value = st.number_input(
                    "Value",
                    min_value=0,
                    value=0,
                    step=1,
                    format="%d",
                    key=f"pr_condition_value_int_{index}",
                )
            else:
                value = st.number_input(
                    "Value",
                    value=0.0,
                    step=0.01,
                    format="%.2f",
                    key=f"pr_condition_value_float_{index}",
                )

        filters.append((metric, operator, value))

    filtered = player_research.filter_players(
        players,
        position=None if position == "All positions" else position,
        team=None if club == "All clubs" else club,
        min_minutes=minimum_minutes,
        min_seasons=minimum_seasons,
        filters=filters,
    )

    if search.strip():
        needle = search.strip().casefold()
        filtered = [
            player
            for player in filtered
            if needle in player["player_name"].casefold()
        ]

    st.markdown(
        "<div class='frl-player-section'>Results</div>",
        unsafe_allow_html=True,
    )

    result_cols = st.columns([2.4, 1.2], gap="small")
    with result_cols[0]:
        st.markdown(
            f"<div class='frl-player-result-note'>{len(filtered):,} player(s) match the current criteria · {scope_label}</div>",
            unsafe_allow_html=True,
        )

    if not filtered:
        st.info("No players match the current criteria.")
        return

    sort_options = {
        "Player": "player_name",
        "Seasons": "season_count",
        "Minutes": "minutes",
        "Goals": "goals",
        "Assists": "assists",
        "xG": "xg",
        "xA": "xa",
        "Goals / 90": "goals_per_90",
        "xG / 90": "xg_per_90",
        "xA / 90": "xa_per_90",
        "FPL points": "points",
        "BPS": "bps",
    }

    sort_cols = st.columns([1.4, 1], gap="medium")

    with sort_cols[0]:
        sort_label = st.selectbox(
            "Sort by",
            list(sort_options.keys()),
            index=3,
            key="pr_sort",
        )

    with sort_cols[1]:
        descending = st.toggle(
            "Highest first",
            value=True,
            key="pr_sort_desc",
        )

    sort_field = sort_options[sort_label]

    filtered = sorted(
        filtered,
        key=lambda player: (
            player.get(sort_field)
            if player.get(sort_field) is not None
            else ("" if sort_field == "player_name" else float("-inf"))
        ),
        reverse=descending,
    )

    rows = []
    for player in filtered:
        rows.append(
            {
                "Player": player["player_name"],
                "Position": player["position"],
                "Club": ", ".join(player["clubs"]),
                "Seasons": player["season_count"],
                "Minutes": int(player["minutes"]),
                "Goals": int(player["goals"]),
                "Assists": int(player["assists"]),
                "xG": fmt(player["xg"]),
                "xA": fmt(player["xa"]),
                "Goals / 90": fmt(player["goals_per_90"], 3),
                "xG / 90": fmt(player["xg_per_90"], 3),
                "xA / 90": fmt(player["xa_per_90"], 3),
                "FPL": int(player["points"]),
                "BPS": int(player["bps"]),
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        width="stretch",
        hide_index=True,
    )

    st.markdown(
        "<div class='frl-player-section'>Player detail</div>",
        unsafe_allow_html=True,
    )

    selected_name = st.selectbox(
        "Player",
        [player["player_name"] for player in filtered],
        key="pr_detail",
    )

    player = next(
        item for item in filtered
        if item["player_name"] == selected_name
    )

    st.markdown(
        "<div class='frl-player-card' style='margin-top:.35rem;'>"
        f"<div class='frl-player-detail-title'>{player['player_name']}</div>"
        f"<div class='frl-player-detail-note'>{', '.join(player['clubs'])} · {player['position']} · {scope_label}</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    metrics = st.columns(6, gap="small")
    metric_values = [
        ("Minutes", f"{int(player['minutes']):,}"),
        ("Goals", int(player["goals"])),
        ("Assists", int(player["assists"])),
        ("xG", fmt(player["xg"])),
        ("xA", fmt(player["xa"])),
        ("FPL points", int(player["points"])),
    ]
    for col, (label, value) in zip(metrics, metric_values):
        with col:
            st.markdown(
                f"<div class='frl-player-card'><div class='frl-player-card-label'>{label}</div>"
                f"<div class='frl-player-card-value'>{value}</div></div>",
                unsafe_allow_html=True,
            )

    rates = st.columns(5, gap="small")
    rate_values = [
        ("Goals / 90", fmt(player["goals_per_90"], 3)),
        ("Assists / 90", fmt(player["assists_per_90"], 3)),
        ("xG / 90", fmt(player["xg_per_90"], 3)),
        ("xA / 90", fmt(player["xa_per_90"], 3)),
        ("BPS / 90", fmt(player["bps_per_90"], 3)),
    ]
    for col, (label, value) in zip(rates, rate_values):
        with col:
            st.markdown(
                f"<div class='frl-player-card'><div class='frl-player-card-label'>{label}</div>"
                f"<div class='frl-player-card-value' style='font-size:1.15rem;'>{value}</div></div>",
                unsafe_allow_html=True,
            )

    with st.expander("Underlying records"):
        records = []
        for row in player["_records"]:
            records.append(
                {
                    "Season": row.get("_season", ""),
                    "Player ID": row.get("element", row.get("player_code", "")),
                    "Club": row.get("_club", ""),
                    "Minutes": row.get("minutes", 0),
                    "Goals": row.get("goals_scored", 0),
                    "Assists": row.get("assists", 0),
                    "xG": row.get("expected_goals", 0),
                    "xA": row.get("expected_assists", 0),
                    "FPL points": row.get("total_points", 0),
                }
            )
        st.dataframe(
            pd.DataFrame(records),
            width="stretch",
            hide_index=True,
        )
