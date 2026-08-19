from pathlib import Path
import ast
import csv
import shutil

ROOT = Path(__file__).resolve().parent.parent
QUERY_API = ROOT / "query_api.py"
APP = ROOT / "gui" / "app_redesign.py"
GOALS = ROOT / "data" / "fixture_goal_events.csv"


def read(path):
    return path.read_text(encoding="utf-8-sig")


def atomic_write(path, content):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def validate_goal_csv():
    if not GOALS.is_file():
        raise RuntimeError(f"Missing canonical goal-event CSV: {GOALS}")

    with GOALS.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    required = {
        "season", "fixture_id", "source_match_id", "source_event_id",
        "source_event_time_label", "source_scorer_name", "source_scorer_team",
        "source_scorer_id", "source_fixture_home", "source_fixture_away",
        "pulse_player_id", "archive_player_id", "identity_status", "fpl_element"
    }
    missing = sorted(required - set(rows[0] if rows else []))
    if missing:
        raise RuntimeError(f"Goal-event CSV missing required fields: {missing}")
    if not rows:
        raise RuntimeError("Goal-event CSV contains no rows")
    if any(row.get("identity_status") != "VERIFIED" for row in rows):
        raise RuntimeError("Goal-event CSV contains non-VERIFIED identity rows")
    if len({row["source_event_id"] for row in rows}) != len(rows):
        raise RuntimeError("Goal-event CSV contains duplicate source_event_id values")

    target = [
        row for row in rows
        if row.get("season") == "2016-17"
        and row.get("fixture_id") == "8"
        and row.get("source_match_id") == "855173"
    ]
    if len(target) != 7:
        raise RuntimeError(
            "Expected exactly 7 verified goal events for 2016-17/8 "
            f"(source match 855173); found {len(target)}"
        )

    return rows


def backup(path):
    backup_path = path.with_suffix(path.suffix + ".pre_goal_scorers.bak")
    if not backup_path.exists():
        shutil.copy2(path, backup_path)


def patch_query_api():
    text = read(QUERY_API)

    marker = 'IDENTITY_FILE = ROOT / "identity" / "team_seasons.csv"\n'
    if marker not in text:
        raise RuntimeError("query_api.py anchor missing: IDENTITY_FILE")

    if 'GOAL_EVENTS_FILE = ROOT / "data" / "fixture_goal_events.csv"' not in text:
        text = text.replace(
            marker,
            marker + 'GOAL_EVENTS_FILE = ROOT / "data" / "fixture_goal_events.csv"\n',
            1,
        )

    helper = '''\n\ndef fixture_goal_events(season, fixture_id):\n    """Return verified goal events for one canonical fixture."""\n    if not GOAL_EVENTS_FILE.is_file():\n        return {\n            "query_type": "fixture_goal_events",\n            "query_version": QUERY_VERSION,\n            "season": season,\n            "fixture_id": str(fixture_id),\n            "source_file": str(GOAL_EVENTS_FILE),\n            "available": False,\n            "home": [],\n            "away": [],\n        }\n\n    rows = [\n        row for row in _load_csv(GOAL_EVENTS_FILE)\n        if row.get("season") == str(season)\n        and str(row.get("fixture_id", "")) == str(fixture_id)\n    ]\n\n    rows = sorted(\n        rows,\n        key=lambda row: (\n            float(row.get("source_event_seconds") or 0),\n            int(row.get("source_event_id") or 0),\n        ),\n    )\n\n    home = []\n    away = []\n\n    for row in rows:\n        if row.get("identity_status") != "VERIFIED":\n            raise ValueError(\n                f"Refusing unverified goal event: "\n                f"{season}/{fixture_id}/{row.get('source_event_id')}"\n            )\n\n        item = {\n            "minute": row.get("source_event_time_label") or "",\n            "player": row.get("player_name") or row.get("source_scorer_name") or "",\n            "source_event_id": row.get("source_event_id") or "",\n            "source_match_id": row.get("source_match_id") or "",\n            "pulse_player_id": row.get("pulse_player_id") or "",\n            "archive_player_id": row.get("archive_player_id") or "",\n            "fpl_element": row.get("fpl_element") or "",\n            "identity_status": row.get("identity_status") or "",\n            "team": row.get("source_scorer_team") or "",\n        }\n\n        if row.get("source_scorer_team") == row.get("source_fixture_home"):\n            home.append(item)\n        elif row.get("source_scorer_team") == row.get("source_fixture_away"):\n            away.append(item)\n        else:\n            raise ValueError(\n                f"Goal event team cannot be reconciled to fixture sides: "\n                f"{season}/{fixture_id}/{row.get('source_event_id')}"\n            )\n\n    return {\n        "query_type": "fixture_goal_events",\n        "query_version": QUERY_VERSION,\n        "season": season,\n        "fixture_id": str(fixture_id),\n        "source_file": str(GOAL_EVENTS_FILE),\n        "available": bool(rows),\n        "total_goals": len(rows),\n        "home": home,\n        "away": away,\n    }\n'''

    if "def fixture_goal_events(season, fixture_id):" not in text:
        fixture_marker = '\ndef fixture_detail(season, fixture_id):\n'
        if fixture_marker not in text:
            raise RuntimeError("query_api.py anchor missing: fixture_detail")
        text = text.replace(fixture_marker, helper + fixture_marker, 1)

    old = '    return query_lab.fixture_detail(season=season, fixture_id=fixture_id)\n'
    new = '    detail = query_lab.fixture_detail(season=season, fixture_id=fixture_id)\n    detail["goal_events"] = fixture_goal_events(season, fixture_id)\n    return detail\n'
    if old not in text:
        raise RuntimeError("query_api.py anchor missing: fixture_detail return")
    text = text.replace(old, new, 1)

    return text


def patch_app():
    text = read(APP)

    import_anchor = 'from gui.player_research_ui import render_player_research_ui\n'
    if import_anchor not in text:
        raise RuntimeError("app_redesign.py anchor missing: player research import")

    helper = '''\n\ndef render_fixture_goal_lines(goal_events, side):\n    events = (goal_events or {}).get(side, []) if isinstance(goal_events, dict) else []\n    if not events:\n        return ""\n\n    lines = []\n    for event in events:\n        minute = str(event.get("minute") or "").strip()\n        player = str(event.get("player") or "").strip()\n        if minute and player:\n            lines.append(\n                f"<div style='color:var(--frl-muted-soft);font-size:.62rem;font-weight:500;line-height:1.25;margin-top:.18rem;'>{minute}' {player}</div>"\n            )\n\n    return "".join(lines)\n'''

    if "def render_fixture_goal_lines(goal_events, side):" not in text:
        text = text.replace(import_anchor, import_anchor + helper, 1)

    goal_marker = '    home_core = stats["home"]["core"]\n    away_core = stats["away"]["core"]\n'
    if goal_marker not in text:
        raise RuntimeError("app_redesign.py anchor missing: match core stats")
    if '    goal_events = detail.get("goal_events", {})\n' not in text:
        text = text.replace(goal_marker, goal_marker + '\n    goal_events = detail.get("goal_events", {})\n', 1)

    home_call = '            kit_markup(home, "home"),\n            unsafe_allow_html=True,\n        )'
    home_replacement = '            kit_markup(home, "home"),\n            unsafe_allow_html=True,\n        )\n        st.markdown(\n            render_fixture_goal_lines(goal_events, "home"),\n            unsafe_allow_html=True,\n        )'

    away_call = '            kit_markup(away, "away"),\n            unsafe_allow_html=True,\n        )'
    away_replacement = '            kit_markup(away, "away"),\n            unsafe_allow_html=True,\n        )\n        st.markdown(\n            render_fixture_goal_lines(goal_events, "away"),\n            unsafe_allow_html=True,\n        )'

    if home_call not in text:
        raise RuntimeError("app_redesign.py anchor missing: home team markup")
    if away_call not in text:
        raise RuntimeError("app_redesign.py anchor missing: away team markup")

    text = text.replace(home_call, home_replacement, 1)
    text = text.replace(away_call, away_replacement, 1)

    return text


def syntax_check(path, content):
    try:
        ast.parse(content, filename=str(path))
    except SyntaxError as exc:
        raise RuntimeError(f"Syntax check failed for {path}: {exc}") from exc


def main():
    rows = validate_goal_csv()
    new_query_api = patch_query_api()
    new_app = patch_app()

    syntax_check(QUERY_API, new_query_api)
    syntax_check(APP, new_app)

    backup(QUERY_API)
    backup(APP)
    atomic_write(QUERY_API, new_query_api)
    atomic_write(APP, new_app)

    print(f"PATCHED: {QUERY_API}")
    print(f"PATCHED: {APP}")
    print(f"VERIFIED GOAL ROWS: {len(rows)}")
    print("TARGET: 2016-17/8 / source match 855173 = 7 verified events")
    print("NON-DESTRUCTION: fixture master and goal-event importer untouched")
    print("BACKUPS: *.pre_goal_scorers.bak created before writes")
    print("SYNTAX: query_api.py and app_redesign.py compile successfully")
    print("NEXT: launch Streamlit and open fixture 2016-17:8")


if __name__ == "__main__":
    main()
