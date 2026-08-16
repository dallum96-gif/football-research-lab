from __future__ import annotations

from pathlib import Path
import py_compile
import subprocess
import tempfile

TARGET = Path("gui/player_research_ui.py")
REMOTE_REF = "origin/redesign-github-sync"


def git_show_clean_file() -> str:
    result = subprocess.run(
        ["git", "show", f"{REMOTE_REF}:gui/player_research_ui.py"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout


def patch_typography(text: str) -> str:
    table_start = text.index("def _render_player_table")
    table_end = text.index("def render_player_research_ui")
    prefix = text[:table_start]
    table = text[table_start:table_end]
    suffix = text[table_end:]

    # Restore the approved Players heading weight while keeping its existing size.
    occurrences = table.count("font-weight:820;")
    if occurrences < 2:
        raise RuntimeError(
            f"Expected at least two table heading weight markers, found {occurrences}."
        )
    table = table.replace("font-weight:820;", "font-weight:800;", 2)

    # Restore the lighter player-name treatment. Do not alter size/layout.
    old_name = ".frl-name {{ font-weight:780; }}"
    new_name = ".frl-name {{ font-weight:720; }}"
    if old_name not in table:
        raise RuntimeError("Approved .frl-name baseline was not found in the clean GitHub source.")
    table = table.replace(old_name, new_name, 1)

    return prefix + table + suffix


def validate_python(text: str) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        encoding="utf-8",
        delete=False,
    ) as tmp:
        tmp.write(text)
        temp_path = Path(tmp.name)
    try:
        py_compile.compile(str(temp_path), doraise=True)
    finally:
        temp_path.unlink(missing_ok=True)


def main() -> None:
    clean = git_show_clean_file()
    validate_python(clean)

    patched = patch_typography(clean)
    validate_python(patched)

    TARGET.write_text(patched, encoding="utf-8")
    py_compile.compile(str(TARGET), doraise=True)

    if "use_container_width" in patched:
        raise RuntimeError("Deprecated use_container_width remains in Players UI.")
    if "data-sort=\"G\"" not in patched or "data-sort=\"xG\"" not in patched:
        raise RuntimeError("Sortable Players headers are missing.")
    if "background:#fffdf8;" not in patched:
        raise RuntimeError("Players white surface is missing.")
    if ".frl-name {{ font-weight:720; }}" not in patched:
        raise RuntimeError("Players name typography was not restored.")

    print("PASS: Restored gui/player_research_ui.py from clean GitHub source.")
    print("PASS: Restored approved heading weight without changing heading size.")
    print("PASS: Restored lighter player-name treatment without changing table layout.")
    print("PASS: Browser-side sorting remains intact.")
    print("PASS: White FRL surface remains intact.")
    print("PASS: player_research_ui.py compiles cleanly.")
    print("Now run the app and review Players visually.")


if __name__ == "__main__":
    main()
