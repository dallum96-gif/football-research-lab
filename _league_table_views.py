from pathlib import Path

path = Path(r".\gui\app_redesign.py")
text = path.read_text(encoding="utf-8-sig")

old = '''elif workspace == "league-table":
    seasons = sorted(get_seasons(), key=season_key, reverse=True)
    season = st.selectbox(
        "Season",
        seasons,
        key="redesign_league_table_season",
    ) if seasons else ""

    table = get_league_table(season) if season else {"teams": []}
'''

new = '''elif workspace == "league-table":
    seasons = sorted(
        get_seasons(),
        key=season_key,
        reverse=True,
    )

    st.markdown(
        "<div style='color:var(--frl-accent);font-size:.60rem;"
        "font-weight:820;letter-spacing:.14em;text-transform:uppercase;'>"
        "League Table</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='color:var(--frl-text);font-size:1.65rem;"
        "font-weight:840;letter-spacing:-.04em;margin-top:.15rem;'>"
        "Choose the table view</div>",
        unsafe_allow_html=True,
    )

    view_key = "redesign_league_table_view"

    selected_view = st.session_state.get(
        view_key,
        "Current season",
    )

    view_cols = st.columns(
        3,
        gap="small",
    )

    view_options = [
        "Current season",
        "Historical season",
        "Custom range",
    ]

    for col, option in zip(
        view_cols,
        view_options,
    ):
        with col:
            if st.button(
                option,
                key=f"league_view_{option}",
                type=(
                    "primary"
                    if selected_view == option
                    else "secondary"
                ),
                width="stretch",
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

        st.caption(
            f"Current season · {season}"
        )

        comparison_seasons = [season]

    elif selected_view == "Historical season":
        historical_seasons = [
            value
            for value in seasons
            if value != "2025-26"
        ]

        default_historical = (
            "2024-25"
            if "2024-25" in historical_seasons
            else historical_seasons[0]
            if historical_seasons
            else seasons[0]
        )

        season = st.selectbox(
            "Historical season",
            historical_seasons or seasons,
            index=(
                (historical_seasons or seasons).index(
                    default_historical
                )
                if default_historical
                in (historical_seasons or seasons)
                else 0
            ),
            key="redesign_league_table_historical",
        )

        comparison_seasons = [season]

    else:
        range_cols = st.columns(
            2,
            gap="small",
        )

        with range_cols[0]:
            start_season = st.selectbox(
                "From",
                seasons,
                key="redesign_league_table_range_start",
            )

        with range_cols[1]:
            valid_end_seasons = [
                value
                for value in seasons
                if season_key(value) >= season_key(start_season)
            ]

            end_season = st.selectbox(
                "To",
                valid_end_seasons,
                key="redesign_league_table_range_end",
            )

        comparison_seasons = [
            value
            for value in seasons
            if season_key(start_season)
            <= season_key(value)
            <= season_key(end_season)
        ]

        season = end_season

    table = (
        get_league_table(season)
        if season
        else {"teams": []}
    )
'''

if old not in text:
    raise SystemExit("Current League Table selector block not found. No changes made.")

path.write_text(
    text.replace(old, new, 1),
    encoding="utf-8",
)

print("PASS  League Table view selector upgraded.")
