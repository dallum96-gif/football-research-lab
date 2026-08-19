from __future__ import annotations

from pathlib import Path
import ast
import shutil

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "gui" / "app_redesign.py"
GOALS = ROOT / "data" / "fixture_goal_events.csv"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def backup(path: Path) -> None:
    backup_path = path.with_suffix(path.suffix + ".pre_goal_block.bak")
    if not backup_path.exists():
        shutil.copy2(path, backup_path)


def validate() -> None:
    if not GOALS.is_file():
        raise RuntimeError(f"FRL goal evidence missing: {GOALS}")

    import csv
    with GOALS.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    required = {
        "season", "fixture_id", "source_match_id", "source_event_id",
        "source_event_time_label", "source_scorer_name", "source_scorer_team",
        "source_fixture_home", "source_fixture_away", "identity_status",
    }
    fields = set(rows[0]) if rows else set()
    missing = sorted(required - fields)
    if missing:
        raise RuntimeError("Goal evidence missing fields: " + ", ".join(missing))

    reference = [
        row for row in rows
        if row.get("season") == "2016-17"
        and row.get("fixture_id") == "8"
        and row.get("source_match_id") == "855173"
    ]
    if len(reference) != 7:
        raise RuntimeError(f"Reference fixture expected 7 verified events; found {len(reference)}")
    if any(row.get("identity_status") != "VERIFIED" for row in reference):
        raise RuntimeError("Reference fixture contains an unverified goal event")


def patch() -> str:
    text = read(APP)

    import_anchor = "from gui.player_research_ui import render_player_research_ui\n"
    import_line = import_anchor + "from gui.fixture_goal_block import render_fixture_goal_block\n"
    if "from gui.fixture_goal_block import render_fixture_goal_block" not in text:
        if import_anchor not in text:
            raise RuntimeError("ABORT: known GUI import anchor not found")
        text = text.replace(import_anchor, import_line, 1)

    score_anchor = '''    with score_cols[2]:\n        st.markdown(\n            kit_markup(away, "away"),\n            unsafe_allow_html=True,\n        )\n\n    if st.button("Back to Fixture Explorer", key="fixture_back_detail", type="tertiary"):\n'''
    if score_anchor not in text:
        raise RuntimeError("ABORT: exact score-header anchor not found; no GUI write performed")

    replacement = '''    with score_cols[2]:\n        st.markdown(\n            kit_markup(away, "away"),\n            unsafe_allow_html=True,\n        )\n\n    render_fixture_goal_block(\n        fixture["season"],\n        fixture["fixture_id"],\n        home,\n        away,\n    )\n\n    if st.button("Back to Fixture Explorer", key="fixture_back_detail", type="tertiary"):\n'''

    if 'render_fixture_goal_block(\n        fixture["season"],\n        fixture["fixture_id"]' not in text:
        text = text.replace(score_anchor, replacement, 1)

    try:
        ast.parse(text, filename=str(APP))
    except SyntaxError as exc:
        raise RuntimeError(f"ABORT: resulting app_redesign.py is invalid: {exc}") from exc

    return text


def main() -> None:
    validate()
    new_text = patch()
    backup(APP)
    APP.write_text(new_text, encoding="utf-8")

    print("FIXTURE GOAL BLOCK: integrated")
    print("REFERENCE FIXTURE EVENTS: 7")
    print("PLACEMENT: directly beneath existing scoreline")
    print("LAYOUT: home scorer | central minute rail | away scorer")
    print("EXISTING SCORE HEADER: preserved")
    print("MATCH AT A GLANCE: preserved")
    print("OTHER GUI ROUTES: untouched")
    print("SYNTAX: app_redesign.py valid")


if __name__ == "__main__":
    main()
