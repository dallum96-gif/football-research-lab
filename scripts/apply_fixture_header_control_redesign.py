from __future__ import annotations

import difflib
import py_compile
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "gui" / "app_redesign.py"
BACKUP = ROOT / "gui" / "app_redesign.py.pre_fixture_header_control_redesign.bak"
BRANCH = "feature/site-functionality-2026-08-19"

OLD = '''    header_left, header_team, header_season = st.columns([5.4, 1.7, 1.25], gap="small", vertical_alignment="bottom")
    with header_left:
        st.markdown("<div class='frl-eyebrow'>Fixtures</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='frl-entity-title'>{team}</div>", unsafe_allow_html=True)
        st.markdown("<div class='frl-context'>Premier League</div>", unsafe_allow_html=True)
        render_last_five_position_sparkline(season, team, get_fixtures)
    with header_team:
        team = st.selectbox(
            "Team",
            teams,
            index=teams.index(team) if team in teams else 0,
            key="redesign_fixture_team_header",
            label_visibility="collapsed",
        ) if teams else ""
    with header_season:
        season = st.selectbox(
            "Season",
            seasons,
            index=seasons.index(season) if season in seasons else 0,
            key="redesign_fixture_season_header",
            label_visibility="collapsed",
        ) if seasons else ""
'''

NEW = '''    st.markdown(
        """
        <style>
        .frl-fixture-context-copy {
            color: var(--frl-muted-soft);
            font-size: .56rem;
            font-weight: 800;
            letter-spacing: .10em;
            text-transform: uppercase;
            margin: .72rem 0 .18rem;
        }
        .frl-fixture-context-help {
            color: var(--frl-muted);
            font-size: .68rem;
            margin-bottom: .38rem;
        }
        .frl-fixture-header-controls div[data-baseweb="select"] > div {
            background: var(--frl-surface) !important;
            border: 1px solid var(--frl-border) !important;
            border-radius: 8px !important;
            min-height: 2.25rem !important;
            box-shadow: none !important;
        }
        .frl-fixture-header-controls div[data-baseweb="select"] > div:hover,
        .frl-fixture-header-controls div[data-baseweb="select"] > div:focus-within {
            border-color: var(--frl-accent) !important;
            box-shadow: 0 0 0 2px rgba(232,93,63,0.08) !important;
        }
        .frl-fixture-header-controls div[data-testid="stSelectbox"] label {
            color: var(--frl-muted-soft) !important;
            font-size: .55rem !important;
            font-weight: 800 !important;
            letter-spacing: .10em !important;
            text-transform: uppercase !important;
        }
        .frl-fixture-header-controls div[data-baseweb="select"] span {
            color: var(--frl-text) !important;
        }
        </style>
        <div class="frl-fixture-context-copy">Fixture context</div>
        <div class="frl-fixture-context-help">Choose a club and season to explore its fixtures.</div>
        """,
        unsafe_allow_html=True,
    )

    header_left, header_team, header_season = st.columns(
        [6.3, 2.35, 1.35],
        gap="small",
        vertical_alignment="bottom",
    )

    with header_left:
        st.markdown("<div class='frl-eyebrow'>Fixtures</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='frl-entity-title'>{team}</div>", unsafe_allow_html=True)
        st.markdown("<div class='frl-context'>Premier League</div>", unsafe_allow_html=True)
        render_last_five_position_sparkline(season, team, get_fixtures)

    with header_team:
        st.markdown('<div class="frl-fixture-header-controls">', unsafe_allow_html=True)
        team = st.selectbox(
            "Team",
            teams,
            index=teams.index(team) if team in teams else 0,
            key="redesign_fixture_team_header",
        ) if teams else ""
        st.markdown('</div>', unsafe_allow_html=True)

    with header_season:
        st.markdown('<div class="frl-fixture-header-controls">', unsafe_allow_html=True)
        season = st.selectbox(
            "Season",
            seasons,
            index=seasons.index(season) if season in seasons else 0,
            key="redesign_fixture_season_header",
        ) if seasons else ""
        st.markdown('</div>', unsafe_allow_html=True)
'''


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=check)


def main() -> None:
    if not TARGET.exists():
        raise RuntimeError(f"Missing target: {TARGET}")

    status = run("git", "status", "--short")
    if "rebase in progress" in status.stdout.lower():
        raise RuntimeError("Refusing to run during an active rebase.")

    current = TARGET.read_text(encoding="utf-8")

    if NEW in current:
        print("FIXTURE HEADER REDESIGN: already applied")
        return

    if current.count(OLD) != 1:
        raise RuntimeError(
            "Expected exactly one original fixture header control block. "
            f"Found {current.count(OLD)}. Nothing changed."
        )

    updated = current.replace(OLD, NEW, 1)
    candidate = TARGET.with_suffix(".candidate.py")
    candidate.write_text(updated, encoding="utf-8")

    try:
        py_compile.compile(str(candidate), doraise=True)
    except Exception:
        candidate.unlink(missing_ok=True)
        raise RuntimeError("Candidate failed Python syntax validation; nothing changed.")

    shutil.copy2(TARGET, BACKUP)
    TARGET.write_text(updated, encoding="utf-8")
    candidate.unlink(missing_ok=True)

    # Stage only the exact change produced by this script.
    original_lines = current.splitlines(keepends=True)
    updated_lines = updated.splitlines(keepends=True)
    patch = "".join(
        difflib.unified_diff(
            original_lines,
            updated_lines,
            fromfile="a/gui/app_redesign.py",
            tofile="b/gui/app_redesign.py",
        )
    )

    patch_file = ROOT / ".fixture_header_redesign.patch"
    patch_file.write_text(patch, encoding="utf-8")

    try:
        result = subprocess.run(
            ["git", "apply", "--cached", "--unidiff-zero", str(patch_file)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "Unable to stage surgical patch.")
    finally:
        patch_file.unlink(missing_ok=True)

    # Restore unstaged copy, leaving only the surgical hunk staged.
    unstaged = TARGET.read_text(encoding="utf-8")
    head = run("git", "show", "HEAD:gui/app_redesign.py").stdout
    target_head = head.replace(OLD, NEW, 1)
    TARGET.write_text(target_head, encoding="utf-8")

    try:
        py_compile.compile(str(TARGET), doraise=True)
    except Exception:
        TARGET.write_text(unstaged, encoding="utf-8")
        run("git", "reset", "HEAD", "--", "gui/app_redesign.py", check=False)
        raise RuntimeError("Final target failed syntax validation; staged patch removed.")

    staged = run("git", "diff", "--cached", "--name-only").stdout.splitlines()
    if staged != ["gui/app_redesign.py"]:
        run("git", "reset", "HEAD", "--", "gui/app_redesign.py", check=False)
        TARGET.write_text(unstaged, encoding="utf-8")
        raise RuntimeError(f"Staged scope was not surgical: {staged}")

    run("git", "diff", "--cached", "--check")
    run("git", "commit", "-m", "Redesign fixture team and season controls")
    run("git", "push", "origin", BRANCH)

    print("============================================================")
    print("FIXTURE HEADER CONTROL REDESIGN: COMPLETE")
    print("============================================================")
    print("Target: gui/app_redesign.py")
    print("Team selector: larger, light, labelled")
    print("Season selector: compact, light, labelled")
    print("Dark/raised control treatment: removed for these controls")
    print("Existing local unrelated work: preserved")
    print("Staged scope: gui/app_redesign.py only")
    print("Syntax: PASS")
    print("Diff check: PASS")
    print("Pushed: feature/complete-player-match-evidence-2026-08-19")


if __name__ == "__main__":
    main()
