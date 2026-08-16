from pathlib import Path
import re
import subprocess
import sys

TARGET = Path("gui/player_research_ui.py")


def replace_once(text: str, pattern: str, replacement: str, label: str) -> str:
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE | re.DOTALL)
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

    required = [
        ".frl-player-table",
        ".frl-player-header",
        ".frl-player-header button",
        ".frl-player-row",
        ".frl-name",
        ".frl-pos",
        ".frl-num",
        'data-sort="G"',
        'data-sort="xG"',
        "components_html(html, height=640, scrolling=False)",
        'background:#fffdf8;',
        'font-family:"Source Sans", sans-serif;',
    ]
    missing = [marker for marker in required if marker not in text]
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

    # The sortable table HTML lives inside a Python f-string, so literal CSS braces
    # are normally doubled ({{ / }}). Previous attempts briefly introduced single
    # braces, which produced the f-string SyntaxError. Repair that malformed form first.
    new_text = new_text.replace(
        '.frl-name { font-size:.71rem; font-weight:720; }}',
        '.frl-name {{ font-size:.71rem; font-weight:720; }}',
        1,
    )

    # Restore the approved heading weight while deliberately keeping the existing size.
    new_text = replace_once(
        new_text,
        r'(\.frl-player-header\s*\{\{.*?font-size\s*:\s*\.55rem\s*;\s*font-weight\s*:\s*)820(\s*;)',
        r'\g<1>800\2',
        "table heading weight",
    )
    new_text = replace_once(
        new_text,
        r'(\.frl-player-header button\s*\{\{.*?font-size\s*:\s*\.55rem\s*;\s*font-weight\s*:\s*)820(\s*;)',
        r'\g<1>800\2',
        "sortable heading weight",
    )

    # Restore the lighter player-name emphasis used by the approved FRL player cards.
    # Accept both doubled-brace f-string CSS and the malformed single-brace form.
    new_text = replace_once(
        new_text,
        r'\.frl-name\s*(?:\{\{|\{)[^\n]*?(?:\}\}|\})',
        '.frl-name {{ font-size:.71rem; font-weight:720; }}',
        "player name typography",
    )

    # Position remains centred and numeric statistics remain right aligned.
    # We intentionally do not alter the grid dimensions or font sizes.

    TARGET.write_text(new_text, encoding="utf-8")

    final = TARGET.read_text(encoding="utf-8-sig")
    checks = {
        "deprecated API absent": "use_container_width" not in final,
        "white FRL surface retained": "background:#fffdf8;" in final,
        "Source Sans retained": 'font-family:"Source Sans", sans-serif;' in final,
        "heading size retained": re.search(
            r'\.frl-player-header\s*\{\{.*?font-size\s*:\s*\.55rem\s*;', final, re.DOTALL
        ) is not None,
        "heading weight restored": re.search(
            r'\.frl-player-header\s*\{\{.*?font-weight\s*:\s*800\s*;', final, re.DOTALL
        ) is not None,
        "sortable heading weight restored": re.search(
            r'\.frl-player-header button\s*\{\{.*?font-weight\s*:\s*800\s*;', final, re.DOTALL
        ) is not None,
        "player name weight restored": '.frl-name {{ font-size:.71rem; font-weight:720; }}' in final,
        "browser sorting retained": 'data-sort="G"' in final and 'data-sort="xG"' in final,
    }

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise SystemExit(
            "ERROR: post-write contract check failed: " + ", ".join(failed)
        )

    # Critical safety gate: the edited Players module must compile before we claim success.
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(TARGET)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(
            "ERROR: player_research_ui.py still fails Python syntax validation. "
            "No further changes made.\n" + result.stderr.strip()
        )

    print("PASS: Players typography restored without changing table size/layout.")
    print("PASS: Instant browser-side sorting remains untouched.")
    print("PASS: White FRL surface and Source Sans declaration remain intact.")
    print("PASS: No deprecated use_container_width API is present.")
    print("PASS: player_research_ui.py passes py_compile.")
    print("Review the Players page before committing the result.")


if __name__ == "__main__":
    main()
