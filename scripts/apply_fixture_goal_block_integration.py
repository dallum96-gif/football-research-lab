from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "gui" / "app_redesign.py"
BLOCK = ROOT / "gui" / "fixture_goal_block.py"

IMPORT_MARKER = "from gui.fixture_explorer import render_fixture_explorer\n"
IMPORT_LINE = "from gui.fixture_goal_block import render_fixture_goal_block\n"
SCORELINE_MARKER = "    with score_cols[2]:\n        st.markdown(\n            kit_markup(away, \"away\"),\n            unsafe_allow_html=True,\n        )\n\n"
CALL_TEXT = "    render_fixture_goal_block(\n        season=fixture[\"season\"],\n        fixture_id=str(fixture[\"fixture_id\"]),\n        home_team=home,\n        away_team=away,\n    )\n\n"


def replace_once(text: str, old: str, new: str, label: str) -> tuple[str, bool]:
    count = text.count(old)
    if count == 0:
        return text, False
    if count != 1:
        raise RuntimeError(f"Expected exactly one {label}, found {count}")
    return text.replace(old, new, 1), True


def main() -> None:
    if not APP.is_file():
        raise FileNotFoundError(APP)
    if not BLOCK.is_file():
        raise FileNotFoundError(BLOCK)

    app = APP.read_text(encoding="utf-8")
    block = BLOCK.read_text(encoding="utf-8")

    changed = False

    if "from gui.fixture_goal_block import render_fixture_goal_block\n" not in app:
        app, did = replace_once(
            app,
            IMPORT_MARKER,
            IMPORT_MARKER + IMPORT_LINE,
            "fixture goal block import marker",
        )
        if not did:
            raise RuntimeError("Could not find fixture_explorer import anchor in app_redesign.py")
        changed = True

    if CALL_TEXT not in app:
        app, did = replace_once(
            app,
            SCORELINE_MARKER,
            SCORELINE_MARKER + CALL_TEXT,
            "fixture scoreline anchor",
        )
        if not did:
            raise RuntimeError("Could not find fixture scoreline anchor in app_redesign.py")
        changed = True

    # Ensure the block consumes the validated scoring_side field for positioning.
    old_home = '''        is_home = scorer_team == str(row.get("source_fixture_home") or "").replace("_", " ").strip()\n        is_away = scorer_team == str(row.get("source_fixture_away") or "").replace("_", " ").strip()\n'''
    new_home = '''        scoring_side = str(row.get("scoring_side") or "").strip().lower()\n        is_home = scoring_side == "home"\n        is_away = scoring_side == "away"\n\n        # Backward-compatible fallback for older canonical rows that predate\n        # the explicit scoring_side field.\n        if not is_home and not is_away:\n            is_home = scorer_team == str(row.get("source_fixture_home") or "").replace("_", " ").strip()\n            is_away = scorer_team == str(row.get("source_fixture_away") or "").replace("_", " ").strip()\n'''
    block, did = replace_once(block, old_home, new_home, "goal scorer side logic")
    if did:
        changed = True

    old_filter = '''        and str(row.get("fixture_id", "")) == str(fixture_id)\n        and row.get("identity_status") == "VERIFIED"\n'''
    new_filter = '''        and str(row.get("fixture_id", "")) == str(fixture_id)\n        and (\n            row.get("identity_status") == "VERIFIED"\n            or row.get("evidence_origin") == "MANUAL_SECONDARY_VERIFIED"\n        )\n'''
    block, did = replace_once(block, old_filter, new_filter, "goal evidence verification filter")
    if did:
        changed = True

    if not changed:
        print("FIXTURE GOAL BLOCK: already integrated")
        return

    app_backup = APP.with_suffix(APP.suffix + ".pre_fixture_goal_block_integration.bak")
    block_backup = BLOCK.with_suffix(BLOCK.suffix + ".pre_fixture_goal_block_integration.bak")
    if not app_backup.exists():
        app_backup.write_text(APP.read_text(encoding="utf-8"), encoding="utf-8")
    if not block_backup.exists():
        block_backup.write_text(BLOCK.read_text(encoding="utf-8"), encoding="utf-8")

    APP.write_text(app, encoding="utf-8")
    BLOCK.write_text(block, encoding="utf-8")

    compile_targets = [APP, BLOCK]
    import py_compile

    for target in compile_targets:
        py_compile.compile(str(target), doraise=True)

    print("FIXTURE GOAL BLOCK: integrated")
    print("PLACEMENT: directly beneath scoreline")
    print("LAYOUT: home scorer | central minute rail | away scorer")
    print("SOURCE: canonical verified goal evidence")
    print("OWN GOALS: positioned using validated scoring_side")
    print("EXISTING FIXTURE HEADER: preserved")
    print("OTHER GUI ROUTES: untouched")
    print("SYNTAX: app_redesign.py + fixture_goal_block.py valid")


if __name__ == "__main__":
    main()
