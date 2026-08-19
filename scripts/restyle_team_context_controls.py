from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "gui" / "team_research_ui_v7.py"

OLD = '''    season = st.selectbox("Season", seasons, index=0, key="frl_team7_season", label_visibility="visible")\n    teams = [r.get("team") for r in _league_table(season).get("teams", []) if r.get("team")]\n    team = st.selectbox("Team", teams, index=0, key="frl_team7_team", label_visibility="visible")\n'''

NEW = '''    st.markdown(\n        """\n        <style>\n        .frl-team-context-controls {\n            margin: 0 0 0.55rem auto;\n            max-width: 620px;\n        }\n        .frl-team-context-controls [data-testid="stHorizontalBlock"] {\n            align-items: end !important;\n            gap: 0.45rem !important;\n        }\n        .frl-team-context-controls [data-testid="stSelectbox"] label {\n            margin-bottom: 0.20rem !important;\n            color: var(--frl-muted-soft) !important;\n            font-size: 0.55rem !important;\n            font-weight: 800 !important;\n            letter-spacing: 0.10em !important;\n            text-transform: uppercase !important;\n        }\n        .frl-team-context-controls div[data-baseweb="select"] > div {\n            min-height: 1.82rem !important;\n            height: 1.82rem !important;\n            border-radius: 6px !important;\n            box-shadow: none !important;\n            background: var(--frl-surface) !important;\n        }\n        .frl-team-context-controls [data-testid="stSelectbox"] {\n            margin: 0 !important;\n        }\n        </style>\n        <div class="frl-team-context-controls">\n        """,\n        unsafe_allow_html=True,\n    )\n    control_left, control_team, control_season = st.columns([1.7, 2.8, 1.1], gap="small")\n    with control_team:\n        teams = [r.get("team") for r in _league_table(seasons[0]).get("teams", []) if r.get("team")]\n        team = st.selectbox("Team", teams, index=0, key="frl_team7_team", label_visibility="visible")\n    with control_season:\n        season = st.selectbox("Season", seasons, index=0, key="frl_team7_season", label_visibility="visible")\n    st.markdown("</div>", unsafe_allow_html=True)\n\n    # Rebuild the team list after season selection so the selector remains historically valid.\n    teams = [r.get("team") for r in _league_table(season).get("teams", []) if r.get("team")]\n    if team not in teams:\n        team = st.selectbox("Team", teams, index=0, key="frl_team7_team_resolved", label_visibility="collapsed")\n'''

text = TARGET.read_text(encoding="utf-8")
if OLD not in text:
    raise RuntimeError("Expected team/season selector block not found; refusing to patch.")
updated = text.replace(OLD, NEW, 1)
compile(updated, str(TARGET), "exec")
TARGET.write_text(updated, encoding="utf-8")
print("TEAM CONTEXT CONTROLS: restyled")
print("LAYOUT: right-aligned compact strip")
print("TEAM: wider searchable control")
print("SEASON: compact control")
print("OTHER TEAM UI: untouched")
print("SYNTAX: team_research_ui_v7.py valid")
