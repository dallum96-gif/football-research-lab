from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "gui" / "app_redesign.py"

DUPLICATE = '''    render_fixture_goal_block(
        fixture["season"],
        fixture["fixture_id"],
        home,
        away,
    )
'''


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    count = text.count(DUPLICATE)
    print("============================================================")
    print("REMOVE POSITIONAL DUPLICATE FIXTURE GOAL BLOCK CALL")
    print("============================================================")
    print(f"Positional duplicate calls found: {count}")

    if count == 0:
        print("POSITIONAL DUPLICATE: already absent")
        return

    if count != 1:
        raise RuntimeError(f"Expected exactly one positional duplicate, found {count}")

    updated = text.replace(DUPLICATE, "", 1)
    TARGET.write_text(updated, encoding="utf-8")

    compile(updated, str(TARGET), "exec")
    print("POSITIONAL DUPLICATE: removed")
    print("KEYWORD GOAL BLOCK CALL: preserved")
    print("GOAL EVIDENCE: untouched")
    print("SYNTAX: app_redesign.py valid")


if __name__ == "__main__":
    main()
