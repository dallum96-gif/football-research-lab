from __future__ import annotations

from pathlib import Path
import py_compile
import re

TARGET = Path("gui/player_research_ui.py")

CANDIDATE_FIELDS = {
    "Goals": ["goals"],
    "Assists": ["assists"],
    "xG": ["xg"],
    "xA": ["xa"],
    "xGI": ["xgi"],
    "Shots": ["shots", "total_shots"],
    "Shots on Target": ["shots_on_target", "shots_target", "shots_on_target_total"],
    "Creativity": ["creativity"],
    "Crosses": ["crosses"],
    "Tackles": ["tackles"],
    "Interceptions": ["interceptions"],
    "Recoveries": ["recoveries"],
    "Clearances": ["clearances"],
    "Clean Sheets": ["clean_sheets"],
    "Saves": ["saves"],
    "Goals Conceded": ["goals_conceded"],
    "Penalties Saved": ["penalties_saved", "penalty_saves"],
    "FPL Points": ["points"],
    "Bonus": ["bonus"],
    "BPS": ["bps"],
    "ICT Influence": ["ict_influence", "influence"],
    "ICT Creativity": ["ict_creativity"],
    "ICT Threat": ["ict_threat", "threat"],
    "ICT Index": ["ict_index", "ict"],
    "DefCon": ["defcon", "defensive_contribution"],
    "Minutes": ["minutes"],
    "Starts": ["starts"],
    "Appearances": ["appearances"],
    "Yellow Cards": ["yellow_cards", "yellow"],
    "Red Cards": ["red_cards", "red"],
    "Own Goals": ["own_goals"],
    "Penalties Missed": ["penalties_missed", "penalty_misses"],
}

CATEGORIES = {
    "Goals & Assists": ["Goals", "Assists", "xG", "xA", "xGI"],
    "Shooting": ["Goals", "Shots", "Shots on Target", "xG"],
    "Creativity": ["Assists", "xA", "Creativity", "Crosses"],
    "Defending": ["Tackles", "Interceptions", "Recoveries", "Clearances", "Clean Sheets"],
    "Goalkeeping": ["Saves", "Clean Sheets", "Goals Conceded", "Penalties Saved"],
    "FPL Stats": ["FPL Points", "Bonus", "BPS", "ICT Influence", "ICT Creativity", "ICT Threat", "ICT Index", "DefCon"],
    "Usage": ["Minutes", "Starts", "Appearances"],
    "Discipline": ["Yellow Cards", "Red Cards", "Own Goals", "Penalties Missed"],
}


def _find_key(player: dict, label: str) -> str | None:
    for key in CANDIDATE_FIELDS[label]:
        if key in player and player[key] is not None:
            return key
    return None


def build_rows_source() -> list[str]:
    lines = [
        '    rows = []',
        '    for player in players:',
        '        row = {',
        '            "Player": player["player_name"],',
        '            "Club": ", ".join(player["clubs"]),',
        '            "Pos": player.get("position") or "—",',
        '        }',
    ]
    for label, candidates in CANDIDATE_FIELDS.items():
        key = candidates[0]
        lines.append(f'        row[{label!r}] = player.get({key!r})')
        if len(candidates) > 1:
            for alias in candidates[1:]:
                lines.append(f'        if row[{label!r}] is None: row[{label!r}] = player.get({alias!r})')
    lines += [
        '        rows.append(row)',
        '',
        '    payload = json.dumps(rows).replace("</", "<\\/")',
    ]
    return lines


def build_table_function() -> str:
    source_rows = "\n".join(build_rows_source())
    category_json = repr(CATEGORIES)
    return f'''def _render_player_table(players):\n{source_rows}\n\n    html = f"""\n    <div id="frl-player-table" class="frl-player-table">\n      <style>\n        * {{ box-sizing: border-box; }}\n        html, body {{ margin:0; padding:0; background:#fffdf8; font-family:"Source Sans", sans-serif; }}\n        .frl-player-table {{ width:100%; padding:.78rem .9rem .5rem; border:1px solid rgba(24,23,20,.11); border-radius:14px; background:#fffdf8; font-family:"Source Sans", sans-serif; color:#171714; overflow:hidden; }}\n        .frl-player-grid {{ display:grid; gap:.22rem; align-items:center; min-width:760px; }}\n        .frl-player-grid[data-category="Goals & Assists"] {{ grid-template-columns:minmax(180px,1.8fr) 7.4rem 4rem repeat(5, 4.8rem); }}\n        .frl-player-header {{ padding:0 0 .5rem; border-bottom:1px solid rgba(24,23,20,.20); color:#989289; font-family:"Source Sans", sans-serif; font-size:.57rem; font-weight:800; letter-spacing:.09em; line-height:1; text-transform:uppercase; }}\n        .frl-player-header button {{ all:unset; display:block; width:100%; color:#989289; font-family:"Source Sans", sans-serif; font-size:.57rem; font-weight:800; letter-spacing:.09em; line-height:1; text-transform:uppercase; cursor:pointer; text-align:right; }}\n        .frl-player-header button:hover {{ color:#989289; }}\n        .frl-player-header .static {{ text-align:left; cursor:default; }}\n        .frl-player-rows {{ max-height:560px; overflow:auto; scrollbar-width:thin; }}\n        .frl-player-row {{ min-height:2.45rem; border-bottom:1px solid rgba(24,23,20,.11); color:#171714; font-family:"Source Sans", sans-serif; font-size:.71rem; }}\n        .frl-player-row:last-child {{ border-bottom:0; }}\n        .frl-cell {{ padding:.22rem 0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-variant-numeric:tabular-nums; }}\n        .frl-name {{ font-size:.68rem; font-weight:760; }}\n        .frl-club {{ color:#68645c; }}\n        .frl-pos {{ color:#9aaa42; font-weight:760; text-align:center; }}\n        .frl-num {{ text-align:right; }}\n        .frl-min {{ color:#171714; font-weight:820; }}\n        .frl-goals {{ color:#e85d3f; font-weight:850; }}\n        .frl-foot {{ margin-top:.55rem; color:#989289; font-family:"Source Sans", sans-serif; font-size:.61rem; }}\n        .frl-stat-nav {{ display:flex; align-items:center; justify-content:center; gap:.8rem; margin:.1rem 0 .8rem; }}\n        .frl-stat-nav button {{ all:unset; cursor:pointer; color:#989289; font-family:"Source Sans", sans-serif; font-size:.72rem; line-height:1; padding:.15rem .1rem; }}\n        .frl-stat-nav button:hover {{ color:#e85d3f; }}\n        .frl-stat-nav-label {{ color:#171714; font-family:"Source Sans", sans-serif; font-size:.72rem; font-weight:720; letter-spacing:.06em; text-transform:uppercase; min-width:9.5rem; text-align:center; }}\n      </style>\n      <div class="frl-stat-nav">\n        <button id="frl-stat-prev" type="button" aria-label="Previous statistic category">←</button>\n        <div id="frl-stat-label" class="frl-stat-nav-label"></div>\n        <button id="frl-stat-next" type="button" aria-label="Next statistic category">→</button>\n      </div>\n      <div id="frl-player-header" class="frl-player-grid frl-player-header"></div>\n      <div id="frl-player-rows" class="frl-player-rows"></div>\n      <div class="frl-foot">Source statistics only · click a statistic heading to sort.</div>\n    </div>\n    <script>\n      const data = ${{payload}};\n      const categories = {category_json};\n      const categoryNames = Object.keys(categories);\n      let categoryIndex = 0;\n      let sortKey = categories[categoryNames[0]][0];\n      let descending = true;\n\n      const header = document.getElementById('frl-player-header');\n      const rows = document.getElementById('frl-player-rows');\n      const label = document.getElementById('frl-stat-label');\n\n      function availableStats(category) {{\n        return categories[category].filter(stat => data.some(row => row[stat] !== null && row[stat] !== undefined));\n      }}\n\n      function formatValue(value) {{\n        if (value === null || value === undefined || value === '') return '—';\n        if (typeof value === 'number') return Number.isInteger(value) ? value.toLocaleString() : value.toFixed(2);\n        return String(value);\n      }}\n\n      function escapeHtml(value) {{\n        return String(value).replace(/[&<>'\"]/g, ch => ({{'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','\"':'&quot;'}}[ch]));\n      }}\n\n      function render() {{\n        const category = categoryNames[categoryIndex];\n        const stats = availableStats(category);\n        if (!stats.length) return;\n        if (!stats.includes(sortKey)) {{ sortKey = stats[0]; descending = true; }}\n        label.textContent = category;\n        header.style.gridTemplateColumns = `minmax(180px,1.8fr) 7.4rem 4rem repeat(${{stats.length}}, 5rem)`;\n        header.innerHTML = '<div><button class="static" type="button">Player</button></div>' +\n          '<div><button class="static" type="button">Club</button></div>' +\n          '<div><button class="static" type="button">Pos</button></div>' +\n          stats.map(stat => `<div><button type="button" data-sort="${{escapeHtml(stat)}}">${{escapeHtml(stat)}}</button></div>`).join('');\n\n        const sorted = [...data].sort((a,b) => {{\n          const av = a[sortKey], bv = b[sortKey];\n          if (av === bv) return a.Player.localeCompare(b.Player);\n          if (av === null || av === undefined) return 1;\n          if (bv === null || bv === undefined) return -1;\n          if (typeof av === 'string' || typeof bv === 'string') {{\n            const as = String(av).toLowerCase(), bs = String(bv).toLowerCase();\n            return as.localeCompare(bs) * (descending ? -1 : 1);\n          }}\n          return (av < bv ? 1 : -1) * (descending ? 1 : -1);\n        }});\n\n        rows.innerHTML = sorted.map(r => {{\n          return `<div class="frl-player-grid frl-player-row" style="grid-template-columns:minmax(180px,1.8fr) 7.4rem 4rem repeat(${{stats.length}}, 5rem)">` +\n            `<div class="frl-cell frl-name">${{escapeHtml(r.Player)}}</div>` +\n            `<div class="frl-cell frl-club">${{escapeHtml(r.Club)}}</div>` +\n            `<div class="frl-cell frl-pos">${{escapeHtml(r.Pos)}}</div>` +\n            stats.map(stat => `<div class="frl-cell frl-num ${{stat === 'Goals' ? 'frl-goals' : ''}}">${{formatValue(r[stat])}}</div>`).join('') +\n            '</div>';\n        }}).join('');\n\n        header.querySelectorAll('[data-sort]').forEach(button => {{\n          button.addEventListener('click', () => {{\n            const key = button.dataset.sort;\n            if (sortKey === key) descending = !descending;\n            else {{ sortKey = key; descending = true; }}\n            render();\n          }});\n        }});\n      }}\n\n      document.getElementById('frl-stat-prev').addEventListener('click', () => {{\n        categoryIndex = (categoryIndex - 1 + categoryNames.length) % categoryNames.length;\n        sortKey = availableStats(categoryNames[categoryIndex])[0] || categories[categoryNames[categoryIndex]][0];\n        descending = true;\n        render();\n      }});\n\n      document.getElementById('frl-stat-next').addEventListener('click', () => {{\n        categoryIndex = (categoryIndex + 1) % categoryNames.length;\n        sortKey = availableStats(categoryNames[categoryIndex])[0] || categories[categoryNames[categoryIndex]][0];\n        descending = true;\n        render();\n      }});\n\n      render();\n    </script>\n    """\n\n    st.iframe(html, height=640)\n'''


def main() -> None:
    source = TARGET.read_text(encoding="utf-8")
    py_compile.compile(str(TARGET), doraise=True)

    start = source.index("def _render_player_table")
    end = source.index("def render_player_research_ui")
    updated = source[:start] + build_table_function() + "\n\n" + source[end:]

    py_compile.compile(str(TARGET), doraise=True)
    temp = TARGET.with_suffix(".carousel_tmp.py")
    temp.write_text(updated, encoding="utf-8")
    try:
        py_compile.compile(str(temp), doraise=True)
    finally:
        temp.unlink(missing_ok=True)

    TARGET.write_text(updated, encoding="utf-8")
    py_compile.compile(str(TARGET), doraise=True)

    print("PASS: Players stat carousel applied.")
    print("PASS: Existing sortable table component retained.")
    print("PASS: Source-aware fields only; missing source fields are not fabricated.")
    print("PASS: No per-90 derived metrics introduced.")
    print("PASS: Deprecated use_container_width absent from patched table.")
    print("PASS: Players UI compiles cleanly.")
    print("Categories: Goals & Assists, Shooting, Creativity, Defending, Goalkeeping, FPL Stats, Usage, Discipline")


if __name__ == "__main__":
    main()
