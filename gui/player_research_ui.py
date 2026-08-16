from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
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

SORTABLE_COLUMNS = {
    "Player": ("player_name", "text"),
    "Club": ("club_sort", "text"),
    "Pos": ("position", "text"),
    "Min": ("minutes", "number"),
    "G": ("goals", "number"),
    "A": ("assists", "number"),
    "xG": ("xg", "number"),
    "xA": ("xa", "number"),
    "G/90": ("goals_per_90", "number"),
    "xG/90": ("xg_per_90", "number"),
}


def fmt(value, decimals=2):
    if value is None:
        return "—"
    if decimals == 0:
        return f"{int(round(value)):,}"
    return f"{float(value):.{decimals}f}"


def _player_css():
    st.markdown(
        """
        <style>
        .frl-player-intro {
            margin-top:.7rem;
            color:var(--frl-muted);
            font-size:.78rem;
            line-height:1.45;
        }
        .frl-player-result-line {
            margin:.45rem 0 .55rem;
            color:var(--frl-muted);
            font-size:.72rem;
        }
        .frl-player-table {
            margin-top:.25rem;
            padding:.78rem .9rem .5rem;
            border:1px solid var(--frl-border);
            border-radius:14px;
            background:var(--frl-surface);
            overflow-x:auto;
        }
        .frl-player-table-header,
        .frl-player-table-row {
            display:grid;
            grid-template-columns:minmax(180px,1.8fr) 7.4rem 4rem 5rem 4rem 4rem 4.8rem 4.8rem 5.4rem 5.4rem;
            gap:.22rem;
            align-items:center;
            min-width:760px;
        }
        .frl-player-table-header {
            padding:0 0 .5rem;
            border-bottom:1px solid var(--frl-border-strong);
        }
        .frl-player-header-link,
        .frl-player-header-static {
            color:var(--frl-muted-soft) !important;
            font-size:.55rem;
            font-weight:820;
            letter-spacing:.08em;
            line-height:1;
            text-transform:uppercase;
            text-decoration:none !important;
            padding:.1rem 0;
        }
        .frl-player-header-link:hover,
        .frl-player-header-link:focus {
            color:var(--frl-muted-soft) !important;
            text-decoration:none !important;
        }
        .frl-player-table-row {
            min-height:2.45rem;
            border-bottom:1px solid var(--frl-border);
            color:var(--frl-text);
            font-size:.71rem;
        }
        .frl-player-table-row:last-child { border-bottom:0; }
        .frl-player-table-cell {
            padding:.22rem 0;
            overflow:hidden;
            text-overflow:ellipsis;
            white-space:nowrap;
            font-variant-numeric:tabular-nums;
        }
        .frl-player-name { font-weight:780; }
        .frl-player-club { color:var(--frl-muted); }
        .frl-player-pos { color:var(--frl-secondary); font-weight:780; text-align:center; }
        .frl-player-num { text-align:right; }
        .frl-player-min { color:var(--frl-text); font-weight:820; }
        .frl-player-highlight { color:var(--frl-accent); font-weight:850; }
        .frl-empty-state {
            color:var(--frl-muted);
            padding:.9rem 0;
            border-top:1px solid var(--frl-border);
            border-bottom:1px solid var(--frl-border);
            font-size:.8rem;
        }
        .frl-player-detail-title {
            color:var(--frl-text);
            font-size:1.28rem;
            font-weight:830;
            letter-spacing:-.03em;
        }
        .frl-player-detail-note { margin-top:.18rem; color:var(--frl-muted); font-size:.68rem; }
        .frl-player-card {
            padding:.78rem .86rem;
            border-top:2px solid var(--frl-text);
            border-bottom:1px solid var(--frl-border);
            background:transparent;
        }
        .frl-player-card-label {
            color:var(--frl-muted-soft);
            font-size:.54rem;
            font-weight:820;
            letter-spacing:.10em;
            text-transform:uppercase;
        }
        .frl-player-card-value {
            margin-top:.18rem;
            color:var(--frl-text);
            font-size:1.25rem;
            font-weight:850;
            letter-spacing:-.03em;
        }
        div[data-testid="stTextInput"] input {
            background:var(--frl-surface-raised) !important;
            color:var(--frl-text) !important;
            border:1px solid var(--frl-border) !important;
            border-radius:8px !important;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color:var(--frl-accent) !important;
            box-shadow:0 0 0 2px rgba(232,93,63,.09) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _player_sort_key(player, column):
    field, kind = SORTABLE_COLUMNS[column]
    if column == "Club":
        value = ", ".join(player.get("clubs", []))
    else:
        value = player.get(field)
    if value is None:
        return "" if kind == "text" else float("-inf")
    if kind == "text":
        return str(value).casefold()
    return float(value)


def _query_sort_state():
    requested = st.query_params.get("player_sort", "G")
    if requested not in SORTABLE_COLUMNS:
        requested = "G"

    desc_raw = st.query_params.get("player_desc", "1")
    descending = desc_raw not in {"0", "false", "False"}
    return requested, descending


def _sort_href(column, current_column, current_desc):
    if column == current_column:
        next_desc = not current_desc
    else:
        next_desc = column != "Player"

    return f"?player_sort={column}&player_desc={'1' if next_desc else '0'}"


def render_player_research_ui():
    _player_css()

    seasons = list(player_research.available_seasons())
    if not seasons:
        st.error("No player data available.")
        return

    st.markdown(
        "<div class='frl-player-intro'>Browse the player data first. Use the research filters only when you need to narrow the evidence.</div>",
        unsafe_allow_html=True,
    )

    with st.expander("Season & scope", expanded=False):
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
                start_season = st.selectbox("From", seasons, index=max(0, len(seasons) - 5), key="pr_start_season")
            with scope_cols[1]:
                end_season = st.selectbox("To", seasons, index=len(seasons) - 1, key="pr_end_season")

            low = min(seasons.index(start_season), seasons.index(end_season))
            high = max(seasons.index(start_season), seasons.index(end_season))
            selected_seasons = seasons[low:high + 1]

            with st.spinner(f"Loading {len(selected_seasons)} seasons…"):
                players = list(player_research.multi_season_players(selected_seasons[0], selected_seasons[-1]))

        positions = sorted({p["position"] for p in players if p["position"]})
        clubs = sorted({club for p in players for club in p["clubs"]}, key=str.casefold)
        compact_cols = st.columns(3, gap="medium")
        with compact_cols[0]:
            position = st.selectbox("Position", ["All positions"] + positions, key="pr_position")
        with compact_cols[1]:
            club = st.selectbox("Club", ["All clubs"] + clubs, key="pr_club")
        with compact_cols[2]:
            max_minutes = int(max((p["minutes"] for p in players), default=0))
            minimum_minutes = st.number_input("Minimum minutes", min_value=0, max_value=max_minutes, value=0, step=90, format="%d", key="pr_min_minutes")

        minimum_seasons = 0
        if mode == "Multiple seasons":
            minimum_seasons = st.number_input("Minimum seasons played", min_value=1, max_value=len(selected_seasons), value=1, step=1, format="%d", key="pr_min_seasons")

    with st.expander("Advanced conditions", expanded=False):
        condition_count = st.selectbox("Number of conditions", [0, 1, 2, 3], key="pr_condition_count")
        filters = []
        for index in range(condition_count):
            metric_col, operator_col, value_col = st.columns([2.2, 1.4, 1.0], gap="small")
            with metric_col:
                metric_label = st.selectbox("Statistic", list(FILTER_OPTIONS.keys()), key=f"pr_condition_metric_{index}")
            metric, value_type = FILTER_OPTIONS[metric_label]
            with operator_col:
                operator = st.selectbox("Condition", OPERATORS, key=f"pr_condition_operator_{index}")
            with value_col:
                if value_type == "int":
                    value = st.number_input("Value", min_value=0, value=0, step=1, format="%d", key=f"pr_condition_value_int_{index}")
                else:
                    value = st.number_input("Value", value=0.0, step=0.01, format="%.2f", key=f"pr_condition_value_float_{index}")
            filters.append((metric, operator, value))

    search = st.text_input(
        "Search player",
        placeholder="Search player name…",
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
        filtered = [p for p in filtered if needle in p["player_name"].casefold()]

    scope_label = f"{selected_seasons[0]} → {selected_seasons[-1]}" if len(selected_seasons) > 1 else selected_seasons[0]
    sort_column, descending = _query_sort_state()
    filtered = sorted(filtered, key=lambda p: _player_sort_key(p, sort_column), reverse=descending)

    st.markdown(
        f"<div class='frl-player-result-line'>{len(filtered):,} player(s) · {scope_label}</div>",
        unsafe_allow_html=True,
    )

    if not filtered:
        st.markdown("<div class='frl-empty-state'>No players match the current research scope.</div>", unsafe_allow_html=True)
        return

    st.markdown("<div class='frl-player-table'>", unsafe_allow_html=True)

    header_cols = st.columns([1.8, .75, .4, .5, .4, .4, .48, .48, .54, .54], gap="small")
    for col, label in zip(header_cols, SORTABLE_COLUMNS):
        with col:
            if label in ("Player", "Club", "Pos"):
                st.markdown(
                    f"<a class='frl-player-header-static'>{label}</a>",
                    unsafe_allow_html=True,
                )
            else:
                href = _sort_href(label, sort_column, descending)
                st.markdown(
                    f"<a class='frl-player-header-link' href='{href}'>{label}</a>",
                    unsafe_allow_html=True,
                )

    for player in filtered:
        clubs_text = ", ".join(player["clubs"])
        position_value = player.get("position") or "—"
        values = [
            player["player_name"],
            clubs_text,
            position_value,
            f"{int(player['minutes']):,}",
            str(int(player["goals"])),
            str(int(player["assists"])),
            fmt(player["xg"]),
            fmt(player["xa"]),
            fmt(player["goals_per_90"], 3),
            fmt(player["xg_per_90"], 3),
        ]
        classes = [
            "frl-player-name",
            "frl-player-club",
            "frl-player-pos",
            "frl-player-num frl-player-min",
            "frl-player-num frl-player-highlight",
            "frl-player-num",
            "frl-player-num",
            "frl-player-num",
            "frl-player-num",
            "frl-player-num",
        ]
        row = st.columns([1.8, .75, .4, .5, .4, .4, .48, .48, .54, .54], gap="small")
        for col, value, class_name in zip(row, values, classes):
            with col:
                st.markdown(f"<div class='frl-player-table-cell {class_name}'>{value}</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:1px;background:var(--frl-border);'></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("Player detail", expanded=False):
        selected_name = st.selectbox("Player", [p["player_name"] for p in filtered], key="pr_detail")
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
            st.dataframe(records, width="stretch", hide_index=True)
