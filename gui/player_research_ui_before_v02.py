import pandas as pd
import streamlit as st

import player_research


def fmt(value, decimals=2):
    if value is None:
        return "—"

    if decimals == 0:
        return f"{int(round(value))}"

    return f"{value:.{decimals}f}"


def render_player_research_ui():
    st.subheader("Player Research")

    st.caption(
        "Search players, build statistical filters, sort results, "
        "and inspect the underlying gameweek evidence."
    )

    seasons = list(
        player_research.available_seasons()
    )

    if not seasons:
        st.error("No player data is available.")
        return

    season = st.selectbox(
        "Season",
        seasons,
        key="player_ui_season",
    )

    players = list(
        player_research.season_players(season)
    )

    if not players:
        st.warning(
            f"No player records found for {season}."
        )
        return

    # ---------------------------------------------------------
    # Search + basic filters
    # ---------------------------------------------------------

    st.markdown("#### Find players")

    search_col, position_col, club_col = st.columns(
        [2.4, 1.4, 1.8]
    )

    with search_col:
        search = st.text_input(
            "Player",
            placeholder="Search by name…",
            key="player_ui_search",
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
            key="player_ui_position",
        )

    clubs = sorted(
        {
            player["club"]
            for player in players
            if player["club"]
        },
        key=str.casefold,
    )

    club_to_code = {
        player["club"]:
            player["team_code"]
        for player in players
        if player["club"]
    }

    with club_col:
        club = st.selectbox(
            "Club",
            ["Any club"] + clubs,
            key="player_ui_club",
        )

    minutes_col, sort_col, direction_col = st.columns(
        [1.5, 2.0, 1.0]
    )

    max_minutes = int(
        max(
            player["minutes"]
            for player in players
        )
    )

    with minutes_col:
        minimum_minutes = st.slider(
            "Minimum minutes",
            min_value=0,
            max_value=max_minutes,
            value=0,
            step=90,
            key="player_ui_minutes",
        )

    stat_options = {
        "Minutes": "minutes",
        "Starts": "starts",
        "Goals": "goals",
        "Assists": "assists",
        "Clean sheets": "clean_sheets",
        "Saves": "saves",
        "Tackles": "tackles",
        "Recoveries": "recoveries",
        "BPS": "bps",
        "Bonus": "bonus",
        "FPL points": "points",
        "xG": "xg",
        "xA": "xa",
        "xGI": "xgi",
        "Goals / 90": "goals_per_90",
        "Assists / 90": "assists_per_90",
        "xG / 90": "xg_per_90",
        "xA / 90": "xa_per_90",
        "xGI / 90": "xgi_per_90",
        "BPS / 90": "bps_per_90",
    }

    sort_labels = [
        "Player",
        "Position",
        "Club",
        "Appearances",
    ] + list(stat_options.keys())

    with sort_col:
        sort_label = st.selectbox(
            "Sort by",
            sort_labels,
            index=sort_labels.index("Goals"),
            key="player_ui_sort",
        )

    with direction_col:
        descending = st.toggle(
            "Highest first",
            value=True,
            key="player_ui_desc",
        )

    selected_position = (
        None
        if position == "Any position"
        else position
    )

    selected_club_code = (
        None
        if club == "Any club"
        else club_to_code[club]
    )

    # ---------------------------------------------------------
    # Dynamic stat filters
    # ---------------------------------------------------------

    st.markdown("#### Statistical filters")

    if "player_ui_filter_count" not in st.session_state:
        st.session_state[
            "player_ui_filter_count"
        ] = 0

    add_col, reset_col = st.columns(2)

    with add_col:
        if st.button(
            "＋ Add filter",
            disabled=(
                st.session_state[
                    "player_ui_filter_count"
                ] >= 5
            ),
            use_container_width=True,
            key="player_ui_add",
        ):
            st.session_state[
                "player_ui_filter_count"
            ] += 1
            st.rerun()

    with reset_col:
        if st.button(
            "Reset stat filters",
            use_container_width=True,
            key="player_ui_reset",
        ):
            st.session_state[
                "player_ui_filter_count"
            ] = 0
            st.rerun()

    operators = [
        "At least",
        "At most",
        "Greater than",
        "Less than",
        "Equals",
    ]

    filters = []

    for index in range(
        st.session_state[
            "player_ui_filter_count"
        ]
    ):
        stat_col, operator_col, value_col, remove_col = (
            st.columns(
                [2.3, 1.5, 1.2, 0.5]
            )
        )

        with stat_col:
            stat_label = st.selectbox(
                "Statistic",
                list(stat_options.keys()),
                key=f"player_ui_stat_{index}",
            )

        with operator_col:
            operator = st.selectbox(
                "Condition",
                operators,
                key=f"player_ui_operator_{index}",
            )

        with value_col:
            value = st.number_input(
                "Value",
                value=0.0,
                step=0.1,
                key=f"player_ui_value_{index}",
            )

        with remove_col:
            st.write("")
            if st.button(
                "×",
                help="Remove filter",
                key=f"player_ui_remove_{index}",
            ):
                st.session_state[
                    "player_ui_filter_count"
                ] -= 1
                st.rerun()

        filters.append(
            (
                stat_options[stat_label],
                operator,
                value,
            )
        )

    # ---------------------------------------------------------
    # Execute filter
    # ---------------------------------------------------------

    filtered = player_research.filter_players(
        players,
        position=selected_position,
        team_code=selected_club_code,
        min_minutes=minimum_minutes,
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

    def sort_value(player):
        if sort_label == "Player":
            return player["player_name"].casefold()

        if sort_label == "Position":
            return player["position"].casefold()

        if sort_label == "Club":
            return player["club"].casefold()

        if sort_label == "Appearances":
            return player["appearances"]

        field = stat_options[sort_label]

        return (
            player[field]
            if player[field] is not None
            else float("-inf")
        )

    filtered = sorted(
        filtered,
        key=sort_value,
        reverse=descending,
    )

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

    result_rows = []

    for player in filtered:
        result_rows.append(
            {
                "Player":
                    player["player_name"],
                "Position":
                    player["position"],
                "Club":
                    player["club"],
                "Apps":
                    player["appearances"],
                "Minutes":
                    int(player["minutes"]),
                "Goals":
                    int(player["goals"]),
                "Assists":
                    int(player["assists"]),
                "xG":
                    fmt(player["xg"]),
                "xA":
                    fmt(player["xa"]),
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
                    int(player["points"]),
                "BPS":
                    int(player["bps"]),
            }
        )

    st.dataframe(
        pd.DataFrame(result_rows),
        width="stretch",
        hide_index=True,
    )

    # ---------------------------------------------------------
    # Detail
    # ---------------------------------------------------------

    st.markdown("#### Player detail")

    player_lookup = {
        player["player_name"]:
            player["player_code"]
        for player in filtered
    }

    selected_name = st.selectbox(
        "Open player",
        list(player_lookup.keys()),
        key="player_ui_detail",
    )

    player = player_research.player_detail(
        season,
        player_lookup[selected_name],
    )

    if not player:
        return

    st.divider()

    st.markdown(
        f"### {player['player_name']}"
    )

    st.caption(
        f"{player['club']} · "
        f"{player['position']} · "
        f"{season}"
    )

    metric_cols = st.columns(6)

    metric_cols[0].metric(
        "Minutes",
        int(player["minutes"]),
    )
    metric_cols[1].metric(
        "Starts",
        int(player["starts"]),
    )
    metric_cols[2].metric(
        "Goals",
        int(player["goals"]),
    )
    metric_cols[3].metric(
        "Assists",
        int(player["assists"]),
    )
    metric_cols[4].metric(
        "xG",
        fmt(player["xg"]),
    )
    metric_cols[5].metric(
        "xA",
        fmt(player["xa"]),
    )

    rate_cols = st.columns(6)

    rate_cols[0].metric(
        "Goals / 90",
        fmt(
            player["goals_per_90"],
            3,
        ),
    )
    rate_cols[1].metric(
        "Assists / 90",
        fmt(
            player["assists_per_90"],
            3,
        ),
    )
    rate_cols[2].metric(
        "xG / 90",
        fmt(
            player["xg_per_90"],
            3,
        ),
    )
    rate_cols[3].metric(
        "xA / 90",
        fmt(
            player["xa_per_90"],
            3,
        ),
    )
    rate_cols[4].metric(
        "BPS / 90",
        fmt(
            player["bps_per_90"],
            3,
        ),
    )
    rate_cols[5].metric(
        "FPL points",
        int(player["points"]),
    )

    with st.expander(
        "Underlying gameweek records"
    ):
        detail_rows = []

        for row in player["_records"]:
            def safe_int(value):
                try:
                    return int(
                        float(value or 0)
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    return 0

            detail_rows.append(
                {
                    "Fixture":
                        row.get(
                            "fixture_code",
                            "",
                        ),
                    "Minutes":
                        safe_int(
                            row.get("minutes")
                        ),
                    "Goals":
                        safe_int(
                            row.get(
                                "goals_scored"
                            )
                        ),
                    "Assists":
                        safe_int(
                            row.get(
                                "assists"
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
                        safe_int(
                            row.get(
                                "total_points"
                            )
                        ),
                    "BPS":
                        safe_int(
                            row.get("bps")
                        ),
                }
            )

        st.dataframe(
            pd.DataFrame(detail_rows),
            width="stretch",
            hide_index=True,
        )

    with st.expander(
        "Research evidence & provenance"
    ):
        st.json(
            player["_evidence"]
        )
