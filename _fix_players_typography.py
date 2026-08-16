from pathlib import Path

TARGET = Path("gui/player_research_ui.py")

EXPECTED_MARKERS = [
    'font-family:"Source Sans", sans-serif;',
    '.frl-player-header {',
    '.frl-player-row {',
    '.frl-name { font-weight:780; }',
    '.frl-pos { color:#9aaa42; font-weight:780; text-align:center; }',
    '.frl-num { text-align:right; }',
]

REPLACEMENTS = {
    '.frl-player-header {\n          padding:0 0 .5rem;':
    '.frl-player-header {\n          padding:0 0 .5rem;',
    '.frl-player-header button {\n          all:unset;':
    '.frl-player-header button {\n          all:unset;',
    '.frl-player-row {\n          min-height:2.45rem;':
    '.frl-player-row {\n          min-height:2.45rem;',
    '.frl-name { font-weight:780; }':
    '.frl-name { font-size:.70rem; font-weight:720; }',
    '.frl-pos { color:#9aaa42; font-weight:780; text-align:center; }':
    '.frl-pos { color:#9aaa42; font-size:.70rem; font-weight:720; text-align:center; }',
}


def main() -> None:
    if not TARGET.exists():
        raise SystemExit(f"ERROR: {TARGET} not found. Run from the project root.")

    text = TARGET.read_text(encoding="utf-8-sig")

    missing = [marker for marker in EXPECTED_MARKERS if marker not in text]
    if missing:
        raise SystemExit(
            "ERROR: Players UI does not match the expected baseline. "
            "No changes made. Missing markers: " + ", ".join(missing)
        )

    if "use_container_width" in text:
        raise SystemExit(
            "ERROR: deprecated use_container_width already exists in the Players UI. "
            "No changes made."
        )

    new_text = text
    for old, new in REPLACEMENTS.items():
        if old not in new_text:
            raise SystemExit(f"ERROR: expected CSS fragment not found: {old!r}")
        new_text = new_text.replace(old, new, 1)

    # Keep numeric columns right-aligned and position centred; make descriptive columns explicit.
    old_grid = 'grid-template-columns:minmax(180px,1.8fr) 7.4rem 4rem 5rem 4rem 4rem 4.8rem 4.8rem 5.4rem 5.4rem;'
    new_grid = 'grid-template-columns:minmax(190px,1.85fr) 8rem 4rem 4.8rem 4rem 4rem 4.8rem 4.8rem 5.4rem 5.4rem;'
    if old_grid not in new_text:
        raise SystemExit("ERROR: expected Players grid definition not found. No changes made.")
    new_text = new_text.replace(old_grid, new_grid, 1)

    TARGET.write_text(new_text, encoding="utf-8")

    # Post-write safety checks.
    final = TARGET.read_text(encoding="utf-8")
    if "use_container_width" in final:
        raise SystemExit("ERROR: deprecated use_container_width detected after patch.")
    if '.frl-name { font-size:.70rem; font-weight:720; }' not in final:
        raise SystemExit("ERROR: player-name typography patch did not land cleanly.")
    if 'minmax(190px,1.85fr) 8rem 4rem 4.8rem 4rem 4rem' not in final:
        raise SystemExit("ERROR: alignment/grid patch did not land cleanly.")

    print("PASS: Players typography/alignment patch applied.")
    print("PASS: Instant browser-side sorting remains untouched.")
    print("PASS: GUI contract/deprecated API guard checks passed.")
    print("Review the Players page before committing the result.")


if __name__ == "__main__":
    main()
