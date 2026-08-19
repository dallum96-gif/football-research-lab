from __future__ import annotations

from pathlib import Path
import ast
import shutil

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "gui" / "app_redesign.py"

CALL = '''    render_fixture_goal_block(
        season=fixture["season"],
        fixture_id=str(fixture["fixture_id"]),
        home_team=home,
        away_team=away,
    )
'''


def main() -> None:
    if not APP.is_file():
        raise FileNotFoundError(APP)

    text = APP.read_text(encoding="utf-8")
    count = text.count(CALL)

    print("============================================================")
    print("DUPLICATE FIXTURE GOAL BLOCK CALL CLEANUP")
    print("============================================================")
    print(f"Goal-block calls found: {count}")

    if count < 2:
        if count == 1:
            print("GOAL BLOCK CALL: already singular")
        else:
            print("GOAL BLOCK CALL: not found")
        return

    # Surgical operation: preserve the first canonical call and remove only
    # additional identical calls.
    first = text.find(CALL)
    second = text.find(CALL, first + len(CALL))
    if second == -1:
        raise RuntimeError("Could not locate second duplicate call")

    new_text = text[:second] + text[second + len(CALL):]

    try:
        ast.parse(new_text, filename=str(APP))
    except SyntaxError as exc:
        raise RuntimeError(f"Refusing write: syntax would break {APP}: {exc}") from exc

    backup = APP.with_suffix(APP.suffix + ".pre_duplicate_goal_block_cleanup.bak")
    if not backup.exists():
        shutil.copy2(APP, backup)

    APP.write_text(new_text, encoding="utf-8")

    remaining = new_text.count(CALL)
    if remaining != 1:
        raise RuntimeError(f"Unexpected remaining goal-block call count: {remaining}")

    print("DUPLICATE GOAL BLOCK CALL: removed")
    print("REMAINING CANONICAL CALLS: 1")
    print("GOAL EVIDENCE: untouched")
    print("FIXTURE GOAL BLOCK: untouched")
    print("OTHER GUI ROUTES: untouched")
    print("SYNTAX: app_redesign.py valid")


if __name__ == "__main__":
    main()
