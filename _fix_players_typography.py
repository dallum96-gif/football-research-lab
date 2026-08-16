from pathlib import Path
import py_compile

TARGET = Path("gui/player_research_ui.py")


def find_block(text: str, selector: str) -> tuple[int, int, str]:
    """Return one CSS rule block from a Python f-string source file."""
    start = text.find(selector)
    if start == -1:
        raise SystemExit(f"ERROR: CSS selector {selector!r} not found. No changes made.")

    open_pos = text.find("{{", start)
    if open_pos == -1:
        open_pos = text.find("{", start)
    if open_pos == -1:
        raise SystemExit(f"ERROR: opening brace not found for {selector!r}. No changes made.")

    # In an f-string CSS rule blocks use doubled braces: {{ ... }}.
    end = text.find("}}", open_pos + 2)
    if end == -1:
        end = text.find("}", open_pos + 1)
    if end == -1:
        raise SystemExit(f"ERROR: closing brace not found for {selector!r}. No changes made.")

    close_len = 2 if text.startswith("}}", end) else 1
    finish = end + close_len
    return start, finish, text[start:finish]


def set_weight_in_block(text: str, selector: str, weight: int) -> str:
    start, end, block = find_block(text, selector)
    marker = "font-weight:820;"
    if marker not in block:
        raise SystemExit(
            f"ERROR: expected current font-weight:820; not found in {selector}. No changes made."
        )
    updated = block.replace(marker, f"font-weight:{weight};", 1)
    return text[:start] + updated + text[end:]


def repair_player_name_rule(text: str) -> str:
    """Restore the player-name rule in valid Python f-string CSS syntax."""
    # Known malformed forms from the previous patch.
    text = text.replace(
        ".frl-name { font-size:.71rem; font-weight:720; }}",
        ".frl-name {{ font-weight:720; }}",
    )
    text = text.replace(
        ".frl-name { font-size:.71rem; font-weight:720; }",
        ".frl-name {{ font-weight:720; }}",
    )

    start, end, block = find_block(text, ".frl-name")
    if "font-weight:780;" in block:
        block = block.replace("font-weight:780;", "font-weight:720;", 1)
    elif "font-weight:720;" in block:
        pass
    else:
        # Keep existing size and add the approved lighter weight only.
        raise SystemExit("ERROR: .frl-name rule has no recognised font-weight. No changes made.")

    # Preserve valid doubled braces if the rule is within the f-string.
    block = block.replace(".frl-name {", ".frl-name {{", 1)
    if block.endswith("}") and not block.endswith("}}"):
        block = block[:-1] + "}}"
    return text[:start] + block + text[end:]


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
        "background:#fffdf8;",
        'font-family:"Source Sans", sans-serif;',
    ]
    missing = [marker for marker in required if marker not in text]
    if missing:
        raise SystemExit(
            "ERROR: Players UI does not match the expected sortable-table baseline. "
            "No changes made. Missing markers: " + ", ".join(missing)
        )

    if "use_container_width" in text:
        raise SystemExit("ERROR: deprecated use_container_width exists in Players UI. No changes made.")

    new_text = repair_player_name_rule(text)
    new_text = set_weight_in_block(new_text, ".frl-player-header", 800)
    new_text = set_weight_in_block(new_text, ".frl-player-header button", 800)

    # Validate the proposed source before writing over the target.
    temp = TARGET.with_suffix(".players_tmp.py")
    try:
        temp.write_text(new_text, encoding="utf-8")
        py_compile.compile(str(temp), doraise=True)
    except py_compile.PyCompileError as exc:
        raise SystemExit("ERROR: proposed Players patch is not valid Python. No changes made.\n" + str(exc))
    finally:
        temp.unlink(missing_ok=True)

    TARGET.write_text(new_text, encoding="utf-8")
    py_compile.compile(str(TARGET), doraise=True)

    final = TARGET.read_text(encoding="utf-8-sig")
    checks = {
        "deprecated API absent": "use_container_width" not in final,
        "white FRL surface retained": "background:#fffdf8;" in final,
        "Source Sans retained": 'font-family:"Source Sans", sans-serif;' in final,
        "heading size retained": "font-size:.55rem;" in final,
        "heading weight restored": "font-weight:800;" in find_block(final, ".frl-player-header")[2],
        "sortable heading weight restored": "font-weight:800;" in find_block(final, ".frl-player-header button")[2],
        "player name weight restored": "font-weight:720;" in find_block(final, ".frl-name")[2],
        "browser sorting retained": 'data-sort="G"' in final and 'data-sort="xG"' in final,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise SystemExit("ERROR: post-write contract check failed: " + ", ".join(failed))

    print("PASS: Players typography restored without changing table size/layout.")
    print("PASS: Instant browser-side sorting remains untouched.")
    print("PASS: White FRL surface and Source Sans declaration remain intact.")
    print("PASS: No deprecated use_container_width API is present.")
    print("PASS: player_research_ui.py compiles cleanly.")
    print("Review the Players page before committing the result.")


if __name__ == "__main__":
    main()
