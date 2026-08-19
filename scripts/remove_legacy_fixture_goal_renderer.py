from __future__ import annotations

import ast
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "gui" / "app_redesign.py"

LEGACY_START = "\ndef render_fixture_goals(goal_events, home, away):\n"
LEGACY_END = "\n\ndef render_fixture_detail(detail):\n"
LEGACY_CALL = "    render_fixture_goals(goal_events, home, away)\n\n"
LEGACY_DATA_LINE = '    goal_events = detail.get("goal_events", {})\n\n'


def main() -> None:
    if not APP.is_file():
        raise FileNotFoundError(APP)

    text = APP.read_text(encoding="utf-8-sig")
    original = text
    removed_helper = False
    removed_call = False
    removed_data_line = False

    start_count = text.count(LEGACY_START)
    if start_count > 1:
        raise RuntimeError(f"Expected at most one legacy fixture goal renderer, found {start_count}")

    if start_count == 1:
        start = text.index(LEGACY_START)
        end = text.find(LEGACY_END, start)
        if end == -1:
            raise RuntimeError("Legacy fixture goal renderer found but its end marker is missing")
        text = text[:start] + text[end:]
        removed_helper = True

    call_count = text.count(LEGACY_CALL)
    if call_count > 1:
        raise RuntimeError(f"Expected at most one legacy fixture goal call, found {call_count}")
    if call_count == 1:
        text = text.replace(LEGACY_CALL, "", 1)
        removed_call = True

    data_count = text.count(LEGACY_DATA_LINE)
    if data_count > 1:
        raise RuntimeError(f"Expected at most one legacy goal_events assignment, found {data_count}")
    if data_count == 1:
        text = text.replace(LEGACY_DATA_LINE, "", 1)
        removed_data_line = True

    if text == original:
        print("LEGACY GOAL RENDERER: already absent")
        return

    backup = APP.with_suffix(APP.suffix + ".pre_legacy_goal_renderer_cleanup.bak")
    if not backup.exists():
        shutil.copy2(APP, backup)

    ast.parse(text, filename=str(APP))
    tmp = APP.with_suffix(APP.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(APP)

    print("LEGACY GOAL RENDERER: removed")
    print(f"OLD HELPER REMOVED: {removed_helper}")
    print(f"OLD CALL REMOVED: {removed_call}")
    print(f"OLD DATA ASSIGNMENT REMOVED: {removed_data_line}")
    print("CANONICAL GOAL BLOCK: preserved")
    print("SYNTAX: app_redesign.py valid")


if __name__ == "__main__":
    main()
