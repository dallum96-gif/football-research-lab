from __future__ import annotations

from pathlib import Path
import ast
import shutil

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "gui" / "app_redesign.py"
QUERY_API = ROOT / "query_api.py"
GOALS = ROOT / "data" / "fixture_goal_events.csv"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def backup(path: Path) -> None:
    backup_path = path.with_suffix(path.suffix + ".pre_goal_timeline.bak")
    if not backup_path.exists():
        shutil.copy2(path, backup_path)


def atomic_write(path: Path, content: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def validate_goal_evidence() -> None:
    if not GOALS.is_file():
        raise RuntimeError(
            f"FRL goal evidence missing: {GOALS}. "
            "Run build_fixture_goal_evidence.py first."
        )

    import csv

    with GOALS.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    required = {
        "frl_source_file",
        "frl_source_sha256",
        "frl_source_row",
        "season",
        "fixture_id",
        "source_event_id",
        "source_event_time_label",
        "source_scorer_name",
        "source_scorer_team",
        "identity_status",
    }
    fields = set(rows[0]) if rows else set()
    missing = sorted(required - fields)
    if missing:
        raise RuntimeError(f"Goal evidence missing required fields: {missing}")

    reference = [
        row for row in rows
        if row.get("season") == "2016-17"
        and row.get("fixture_id") == "8"
        and row.get("source_match_id") == "855173"
    ]

    if len(reference) != 7:
        raise RuntimeError(
            f"Expected 7 goal events for 2016-17 fixture 8 / source match 855173; "
            f"found {len(reference)}"
        )

    if any(row.get("identity_status") != "VERIFIED" for row in reference):
        raise RuntimeError("Reference fixture contains an unverified goal identity")


def patch_query_api() -> str:
    text = read(QUERY_API)

    if "GOAL_EVENTS_FILE = ROOT / \"data\" / \"fixture_goal_events.csv\"" not in text:
        anchor = 'IDENTITY_FILE = ROOT / "identity" / "team_seasons.csv"\n'
        if anchor not in text:
            raise RuntimeError("query_api.py identity-file anchor not found")
        text = text.replace(
            anchor,
            anchor + 'GOAL_EVENTS_FILE = ROOT / "data" / "fixture_goal_events.csv"\n',
            1,
        )

    helper = '''\n\ndef fixture_goal_events(season, fixture_id):\n    """Return verified goal events attached to one canonical fixture."""\n    if not GOAL_EVENTS_FILE.is_file():\n        return {\n            "query_type": "fixture_goal_events",\n            "query_version": QUERY_VERSION,\n            "season": season,\n            "fixture_id": str(fixture_id),\n            "source_file": str(GOAL_EVENTS_FILE),\n            "available": False,\n            "home": [],\n            "away": [],\n        }\n\n    rows = [\n        row for row in _load_csv(GOAL_EVENTS_FILE)\n        if row.get("season") == str(season)\n        and str(row.get("fixture_id", "")) == str(fixture_id)\n    ]\n\n    rows.sort(\n        key=lambda row: (\n            float(row.get("source_event_seconds") or 0),\n            str(row.get("source_event_id") or ""),\n        )\n    )\n\n    fixture_detail_base = query_lab.fixture_detail(\n        season=season,\n        fixture_id=fixture_id,\n    )\n    home_team = fixture_detail_base["fixture"].get("home_team_name", "")\n    away_team = fixture_detail_base["fixture"].get("away_team_name", "")\n\n    home = []\n    away = []\n\n    for row in rows:\n        if row.get("identity_status") != "VERIFIED":\n            raise ValueError(\n                f"Refusing unverified goal event for {season}/{fixture_id}: "\n                f"{row.get('source_event_id')}"\n            )\n\n        item = {\n            "minute": row.get("source_event_time_label") or "",\n            "player": row.get("source_scorer_name") or "",\n            "team": row.get("source_scorer_team") or "",\n            "source_event_id": row.get("source_event_id") or "",\n        }\n\n        scorer_team = str(row.get("source_scorer_team") or "").replace("_", " ").strip()\n        fixture_home = str(row.get("source_fixture_home") or "").replace("_", " ").strip()\n        fixture_away = str(row.get("source_fixture_away") or "").replace("_", " ").strip()\n\n        if scorer_team == fixture_home or scorer_team == home_team:\n            home.append(item)\n        elif scorer_team == fixture_away or scorer_team == away_team:\n            away.append(item)\n        else:\n            raise ValueError(\n                f"Goal event team cannot be reconciled to fixture sides for "\n                f"{season}/{fixture_id}: {row.get('source_event_id')}"\n            )\n\n    return {\n        "query_type": "fixture_goal_events",\n        "query_version": QUERY_VERSION,\n        "season": season,\n        "fixture_id": str(fixture_id),\n        "source_file": str(GOAL_EVENTS_FILE),\n        "available": bool(rows),\n        "total_goals": len(rows),\n        "home": home,\n        "away": away,\n    }\n'''

    if "def fixture_goal_events(season, fixture_id):" not in text:
        anchor = "\ndef fixture_detail(season, fixture_id):\n"
        if anchor not in text:
            raise RuntimeError("query_api.py fixture_detail anchor not found")
        text = text.replace(anchor, helper + anchor, 1)

    old = 'def fixture_detail(season, fixture_id):\n    return query_lab.fixture_detail(season=season, fixture_id=fixture_id)\n'
    new = '''def fixture_detail(season, fixture_id):\n    detail = query_lab.fixture_detail(season=season, fixture_id=fixture_id)\n    detail["goal_events"] = fixture_goal_events(season, fixture_id)\n    return detail\n'''
    if old not in text and 'detail["goal_events"] = fixture_goal_events(season, fixture_id)' not in text:
        raise RuntimeError("query_api.py fixture_detail body does not match expected contract")

    if old in text:
        text = text.replace(old, new, 1)

    return text


def patch_app() -> str:
    text = read(APP)

    import_anchor = "from gui.player_research_ui import render_player_research_ui\n"
    import_line = import_anchor + "from gui.fixture_goal_timeline import render_fixture_goal_timeline\n"
    if "from gui.fixture_goal_timeline import render_fixture_goal_timeline" not in text:
        if import_anchor not in text:
            raise RuntimeError("app_redesign.py import anchor not found")
        text = text.replace(import_anchor, import_line, 1)

    section_anchor = "    # ------------------------------------------------------------\n    # MATCH AT A GLANCE\n    # ------------------------------------------------------------\n"
    call = "    render_fixture_goal_timeline(detail.get(\"goal_events\"))\n\n"
    if call not in text:
        if section_anchor not in text:
            raise RuntimeError("app_redesign.py match-at-a-glance anchor not found")
        text = text.replace(section_anchor, call + section_anchor, 1)

    return text


def syntax_check(path: Path, content: str) -> None:
    try:
        ast.parse(content, filename=str(path))
    except SyntaxError as exc:
        raise RuntimeError(f"Syntax error in {path}: {exc}") from exc


def main() -> None:
    validate_goal_evidence()

    new_query = patch_query_api()
    new_app = patch_app()

    syntax_check(QUERY_API, new_query)
    syntax_check(APP, new_app)

    backup(QUERY_API)
    backup(APP)
    atomic_write(QUERY_API, new_query)
    atomic_write(APP, new_app)

    print("FIXTURE GOAL TIMELINE: integrated")
    print("REFERENCE FIXTURE: 2016-17 / 8 / source match 855173 = 7 verified events")
    print("EVIDENCE SCHEMA: promoted source fields + FRL provenance metadata")
    print("EXISTING FIXTURE HEADER: preserved")
    print("MATCH AT A GLANCE: preserved")
    print("OTHER GUI ROUTES: untouched")
    print("BACKUPS: created before writes")
    print("SYNTAX: query_api.py + app_redesign.py valid")


if __name__ == "__main__":
    main()
