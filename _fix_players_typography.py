from pathlib import Path
import py_compile

TARGET = Path("gui/player_research_ui.py")


def find_block(text: str, selector: str) -> tuple[int, int, str]:
    """Return the start/end/source for one CSS rule in the Python f-string."""
    starts = [f"{selector} {{", f"{selector} {{{{"}
    start = -1
    marker = ""
    for candidate in starts:
        idx = text.find(candidate)
        if idx != -1 and (start == -1 or idx < start):
            start = idx
            marker = candidate
    if start == -1:
        raise SystemExit(
            f"ERROR: CSS selector {selector!r} not found. No changes made."
        )

    end_tokens = ["}}", "}"] if marker.endswith("{{") else ["}", "}}"]
    end = -1
    token_used = ""
    for token in end_tokens:
        idx = text.find(token, start + len(marker))
        if idx != -1 and (end == -1 or idx < end):
            end = idx
            token_used = token
    if end == -1:
        raise SystemExit(
            f"ERROR: CSS rule {selector!r} has no closing brace. No changes made."
        )

    end += len(token_used)
    return start, end, text[start:end]


def set_weight_in_block(text: str, selector: str, weight: int) -> str:
    start, end, block = find_block(text, selector)
    needle = "font-weight:820;"
    if needle not in block:
        needle = "font-weight:820;"
    if needle not in block:
        raise SystemExit(
            f"ERROR: expected 820 font weight not found in {selector}. No changes made."
        )
    updated = block.replace(needle, f"font-weight:{weight};", 1)
    return text[:start] + updated + text[end:]


def repair_player_name_rule(text: str) -> str:
    """Restore the name rule in valid Python-f-string CSS syntax."""
    bad_forms = [
        '.frl-name { font-size:.71rem; font-weight:720; }}',
        '.frl-name { font-weight:720; }}',
        '.frl-name { font-size:.71rem; font-weight:720; }',
        '.frl-name {{ font-size:.71rem; font-weight:720; }}',
        '.frl-name {{ font-weight:720; }}',
        '.frl-name { font-weight:780; }',
        '.frl-name {{ font-weight:780; }}',
    ]
    good = '.frl-name {{ font-weight:720; }}'

    for form in bad_forms:
        if form in text:
            return text.replace(form, good, 1)

    raise SystemExit(
        "ERROR: .frl-name rule not found in a recognised form. No changes made."
    )


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

    # Repair the previous malformed f-string CSS first, then restore the approved
    # typography weights. Do not change sizes, grid widths, colours, surface, or sorter.
    new_text = repair_player_name_rule(text)
    new_text = set_weight_in_block(new_text, ".frl-player-header", 800)
    new_text = set_weight_in_block(new_text, ".frl-player-header button", 800)

    # Verify the CSS source is valid Python before writing it.
    candidate = TARGET.with_suffix(".players_tmp.py")
    try:
        candidate.write_text(new_text, encoding="utf-8")
        py_compile.compile(str(candidate), doraise=True)
    except py_compile.PyCompileError as exc:
        raise SystemExit(
            "ERROR: proposed Players patch is not valid Python. No changes made.\n"
            + str(exc)
        )
    finally:
        candidate.unlink(missing_ok=True)

    TARGET.write_text(new_text, encoding="utf-8")

    # Final safety checks.
    final = TARGET.read_text(encoding="utf-8-sig")
    py_compile.compile(str(TARGET), doraise=True)

    checks = {
        "deprecated API absent": "use_container_width" not in final,
        "white FRL surface retained": "background:#fffdf8;" in final,
        "Source Sans retained": 'font-family:"Source Sans", sans-serif;' in final,
        "heading size retained": "font-size:.55rem;" in final,
        "heading weight restored": "font-weight:800;" in find_block(final, ".frl-player-header")[2],
        "sortable heading weight restored": "font-weight:800;" in find_block(final, ".frl-player-header button")[2],
        "player name weight restored": ".frl-name {{ font-weight:720; }}" in final,
        "browser sorting retained": 'data-sort="G"' in final and 'data-sort="xG"' in final,
        "module compiles": True,
    }

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise SystemExit(
            "ERROR: post-write contract check failed: " + ", ".join(failed)
        )

    print("PASS: Players typography restored without changing table size/layout.")
    print("PASS: Instant browser-side sorting remains untouched.")
    print("PASS: White FRL surface and Source Sans declaration remain intact.")
    print("PASS: No deprecated use_container_width API is present.")
    print("PASS: player_research_ui.py compiles cleanly.")
    print("Review the Players page before committing the result.")


if __name__ == "__main__":
    main()
