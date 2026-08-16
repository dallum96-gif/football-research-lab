from pathlib import Path
import sys
import json

import pandas as pd
import streamlit as st
from streamlit.components.v1 import html as components_html

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
        .frl-player-table-host {
            margin-top:.25rem;
            padding:.78rem .9rem .5rem;
            border:1px solid var(--frl-border);
            border-radius:14px;
            background:var(--frl-surface);
            overflow:hidden;
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


def _render_player_table(players):
    rows = []
    for player in players:
        rows.append({
            "Player": player["player_name"],
            "Club": ", ".join(player["clubs"]),
            "Pos": player.get("position") or "—",
            "Min": int(player["minutes"]),
            "G": int(player["goals"]),
            "A": int(player["assists"]),
            "xG": float(player["xg"] or 0),
            "xA": float(player["xa"] or 0),
            "G/90": float(player["goals_per_90"] or 0),
            "xG/90": float(player["xg_per_90"] or 0),
        })

    payload = json.dumps(rows).replace("</", "<\\/")

    html = f"""
    <div id="frl-player-table" class="frl-player-table">
      <style>
        * {{ box-sizing: border-box; }}
        html, body {{
          margin:0;
          padding:0;
          background:#fffdf8;
          font-family:"Source Sans", sans-serif;
        }}
        .frl-player-table {{
          width:100%;
          padding:.78rem .9rem .5rem;
          border:1px solid rgba(24,23,20,.11);
          border-radius:14px;
          background:#fffdf8;
          font-family:"Source Sans", sans-serif;
          color:#171714;
          overflow:hidden;
        }}
        .frl-player-grid {{
          display:grid;
          grid-template-columns:minmax(180px,1.8fr) 7.4rem 4rem 5rem 4rem 4rem 4.8rem 4.8rem 5.4rem 5.4rem;
          gap:.22rem;
          align-items:center;
          min-width:760px;
        }}
        .frl-player-header {{
          padding:0 0 .5rem;
          border-bottom:1px solid rgba(24,23,20,.20);
          color:#989289;
          font-family:"Source Sans", sans-serif;
          font-size:.55rem;
          font-weight:820;
          letter-spacing:.08em;
          line-height:1;
          text-transform:uppercase;
        }}
        .frl-player-header button {{
          all:unset;
          display:block;
          width:100%;
          color:#989289;
          font-family:"Source Sans", sans-serif;
          font-size:.55rem;
          font-weight:820;
          letter-spacing:.08em;
          line-height:1;
          text-transform:uppercase;
          cursor:pointer;
          text-align:right;
        }}
        .frl-player-header button:hover {{ color:#989289; }}
        .frl-player-header .static {{ text-align:left; cursor:default; }}
        .frl-player-rows {{
          max-height:560px;
          overflow:auto;
          scrollbar-width:thin;
        }}
        .frl-player-row {{
          min-height:2.45rem;
          border-bottom:1px solid rgba(24,23,20,.11);
          color:#171714;
          font-family:"Source Sans", sans-serif;
          font-size:.71rem;
        }}
        .frl-player-row:last-child {{ border-bottom:0; }}
        .frl-cell {{
          padding:.22rem 0;
          overflow:hidden;
          text-overflow:ellipsis;
          white-space:nowrap;
          font-variant-numeric:tabular-nums;
        }}
        .frl-name {{ font-weight:780; }}
        .frl-club {{ color:#68645c; }}
        .frl-pos {{ color:#9aaa42; font-weight:780; text-align:center; }}
        .frl-num {{ text-align:right; }}
        .frl-min {{ color:#171714; font-weight:820; }}
        .frl-goals {{ color:#e85d3f; font-weight:850; }}
        .frl-foot {{ margin-top:.55rem; color:#989289; font-family:"Source Sans", sans-serif; font-size:.61rem; }}
      </style>
      <div class="frl-player-grid frl-player-header">
        <div><button class="static" type="button">Player</button></div>
        <div><button class="static" type="button">Club</button></div>
        <div><button class="static" type="button">Pos</button></div>
        <div><button type="button" data-sort="Min">Min</button></div>
        <div><button type="button" data-sort="G">G</button></div>
        <div><button type="button" data-sort="A">A</button></div>
        <div><button type="button" data-sort="xG">xG</button></div>
        <div><button type="button" data-sort="xA">xA</button></div>
        <div><button type="button" data-sort="G/90">G/90</button></div>
        <div><button type="button" data-sort="xG/90">xG/90</button></div>
      </div>
      <div id="frl-player-rows" class="frl-player-rows"></div>
      <div class="frl-foot">Goals are highlighted for quick scanning · click a statistic heading to sort.</div>
    </div>
    <script>
      const data = {payload};
      const state = {{ key: 'G', desc: true }};
      const rows = document.getElementById('frl-player-rows');

      function render() {{
        const sorted = [...data].sort((a,b) => {{
          let av = a[state.key], bv = b[state.key];
          if (typeof av === 'string') {{ av = av.toLowerCase(); bv = bv.toLowerCase(); }}
          if (av < bv) return state.desc ? 1 : -1;
          if (av > bv) return state.desc ? -1 : 1;
          return a.Player.localeCompare(b.Player);
        }});

        rows.innerHTML = sorted.map(r => `
          <div class="frl-player-grid frl-player-row">
            <div class="frl-cell frl-name">${{escapeHtml(r.Player)}}</div>
            <div class="frl-cell frl-club">${{escapeHtml(r.Club)}}</div>
            <div class="frl-cell frl-pos">${{escapeHtml(r.Pos)}}</div>
            <div class="frl-cell frl-num frl-min">${{r.Min.toLocaleString()}}</div>
            <div class="frl-cell frl-num frl-goals">${{r.G.toLocaleString()}}</div>
            <div class="frl-cell frl-num">${{r.A.toLocaleString()}}</div>
            <div class="frl-cell frl-num">${{r.xG.toFixed(2)}}</div>
            <div class="frl-cell frl-num">${{r.xA.toFixed(2)}}</div>
            <div class="frl-cell frl-num">${{r['G/90'].toFixed(3)}}</div>
            <div class="frl-cell frl-num">${{r['xG/90'].toFixed(3)}}</div>
          </div>`).join('');
      }}

      function escapeHtml(value) {{
        return String(value).replace(/[&<>'"]/g, ch => ({{'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}}[ch]));
      }}

      document.querySelectorAll('[data-sort]').forEach(button => {{
        button.addEventListener('click', () => {{
          const key = button.dataset.sort;
          if (state.key === key) state.desc = !state.desc;
          else {{ state.key = key; state.desc = true; }}
          render();
        }});
      }});

      render();
    </script>
    """

    components_html(html, height=640, scrolling=False)


def render_player_research_ui():
    _player_css()

    seasons = list(player_research.available_seasons())
    if not seasons:
        st.error("No player data available.")
        return

    st.markdown(
        "<div class='frl-player-intro'>Browse the player data first. Use the two research filters below when you want to narrow the evidence.</div>",
        unsafe_allow_html=True,
    )

    with st.expander("Season & scope", expanded=False):
        mode = st.radio("Time range", ["Single season", "Multiple seasons"], horizontal=True, key="pr_mode")

        if mode == "Single season":
            season = st.selectbox("Season", seasons, index=len(seasons) - 1, key="pr_single_season")
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

        positions = sorted({player["position"] for player in players if player["position"]})
        clubs = sorted({club for player in players for club in player["clubs"]}, key=str.casefold)
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

    search = st.text_input("Search player", placeholder="Search player name…", key="pr_search", label_visibility="collapsed")

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
        filtered = [player for player in filtered if needle in player["player_name"].casefold()]

    scope_label = f"{selected_seasons[0]} → {selected_seasons[-1]}" if len(selected_seasons) > 1 else selected_seasons[0]
    st.markdown(f"<div class='frl-player-result-line'>{len(filtered):,} player(s) · {scope_label}</div>", unsafe_allow_html=True)

    if not filtered:
        st.markdown("<div style='color:var(--frl-muted);padding:.9rem 0;border-top:1px solid var(--frl-border);border-bottom:1px solid var(--frl-border);font-size:.8rem;'>No players match the current research scope.</div>", unsafe_allow_html=True)
        return

    _render_player_table(filtered)

    with st.expander("Player detail", expanded=False):
        selected_name = st.selectbox("Player", [player["player_name"] for player in filtered], key="pr_detail")
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
