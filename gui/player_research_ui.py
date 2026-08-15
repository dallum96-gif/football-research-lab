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

INTEGER_METRICS = {
    metric
    for metric, value_type in FILTER_OPTIONS.values()
    if value_type == "int"
}


def fmt(value, decimals=2):
    if value is None:
        return "—"

    if decimals == 0:
        return f"{int(round(value)):,}"

    return f"{value:.{decimals}f}"


def render_player_research_ui():
    st.subheader("Player Research")

    st.caption(
        "Explore player performance across one season "
        "or a historical range."
    )

    # =========================================================
    # Research scope
    # =========================================================

    st.markdown("#### Research scope")

    seasons = list(
        player_research.available_seasons()
    )

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
            players = list(
                player_research.season_players(
                    season
                )
            )

    else:

        scope_cols = st.columns(2)

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

        start_index = seasons.index(
            start_season
        )
        end_index = seasons.index(
            end_season
        )

        low = min(
            start_index,
            end_index,
        )
        high = max(
            start_index,
            end_index,
        )

        selected_seasons = seasons[
            low:high + 1
        ]

        with st.spinner(
            f"Loading {len(selected_seasons)} seasons…"
        ):
            players = list(
                player_research.multi_season_players(
                    selected_seasons[0],
                    selected_seasons[-1],
                )
            )

        st.caption(
            f"{len(selected_seasons)} seasons selected"
        )

    # =========================================================
    # Player filters
    # =========================================================

    st.markdown("#### Find players")

    search = st.text_input(
        "Player",
        placeholder="Search by player name…",
        key="pr_search",
    )

    filter_cols = st.columns(3)

    positions = sorted(
        {
            player["position"]
            for player in players
            if player["position"]
        }
    )

    clubs = sorted(
        {
            club
            for player in players
            for club in player["clubs"]
        },
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
        max(
            (
                player["minutes"]
                for player in players
            ),
            default=0,
        )
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

    # =========================================================
    # Conditions
    # =========================================================

    st.markdown("#### Conditions")

    condition_count = st.selectbox(
        "Number of conditions",
        [0, 1, 2, 3],
        key="pr_condition_count",
    )

    filters = []

    for index in range(
        condition_count
    ):
        metric_col, operator_col, value_col = st.columns(
            [2.2, 1.4, 1.0]
        )

        with metric_col:
            metric_label = st.selectbox(
                "Statistic",
                list(FILTER_OPTIONS.keys()),
                key=f"pr_condition_metric_{index}",
            )

        metric, value_type = FILTER_OPTIONS[
            metric_label
        ]

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

        filters.append(
            (
                metric,
                operator,
                value,
            )
        )

    # =========================================================
    # Apply filtering
    # =========================================================

    filtered = player_research.filter_players(
        players,
        position=(
            None
            if position == "All positions"
            else position
        ),
        team=(
            None
            if club == "All clubs"
            else club
        ),
        min_minutes=minimum_minutes,
        min_seasons=minimum_seasons,
        filters=filters,
    )

    if search.strip():
        needle = search.strip().casefold()

        filtered = [
            player
            for player in filtered
            if needle
            in player["player_name"].casefold()
        ]

    # =========================================================
    # Results
    # =========================================================

    st.markdown("#### Results")

    st.caption(
        f"{len(filtered)} player(s) match the current criteria."
    )

    if not filtered:
        st.info(
            "No players match the current criteria."
        )
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

    sort_cols = st.columns(
        [2.5, 1]
    )

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

    sort_field = sort_options[
        sort_label
    ]

    filtered = sorted(
        filtered,
        key=lambda player: (
            player.get(sort_field)
            if player.get(sort_field)
            is not None
            else (
                ""
                if sort_field == "player_name"
                else float("-inf")
            )
        ),
        reverse=descending,
    )

    rows = []

    for player in filtered:
        rows.append(
            {
                "Player":
                    player["player_name"],
                "Position":
                    player["position"],
                "Club":
                    ", ".join(
                        player["clubs"]
                    ),
                "Seasons":
                    player["season_count"],
                "Minutes":
                    int(
                        player["minutes"]
                    ),
                "Goals":
                    int(
                        player["goals"]
                    ),
                "Assists":
                    int(
                        player["assists"]
                    ),
                "xG":
                    fmt(
                        player["xg"]
                    ),
                "xA":
                    fmt(
                        player["xa"]
                    ),
                "Goals / 90":
                    fmt(
                        player["goals_per_90"],
                        3,
                    ),
                "xG / 90":
                    fmt(
                        player["xg_per_90"],
                        3,
                    ),
                "xA / 90":
                    fmt(
                        player["xa_per_90"],
                        3,
                    ),
                "FPL":
                    int(
                        player["points"]
                    ),
                "BPS":
                    int(
                        player["bps"]
                    ),
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        width="stretch",
        hide_index=True,
    )

    # =========================================================
    # Player detail
    # =========================================================

    st.markdown("#### Player detail")

    selected_name = st.selectbox(
        "Player",
        [
            player["player_name"]
            for player in filtered
        ],
        key="pr_detail",
    )

    player = next(
        item
        for item in filtered
        if item["player_name"]
        == selected_name
    )

    st.divider()

    st.markdown(
        f"### {player['player_name']}"
    )

    scope_label = (
        (
            f"{selected_seasons[0]} → "
            f"{selected_seasons[-1]}"
        )
        if mode == "Multiple seasons"
        else selected_seasons[0]
    )

    st.caption(
        f"{', '.join(player['clubs'])} · "
        f"{player['position']} · "
        f"{scope_label}"
    )

    metrics = st.columns(6)

    metrics[0].metric(
        "Minutes",
        f"{int(player['minutes']):,}",
    )

    metrics[1].metric(
        "Goals",
        int(player["goals"]),
    )

    metrics[2].metric(
        "Assists",
        int(player["assists"]),
    )

    metrics[3].metric(
        "xG",
        fmt(player["xg"]),
    )

    metrics[4].metric(
        "xA",
        fmt(player["xa"]),
    )

    metrics[5].metric(
        "FPL points",
        int(player["points"]),
    )

    rates = st.columns(5)

    rates[0].metric(
        "Goals / 90",
        fmt(
            player["goals_per_90"],
            3,
        ),
    )

    rates[1].metric(
        "Assists / 90",
        fmt(
            player["assists_per_90"],
            3,
        ),
    )

    rates[2].metric(
        "xG / 90",
        fmt(
            player["xg_per_90"],
            3,
        ),
    )

    rates[3].metric(
        "xA / 90",
        fmt(
            player["xa_per_90"],
            3,
        ),
    )

    rates[4].metric(
        "BPS / 90",
        fmt(
            player["bps_per_90"],
            3,
        ),
    )

    with st.expander(
        "Underlying records"
    ):
        records = []

        for row in player["_records"]:
            records.append(
                {
                    "Season":
                        row.get(
                            "_season",
                            "",
                        ),
                    "Minutes":
                        int(
                            float(
                                row.get(
                                    "minutes",
                                    0,
                                )
                                or 0
                            )
                        ),
                    "Goals":
                        int(
                            float(
                                row.get(
                                    "goals_scored",
                                    0,
                                )
                                or 0
                            )
                        ),
                    "Assists":
                        int(
                            float(
                                row.get(
                                    "assists",
                                    0,
                                )
                                or 0
                            )
                        ),
                    "xG":
                        row.get(
                            "expected_goals",
                            "",
                        ),
                    "xA":
                        row.get(
                            "expected_assists",
                            "",
                        ),
                    "FPL":
                        int(
                            float(
                                row.get(
                                    "total_points",
                                    0,
                                )
                                or 0
                            )
                        ),
                    "BPS":
                        int(
                            float(
                                row.get(
                                    "bps",
                                    0,
                                )
                                or 0
                            )
                        ),
                }
            )

        st.dataframe(
            pd.DataFrame(records),
            width="stretch",
            hide_index=True,
        )
