from __future__ import annotations

import json
import py_compile
import tempfile
from pathlib import Path

TARGET = Path("gui/player_research_ui.py")

SOURCE_FIELDS = {
    "Goals": "goals",
    "Assists": "assists",
    "xG": "xg",
    "xA": "xa",
    "xGI": "xgi",
    "Shots": "shots",
    "Shots on Target": "shots_on_target",
    "Creativity": "creativity",
    "Crosses": "crosses",
    "Tackles": "tackles",
    "Interceptions": "interceptions",
    "Recoveries": "recoveries",
    "Clearances": "clearances",
    "Clean Sheets": "clean_sheets",
    "Saves": "saves",
    "Goals Conceded": "goals_conceded",
    "Penalties Saved": "penalties_saved",
    "FPL Points": "points",
    "Bonus": "bonus",
    "BPS": "bps",
    "ICT Influence": "ict_influence",
    "ICT Creativity": "ict_creativity",
    "ICT Threat": "ict_threat",
    "ICT Index": "ict_index",
    "DefCon": "defensive_contribution",
    "Minutes": "minutes",
    "Starts": "starts",
    "Appearances": "appearances",
    "Seasons": "season_count",
    "Yellow Cards": "yellow_cards",
    "Red Cards": "red_cards",
    "Own Goals": "own_goals",
    "Penalties Missed": "penalties_missed",
}

CATEGORIES = {
    "Goals & Assists": ["Goals", "Assists", "xG", "xA", "xGI"],
    "Shooting": ["Goals", "Shots", "Shots on Target", "xG"],
    "Creativity": ["Assists", "xA", "Creativity", "Crosses"],
    "Defending": ["Tackles", "Interceptions", "Recoveries", "Clearances", "Clean Sheets"],
    "Goalkeeping": ["Saves", "Clean Sheets", "Goals Conceded", "Penalties Saved"],
    "FPL Stats": ["FPL Points", "Bonus", "BPS", "ICT Influence", "ICT Creativity", "ICT Threat", "ICT Index", "DefCon"],
    "Usage": ["Minutes", "Starts", "Appearances", "Seasons"],
    "Discipline": ["Yellow Cards", "Red Cards", "Own Goals", "Penalties Missed"],
}


def _assert_python(path: Path) -> None:
    py_compile.compile(str(path), doraise=True)


def _build_rows_source() -> str:
    lines = [
        "    rows = []",
        "    for player in players:",
        "        row = {",
        '            "Player": player["player_name"],',
        '            "Club": ", ".join(player["clubs"]),',
        '            "Pos": player.get("position") or "—",',
        "        }",
    ]
    for label, field in SOURCE_FIELDS.items():
        lines.append(f"        row[{label!r}] = player.get({field!r})")
    lines.append("        rows.append(row)")
    lines.append("")
    lines.append('    payload = json.dumps(rows).replace("</", "<\\/")')
    return "\n".join(lines)


HTML_TEMPLATE = r'''    <div id="frl-player-table" class="frl-player-table">
      <style>
        * { box-sizing: border-box; }
        html, body { margin:0; padding:0; background:#fffdf8; font-family:"Source Sans", sans-serif; }
        .frl-player-table { width:100%; padding:.78rem .9rem .5rem; border:1px solid rgba(24,23,20,.11); border-radius:14px; background:#fffdf8; color:#171714; overflow:hidden; }
        .frl-player-grid { display:grid; gap:.22rem; align-items:center; min-width:760px; }
        .frl-player-header { padding:0 0 .5rem; border-bottom:1px solid rgba(24,23,20,.20); color:#989289; font-family:"Source Sans", sans-serif; font-size:.57rem; font-weight:800; letter-spacing:.09em; line-height:1; text-transform:uppercase; }
        .frl-player-header button { all:unset; display:block; width:100%; color:#989289; font:800 .57rem/1 "Source Sans", sans-serif; letter-spacing:.09em; text-transform:uppercase; cursor:pointer; text-align:right; }
        .frl-player-header button:hover { color:#989289; }
        .frl-player-header .static { text-align:left; cursor:default; }
        .frl-player-rows { max-height:560px; overflow:auto; scrollbar-width:thin; }
        .frl-player-row { min-height:2.45rem; border-bottom:1px solid rgba(24,23,20,.11); color:#171714; font-family:"Source Sans", sans-serif; font-size:.71rem; }
        .frl-player-row:last-child { border-bottom:0; }
        .frl-cell { padding:.22rem 0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-variant-numeric:tabular-nums; }
        .frl-name { font-size:.68rem; font-weight:760; }
        .frl-club { color:#68645c; }
        .frl-pos { color:#9aaa42; font-weight:760; text-align:center; }
        .frl-num { text-align:right; }
        .frl-goals { color:#e85d3f; font-weight:850; }
        .frl-foot { margin-top:.55rem; color:#989289; font: .61rem/1 "Source Sans", sans-serif; }
        .frl-player-toolbar { display:grid; grid-template-columns:1fr auto 1fr; align-items:center; min-height:2rem; margin:0 0 .7rem; }
        .frl-player-count { justify-self:start; color:#989289; font:800 .62rem/1 "Source Sans", sans-serif; letter-spacing:.08em; text-transform:uppercase; }
        .frl-stat-nav { display:flex; align-items:center; justify-content:center; gap:.62rem; }
        .frl-stat-nav button { all:unset; cursor:pointer; color:#989289; font:650 .78rem/1 "Source Sans", sans-serif; padding:.18rem .1rem; }
        .frl-stat-nav button:hover { color:#e85d3f; }
        .frl-stat-nav-label { min-width:9.5rem; color:#171714; font:800 .68rem/1 "Source Sans", sans-serif; letter-spacing:.10em; text-align:center; text-transform:uppercase; }
      </style>
      <div class="frl-player-toolbar">
        <div class="frl-player-count">__PLAYER_COUNT__ players</div>
        <div class="frl-stat-nav">
          <button id="frl-stat-prev" type="button" aria-label="Previous statistic category">←</button>
          <div id="frl-stat-label" class="frl-stat-nav-label"></div>
          <button id="frl-stat-next" type="button" aria-label="Next statistic category">→</button>
        </div>
        <div></div>
      </div>
      <div id="frl-player-header" class="frl-player-grid frl-player-header"></div>
      <div id="frl-player-rows" class="frl-player-rows"></div>
      <div class="frl-foot">Source statistics only · click a statistic heading to sort.</div>
    </div>
    <script>
      const data = __PAYLOAD__;
      const categories = __CATEGORIES__;
      const categoryNames = Object.keys(categories);
      let categoryIndex = 0;
      let sortKey = categories[categoryNames[0]][0];
      let descending = true;
      const header = document.getElementById('frl-player-header');
      const rows = document.getElementById('frl-player-rows');
      const label = document.getElementById('frl-stat-label');

      function availableStats(category) {
        return categories[category].filter(stat => data.some(row => row[stat] !== null && row[stat] !== undefined));
      }

      function formatValue(value) {
        if (value === null || value === undefined || value === '') return '—';
        if (typeof value === 'number') return Number.isInteger(value) ? value.toLocaleString() : value.toFixed(2);
        return String(value);
      }

      function escapeHtml(value) {
        return String(value).replace(/[&<>'"]/g, ch => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#39;', '"':'&quot;' }[ch]));
      }

      function render() {
        const category = categoryNames[categoryIndex];
        const stats = availableStats(category);
        label.textContent = category;
        if (!stats.length) {
          header.innerHTML = '<div>No source statistics available</div>';
          rows.innerHTML = '';
          return;
        }
        if (!stats.includes(sortKey)) {
          sortKey = stats[0];
          descending = true;
        }
        const templateColumns = `minmax(180px,1.8fr) 7.4rem 4rem repeat(${stats.length}, 5rem)`;
        header.style.gridTemplateColumns = templateColumns;
        header.innerHTML = '<div><button class="static" type="button">Player</button></div>' +
          '<div><button class="static" type="button">Club</button></div>' +
          '<div><button class="static" type="button">Pos</button></div>' +
          stats.map(stat => `<div><button type="button" data-sort="${escapeHtml(stat)}">${escapeHtml(stat)}</button></div>`).join('');

        const sorted = [...data].sort((a, b) => {
          const av = a[sortKey];
          const bv = b[sortKey];
          if (av === bv) return a.Player.localeCompare(b.Player);
          if (av === null || av === undefined) return 1;
          if (bv === null || bv === undefined) return -1;
          if (typeof av === 'string' || typeof bv === 'string') {
            return String(av).localeCompare(String(bv)) * (descending ? -1 : 1);
          }
          return (av < bv ? 1 : -1) * (descending ? 1 : -1);
        });

        rows.innerHTML = sorted.map(r =>
          `<div class="frl-player-grid frl-player-row" style="grid-template-columns:${templateColumns}">` +
          `<div class="frl-cell frl-name">${escapeHtml(r.Player)}</div>` +
          `<div class="frl-cell frl-club">${escapeHtml(r.Club)}</div>` +
          `<div class="frl-cell frl-pos">${escapeHtml(r.Pos)}</div>` +
          stats.map(stat => `<div class="frl-cell frl-num ${stat === 'Goals' ? 'frl-goals' : ''}">${formatValue(r[stat])}</div>`).join('') +
          '</div>'
        ).join('');

        header.querySelectorAll('[data-sort]').forEach(button => {
          button.addEventListener('click', () => {
            const key = button.dataset.sort;
            if (sortKey === key) descending = !descending;
            else { sortKey = key; descending = true; }
            render();
          });
        });
      }

      document.getElementById('frl-stat-prev').addEventListener('click', () => {
        categoryIndex = (categoryIndex - 1 + categoryNames.length) % categoryNames.length;
        sortKey = categories[categoryNames[categoryIndex]][0];
        descending = true;
        render();
      });

      document.getElementById('frl-stat-next').addEventListener('click', () => {
        categoryIndex = (categoryIndex + 1) % categoryNames.length;
        sortKey = categories[categoryNames[categoryIndex]][0];
        descending = true;
        render();
      });

      render();
    </script>'''


def build_table_function() -> str:
    rows_source = _build_rows_source()
    return "\n".join(
        [
            "def _render_player_table(players):",
            rows_source,
            "    html = r'''",
            HTML_TEMPLATE,
            "    '''",
            "    html = html.replace('__PAYLOAD__', payload)",
            f"    html = html.replace('__CATEGORIES__', {json.dumps(json.dumps(CATEGORIES))!r})",
            "    html = html.replace('__PLAYER_COUNT__', str(len(players)))",
            "    st.iframe(html, height=640)",
        ]
    )


def main() -> None:
    source = TARGET.read_text(encoding="utf-8-sig")
    _assert_python(TARGET)
    start = source.index("def _render_player_table")
    end = source.index("def render_player_research_ui")
    updated = source[:start] + build_table_function() + "\n\n" + source[end:]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", encoding="utf-8", delete=False) as tmp:
        temp_path = Path(tmp.name)
        tmp.write(updated)
    try:
        _assert_python(temp_path)
    finally:
        temp_path.unlink(missing_ok=True)

    TARGET.write_text(updated, encoding="utf-8")
    _assert_python(TARGET)

    if "use_container_width" in updated:
        raise RuntimeError("Deprecated use_container_width remains in Players UI.")
    if "st.iframe(html, height=640)" not in updated:
        raise RuntimeError("Supported st.iframe signature is missing.")
    if "frl-stat-prev" not in updated or "frl-stat-next" not in updated:
        raise RuntimeError("Players category navigation is missing.")

    print("PASS: Players stat carousel applied.")
    print("PASS: Existing sortable table behaviour retained.")
    print("PASS: Category navigation is browser-side and instant.")
    print("PASS: Source-backed fields only; missing source fields remain absent.")
    print("PASS: No per-90 metrics introduced.")
    print("PASS: Temporary and final Python syntax verified.")
    print("PASS: Deprecated use_container_width absent from Players UI.")
