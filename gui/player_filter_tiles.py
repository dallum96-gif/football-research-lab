"""Compact FRL dashboard filter tiles for the Players workspace."""
from __future__ import annotations

import streamlit as st

import player_research
import player_research_player_match
from gui.player_research_ui import FILTER_OPTIONS, OPERATORS, _render_player_table


def _style_tiles() -> None:
    st.markdown(
        """
        <style>
        .frl-filter-row {
            display:grid;
            grid-template-columns:1.35fr 1fr 1.35fr 1fr 1.12fr;
            gap:.52rem;
            margin:.9rem 0 .55rem;
        }
        .frl-filter-tile {
            min-width:0;
            padding:.62rem .7rem .58rem;
            border:1px solid rgba(24,23,20,.13);
            border-radius:10px;
            background:transparent;
        }
        .frl-filter-tile::before {
            content:"";
            display:block;
            width:1.35rem;
            height:2px;
            margin-bottom:.5rem;
            background:var(--frl-accent);
        }
        .frl-filter-tile-label {
            color:var(--frl-muted-soft);
            font-family:"Source Sans",sans-serif;
            font-size:.54rem;
            font-weight:820;
            letter-spacing:.12em;
            line-height:1;
            text-transform:uppercase;
            margin-bottom:.35rem;
        }
        .frl-filter-tile-value {
            color:var(--frl-text);
            font-family:"Source Sans",sans-serif;
            font-size:.84rem;
            font-weight:760;
            line-height:1.08;
        }
        .frl-filter-tile-note {
            color:var(--frl-muted);
            font-family:"Source Sans",sans-serif;
            font-size:.59rem;
            line-height:1.25;
            margin-top:.16rem;
        }
        .frl-filter-tile .stSelectbox,
        .frl-filter-tile .stNumberInput,
        .frl-filter-tile .stSlider,
        .frl-filter-tile .stToggle {
            margin:0 !important;
            padding:0 !important;
        }
        .frl-filter-tile label {
            display:none !important;
        }
        .frl-filter-tile div[data-baseweb="select"] > div {
            min-height:1.78rem !important;
            height:1.78rem !important;
            padding:0 .08rem !important;
            background:transparent !important;
            border:0 !important;
            border-radius:6px !important;
            box-shadow:none !important;
            color:var(--frl-text) !important;
            font-family:"Source Sans",sans-serif !important;
            font-size:.79rem !important;
            font-weight:760 !important;
        }
        .frl-filter-tile div[data-baseweb="select"] > div:hover,
        .frl-filter-tile div[data-baseweb="select"] > div:focus-within {
            background:rgba(232,93,63,.045) !important;
        }
        .frl-filter-tile input {
            min-height:1.78rem !important;
            height:1.78rem !important;
            padding:.1rem .05rem !important;
            background:transparent !important;
            border:0 !important;
            border-bottom:1px solid rgba(24,23,20,.13) !important;
            border-radius:0 !important;
            box-shadow:none !important;
            color:var(--frl-text) !important;
            font-family:"Source Sans",sans-serif !important;
            font-size:.78rem !important;
            font-weight:720 !important;
        }
        .frl-filter-tile input:focus {
            border-bottom-color:var(--frl-accent) !important;
            box-shadow:none !important;
        }
        .frl-filter-tile [data-testid="stSlider"] {
            padding-top:.18rem !important;
        }
        .frl-filter-tile [data-testid="stSlider"] [role="slider"] {
            background:var(--frl-accent) !important;
        }
        .frl-filter-tile-advanced {
            border-color:rgba(232,93,63,.30);
        }
        .frl-filter-tile-advanced::before {
            background:var(--frl-text);
        }
        .frl-filter-tile-advanced [data-testid="stToggle"] label {
            display:flex !important;
            align-items:center !important;
            gap:.3rem !important;
            color:var(--frl-text) !important;
            font-family:"Source Sans",sans-serif !important;
            font-size:.68rem !important;
            font-weight:760 !important;
        }
        .frl-filter-advanced-panel {
            margin:.3rem 0 .7rem;
            padding:.7rem .05rem .75rem;
            border-top:1px solid rgba(24,23,20,.14);
            border-bottom:1px solid rgba(24,23,20,.10);
        }
        .frl-filter-advanced-title {
            color:var(--frl-text);
            font-family:"Source Sans",sans-serif;
            font-size:.72rem;
            font-weight:800;
            letter-spacing:.04em;
            margin-bottom:.18rem;
        }
        .frl-filter-advanced-note {
            color:var(--frl-muted);
            font-family:"Source Sans",sans-serif;
            font-size:.64rem;
            margin-bottom:.55rem;
        }
        .frl-filter-add button {
            min-height:1.7rem !important;
            height:1.7rem !important;
            padding:.12rem .42rem !important;
            border:0 !important;
            border-radius:999px !important;
            background:transparent !important;
            color:var(--frl-accent) !important;
            box-shadow:none !important;
            font-family:"Source Sans",sans-serif !important;
            font-size:.66rem !important;
            font-weight:780 !important;
        }
        .frl-filter-add button:hover {
            background:rgba(232,93,63,.06) !important;
        }
        .frl-player-search input {
            min-height:1.9rem !important;
            height:1.9rem !important;
            background:transparent !important;
            border:0 !important;
            border-bottom:1px solid rgba(24,23,20,.14) !important;
            border-radius:0 !important;
            box-shadow:none !important;
            font-family:"Source Sans",sans-serif !important;
            font-size:.72rem !important;
        }
        .frl-player-search input:focus {
            border-bottom-color:var(--frl-accent) !important;
            box-shadow:none !important;
        }
        .frl-active-filters {
            display:flex;
            flex-wrap:wrap;
            gap:.28rem;
            margin:.34rem 0 .55rem;
        }
        .frl-active-filter {
            display:inline-flex;
            align-items:center;
            min-height:1.45rem;
            padding:.14rem .46rem;
            border-radius:999px;
            background:rgba(232,93,63,.055);
            color:var(--frl-text);
            font-family:"Source Sans",sans-serif;
            font-size:.61rem;
            font-weight:700;
        }
        @media (max-width:950px) {
            .frl-filter-row { grid-template-columns:repeat(2,minmax(0,1fr)); }
        }
        @media (max-width:620px) {
            .frl-filter-row { grid-template-columns:1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _enrich_verified_passing(players: list[dict]) -> list[dict]:
    """Add verified player-match passing values while failing closed."""
    enriched = player_research_player_match.enrich_players(players)
    mapping = {
        "attempted_passes": "player_match_passes",
        "completed_passes": "player_match_accurate_passes",
        "key_passes": "player_match_key_passes",
        "big_chances_created": "player_match_big_chances_created",
    }
    for player in enriched:
        verified = player.get("player_match_identity_status") == "VERIFIED"
        for target, source in mapping.items():
            player[target] = player.get(source) if verified else None
    return enriched


def _active_filter_chips(
    selected_seasons: list[str],
    position: str,
    club_query: str,
    minimum_minutes: int,
    filters: list[tuple[str, str, float]],
) -> None:
    chips = []
    if len(selected_seasons) == 1:
        chips.append(selected_seasons[0])
    else:
        chips.append(f"{selected_seasons[0]} – {selected_seasons[-1]}")
    if position != "All positions":
        chips.append(position)
    if club_query.strip():
        chips.append(club_query.strip())
    if minimum_minutes:
        chips.append(f"≥ {minimum_minutes:,} mins")
    for metric, operator, value in filters:
        chips.append(f"{metric} {operator.lower()} {value}")

    st.markdown(
        "<div class='frl-active-filters'>" +
        "".join(
            f"<span class='frl-active-filter'>{chip}</span>"
            for chip in chips
        ) +
        "</div>",
        unsafe_allow_html=True,
    )


def render_player_research_ui_tiles() -> None:
    _style_tiles()

    seasons = list(player_research.available_seasons())
    if not seasons:
        st.error("No player data available.")
        return

    st.markdown(
        "<div class='frl-player-intro'>Explore the player data, then build a shortlist from the numbers that interest you.</div>",
        unsafe_allow_html=True,
    )

    mode = st.session_state.get("pr_mode", "Single season")
    if mode not in {"Single season", "Multiple seasons"}:
        mode = "Single season"

    if mode == "Single season":
        selected_season = st.session_state.get("pr_single_season", seasons[-1])
        if selected_season not in seasons:
            selected_season = seasons[-1]
        selected_seasons = [selected_season]
        players = list(player_research.season_players(selected_season))
    else:
        start_season = st.session_state.get("pr_start_season", seasons[max(0, len(seasons) - 5)])
        end_season = st.session_state.get("pr_end_season", seasons[-1])
        if start_season not in seasons:
            start_season = seasons[max(0, len(seasons) - 5)]
        if end_season not in seasons:
            end_season = seasons[-1]
        low = min(seasons.index(start_season), seasons.index(end_season))
        high = max(seasons.index(start_season), seasons.index(end_season))
        selected_seasons = seasons[low:high + 1]
        players = list(player_research.multi_season_players(selected_seasons[0], selected_seasons[-1]))

    positions = sorted({p["position"] for p in players if p.get("position")})
    clubs = sorted({club for p in players for club in p.get("clubs", [])}, key=str.casefold)

    position_options = ["All positions"] + positions
    position = st.session_state.get("pr_position", "All positions")
    if position not in position_options:
        position = "All positions"

    club = st.session_state.get("pr_club", "All clubs")
    if club not in (["All clubs"] + clubs):
        club = "All clubs"

    max_minutes = int(max((p.get("minutes", 0) for p in players), default=0))
    minimum_minutes = min(int(st.session_state.get("pr_min_minutes", 0)), max_minutes)
    minimum_seasons = int(st.session_state.get("pr_min_seasons", 1 if mode == "Multiple seasons" else 0))
    minimum_seasons = max(1, min(minimum_seasons, len(selected_seasons))) if mode == "Multiple seasons" else 0

    tile_cols = st.columns(5, gap="small")

    with tile_cols[0]:
        st.markdown(
            "<div class='frl-filter-tile'><div class='frl-filter-tile-label'>Period</div>",
            unsafe_allow_html=True,
        )
        mode = st.radio(
            "Time range",
            ["Single season", "Multiple seasons"],
            horizontal=True,
            index=0 if mode == "Single season" else 1,
            key="pr_mode",
            label_visibility="collapsed",
        )
        if mode == "Single season":
            selected_season = st.select_slider(
                "Season",
                options=seasons,
                value=selected_seasons[-1],
                key="pr_single_season",
                label_visibility="collapsed",
            )
            selected_seasons = [selected_season]
            players = list(player_research.season_players(selected_season))
        else:
            scope_cols = st.columns(2, gap="small")
            with scope_cols[0]:
                start_season = st.select_slider(
                    "From",
                    options=seasons,
                    value=selected_seasons[0],
                    key="pr_start_season",
                    label_visibility="collapsed",
                )
            with scope_cols[1]:
                end_season = st.select_slider(
                    "To",
                    options=seasons,
                    value=selected_seasons[-1],
                    key="pr_end_season",
                    label_visibility="collapsed",
                )
            low = min(seasons.index(start_season), seasons.index(end_season))
            high = max(seasons.index(start_season), seasons.index(end_season))
            selected_seasons = seasons[low:high + 1]
            players = list(player_research.multi_season_players(selected_seasons[0], selected_seasons[-1]))
        st.markdown("</div>", unsafe_allow_html=True)

    positions = sorted({p["position"] for p in players if p.get("position")})
    clubs = sorted({club for p in players for club in p.get("clubs", [])}, key=str.casefold)
    position_options = ["All positions"] + positions

    with tile_cols[1]:
        st.markdown(
            "<div class='frl-filter-tile'><div class='frl-filter-tile-label'>Position</div>",
            unsafe_allow_html=True,
        )
        position = st.radio(
            "Position",
            position_options,
            horizontal=True,
            index=position_options.index(position) if position in position_options else 0,
            key="pr_position",
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with tile_cols[2]:
        st.markdown(
            "<div class='frl-filter-tile'><div class='frl-filter-tile-label'>Club</div>",
            unsafe_allow_html=True,
        )
        club = st.selectbox(
            "Club",
            ["All clubs"] + clubs,
            index=(["All clubs"] + clubs).index(club) if club in (["All clubs"] + clubs) else 0,
            key="pr_club",
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with tile_cols[3]:
        st.markdown(
            "<div class='frl-filter-tile'><div class='frl-filter-tile-label'>Minutes</div>",
            unsafe_allow_html=True,
        )
        minimum_minutes = st.slider(
            "Minimum minutes",
            min_value=0,
            max_value=int(max((p.get("minutes", 0) for p in players), default=0)),
            value=min(minimum_minutes, int(max((p.get("minutes", 0) for p in players), default=0))),
            step=90,
            key="pr_min_minutes",
            label_visibility="collapsed",
        )
        st.markdown(
            f"<div class='frl-filter-tile-note'>{minimum_minutes:,} minimum minutes</div></div>",
            unsafe_allow_html=True,
        )

    with tile_cols[4]:
        st.markdown(
            "<div class='frl-filter-tile frl-filter-tile-advanced'><div class='frl-filter-tile-label'>Advanced</div>",
            unsafe_allow_html=True,
        )
        advanced = st.toggle(
            "Build a shortlist",
            value=st.session_state.get("pr_advanced", False),
            key="pr_advanced",
        )
        if mode == "Multiple seasons":
            minimum_seasons = st.number_input(
                "Minimum seasons",
                min_value=1,
                max_value=len(selected_seasons),
                value=minimum_seasons,
                step=1,
                format="%d",
                key="pr_min_seasons",
                label_visibility="collapsed",
            )
        st.markdown("</div>", unsafe_allow_html=True)

    filters = []
    if advanced:
        st.markdown(
            "<div class='frl-filter-advanced-panel'>"
            "<div class='frl-filter-advanced-title'>Build a statistical shortlist</div>"
            "<div class='frl-filter-advanced-note'>Choose the statistic, rule and value. Add another condition only when you need it.</div>",
            unsafe_allow_html=True,
        )

        count = st.session_state.get("pr_filter_count", 1)
        for index in range(count):
            metric_col, operator_col, value_col = st.columns([2.2, 1.4, 1.0], gap="small")
            with metric_col:
                metric_label = st.selectbox(
                    "Statistic",
                    list(FILTER_OPTIONS.keys()),
                    key=f"pr_condition_metric_{index}",
                )
            metric, value_type = FILTER_OPTIONS[metric_label]
            with operator_col:
                operator = st.selectbox(
                    "Filter",
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

        if count < 3:
            st.markdown("<div class='frl-filter-add'>", unsafe_allow_html=True)
            if st.button("＋ Add another condition", key=f"pr_add_filter_{count}"):
                st.session_state["pr_filter_count"] = count + 1
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    search = st.text_input(
        "Search players",
        placeholder="Search players by name…",
        key="pr_search",
        label_visibility="collapsed",
    )

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

    filtered = _enrich_verified_passing(filtered)

    _active_filter_chips(
        selected_seasons,
        position,
        "" if club == "All clubs" else club,
        minimum_minutes,
        filters,
    )

    scope_label = (
        f"{selected_seasons[0]} → {selected_seasons[-1]}"
        if len(selected_seasons) > 1
        else selected_seasons[0]
    )

    st.markdown(
        f"<div class='frl-player-result-line'>{len(filtered):,} player(s) · {scope_label}</div>",
        unsafe_allow_html=True,
    )

    if not filtered:
        st.markdown(
            "<div style='color:var(--frl-muted);padding:.9rem 0;border-top:1px solid var(--frl-border);border-bottom:1px solid var(--frl-border);font-size:.8rem;'>No players match the current research scope.</div>",
            unsafe_allow_html=True,
        )
        return

    _render_player_table(filtered)

    with st.expander("Player detail", expanded=False):
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
            f"<div class='frl-player-detail-title'>{player['player_name']}</div>"
            f"<div class='frl-player-detail-note'>{', '.join(player['clubs'])} · {player['position'] or 'Unknown'} · {scope_label}</div>",
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

        with st.expander("Underlying records", expanded=False):
            import pandas as pd
            records = []
            for row in player["_records"]:
                records.append({
                    "Season": row.get("_season", ""),
                    "Player ID": row.get("element", row.get("player_code", "")),
                    "Club": row.get("_club", ""),
                    "Minutes": row.get("minutes", 0),
                    "Goals": row.get("goals_scored", 0),
                    "Assists": row.get("assists", 0),
                    "xG": row.get("expected_goals", 0),
                    "xA": row.get("expected_assists", 0),
                    "FPL points": row.get("total_points", 0),
                })
            st.dataframe(
                pd.DataFrame(records),
                width="stretch",
                hide_index=True,
            )
