from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "gui" / "team_research_ui_v7.py"

PATTERN = re.compile(
    r'(?m)^    season = st\.selectbox\("Season", seasons, index=0, key="frl_team7_season", label_visibility="visible"\)\n'
    r'    teams = \[r\.get\("team"\) for r in _league_table\(season\)\.get\("teams", \[\]\) if r\.get\("team"\)\]\n'
    r'    team = st\.selectbox\("Team", teams, index=0, key="frl_team7_team", label_visibility="visible"\)\n'
)

NEW = '''    st.markdown(
        """
        <style>
        .frl-team-context-controls { margin:0 0 0.75rem auto; max-width:620px; }
        .frl-team-context-controls .stSelectbox { margin:0 !important; }
        .frl-team-context-controls label { margin-bottom:0.18rem !important; color:var(--frl-muted-soft) !important; font-size:0.53rem !important; font-weight:800 !important; letter-spacing:0.10em !important; text-transform:uppercase !important; }
        .frl-team-context-controls div[data-baseweb="select"] > div { min-height:1.82rem !important; height:1.82rem !important; border-radius:6px !important; box-shadow:none !important; background:var(--frl-surface) !important; }
        .frl-team-context-controls div[data-baseweb="select"] > div:hover,
        .frl-team-context-controls div[data-baseweb="select"] > div:focus-within { border-color:var(--frl-accent) !important; box-shadow:0 0 0 1px rgba(232,93,63,0.10) !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    control_spacer, control_team, control_season = st.columns([1.8, 2.7, 1.15], gap="small")
    with control_season:
        season = st.selectbox("Season", seasons, index=0, key="frl_team7_season", label_visibility="visible")
    teams = [r.get("team") for r in _league_table(season).get("teams", []) if r.get("team")]
    with control_team:
        current_team = st.session_state.get("frl_team7_team")
        team_index = teams.index(current_team) if current_team in teams else 0
        team = st.selectbox("Team", teams, index=team_index, key="frl_team7_team", label_visibility="visible")
'''

text = TARGET.read_text(encoding="utf-8")
match = PATTERN.search(text)
if not match:
    raise RuntimeError("Expected team/season selector block not found; refusing to patch.")

updated = PATTERN.sub(NEW, text, count=1)
compile(updated, str(TARGET), "exec")
TARGET.write_text(updated, encoding="utf-8")

print("TEAM CONTEXT CONTROLS: restyled")
print("LAYOUT: right-aligned compact strip")
print("TEAM: wider searchable control")
print("SEASON: compact control")
print("SEASON-TEAM ORDER: preserved for historical validity")
print("OTHER TEAM UI: untouched")
print("SYNTAX: team_research_ui_v7.py valid")
