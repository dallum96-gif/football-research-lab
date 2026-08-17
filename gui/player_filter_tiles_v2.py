"""Modern, compact FRL dashboard filter presentation for Players."""
from __future__ import annotations

import pandas as pd
import streamlit as st

import player_research
import player_research_player_match
from gui.player_research_ui import FILTER_OPTIONS, OPERATORS, _render_player_table


PASSING_MAP = {
    "attempted_passes": "player_match_passes",
    "completed_passes": "player_match_accurate_passes",
    "key_passes": "player_match_key_passes",
    "big_chances_created": "player_match_big_chances_created",
}


def _style():
    st.markdown(
        """
        <style>
        .frl-filter-kicker {
            color:var(--frl-accent);
            font-family:"Source Sans",sans-serif;
            font-size:.52rem;
            font-weight:840;
            letter-spacing:.12em;
            text-transform:uppercase;
            margin-bottom:.18rem;
        }
        .frl-filter-value {
            color:var(--frl-text);
            font-family:"Source Sans",sans-serif;
            font-size:.88rem;
            font-weight:790;
            line-height:1.05;
            letter-spacing:-.01em;
        }
        .frl-filter-note {
            color:var(--frl-muted);
            font-family:"Source Sans",sans-serif;
            font-size:.58rem;
            margin-top:.18rem;
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            border:1px solid rgba(24,23,20,.13) !important;
            border-radius:10px !important;
            background:transparent !important;
            box-shadow:none !important;
            padding:.58rem .68rem .5rem !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color:rgba(232,93,63,.28) !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] label {
            color:var(--frl-muted-soft) !important;
            font-family:"Source Sans",sans-serif !important;
            font-size:.55rem !important;
            font-weight:810 !important;
            letter-spacing:.09em !important;
            text-transform:uppercase !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] div[data-baseweb="select"] > div {
            min-height:1.82rem !important;
            height:1.82rem !important;
            background:transparent !important;
            border:0 !important;
            border-radius:6px !important;
            box-shadow:none !important;
            color:var(--frl-text) !important;
            font-family:"Source Sans",sans-serif !important;
            font-size:.76rem !important;
            font-weight:760 !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] div[data-baseweb="select"] > div:hover,
        [data-testid="stVerticalBlockBorderWrapper"] div[data-baseweb="select"] > div:focus-within {
            background:rgba(232,93,63,.045) !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] input {
            min-height:1.82rem !important;
            height:1.82rem !important;
            background:transparent !important;
            border:0 !important;
            border-bottom:1px solid rgba(24,23,20,.14) !important;
            border-radius:0 !important;
            box-shadow:none !important;
            color:var(--frl-text) !important;
            font-family:"Source Sans",sans-serif !important;
            font-size:.76rem !important;
            font-weight:720 !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] input:focus {
            border-bottom-color:var(--frl-accent) !important;
            box-shadow:none !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stSlider"] {
            padding-top:.05rem !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] [role="slider"] {
            background:var(--frl-accent) !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stToggle"] label {
            color:var(--frl-text) !important;
            font-family:"Source Sans",sans-serif !important;
            font-size:.66rem !important;
            font-weight:760 !important;
            letter-spacing:0 !important;
            text-transform:none !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] [role="radiogroup"] {
            gap:.22rem !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] label {
            min-height:1.65rem !important;
            padding:.16rem .34rem !important;
            border:1px solid rgba(24,23,20,.11) !important;
            border-radius:999px !important;
            background:transparent !important;
            color:var(--frl-muted) !important;
            font-size:.60rem !important;
            font-weight:690 !important;
            letter-spacing:0 !important;
            text-transform:none !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] label:hover {
            border-color:rgba(232,93,63,.30) !important;
            color:var(--frl-text) !important;
        }
        .frl-advanced-panel {
            margin:.45rem 0 .7rem;
            padding:.68rem 0 .72rem;
            border-top:1px solid rgba(24,23,20,.14);
            border-bottom:1px solid rgba(24,23,20,.10);
        }
        .frl-advanced-title {
            color:var(--frl-text);
            font-family:"Source Sans",sans-serif;
            font-size:.75rem;
            font-weight:820;
            letter-spacing:.015em;
        }
        .frl-advanced-note {
            color:var(--frl-muted);
            font-family:"Source Sans",sans-serif;
            font-size:.62rem;
            margin:.12rem 0 .5rem;
        }
        .frl-add-condition button {
            min-height:1.65rem !important;
            height:1.65rem !important;
            padding:.12rem .45rem !important;
            border:0 !important;
            border-radius:999px !important;
            background:transparent !important;
            color:var(--frl-accent) !important;
            box-shadow:none !important;
            font-family:"Source Sans",sans-serif !important;
            font-size:.64rem !important;
            font-weight:780 !important;
        }
        .frl-add-condition button:hover {
            background:rgba(232,93,63,.055) !important;
        }
        .frl-search input {
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
        .frl-search input:focus {
            border-bottom-color:var(--frl-accent) !important;
            box-shadow:none !important;
        }
        .frl-active-filters {
            display:flex;
            flex-wrap:wrap;
            gap:.28rem;
            margin:.32rem 0 .56rem;
        }
        .frl-active-filter {
            min-height:1.42rem;
            display:inline-flex;
            align-items:center;
            padding:.12rem .45rem;
            border-radius:999px;
            background:rgba(232,93,63,.055);
            color:var(--frl-text);
            font-family:"Source Sans",sans-serif;
            font-size:.60rem;
            font-weight:700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _enrich_passing(players: list[dict]) -> list[dict]:
    enriched = player_research_player_match.enrich_players(players)
    for player in enriched:
        verified = player.get("player_match_identity_status") == "VERIFIED"
        for target, source in PASSING_MAP.items():
            player[target] = player.get(source) if verified else None
    return enriched


def render_player_research_ui_tiles() -> None:
    _style()

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
        season = st.session_state.get("pr_single_season", seasons[-1])
        if season not in seasons:
            season = seasons[-1]
        selected_seasons = [season]
        players = list(player_research.season_players(season))
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
    club_options = ["All clubs"] + clubs

    position = st.session_state.get("pr_position", "All positions")
    if position not in position_options:
        position = "All positions"
    club_query = st.session_state.get("pr_club_query", "")
    minimum_minutes = int(st.session_state.get("pr_min_minutes", 0))
    max_minutes = int(max((p.get("minutes", 0) for p in players), default=0))
    minimum_minutes = min(minimum_minutes, max_minutes)
    minimum_seasons = int(st.session_state.get("pr_min_seasons", 1 if mode == "Multiple seasons" else 0))
    if mode == "Multiple seasons":
        minimum_seasons = max(1, min(minimum_seasons, len(selected_seasons)))
    else:
        minimum_seasons = 0

    advanced = st.session_state.get("pr_advanced", False)
    tile_cols = st.columns(5, gap="small")

    with tile_cols[0]:
        with st.container(border=True):
            st.markdown("<div class='frl-filter-kicker'>Period</div>", unsafe_allow_html=True)
            mode = st.radio(
                "Time range",
                ["Single season", "Multiple seasons"],
                index=0 if mode == "Single season" else 1,
                horizontal=True,
                key="pr_mode",
                label_visibility="collapsed",
            )
            if mode == "Single season":
                season = st.select_slider(
                    "Season",
                    options=seasons,
                    value=selected_seasons[-1],
                    key="pr_single_season",
                    label_visibility="collapsed",
                )
                selected_seasons = [season]
                players = list(player_research.season_players(season))
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

    positions = sorted({p["position"] for p in players if p.get("position")})
    position_options = ["All positions"] + positions

    with tile_cols[1]:
        with st.container(border=True):
            st.markdown("<div class='frl-filter-kicker'>Position</div>", unsafe_allow_html=True)
            position = st.radio(
                "Position",
                position_options,
                index=position_options.index(position) if position in position_options else 0,
                horizontal=True,
                key="pr_position",
                label_visibility="collapsed",
            )

    clubs = sorted({club for p in players for club in p.get("clubs", [])}, key=str.casefold)

    with tile_cols[2]:
        with st.container(border=True):
            st.markdown("<div class='frl-filter-kicker'>Club</div>", unsafe_allow_html=True)
            club_query = st.text_input(
                "Club",
                value=club_query,
                placeholder="Any club",
                key="pr_club_query",
                label_visibility="collapsed",
            )
            if club_query.strip():
                matches = [c for c in clubs if club_query.strip().casefold() in c.casefold()]
                st.markdown(
                    f"<div class='frl-filter-note'>{len(matches)} matching club{'s' if len(matches) != 1 else ''}</div>",
                    unsafe_allow_html=True,
                )

    max_minutes = int(max((p.get("minutes", 0) for p in players), default=0))
    minimum_minutes = min(minimum_minutes, max_minutes)

    with tile_cols[3]:
        with st.container(border=True):
            st.markdown("<div class='frl-filter-kicker'>Minutes</div>", unsafe_allow_html=True)
            minimum_minutes = st.slider(
                "Minimum minutes",
                min_value=0,
                max_value=max_minutes,
                value=minimum_minutes,
                step=90,
                key="pr_min_minutes",
                label_visibility="collapsed",
            )
            st.markdown(
                f"<div class='frl-filter-note'>≥ {minimum_minutes:,} minutes</div>",
                unsafe_allow_html=True,
            )

    with tile_cols[4]:
        with st.container(border=True):
            st.markdown("<div class='frl-filter-kicker'>Advanced</div>", unsafe_allow_html=True)
            advanced = st.toggle(
                "Build a shortlist",
                value=advanced,
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

    filters = []
    if advanced:
        count = st.session_state.get("pr_filter_count", 1)
        st.markdown(
            "<div class='frl-advanced-panel'>"
            "<div class='frl-advanced-title'>Build a statistical shortlist</div>"
            "<div class='frl-advanced-note'>Pick the number that matters, then add another condition only when you need it.</div>",
            unsafe_allow_html=True,
        )
        for index in range(count):
            metric_col, operator_col, value_col = st.columns([2.2, 1.35, 1.0], gap="small")
            with metric_col:
                metric_label = st.selectbox("Statistic", list(FILTER_OPTIONS.keys()), key=f"pr_condition_metric_{index}")
            metric, value_type = FILTER_OPTIONS[metric_label]
            with operator_col:
                operator = st.selectbox("Filter", OPERATORS, key=f"pr_condition_operator_{index}")
            with value_col:
                if value_type == "int":
                    value = st.number_input("Value", min_value=0, value=0, step=1, format="%d", key=f"pr_condition_value_int_{index}")
                else:
                    value = st.number_input("Value", value=0.0, step=0.01, format="%.2f", key=f"pr_condition_value_float_{index}")
            filters.append((metric, operator, value))

        if count < 3:
            st.markdown("<div class='frl-add-condition'>", unsafe_allow_html=True)
            if st.button("＋ Add another condition", key=f"pr_add_filter_{count}"):
                st.session_state["pr_filter_count"] = count + 1
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        search = st.text_input(
            "Search players",
            placeholder="Search players by name…",
            key="pr_search",
            label_visibility="collapsed",
        )

    filtered = player_research.filter_players(
        players,
        position=None if position == "All positions" else position,
        team=None,
        min_minutes=minimum_minutes,
        min_seasons=minimum_seasons,
        filters=filters,
    )

    if club_query.strip():
        needle = club_query.strip().casefold()
        filtered = [
            player
            for player in filtered
            if any(needle in club.casefold() for club in player.get("clubs", []))
        ]

    if search.strip():
        needle = search.strip().casefold()
        filtered = [
            player
            for player in filtered
            if needle in player["player_name"].casefold()
        ]

    filtered = _enrich_passing(filtered)

    chips = [
        selected_seasons[0] if len(selected_seasons) == 1 else f"{selected_seasons[0]} – {selected_seasons[-1]}",
    ]
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
        "".join(f"<span class='frl-active-filter'>{chip}</span>" for chip in chips) +
        "</div>",
        unsafe_allow_html=True,
    )

    scope_label = f"{selected_seasons[0]} → {selected_seasons[-1]}" if len(selected_seasons) > 1 else selected_seasons[0]
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
        player = next(item for item in filtered if item["player_name"] == selected_name)
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
            st.dataframe(pd.DataFrame(records), width="stretch", hide_index=True)
