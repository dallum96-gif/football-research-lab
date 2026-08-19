from __future__ import annotations

from pathlib import Path
import ast
import csv
import shutil

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "gui" / "app_redesign.py"
QUERY_API = ROOT / "query_api.py"
GOALS = ROOT / "data" / "fixture_goal_events.csv"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def backup(path: Path) -> None:
    backup_path = path.with_suffix(path.suffix + ".pre_goal_scorer_compat.bak")
    if not backup_path.exists():
        shutil.copy2(path, backup_path)


def atomic_write(path: Path, content: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def load_goal_rows():
    if not GOALS.is_file():
        raise RuntimeError(f"FRL goal evidence missing: {GOALS}")
    with GOALS.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        rows = list(reader)
    required = {
        "season",
        "fixture_id",
        "source_match_id",
        "source_event_id",
        "source_event_time_label",
        "source_scorer_name",
        "source_scorer_team",
        "source_fixture_home",
        "source_fixture_away",
        "identity_status",
    }
    missing = sorted(required - set(fields))
    if missing:
        raise RuntimeError("FRL goal evidence missing fields: " + ", ".join(missing))
    target = [
        row for row in rows
        if row.get("season") == "2016-17"
        and row.get("fixture_id") == "8"
        and row.get("source_match_id") == "855173"
    ]
    if len(target) != 7:
        raise RuntimeError(f"Expected 7 reference goal events; found {len(target)}")
    if any(row.get("identity_status") != "VERIFIED" for row in target):
        raise RuntimeError("Reference fixture contains an unverified goal identity")
    return rows


def patch_query_api() -> str:
    text = read(QUERY_API)

    if "GOAL_EVENTS_FILE = ROOT / \"data\" / \"fixture_goal_events.csv\"" not in text:
        anchor = 'IDENTITY_FILE = ROOT / "identity" / "team_seasons.csv"\n'
        if anchor not in text:
            raise RuntimeError("query_api.py identity anchor not found")
        text = text.replace(
            anchor,
            anchor + 'GOAL_EVENTS_FILE = ROOT / "data" / "fixture_goal_events.csv"\n',
            1,
        )

    helper = '''\n\ndef fixture_goal_events(season, fixture_id):\n    """Return verified goal events for one canonical fixture."""\n    if not GOAL_EVENTS_FILE.is_file():\n        return {\n            "query_type": "fixture_goal_events",\n            "query_version": QUERY_VERSION,\n            "season": season,\n            "fixture_id": str(fixture_id),\n            "source_file": str(GOAL_EVENTS_FILE),\n            "available": False,\n            "home": [],\n            "away": [],\n        }\n\n    rows = [\n        row for row in _load_csv(GOAL_EVENTS_FILE)\n        if row.get("season") == str(season)\n        and str(row.get("fixture_id", "")) == str(fixture_id)\n    ]\n\n    rows.sort(\n        key=lambda row: (\n            float(row.get("source_event_seconds") or 0),\n            str(row.get("source_event_id") or ""),\n        )\n    )\n\n    home = []\n    away = []\n\n    for row in rows:\n        if row.get("identity_status") != "VERIFIED":\n            raise ValueError(\n                f"Refusing unverified goal event: {season}/{fixture_id}/{row.get('source_event_id')}"\n            )\n\n        item = {\n            "minute": row.get("source_event_time_label") or "",\n            "player": row.get("source_scorer_name") or "",\n            "source_event_id": row.get("source_event_id") or "",\n            "source_match_id": row.get("source_match_id") or "",\n            "team": row.get("source_scorer_team") or "",\n        }\n\n        scorer_team = str(row.get("source_scorer_team") or "").replace("_", " ").strip()\n        fixture_home = str(row.get("source_fixture_home") or "").replace("_", " ").strip()\n        fixture_away = str(row.get("source_fixture_away") or "").replace("_", " ").strip()\n\n        if scorer_team == fixture_home:\n            home.append(item)\n        elif scorer_team == fixture_away:\n            away.append(item)\n        else:\n            raise ValueError(\n                f"Goal event team cannot be reconciled to fixture sides: "\n                f"{season}/{fixture_id}/{row.get('source_event_id')}"\n            )\n\n    return {\n        "query_type": "fixture_goal_events",\n        "query_version": QUERY_VERSION,\n        "season": season,\n        "fixture_id": str(fixture_id),\n        "source_file": str(GOAL_EVENTS_FILE),\n        "available": bool(rows),\n        "total_goals": len(rows),\n        "home": home,\n        "away": away,\n    }\n'''

    if "def fixture_goal_events(season, fixture_id):" not in text:
        anchor = "\ndef fixture_detail(season, fixture_id):\n"
        if anchor not in text:
            raise RuntimeError("query_api.py fixture_detail anchor not found")
        text = text.replace(anchor, helper + anchor, 1)

    old = 'def fixture_detail(season, fixture_id):\n    return query_lab.fixture_detail(season=season, fixture_id=fixture_id)\n'
    new = '''def fixture_detail(season, fixture_id):\n    detail = query_lab.fixture_detail(season=season, fixture_id=fixture_id)\n    detail["goal_events"] = fixture_goal_events(season, fixture_id)\n    return detail\n'''

    if old in text:
        text = text.replace(old, new, 1)
    elif '    detail["goal_events"] = fixture_goal_events(season, fixture_id)' not in text:
        raise RuntimeError("query_api.py fixture_detail contract not found")

    return text


def patch_app() -> str:
    text = read(APP)

    import_anchor = 'from gui.player_research_ui import render_player_research_ui\n'
    if "def render_fixture_goal_lines(goal_events, side):" not in text:
        if import_anchor not in text:
            raise RuntimeError("app_redesign.py player import anchor not found")
        helper = '''\n\ndef render_fixture_goal_lines(goal_events, side):\n    events = (goal_events or {}).get(side, []) if isinstance(goal_events, dict) else []\n    if not events:\n        return ""\n\n    lines = []\n    for event in events:\n        minute = str(event.get("minute") or "").strip()\n        player = str(event.get("player") or "").strip()\n        if minute and player:\n            lines.append(\n                f"<div style='color:var(--frl-muted-soft);font-size:.62rem;"\n                f"font-weight:500;line-height:1.25;margin-top:.18rem;'>{minute}' {player}</div>"\n            )\n\n    return "".join(lines)\n'''
        text = text.replace(import_anchor, import_anchor + helper, 1)

    if '    goal_events = detail.get("goal_events", {})\n' not in text:
        anchor = '    def kit_markup(team, side):\n'
        if anchor not in text:
            raise RuntimeError("app_redesign.py kit_markup anchor not found")
        text = text.replace(
            anchor,
            '    goal_events = detail.get("goal_events", {})\n\n' + anchor,
            1,
        )

    goal_call = '            + render_fixture_goal_lines(goal_events, side)\n'
    if goal_call not in text:
        anchor = '            f"</div>"\n        )\n'
        if anchor not in text:
            raise RuntimeError("app_redesign.py team header close anchor not found")
        replacement = (
            '            + render_fixture_goal_lines(goal_events, side)\n'
            '            + f"</div>"\n'
            '        )\n'
        )
        text = text.replace(anchor, replacement, 1)

    return text


def syntax_check(path: Path, content: str) -> None:
    try:
        ast.parse(content, filename=str(path))
    except SyntaxError as exc:
        raise RuntimeError(f"Syntax error in {path}: {exc}") from exc


def main() -> None:
    rows = load_goal_rows()
    new_query = patch_query_api()
    new_app = patch_app()

    syntax_check(QUERY_API, new_query)
    syntax_check(APP, new_app)

    backup(QUERY_API)
    backup(APP)
    atomic_write(QUERY_API, new_query)
    atomic_write(APP, new_app)

    print("GOAL SCORER HEADER COMPATIBILITY: integrated")
    print(f"REFERENCE FIXTURE EVENTS: {sum(1 for r in rows if r.get('season') == '2016-17' and r.get('fixture_id') == '8' and r.get('source_match_id') == '855173')}")
    print("PLACEMENT: existing team header blocks")
    print("STYLE: historical compact scorer/time treatment")
    print("STANDALONE TIMELINE: not used")
    print("MATCH AT A GLANCE: preserved")
    print("OTHER GUI ROUTES: untouched")
    print("SYNTAX: query_api.py + app_redesign.py valid")


if __name__ == "__main__":
    main()
