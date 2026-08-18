from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "gui" / "app_redesign.py"
IMPORT_LINE = "from fixture_goal_events import fixture_goal_events, render_fixture_goal_timeline"
CALL_BLOCK = (
    "    goal_rows = fixture_goal_events(\n"
    "        fixture[\"season\"],\n"
    "        fixture[\"fixture_id\"],\n"
    "        stats.get(\"source_match_id\"),\n"
    "    )\n"
    "    render_fixture_goal_timeline(goal_rows, home, away)\n\n"
)
ANCHOR = '    if st.button("Back to Fixture Explorer", key="fixture_back_detail", type="tertiary"):\n'


def main() -> None:
    if not APP.is_file():
        raise FileNotFoundError(f"FRL app file not found: {APP}")

    source = APP.read_text(encoding="utf-8-sig")

    if IMPORT_LINE not in source:
        if "import query_api\n" not in source:
            raise RuntimeError("Could not find the query_api import anchor in app_redesign.py")
        source = source.replace(
            "import query_api\n",
            f"import query_api\n{IMPORT_LINE}\n",
            1,
        )

    if "goal_rows = fixture_goal_events(" in source:
        print("[OK] Fixture goal timeline UI is already patched.")
        return

    if ANCHOR not in source:
        raise RuntimeError("Could not find the fixture detail back-button anchor in app_redesign.py")

    source = source.replace(ANCHOR, CALL_BLOCK + ANCHOR, 1)
    APP.write_text(source, encoding="utf-8-sig")
    print(f"[OK] Patched {APP}")
    print("[OK] Goal timeline will use canonical fixture -> source match -> PulseLive -> verified player identity.")


if __name__ == "__main__":
    main()
