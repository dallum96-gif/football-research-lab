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
        return f"{int(round(value))}"

    return f"{value:.{decimals}f}"


def render_player_research_ui():
    st.title("Players")
    st.caption(
        "Search, filter and compare player performance across time."
    )

    seasons = list(
        player_research.available_seasons()
    )

    # ---------------------------------------------------------
    # Time range
    # ---------------------------------------------------------

    mode = st.radio(
        "Time range",
        ["Single season", "Multiple seasons"],
        horizontal=True,
        key="player_time_mode",
    )

    if mode == "Single season":
        season = st.selectbox(
            "Season",
            seasons,
            index=len(seasons) - 1,
            key="player_single_season",
        )

        selected_seasons = [season]

        players = list(
            player_research.season_players(
                season
            )
        )

    else:
        start_col, end_col = st.columns(2)

        with start_col:
            start_season = st.selectbox(
                "From",
                seasons,
                index=max(
                    0,
                    len(seasons) - 5,
                ),
                key="player_start_season",
            )

        with end_col:
            end_season = st.selectbox(
                "To",
                seasons,
                index=len(seasons) - 1,
                key="player_end_season",
            )

        start_index = seasons.index(
            start_season
        )
        end_index = seasons.index(
            end_season
        )

        if start_index <= end_index:
            selected_seasons = seasons[
                start_index:end_index + 1
            ]
        else:
            selected_seasons = seasons[
                end_index:start_index + 1
            ]

        players = list(
            player_research.multi_season_players(
                selected_seasons[0],
                selected_seasons[-1],
            )
        )

        st.caption(
            f"{len(selected_seasons)} seasons selected"
        )

    # ---------------------------------------------------------
    # Basic filters
    # ---------------------------------------------------------

    search_col, position_col, club_col = st.columns(
        [2.4, 1.3, 1.8]
    )

    with search_col:
        search = st.text_input(
            "Player",
            placeholder="Search by player name…",
            key="player_search",
        )

    positions = sorted(
        {
            player["position"]
            for player in players
            if player["position"]
        }
    )

    with position_col:
        position = st.selectbox(
            "Position",
            ["Any position"] + positions,
            key="player_position",
        )

    clubs = sorted(
        {
            club
            for player in players
            for club in player["clubs"]
        },
        key=str.casefold,
    )

    with club_col:
        club = st.selectbox(
            "Club",
            ["Any club"] + clubs,
            key="player_club",
        )

    minutes_max = int(
        max(
            (
                player["minutes"]
                for player in players
            ),
            default=0,
        )
    )

    min_col, seasons_col = st.columns(2)

    with min_col:
        minimum_minutes = st.number_input(
            "Minimum minutes",
            min_value=0,
            max_value=minutes_max,
            value=0,
            step=90,
            format="%d",
            key="player_min_minutes",
        )

    with seasons_col:
        if mode == "Multiple seasons":
            minimum_seasons = st.number_input(
                "Minimum seasons played",
                min_value=1,
                max_value=len(
                    selected_seasons
                ),
                value=1,
                step=1,
                format="%d",
                key="player_min_seasons",
            )
        else:
            minimum_seasons = 0

    # ---------------------------------------------------------
    # Conditions
    # ---------------------------------------------------------

    st.markdown("#### Conditions")

    if "player_conditions" not in st.session_state:
        st.session_state[
            "player_conditions"
        ] = []

    add_condition = st.popover(
        "＋ Add condition"
    )

    with add_condition:
        metric_label = st.selectbox(
            "Statistic",
            list(FILTER_OPTIONS.keys()),
            key="player_new_metric",
        )

        metric, metric_type = FILTER_OPTIONS[
            metric_label
        ]

        operator = st.selectbox(
            "Condition",
            OPERATORS,
            key="player_new_operator",
        )

        if metric_type == "int":
            value = st.number_input(
                "Value",
                min_value=0,
                value=0,
                step=1,
                format="%d",
                key="player_new_value_int",
            )
        else:
            value = st.number_input(
                "Value",
                value=0.00,
                step=0.01,
                format="%.2f",
                key="player_new_value_float",
            )

        if st.button(
            "Add",
            type="primary",
            use_container_width=True,
            key="player_add_condition",
        ):
            st.session_state[
                "player_conditions"
            ].append(
                {
                    "label": metric_label,
                    "metric": metric,
                    "operator": operator,
                    "value": value,
                }
            )

            st.rerun()

    conditions = st.session_state[
        "player_conditions"
    ]

    if conditions:
        for index, condition in enumerate(
            conditions
        ):
            cols = st.columns(
                [2.4, 1.5, 1.0, 0.4]
            )

            with cols[0]:
                st.write(
                    f"**{condition['label']}**"
                )

            with cols[1]:
                st.write(
                    condition["operator"]
                )

            with cols[2]:
                if condition["metric"] in {
                    "minutes",
                    "starts",
                    "goals",
                    "assists",
                    "clean_sheets",
                    "saves",
                    "tackles",
                    "recoveries",
                    "bps",
                    "bonus",
                    "points",
                }:
                    st.write(
                        str(
                            int(
                                condition["value"]
                            )
                        )
                    )
                else:
                    st.write(
                        fmt(
                            condition["value"],
                            2,
                        )
                    )

            with cols[3]:
                if st.button(
                    "×",
                    key=f"player_remove_condition_{index}",
                ):
                    conditions.pop(index)
                    st.rerun()

        if st.button(
            "Clear conditions",
            key="player_clear_conditions",
        ):
            st.session_state[
                "player_conditions"
            ] = []
            st.rerun()

    else:
        st.caption(
            "No statistical conditions applied."
        )

    # ---------------------------------------------------------
    # Apply filtering
    # ---------------------------------------------------------

    filtered = player_research.filter_players(
        players,
        position=(
            None
            if position == "Any position"
            else position
        ),
        team=(
            None
            if club == "Any club"
            else club
        ),
        min_minutes=minimum_minutes,
        min_seasons=minimum_seasons,
        filters=[
            (
                condition["metric"],
                condition["operator"],
                condition["value"],
            )
            for condition in conditions
        ],
    )

    if search.strip():
        needle = search.strip().casefold()

        filtered = [
            player
            for player in filtered
            if needle in player[
                "player_name"
            ].casefold()
        ]

    # ---------------------------------------------------------
    # Results
    # ---------------------------------------------------------

    st.markdown("#### Results")

    st.caption(
        f"{len(filtered)} player(s) match the current criteria."
    )

    if not filtered:
        st.info(
            "No players match those criteria."
        )
        return

    sort_map = {
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

    sort_col, direction_col = st.columns(
        [2.5, 1]
    )

    with sort_col:
        sort_label = st.selectbox(
            "Sort by",
            list(sort_map.keys()),
            index=3,
            key="player_sort",
        )

    with direction_col:
        descending = st.toggle(
            "Highest first",
            value=True,
            key="player_sort_descending",
        )

    sort_field = sort_map[
        sort_label
    ]

    filtered = sorted(
        filtered,
        key=lambda player: (
            player.get(sort_field)
            if player.get(sort_field)
            is not None
            else ""
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

    # ---------------------------------------------------------
    # Detail
    # ---------------------------------------------------------

    st.markdown("#### Player detail")

    lookup = {
        player["player_name"]:
            player
        for player in filtered
    }

    selected_name = st.selectbox(
        "Player",
        list(lookup.keys()),
        key="player_detail",
    )

    player = lookup[
        selected_name
    ]

    st.divider()

    st.markdown(
        f"### {player['player_name']}"
    )

    st.caption(
        " · ".join(
            [
                ", ".join(
                    player["clubs"]
                ),
                player["position"],
                (
                    f"{player['season_count']} season(s)"
                    if mode == "Multiple seasons"
                    else selected_seasons[0]
                ),
            ]
        )
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

    with st.expander(
        "Research evidence & provenance"
    ):
        st.json(
            {
                "canonical_player":
                    player[
                        "canonical_name"
                    ],
                "seasons":
                    list(
                        player[
                            "seasons"
                        ]
                    ),
                "season_count":
                    player[
                        "season_count"
                    ],
                "source_files":
                    list(
                        player[
                            "_source_files"
                        ]
                    ),
                "source_rows_scanned":
                    sum(
                        len(
                            player_research._load_season_rows(
                                selected_season
                            )
                        )
                        for selected_season
                        in player["seasons"]
                    ),
            }
        )

