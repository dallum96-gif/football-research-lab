from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parent.parent
QUERY_API = ROOT / "query_api.py"
APP = ROOT / "gui" / "app_redesign.py"
GOALS = ROOT / "data" / "fixture_goal_events.csv"


def read(path):
    return path.read_text(encoding="utf-8-sig")


def write(path, content):
    path.write_text(content, encoding="utf-8")


def validate_goal_csv():
    if not GOALS.is_file():
        raise RuntimeError(f"Missing canonical goal-event CSV: {GOALS}")

    with GOALS.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    required = {
        "season", "fixture_id", "source_match_id", "source_event_id",
        "source_event_time_label", "source_scorer_name", "source_scorer_team",
        "source_scorer_id", "pulse_player_id", "archive_player_id",
        "identity_status", "fpl_element"
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

    return rows


def patch_query_api():
    text = read(QUERY_API)

    marker = 'IDENTITY_FILE = ROOT / "identity" / "team_seasons.csv"\n'
    if marker not in text:
        raise RuntimeError("query_api.py anchor missing: IDENTITY_FILE")

    if "GOAL_EVENTS_FILE = ROOT / \"data\" / \"fixture_goal_events.csv\"" not in text:
        text = text.replace(
            marker,
            marker + 'GOAL_EVENTS_FILE = ROOT / "data" / "fixture_goal_events.csv"\n',
            1,
        )

    helper = '''\n\ndef fixture_goal_events(season, fixture_id):\n    """Return verified goal events for one canonical fixture.\n\n    This is deliberately read-only: it consumes the already validated\n    canonical goal-event evidence and never reconstructs fixture identity.\n    """\n    if not GOAL_EVENTS_FILE.is_file():\n        return {\n            "query_type": "fixture_goal_events",\n            "query_version": QUERY_VERSION,\n            "season": season,\n            "fixture_id": str(fixture_id),\n            "source_file": str(GOAL_EVENTS_FILE),\n            "available": False,\n            "home": [],\n            "away": [],\n        }\n\n    rows = [\n        row for row in _load_csv(GOAL_EVENTS_FILE)\n        if row.get("season") == str(season)\n        and str(row.get("fixture_id", "")) == str(fixture_id)\n    ]\n\n    rows = sorted(\n        rows,\n        key=lambda row: (\n            float(row.get("source_event_seconds") or 0),\n            int(row.get("source_event_id") or 0),\n        ),\n    )\n\n    home = []\n    away = []\n\n    for row in rows:\n        item = {\n            "minute": row.get("source_event_time_label") or "",\n            "player": row.get("player_name") or row.get("source_scorer_name") or "",\n            "source_event_id": row.get("source_event_id") or "",\n            "source_match_id": row.get("source_match_id") or "",\n            "pulse_player_id": row.get("pulse_player_id") or "",\n            "archive_player_id": row.get("archive_player_id") or "",\n            "fpl_element": row.get("fpl_element") or "",\n            "identity_status": row.get("identity_status") or "",\n            "team": row.get("source_scorer_team") or "",\n        }\n\n        # Side is evidence-derived from the verified scorer team and the\n        # verified fixture home/away fields stored with the canonical event.\n        if row.get("source_scorer_team") == row.get("source_fixture_home"):\n            home.append(item)\n        elif row.get("source_scorer_team") == row.get("source_fixture_away"):\n            away.append(item)\n        else:\n            raise ValueError(\n                f"Goal event team cannot be reconciled to fixture sides: "\n                f"{season}/{fixture_id}/{row.get('source_event_id')}"\n            )\n\n    return {\n        "query_type": "fixture_goal_events",\n        "query_version": QUERY_VERSION,\n        "season": season,\n        "fixture_id": str(fixture_id),\n        "source_file": str(GOAL_EVENTS_FILE),\n        "available": bool(rows),\n        "total_goals": len(rows),\n        "home": home,\n        "away": away,\n    }\n'''

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

    write(QUERY_API, text)


def patch_app():
    text = read(APP)

    old_import = 'from gui.player_research_ui import render_player_research_ui\n'
    if old_import not in text:
        raise RuntimeError("app_redesign.py anchor missing: player research import")

    marker = '''\n\ndef render_fixture_goal_lines(goal_events, side):\n    events = (goal_events or {}).get(side, []) if isinstance(goal_events, dict) else []\n    if not events:\n        return ""\n\n    lines = []\n    for event in events:\n        minute = str(event.get("minute") or "").strip()\n        player = str(event.get("player") or "").strip()\n        if minute and player:\n            lines.append(\n                f"<div style='color:var(--frl-muted-soft);font-size:.62rem;"\n                f"font-weight:500;line-height:1.25;margin-top:.18rem;'>{minute}' {player}</div>"\n            )\n\n    return "".join(lines)\n'''

    if "def render_fixture_goal_lines(goal_events, side):" not in text:
        text = text.replace(old_import, old_import + marker, 1)

    header_anchor = '    def kit_markup(team, side):\n'
    if header_anchor not in text:
        raise RuntimeError("app_redesign.py anchor missing: kit_markup")

    old_signature = '    def kit_markup(team, side):\n'
    new_signature = '    goal_events = detail.get("goal_events", {})\n\n    def kit_markup(team, side):\n'
    if '    goal_events = detail.get("goal_events", {})\n\n    def kit_markup(team, side):\n' not in text:
        text = text.replace(old_signature, new_signature, 1)

    old_return = '            f"font-weight:820;line-height:1.05;\'>{team}</span>"\n'
    new_return = '            f"font-weight:820;line-height:1.05;\'>{team}</span>"\n'
    if old_return not in text:
        raise RuntimeError("app_redesign.py anchor missing: team header span")

    inject_before = '            f"</div>"\n        )\n'
    replacement = '            + render_fixture_goal_lines(goal_events, side)\n            + f"</div>"\n        )\n'
    if replacement not in text:
        text = text.replace(inject_before, replacement, 1)

    if text == read(APP):
        raise RuntimeError("app_redesign.py was not changed; refusing a no-op patch")

    write(APP, text)


def main():
    rows = validate_goal_csv()
    fixture_keys = {(r["season"], r["fixture_id"]) for r in rows}
    if len(fixture_keys) == 0:
        raise RuntimeError("No canonical fixtures found in goal-event CSV")

    patch_query_api()
    patch_app()

    print(f"PATCHED: {QUERY_API}")
    print(f"PATCHED: {APP}")
    print(f"VERIFIED GOAL ROWS: {len(rows)}")
    print(f"FIXTURES COVERED: {len(fixture_keys)}")
    print("NON-DESTRUCTION: no fixture master or importer files touched")
    print("NEXT: run the app and open the fixture landing page")


if __name__ == "__main__":
    main()
