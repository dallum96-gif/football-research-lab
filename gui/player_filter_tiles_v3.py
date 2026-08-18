"""FRL Players dashboard tiles v3: transparent, light, inline filters."""
from __future__ import annotations

import pandas as pd
import streamlit as st

import player_research
import player_research_player_match
from gui.player_research_ui import FILTER_OPTIONS, OPERATORS, _render_player_table, fmt


PASSING_MAP = {
    "attempted_passes": "player_match_passes",
    "completed_passes": "player_match_accurate_passes",
    "key_passes": "player_match_key_passes",
    "big_chances_created": "player_match_big_chances_created",
}


def _style() -> None:
    st.markdown(
        """
        <style>
        .frl-filter-kicker{color:var(--frl-accent);font-family:"Source Sans",sans-serif;font-size:.52rem;font-weight:840;letter-spacing:.12em;text-transform:uppercase;margin-bottom:.2rem}
        .frl-filter-note{color:var(--frl-muted);font-family:"Source Sans",sans-serif;font-size:.58rem;margin-top:.14rem}
        [data-testid="stVerticalBlockBorderWrapper"]{border:1px solid rgba(24,23,20,.13)!important;border-radius:10px!important;background:transparent!important;box-shadow:none!important;padding:.56rem .64rem .48rem!important}
        [data-testid="stVerticalBlockBorderWrapper"]:hover{border-color:rgba(232,93,63,.28)!important}
        [data-testid="stVerticalBlockBorderWrapper"] label{color:var(--frl-muted-soft)!important;font-family:"Source Sans",sans-serif!important;font-size:.54rem!important;font-weight:810!important;letter-spacing:.08em!important;text-transform:uppercase!important}
        [data-testid="stVerticalBlockBorderWrapper"] [data-baseweb="select"]>div{min-height:1.78rem!important;height:1.78rem!important;background:transparent!important;border:0!important;box-shadow:none!important;color:var(--frl-text)!important;font-family:"Source Sans",sans-serif!important;font-size:.75rem!important;font-weight:760!important}
        [data-testid="stVerticalBlockBorderWrapper"] [data-baseweb="select"]>div:hover,[data-testid="stVerticalBlockBorderWrapper"] [data-baseweb="select"]>div:focus-within{background:rgba(232,93,63,.045)!important}
        [data-testid="stVerticalBlockBorderWrapper"] input{min-height:1.78rem!important;height:1.78rem!important;background:transparent!important;border:0!important;border-bottom:1px solid rgba(24,23,20,.14)!important;border-radius:0!important;box-shadow:none!important;color:var(--frl-text)!important;font-family:"Source Sans",sans-serif!important;font-size:.75rem!important}
        [data-testid="stVerticalBlockBorderWrapper"] input:focus{border-bottom-color:var(--frl-accent)!important;box-shadow:none!important}
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] [role="radiogroup"]{gap:.22rem!important}
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] label{min-height:1.58rem!important;padding:.14rem .3rem!important;border:1px solid rgba(24,23,20,.11)!important;border-radius:999px!important;background:transparent!important;color:var(--frl-muted)!important;font-size:.59rem!important;letter-spacing:0!important;text-transform:none!important;font-weight:690!important}
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] label:hover{border-color:rgba(232,93,63,.3)!important;color:var(--frl-text)!important}
        [data-testid="stVerticalBlockBorderWrapper"] [role="radiogroup"] label[data-checked="true"]{border-color:rgba(232,93,63,.5)!important;color:var(--frl-text)!important;background:rgba(232,93,63,.045)!important}
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stSlider"] [role="slider"]{background:var(--frl-accent)!important}
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stToggle"] label{color:var(--frl-text)!important;font-family:"Source Sans",sans-serif!important;font-size:.65rem!important;font-weight:760!important;letter-spacing:0!important;text-transform:none!important}
        /* Never use dark query/selector surfaces. */
        [data-baseweb="menu"],[data-baseweb="popover"],[role="listbox"],[data-testid="stSelectboxVirtualDropdown"]{background:var(--frl-surface)!important;color:var(--frl-text)!important;border:1px solid var(--frl-border)!important;box-shadow:0 8px 24px rgba(24,23,20,.08)!important}
        [data-baseweb="menu"] li,[role="option"]{background:transparent!important;color:var(--frl-text)!important;font-family:"Source Sans",sans-serif!important;font-size:.72rem!important}
        [data-baseweb="menu"] li:hover,[role="option"]:hover{background:rgba(232,93,63,.06)!important}
        button{font-family:"Source Sans",sans-serif!important}
        .frl-advanced-panel{margin:.42rem 0 .68rem;padding:.65rem 0 .68rem;border-top:1px solid rgba(24,23,20,.14);border-bottom:1px solid rgba(24,23,20,.1)}
        .frl-advanced-title{color:var(--frl-text);font-family:"Source Sans",sans-serif;font-size:.74rem;font-weight:820}
        .frl-advanced-note{color:var(--frl-muted);font-family:"Source Sans",sans-serif;font-size:.61rem;margin:.12rem 0 .48rem}
        .frl-add-condition button{min-height:1.6rem!important;height:1.6rem!important;padding:.1rem .42rem!important;border:0!important;border-radius:999px!important;background:transparent!important;color:var(--frl-accent)!important;box-shadow:none!important;font-size:.63rem!important;font-weight:780!important}
        .frl-add-condition button:hover{background:rgba(232,93,63,.055)!important}
        .frl-active-filters{display:flex;flex-wrap:wrap;gap:.26rem;margin:.3rem 0 .52rem}
        .frl-active-filter{display:inline-flex;align-items:center;min-height:1.4rem;padding:.11rem .43rem;border-radius:999px;background:rgba(232,93,63,.055);color:var(--frl-text);font-family:"Source Sans",sans-serif;font-size:.59rem;font-weight:700}
        @media(max-width:950px){.frl-filter-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important}}
        @media(max-width:620px){.frl-filter-grid{grid-template-columns:1fr!important}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _passing(players: list[dict]) -> list[dict]:
    """Enrich Passing from verified player-match data without erasing FPL data when unavailable."""
    enriched = player_research_player_match.enrich_players(players)
    for player in enriched:
        verified = player.get("player_match_identity_status") == "VERIFIED"
        if not verified:
            continue
        for target, source in PASSING_MAP.items():
            source_value = player.get(source)
            if source_value is not None:
                player[target] = source_value
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

    def load_scope(current_mode: str):
        if current_mode == "Single season":
            season = st.session_state.get("pr_single_season", seasons[-1])
            if season not in seasons:
                season = seasons[-1]
            return [season], list(player_research.season_players(season))
        start = st.session_state.get("pr_start_season", seasons[max(0, len(seasons)-5)])
        end = st.session_state.get("pr_end_season", seasons[-1])
        if start not in seasons:
            start = seasons[max(0, len(seasons)-5)]
        if end not in seasons:
            end = seasons[-1]
        low, high = sorted((seasons.index(start), seasons.index(end)))
        selected = seasons[low:high+1]
        return selected, list(player_research.multi_season_players(selected[0], selected[-1]))

    selected_seasons, players = load_scope(mode)
    positions = sorted({p["position"] for p in players if p.get("position")})
    position_options = ["All positions"] + positions
    position = st.session_state.get("pr_position", "All positions")
    if position not in position_options:
        position = "All positions"

    clubs = sorted({c for p in players for c in p.get("clubs", [])}, key=str.casefold)
    club_query = st.session_state.get("pr_club_query", "")
    max_minutes = int(max((p.get("minutes", 0) for p in players), default=0))
    minimum_minutes = min(int(st.session_state.get("pr_min_minutes", 0)), max_minutes)
    minimum_seasons = int(st.session_state.get("pr_min_seasons", 1 if mode == "Multiple seasons" else 0))
    if mode == "Multiple seasons":
        minimum_seasons = max(1, min(minimum_seasons, len(selected_seasons)))
    else:
        minimum_seasons = 0

    tile_cols = st.columns(5, gap="small")

    with tile_cols[0]:
        with st.container(border=True):
            st.markdown("<div class='frl-filter-kicker'>Period</div>", unsafe_allow_html=True)
            mode = st.radio("Time range", ["Single season", "Multiple seasons"], horizontal=True, index=0 if mode == "Single season" else 1, key="pr_mode", label_visibility="collapsed")
            if mode == "Single season":
                season = st.select_slider("Season", options=seasons, value=selected_seasons[-1], key="pr_single_season", label_visibility="collapsed")
                selected_seasons, players = [season], list(player_research.season_players(season))
            else:
                scope = st.columns(2, gap="small")
                with scope[0]:
                    start = st.select_slider("From", options=seasons, value=selected_seasons[0], key="pr_start_season", label_visibility="collapsed")
                with scope[1]:
                    end = st.select_slider("To", options=seasons, value=selected_seasons[-1], key="pr_end_season", label_visibility="collapsed")
                low, high = sorted((seasons.index(start), seasons.index(end)))
                selected_seasons = seasons[low:high+1]
                players = list(player_research.multi_season_players(selected_seasons[0], selected_seasons[-1]))

    positions = sorted({p["position"] for p in players if p.get("position")})
    position_options = ["All positions"] + positions
    clubs = sorted({c for p in players for c in p.get("clubs", [])}, key=str.casefold)

    with tile_cols[1]:
        with st.container(border=True):
            st.markdown("<div class='frl-filter-kicker'>Position</div>", unsafe_allow_html=True)
            position = st.radio("Position", position_options, horizontal=True, index=position_options.index(position) if position in position_options else 0, key="pr_position", label_visibility="collapsed")

    with tile_cols[2]:
        with st.container(border=True):
            st.markdown("<div class='frl-filter-kicker'>Club</div>", unsafe_allow_html=True)
            club_query = st.text_input("Club", value=club_query, placeholder="Any club", key="pr_club_query", label_visibility="collapsed")
            if club_query.strip():
                matches = [c for c in clubs if club_query.strip().casefold() in c.casefold()]
                st.markdown(f"<div class='frl-filter-note'>{len(matches)} matching club{'s' if len(matches) != 1 else ''}</div>", unsafe_allow_html=True)

    max_minutes = int(max((p.get("minutes", 0) for p in players), default=0))
    minimum_minutes = min(minimum_minutes, max_minutes)
    with tile_cols[3]:
        with st.container(border=True):
            st.markdown("<div class='frl-filter-kicker'>Minutes</div>", unsafe_allow_html=True)
            minimum_minutes = st.slider("Minimum minutes", 0, max_minutes, minimum_minutes, 90, key="pr_min_minutes", label_visibility="collapsed")
            st.markdown(f"<div class='frl-filter-note'>≥ {minimum_minutes:,} minutes</div>", unsafe_allow_html=True)

    with tile_cols[4]:
        with st.container(border=True):
            st.markdown("<div class='frl-filter-kicker'>Advanced</div>", unsafe_allow_html=True)
            advanced = st.toggle("＋ Build a shortlist", value=st.session_state.get("pr_advanced", False), key="pr_advanced")
            st.markdown("<div class='frl-filter-note'>Stats, thresholds & combinations</div>", unsafe_allow_html=True)

    filters = []
    if advanced:
        count = st.session_state.get("pr_filter_count", 1)
        st.markdown("<div class='frl-advanced-panel'><div class='frl-advanced-title'>Build a statistical shortlist</div><div class='frl-advanced-note'>Choose the statistic, rule and value.</div>", unsafe_allow_html=True)
        for index in range(count):
            metric_col, operator_col, value_col = st.columns([2.2,1.35,1.0], gap="small")
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
            st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            st.markdown("</div>", unsafe_allow_html=True)

    search = st.text_input("Search players", placeholder="Search players by name…", key="pr_search", label_visibility="collapsed")

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
        filtered = [p for p in filtered if any(needle in club.casefold() for club in p.get("clubs", []))]
    if search.strip():
        needle = search.strip().casefold()
        filtered = [p for p in filtered if needle in p["player_name"].casefold()]

    filtered = _passing(filtered)

    chips = [selected_seasons[0] if len(selected_seasons)==1 else f"{selected_seasons[0]} – {selected_seasons[-1]}"]
    if position != "All positions":
        chips.append(position)
    if club_query.strip():
        chips.append(club_query.strip())
    if minimum_minutes:
        chips.append(f"≥ {minimum_minutes:,} mins")
    for metric, operator, value in filters:
        chips.append(f"{metric} {operator.lower()} {value}")
    st.markdown("<div class='frl-active-filters'>" + "".join(f"<span class='frl-active-filter'>{chip}</span>" for chip in chips) + "</div>", unsafe_allow_html=True)

    scope_label = f"{selected_seasons[0]} → {selected_seasons[-1]}" if len(selected_seasons)>1 else selected_seasons[0]
    st.markdown(f"<div class='frl-player-result-line'>{len(filtered):,} player(s) · {scope_label}</div>", unsafe_allow_html=True)
    if not filtered:
        st.markdown("<div style='color:var(--frl-muted);padding:.9rem 0;border-top:1px solid var(--frl-border);border-bottom:1px solid var(--frl-border);font-size:.8rem;'>No players match the current research scope.</div>", unsafe_allow_html=True)
        return

    _render_player_table(filtered)

    with st.expander("Player detail", expanded=False):
        selected_name = st.selectbox("Player", [p["player_name"] for p in filtered], key="pr_detail")
        player = next(p for p in filtered if p["player_name"] == selected_name)
        st.markdown(f"<div class='frl-player-detail-title'>{player['player_name']}</div><div class='frl-player-detail-note'>{', '.join(player['clubs'])} · {player['position'] or 'Unknown'} · {scope_label}</div>", unsafe_allow_html=True)
        cards = st.columns(6, gap="small")
        values = [("Minutes", f"{int(player['minutes']):,}"),("Goals",int(player['goals'])),("Assists",int(player['assists'])),("xG",fmt(player['xg'])),("xA",fmt(player['xa'])),("FPL points",int(player['points']))]
        for col,(label,value) in zip(cards, values):
            with col:
                st.markdown(f"<div class='frl-player-card'><div class='frl-player-card-label'>{label}</div><div class='frl-player-card-value'>{value}</div></div>", unsafe_allow_html=True)

        with st.expander("Underlying records", expanded=False):
            records = [{"Season":r.get("_season",""),"Player ID":r.get("element",r.get("player_code","")),"Club":r.get("_club",""),"Minutes":r.get("minutes",0),"Goals":r.get("goals_scored",0),"Assists":r.get("assists",0),"xG":r.get("expected_goals",0),"xA":r.get("expected_assists",0),"FPL points":r.get("total_points",0)} for r in player["_records"]]
            st.dataframe(pd.DataFrame(records), width="stretch", hide_index=True)
