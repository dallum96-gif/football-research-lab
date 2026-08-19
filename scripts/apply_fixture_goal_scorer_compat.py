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
        "season", "fixture_id", "source_match_id", "source_event_id",
        "source_event_time_label", "source_event_seconds", "source_scorer_name",
        "source_scorer_team", "source_fixture_home", "source_fixture_away",
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

    helper = '''\n\ndef fixture_goal_events(season, fixture_id):\n    """Return verified goal events for one canonical fixture."""\n    if not GOAL_EVENTS_FILE.is_file():\n        return {\n            "query_type": "fixture_goal_events",\n            "query_version": QUERY_VERSION,\n            "season": season,\n            "fixture_id": str(fixture_id),\n            "source_file": str(GOAL_EVENTS_FILE),\n            "available": False,\n            "home": [],\n            "away": [],\n        }\n\n    rows = [\n        row for row in _load_csv(GOAL_EVENTS_FILE)\n        if row.get("season") == str(season)\n        and str(row.get("fixture_id", "")) == str(fixture_id)\n    ]\n\n    rows.sort(\n        key=lambda row: (\n            float(row.get("source_event_seconds") or 0),\n            str(row.get("source_event_id") or ""),\n        )\n    )\n\n    home = []\n    away = []\n\n    for row in rows:\n        if row.get("identity_status") != "VERIFIED":\n            raise ValueError(\n                f"Refusing unverified goal event: {season}/{fixture_id}/{row.get('source_event_id')}"\n            )\n\n        item = {\n            "minute": row.get("source_event_time_label") or "",\n            "player": row.get("source_scorer_name") or "",\n            "source_event_id": row.get("source_event_id") or "",\n            "source_match_id": row.get("source_match_id") or "",\n            "team": row.get("source_scorer_team") or "",\n            "seconds": row.get("source_event_seconds") or "0",\n        }\n\n        scorer_team = str(row.get("source_scorer_team") or "").replace("_", " ").strip()\n        fixture_home = str(row.get("source_fixture_home") or "").replace("_", " ").strip()\n        fixture_away = str(row.get("source_fixture_away") or "").replace("_", " ").strip()\n\n        if scorer_team == fixture_home:\n            home.append(item)\n        elif scorer_team == fixture_away:\n            away.append(item)\n        else:\n            raise ValueError(\n                f"Goal event team cannot be reconciled to fixture sides: "\n                f"{season}/{fixture_id}/{row.get('source_event_id')}"\n            )\n\n    return {\n        "query_type": "fixture_goal_events",\n        "query_version": QUERY_VERSION,\n        "season": season,\n        "fixture_id": str(fixture_id),\n        "source_file": str(GOAL_EVENTS_FILE),\n        "available": bool(rows),\n        "total_goals": len(rows),\n        "home": home,\n        "away": away,\n    }\n'''

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


def _remove_old_goal_helper(text: str) -> str:
    start_marker = "\ndef render_fixture_goal_lines(goal_events, side):\n"
    start = text.find(start_marker)
    if start == -1:
        return text
    end_marker = "\n\ndef render_fixture_detail(detail):\n"
    end = text.find(end_marker, start)
    if end == -1:
        raise RuntimeError("Could not locate end of old goal helper")
    return text[:start] + text[end:]


def patch_app() -> str:
    text = read(APP)

    old_import = 'from gui.player_research_ui import render_player_research_ui\n'
    if "def render_fixture_goals(goal_events, home, away):" not in text:
        if old_import not in text:
            raise RuntimeError("app_redesign.py player import anchor not found")

        text = _remove_old_goal_helper(text)

        helper = '''\n\ndef render_fixture_goals(goal_events, home, away):\n    if not isinstance(goal_events, dict) or not goal_events.get("available"):\n        return\n\n    events = [\n        *(dict(event, side="home") for event in goal_events.get("home", [])),\n        *(dict(event, side="away") for event in goal_events.get("away", [])),\n    ]\n    if not events:\n        return\n\n    def event_seconds(event):\n        try:\n            return float(event.get("seconds") or 0)\n        except (TypeError, ValueError):\n            return 0.0\n\n    events.sort(key=lambda event: (event_seconds(event), str(event.get("source_event_id") or "")))\n\n    st.markdown(\n        "<div style='margin-top:.95rem;text-align:center;color:var(--frl-muted-soft);"\n        "font-size:.56rem;font-weight:820;letter-spacing:.14em;text-transform:uppercase;'>"\n        "Goals</div>",\n        unsafe_allow_html=True,\n    )\n\n    rows = []\n    for event in events:\n        minute = str(event.get("minute") or "").strip()\n        player = str(event.get("player") or "").strip()\n        if event.get("side") == "home":\n            rows.append(\n                f"<div style='display:grid;grid-template-columns:1fr 58px 1fr;align-items:center;"\n                f"min-height:1.45rem;'>"\n                f"<div style='text-align:right;color:var(--frl-text);font-size:.72rem;font-weight:760;'>"\n                f"{player}</div>"\n                f"<div style='position:relative;text-align:center;color:var(--frl-muted-soft);font-size:.62rem;font-weight:820;'>"\n                f"<span style='position:absolute;left:50%;top:-.35rem;bottom:-.35rem;width:1px;"\n                f"background:var(--frl-border);transform:translateX(-50%);'></span>"\n                f"<span style='position:relative;background:var(--frl-surface);padding:0 .28rem;'>{minute}'</span>"\n                f"</div>"\n                f"<div></div></div>"\n            )\n        else:\n            rows.append(\n                f"<div style='display:grid;grid-template-columns:1fr 58px 1fr;align-items:center;"\n                f"min-height:1.45rem;'>"\n                f"<div></div>"\n                f"<div style='position:relative;text-align:center;color:var(--frl-muted-soft);font-size:.62rem;font-weight:820;'>"\n                f"<span style='position:absolute;left:50%;top:-.35rem;bottom:-.35rem;width:1px;"\n                f"background:var(--frl-border);transform:translateX(-50%);'></span>"\n                f"<span style='position:relative;background:var(--frl-surface);padding:0 .28rem;'>{minute}'</span>"\n                f"</div>"\n                f"<div style='text-align:left;color:var(--frl-text);font-size:.72rem;font-weight:760;'>"\n                f"{player}</div></div>"\n            )\n\n    st.markdown(\n        "<div style='margin:.15rem auto .65rem;max-width:760px;'>"\n        + "".join(rows)\n        + "</div>",\n        unsafe_allow_html=True,\n    )\n'''
        text = text.replace(old_import, old_import + helper, 1)

    if '    goal_events = detail.get("goal_events", {})\n' not in text:
        anchor = '    def kit_markup(team, side):\n'
        if anchor not in text:
            raise RuntimeError("app_redesign.py kit_markup anchor not found")
        text = text.replace(
            anchor,
            '    goal_events = detail.get("goal_events", {})\n\n' + anchor,
            1,
        )

    old_goal_call = '            + render_fixture_goal_lines(goal_events, side)\n'
    if old_goal_call in text:
        text = text.replace(old_goal_call, '', 1)

    if '    render_fixture_goals(goal_events, home, away)\n\n' not in text:
        back_button_anchor = '    if st.button("Back to Fixture Explorer", key="fixture_back_detail", type="tertiary"):\n'
        if back_button_anchor not in text:
            raise RuntimeError("app_redesign.py back button anchor not found")
        text = text.replace(
            back_button_anchor,
            '    render_fixture_goals(goal_events, home, away)\n\n' + back_button_anchor,
            1,
        )

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

    print("GOAL SCORER TIMELINE: integrated")
    print("REFERENCE FIXTURE EVENTS: 7")
    print("PLACEMENT: beneath scoreline")
    print("LAYOUT: home scorer | minute rail | away scorer")
    print("STYLE: compact historical treatment")
    print("EXISTING FIXTURE HEADER: preserved")
    print("MATCH AT A GLANCE: preserved")
    print("OTHER GUI ROUTES: untouched")
    print("SYNTAX: query_api.py + app_redesign.py valid")


if __name__ == "__main__":
    main()
