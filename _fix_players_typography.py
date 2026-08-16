from pathlib import Path
import re

TARGET = Path("gui/player_research_ui.py")


def replace_once(text: str, pattern: str, replacement: str, label: str) -> str:
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit(
            f"ERROR: expected Players CSS fragment not found for {label}. "
            "No changes made."
        )
    return new_text


def main() -> None:
    if not TARGET.exists():
        raise SystemExit(f"ERROR: {TARGET} not found. Run from the project root.")

    text = TARGET.read_text(encoding="utf-8-sig")

    # Structural baseline checks rather than brittle exact-line matching.
    required_fragments = [
        '.frl-player-header {',
        '.frl-player-header button {',
        '.frl-player-row {',
        '.frl-name {',
        '.frl-pos {',
        '.frl-num {',
        'data-sort="Min"',
        'data-sort="G"',
        'components_html(html, height=640, scrolling=False)',
    ]
    missing = [fragment for fragment in required_fragments if fragment not in text]
    if missing:
        raise SystemExit(
            "ERROR: Players UI does not match the expected sortable-table baseline. "
            "No changes made. Missing markers: " + ", ".join(missing)
        )

    if "use_container_width" in text:
        raise SystemExit(
            "ERROR: deprecated use_container_width already exists in the Players UI. "
            "No changes made."
        )

    new_text = text

    # Restore the approved, compact FRL table typography without changing heading size.
    new_text = replace_once(
        new_text,
        r'(\.frl-player-header\s*\{.*?\n\s*font-size:)\.55rem(;)'.replace("\\", "\\"),
        r'\g<1>.55rem\2',
        "table heading size",
    )
    new_text = replace_once(
        new_text,
        r'(\.frl-player-header\s*\{.*?\n\s*font-weight:)820(;)'.replace("\\", "\\"),
        r'\g<1>800\2',
        "table heading weight",
    )

    # Match the smaller/lighter player-name treatment from the approved Players design.
    new_text = replace_once(
        new_text,
        r'\.frl-name\s*\{[^}]*\}',
        '.frl-name { font-size:.70rem; font-weight:720; }',
        "player name typography",
    )

    # Position remains centred, numeric stats right aligned, descriptive columns left aligned.
    new_text = replace_once(
        new_text,
        r'\.frl-pos\s*\{[^}]*\}',
        '.frl-pos { color:#9aaa42; font-size:.70rem; font-weight:720; text-align:center; }',
        "position alignment/typography",
    )
    new_text = replace_once(
        new_text,
        r'\.frl-num\s*\{[^}]*\}',
        '.frl-num { text-align:right; }',
        "numeric alignment",
    )

    # Slightly widen the descriptive columns so the table breathes without changing its structure.
    old_grid = 'grid-template-columns:minmax(180px,1.8fr) 7.4rem 4rem 5rem 4rem 4rem 4.8rem 4.8rem 5.4rem 5.4rem;'
    new_grid = 'grid-template-columns:minmax(190px,1.85fr) 8rem 4rem 4.8rem 4rem 4rem 4.8rem 4.8rem 5.4rem 5.4rem;'
    if old_grid in new_text:
        new_text = new_text.replace(old_grid, new_grid, 1)

    # Preserve the working sortable-table architecture and FRL white surface.
    if 'background:#fffdf8;' not in new_text:
        raise SystemExit("ERROR: Players surface background marker missing. No changes made.")
    if 'font-family:"Source Sans", sans-serif;' not in new_text:
        raise SystemExit("ERROR: Players font-family marker missing. No changes made.")

    TARGET.write_text(new_text, encoding="utf-8")

    final = TARGET.read_text(encoding="utf-8-sig")
    if "use_container_width" in final:
        raise SystemExit("ERROR: deprecated use_container_width detected after patch.")
    if '.frl-name { font-size:.70rem; font-weight:720; }' not in final:
        raise SystemExit("ERROR: player-name typography patch did not land cleanly.")
    if '.frl-pos { color:#9aaa42; font-size:.70rem; font-weight:720; text-align:center; }' not in final:
        raise SystemExit("ERROR: position typography patch did not land cleanly.")
    if '.frl-num { text-align:right; }' not in final:
        raise SystemExit("ERROR: numeric alignment patch did not land cleanly.")
    if 'background:#fffdf8;' not in final:
        raise SystemExit("ERROR: Players white surface background was lost.")
    if 'font-family:"Source Sans", sans-serif;' not in final:
        raise SystemExit("ERROR: Players Source Sans font declaration was lost.")

    print("PASS: Players typography/alignment patch applied.")
    print("PASS: Instant browser-side sorting remains untouched.")
    print("PASS: White FRL surface remains intact.")
    print("PASS: Deprecated Streamlit API guard passed.")
    print("Review the Players page before committing the result.")


if __name__ == "__main__":
    main()
