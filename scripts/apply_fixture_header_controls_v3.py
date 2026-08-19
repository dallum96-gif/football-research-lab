from __future__ import annotations

import difflib
import os
import py_compile
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "gui" / "app_redesign.py"
BACKUP = ROOT / "gui" / "app_redesign.py.pre_fixture_header_controls_v3.bak"
BRANCH = "feature/site-functionality-2026-08-19"

HEADER_OLD = '    header_left, header_team, header_season = st.columns([7.2, 1.65, 0.9], gap="small", vertical_alignment="bottom")\n'
HEADER_OLD_BASE = '    header_left, header_team, header_season = st.columns([5.4, 1.7, 1.25], gap="small", vertical_alignment="bottom")\n'
HEADER_END = '        ) if seasons else ""\n'

NEW_HEADER = '''    st.markdown("""
        <style>
        .frl-fixture-context-copy { color:var(--frl-muted-soft); font-size:.56rem; font-weight:800; letter-spacing:.10em; text-transform:uppercase; margin:.72rem 0 .18rem; }
        .frl-fixture-context-help { color:var(--frl-muted); font-size:.68rem; margin-bottom:.38rem; }
        .frl-fixture-header-controls div[data-baseweb="select"] > div { background:var(--frl-surface) !important; border:1px solid var(--frl-border) !important; border-radius:8px !important; min-height:2.25rem !important; box-shadow:none !important; }
        .frl-fixture-header-controls div[data-baseweb="select"] > div:hover, .frl-fixture-header-controls div[data-baseweb="select"] > div:focus-within { border-color:var(--frl-accent) !important; box-shadow:0 0 0 2px rgba(232,93,63,0.08) !important; }
        .frl-fixture-header-controls div[data-testid="stSelectbox"] label { color:var(--frl-muted-soft) !important; font-size:.55rem !important; font-weight:800 !important; letter-spacing:.10em !important; text-transform:uppercase !important; }
        .frl-fixture-header-controls div[data-baseweb="select"] span { color:var(--frl-text) !important; }
        </style>
        <div class="frl-fixture-context-copy">Fixture context</div>
        <div class="frl-fixture-context-help">Choose a club and season to explore its fixtures.</div>
        """, unsafe_allow_html=True)

    header_left, header_team, header_season = st.columns([6.3, 2.35, 1.35], gap="small", vertical_alignment="bottom")

    with header_left:
        st.markdown("<div class='frl-eyebrow'>Fixtures</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='frl-entity-title'>{team}</div>", unsafe_allow_html=True)
        st.markdown("<div class='frl-context'>Premier League</div>", unsafe_allow_html=True)
        render_last_five_position_sparkline(season, team, get_fixtures)

    with header_team:
        st.markdown('<div class="frl-fixture-header-controls">', unsafe_allow_html=True)
        team = st.selectbox("Team", teams, index=teams.index(team) if team in teams else 0, key="redesign_fixture_team_header") if teams else ""
        st.markdown('</div>', unsafe_allow_html=True)

    with header_season:
        st.markdown('<div class="frl-fixture-header-controls">', unsafe_allow_html=True)
        season = st.selectbox("Season", seasons, index=seasons.index(season) if season in seasons else 0, key="redesign_fixture_season_header") if seasons else ""
        st.markdown('</div>', unsafe_allow_html=True)
'''

NAVIGATION_MARKERS = ('target="_blank"', "target='_blank'", "window.open(")


def git(*args: str, index: str | None = None, check: bool = True):
    env = os.environ.copy()
    if index:
        env["GIT_INDEX_FILE"] = index
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, env=env, check=check)


def main() -> None:
    if not TARGET.exists():
        raise RuntimeError(f"Missing target: {TARGET}")

    status = git("git", "status", "--short").stdout.lower()
    if "rebase in progress" in status:
        raise RuntimeError("Refusing to run during an active rebase.")

    staged_target = git("git", "diff", "--cached", "--name-only").stdout.splitlines()
    if "gui/app_redesign.py" in staged_target:
        raise RuntimeError("gui/app_redesign.py already has staged local edits; refusing to mix them.")

    current = TARGET.read_text(encoding="utf-8")
    if "frl-fixture-context-copy" in current:
        print("FIXTURE HEADER CONTROLS V3: already applied")
        return

    marker = HEADER_OLD if HEADER_OLD in current else HEADER_OLD_BASE if HEADER_OLD_BASE in current else None
    if marker is None:
        raise RuntimeError("Known fixture header block not found; nothing changed.")

    start = current.index(marker)
    end = current.find(HEADER_END, start)
    if end < 0:
        raise RuntimeError("Fixture header block end not found; nothing changed.")
    end += len(HEADER_END)

    before_nav = {x: current.count(x) for x in NAVIGATION_MARKERS}
    updated = current[:start] + NEW_HEADER + current[end:]

    updated = updated.replace(
        '    return query_api.team_form(season=season, team=team)\n',
        '    return query_api.team_form(\n        season=season,\n        team=team,\n    )\n',
        1,
    )
    if '        # Current streaks\n        results = [' not in updated:
        updated = updated.replace('        results = [\n', '        # Current streaks\n        results = [\n', 1)

    after_nav = {x: updated.count(x) for x in NAVIGATION_MARKERS}
    if before_nav != after_nav:
        raise RuntimeError("Navigation/new-tab markers changed; refusing to continue.")

    candidate = TARGET.with_suffix('.fixture-header-v3.py')
    candidate.write_text(updated, encoding='utf-8')
    try:
        py_compile.compile(str(candidate), doraise=True)
    finally:
        candidate.unlink(missing_ok=True)

    shutil.copy2(TARGET, BACKUP)
    TARGET.write_text(updated, encoding='utf-8')

    patch = ''.join(difflib.unified_diff(current.splitlines(True), updated.splitlines(True), fromfile='a/gui/app_redesign.py', tofile='b/gui/app_redesign.py'))

    with tempfile.TemporaryDirectory(prefix='frl-index-') as td:
        temp_index = str(Path(td) / 'index')
        original_index = ROOT / '.git' / 'index'
        if original_index.exists():
            shutil.copy2(original_index, temp_index)
        else:
            temp_index = str(Path(td) / 'index-empty')

        patch_file = ROOT / '.fixture_header_v3.patch'
        patch_file.write_text(patch, encoding='utf-8')
        try:
            result = git('git', 'apply', '--cached', '--unidiff-zero', str(patch_file), index=temp_index, check=False)
            if result.returncode:
                raise RuntimeError(result.stderr.strip() or 'Unable to stage surgical patch.')
        finally:
            patch_file.unlink(missing_ok=True)

        staged = git('git', 'diff', '--cached', '--name-only', index=temp_index).stdout.splitlines()
        if staged != ['gui/app_redesign.py']:
            raise RuntimeError(f'Surgical index contained unexpected paths: {staged}')

        git('git', 'diff', '--cached', '--check', index=temp_index)
        diff = git('git', 'diff', '--cached', '--', 'gui/app_redesign.py', index=temp_index).stdout
        if 'frl-fixture-context-copy' not in diff or 'frl-fixture-header-controls' not in diff:
            raise RuntimeError('Surgical index does not contain the intended fixture-control redesign.')

        py_compile.compile(str(TARGET), doraise=True)
        commit = git('git', 'commit', '--only', 'gui/app_redesign.py', '-m', 'Redesign fixture team and season controls', index=temp_index, check=False)
        if commit.returncode:
            raise RuntimeError(commit.stderr.strip() or 'Isolated commit failed.')

        push = git('git', 'push', 'origin', BRANCH, check=False)
        if push.returncode:
            raise RuntimeError(push.stderr.strip() or 'Push failed.')

    print('FIXTURE HEADER CONTROLS V3: COMPLETE')
    print('Team + season controls: light, labelled, compact and interactive')
    print('Dark/raised treatment: removed for these controls')
    print('Navigation/new-tab contract: unchanged')
    print('Target file syntax: PASS')
    print('Isolated commit: PASS')
    print('Existing local staging/index: preserved')
    print('Pushed: feature/site-functionality-2026-08-19')


if __name__ == '__main__':
    main()
