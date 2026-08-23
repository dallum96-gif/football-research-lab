from __future__ import annotations

import html
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import query_api
from gui.theme import apply_theme, render_sidebar_controls

st.set_page_config(
    page_title="FRL — Fixture Result Prototype",
    page_icon="⚽",
    layout="wide",
)
apply_theme()
render_sidebar_controls()

SEASON = st.query_params.get("season", "2016-17")
FIXTURE_ID = st.query_params.get("fixture", "8")

LINEUPS = {
    "Arsenal": {
        "formation": "4–2–3–1",
        "manager": "Arsène Wenger",
        "players": [
            ("Petr Cech", "GK", "gk"),
            ("Héctor Bellerín", "RB", "d"),
            ("Rob Holding", "CB", "d"),
            ("Calum Chambers", "CB", "d"),
            ("Nacho Monreal", "LB", "d"),
            ("Mohamed Elneny", "DM", "m"),
            ("Francis Coquelin", "DM", "m"),
            ("Theo Walcott", "RW", "a"),
            ("Aaron Ramsey", "AM", "m"),
            ("Alex Iwobi", "LW", "a"),
            ("Alexis Sánchez", "ST", "a"),
        ],
        "subs": [
            "David Ospina", "Kieran Gibbs", "Alex Oxlade-Chamberlain",
            "Granit Xhaka", "Santi Cazorla", "Jack Wilshere", "Chuba Akpom",
        ],
    },
    "Liverpool": {
        "formation": "4–3–3",
        "manager": "Jürgen Klopp",
        "players": [
            ("Simon Mignolet", "GK", "gk"),
            ("Nathaniel Clyne", "RB", "d"),
            ("Dejan Lovren", "CB", "d"),
            ("Ragnar Klavan", "CB", "d"),
            ("Alberto Moreno", "LB", "d"),
            ("Jordan Henderson", "CM", "m"),
            ("Georginio Wijnaldum", "CM", "m"),
            ("Adam Lallana", "CM", "m"),
            ("Sadio Mané", "RW", "a"),
            ("Roberto Firmino", "CF", "a"),
            ("Philippe Coutinho", "LW", "a"),
        ],
        "subs": [
            "Alexander Manninger", "Joël Matip", "Trent Alexander-Arnold",
            "Marko Grujic", "Emre Can", "Kevin Stewart", "Divock Origi",
        ],
    },
}

TIMELINE = [
    ("31'", "ARS", "goal", "Theo Walcott", "Assist: Alex Iwobi · 1–0"),
    ("45+1'", "LIV", "goal", "Philippe Coutinho", "Free-kick · 1–1"),
    ("49'", "LIV", "goal", "Adam Lallana", "Assist: Georginio Wijnaldum · 1–2"),
    ("56'", "LIV", "goal", "Philippe Coutinho", "Assist: Nathaniel Clyne · 1–3"),
    ("63'", "LIV", "goal", "Sadio Mané", "Assist: Adam Lallana · 1–4"),
    ("64'", "ARS", "goal", "Alex Oxlade-Chamberlain", "Assist: Santi Cazorla · 2–4"),
    ("75'", "ARS", "goal", "Calum Chambers", "Assist: Santi Cazorla · 3–4"),
    ("26'", "LIV", "card", "Adam Lallana", "Yellow card"),
    ("37'", "ARS", "card", "Francis Coquelin", "Yellow card"),
    ("57'", "ARS", "card", "Alex Iwobi", "Yellow card"),
    ("59'", "ARS", "sub", "Alex Oxlade-Chamberlain", "On for Alex Iwobi"),
    ("61'", "ARS", "sub", "Santi Cazorla", "On for Aaron Ramsey"),
    ("70'", "LIV", "sub", "Emre Can", "On for Philippe Coutinho"),
    ("76'", "LIV", "sub", "Divock Origi", "On for Adam Lallana"),
]


@st.cache_data
def get_fixture(season: str, fixture_id: str):
    return query_api.fixture_detail(season=season, fixture_id=fixture_id)


def kit_svg(team: str) -> str:
    if team == "Arsenal":
        body, sleeve, collar, sock = "#d71920", "#ffffff", "#ffffff", "#ffffff"
    else:
        body, sleeve, collar, sock = "#d71920", "#f3f3f3", "#f3f3f3", "#d71920"
    return f"""
    <svg width='52' height='64' viewBox='0 0 52 64' aria-label='{html.escape(team)} kit'>
      <path d='M17 4 L5 12 L10 24 L17 20 L17 45 Q26 51 35 45 L35 20 L42 24 L47 12 L35 4 L31 8 L21 8 Z'
            fill='{body}' stroke='rgba(24,23,20,.16)' stroke-width='1.5'/>
      <path d='M17 4 L21 8 L17 16 L10 20 L5 12 Z' fill='{sleeve}' opacity='.95'/>
      <path d='M35 4 L31 8 L35 16 L42 20 L47 12 Z' fill='{sleeve}' opacity='.95'/>
      <path d='M20 8 Q26 13 32 8' fill='none' stroke='{collar}' stroke-width='3'/>
      <rect x='17' y='45' width='7' height='14' rx='2' fill='{sock}' opacity='.95'/>
      <rect x='28' y='45' width='7' height='14' rx='2' fill='{sock}' opacity='.95'/>
    </svg>
    """


def token_markup(name: str, pos: str, role: str, team: str, x: float, y: float) -> str:
    fill = "#ffffff" if role == "gk" else "#fffdf8"
    accent = "#9aaa42" if role == "m" else "#e85d3f" if role == "a" else "#68645c"
    return f"""
    <div class='player-token' style='left:{x}%;top:{y}%'>
      <div class='player-shirt' style='--accent:{accent};background:{fill}'>
        <span>{html.escape(pos)}</span>
      </div>
      <div class='player-name'>{html.escape(name)}</div>
    </div>
    """


def formation_pitch(team: str) -> str:
    data = LINEUPS[team]
    positions = [
        (50, 89),
        (12, 72), (38, 75), (62, 75), (88, 72),
        (34, 57), (66, 57),
        (15, 38), (50, 39), (85, 38),
        (50, 17),
    ] if team == "Arsenal" else [
        (50, 89),
        (12, 72), (38, 75), (62, 75), (88, 72),
        (25, 54), (50, 58), (75, 54),
        (16, 32), (50, 25), (84, 32),
    ]
    tokens = "".join(
        token_markup(name, pos, role, team, *positions[i])
        for i, (name, pos, role) in enumerate(data["players"])
    )
    return f"""
    <div class='pitch-wrap'>
      <div class='pitch'>
        <div class='pitch-mid'></div><div class='pitch-circle'></div>
        <div class='pitch-box top'></div><div class='pitch-box bottom'></div>
        {tokens}
      </div>
    </div>
    """


def timeline_icon(kind: str) -> str:
    return {"goal": "⚽", "card": "▮", "sub": "↕"}.get(kind, "·")


st.markdown(
    """
    <style>
    .proto-kicker{color:var(--frl-accent);font-size:.62rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase;margin-bottom:.45rem}
    .proto-title{color:var(--frl-text);font-size:1.1rem;font-weight:800;line-height:1.1;margin:0}
    .proto-meta{color:var(--frl-muted);font-size:.74rem;line-height:1.45}
    .fixture-head{display:grid;grid-template-columns:1fr 170px 1fr;gap:1.5rem;align-items:center;margin:1rem 0 1.5rem}
    .fixture-team{text-align:center}
    .fixture-kit{height:66px;display:flex;justify-content:center;align-items:center;margin-bottom:.25rem}
    .fixture-team-name{color:var(--frl-text);font-size:1.25rem;font-weight:850;letter-spacing:-.03em}
    .fixture-team-meta{color:var(--frl-muted-soft);font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;margin-top:.25rem}
    .fixture-score{text-align:center}
    .fixture-scoreline{color:var(--frl-text);font-size:4.2rem;font-weight:900;letter-spacing:-.07em;line-height:.9}
    .fixture-status{color:var(--frl-muted);font-size:.67rem;font-weight:800;text-transform:uppercase;letter-spacing:.12em;margin-top:.5rem}
    .proto-rule{height:2px;background:var(--frl-text);opacity:.9;margin:1rem 0 1.3rem}
    .section-kicker{color:var(--frl-accent);font-size:.61rem;font-weight:800;letter-spacing:.15em;text-transform:uppercase;margin-bottom:.55rem}
    .timeline{border-top:1px solid var(--frl-border)}
    .event{display:grid;grid-template-columns:50px 28px 1fr 45px;gap:.65rem;align-items:center;padding:.58rem 0;border-bottom:1px solid var(--frl-border)}
    .event-minute{font-size:.67rem;color:var(--frl-muted-soft);font-weight:800;text-align:right}
    .event-icon{width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:var(--frl-surface-raised);border:1px solid var(--frl-border);font-size:.65rem}
    .event-main{font-size:.75rem;color:var(--frl-text);font-weight:800}.event-copy{font-size:.68rem;color:var(--frl-muted);margin-top:.07rem}
    .event-side{font-size:.62rem;font-weight:900;letter-spacing:.05em;text-align:right;color:var(--frl-muted)}
    .event.goal .event-icon{background:rgba(154,170,66,.16);border-color:rgba(154,170,66,.35)}
    .event.card .event-icon{background:rgba(232,93,63,.10);border-color:rgba(232,93,63,.28)}
    .pitch-wrap{background:#eef0dd;border:1px solid rgba(24,23,20,.1);border-radius:17px;padding:.8rem;box-shadow:0 10px 35px rgba(24,23,20,.05)}
    .pitch{position:relative;height:500px;border-radius:12px;overflow:hidden;background:#dfe6c3;border:2px solid rgba(255,255,255,.75)}
    .pitch-mid{position:absolute;left:0;right:0;top:50%;border-top:2px solid rgba(255,255,255,.72)}
    .pitch-circle{position:absolute;left:50%;top:50%;width:92px;height:92px;margin:-46px;border:2px solid rgba(255,255,255,.72);border-radius:50%}
    .pitch-box{position:absolute;left:50%;transform:translateX(-50%);width:190px;height:94px;border:2px solid rgba(255,255,255,.72)}
    .pitch-box.top{top:0;border-top:0;border-radius:0 0 75px 75px}.pitch-box.bottom{bottom:0;border-bottom:0;border-radius:75px 75px 0 0}
    .player-token{position:absolute;transform:translate(-50%,-50%);width:84px;text-align:center;z-index:2}
    .player-shirt{width:28px;height:30px;margin:auto;border-radius:8px 8px 9px 9px;border:1px solid rgba(24,23,20,.15);position:relative;box-shadow:0 3px 9px rgba(24,23,20,.10)}
    .player-shirt:before,.player-shirt:after{content:'';position:absolute;top:2px;width:9px;height:14px;background:var(--accent);border-radius:3px}.player-shirt:before{left:-6px}.player-shirt:after{right:-6px}
    .player-shirt span{font-size:.48rem;font-weight:900;color:#37352f;position:absolute;left:0;right:0;top:9px}
    .player-name{font-size:.55rem;line-height:1.05;font-weight:800;color:#26251f;margin-top:.16rem;text-shadow:0 1px 0 rgba(255,255,255,.45)}
    .kit-inline{display:flex;align-items:center;gap:.7rem}
    .kit-inline svg{display:block;flex:none}.kit-copy strong{display:block;color:var(--frl-text);font-size:1.05rem;font-weight:850}.kit-copy span{display:block;color:var(--frl-muted-soft);font-size:.63rem;text-transform:uppercase;letter-spacing:.1em;margin-top:.15rem}
    .stat-table{font-size:.73rem}
    </style>
    """,
    unsafe_allow_html=True,
)

try:
    detail = get_fixture(SEASON, FIXTURE_ID)
except Exception as exc:
    st.error(f"Unable to load fixture: {exc}")
    st.stop()

fixture = detail["fixture"]
stats = detail["stats"]

# Header
st.markdown("<div class='proto-kicker'>Fixture · Result</div>", unsafe_allow_html=True)
header_meta = f"{fixture['season']} · Matchweek {fixture['gameweek']} · {fixture['kickoff_time'][:10]}"
st.markdown(f"<div class='proto-meta'>{html.escape(header_meta)} · {html.escape('Emirates Stadium')}</div>", unsafe_allow_html=True)

home = fixture["home_team_name"]
away = fixture["away_team_name"]

st.markdown(
    f"""
    <div class='fixture-head'>
      <div class='fixture-team'>
        <div class='fixture-kit'>{kit_svg(home)}</div>
        <div class='fixture-team-name'>{html.escape(home)}</div>
        <div class='fixture-team-meta'>{html.escape(LINEUPS.get(home, {}).get('formation',''))} · {html.escape(LINEUPS.get(home, {}).get('manager',''))}</div>
      </div>
      <div class='fixture-score'>
        <div class='fixture-scoreline'>{home_score}–{away_score}</div>
        <div class='fixture-status'>Full time</div>
      </div>
      <div class='fixture-team'>
        <div class='fixture-kit'>{kit_svg(away)}</div>
        <div class='fixture-team-name'>{html.escape(away)}</div>
        <div class='fixture-team-meta'>{html.escape(LINEUPS.get(away, {}).get('formation',''))} · {html.escape(LINEUPS.get(away, {}).get('manager',''))}</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='proto-rule'></div>", unsafe_allow_html=True)

left, right = st.columns([1.1, 1.45], gap="large")

with left:
    st.markdown("<div class='section-kicker'>Match story</div>", unsafe_allow_html=True)
    st.markdown("<div class='proto-title'>A seven-goal classic</div>", unsafe_allow_html=True)
    st.caption("A deliberately compact first read of the match. The deeper evidence stays one layer away.")
    st.markdown("<div class='timeline'>", unsafe_allow_html=True)
    for minute, side, kind, title, copy in sorted(TIMELINE, key=lambda x: (x[0].replace("+", "."))):
        st.markdown(
            f"<div class='event {kind}'>"
            f"<div class='event-minute'>{html.escape(minute)}</div>"
            f"<div class='event-icon'>{timeline_icon(kind)}</div>"
            f"<div><div class='event-main'>{html.escape(title)}</div><div class='event-copy'>{html.escape(copy)}</div></div>"
            f"<div class='event-side'>{side}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='section-kicker'>Starting XI</div>", unsafe_allow_html=True)
    tabs = st.tabs([home, away])
    for tab, team in zip(tabs, [home, away]):
        with tab:
            if team not in LINEUPS:
                st.info("Line-up evidence is not available for this fixture.")
            else:
                info = LINEUPS[team]
                st.markdown(
                    f"<div class='kit-inline'>{kit_svg(team)}<div class='kit-copy'><strong>{html.escape(team)}</strong><span>{html.escape(info['formation'])} · {html.escape(info['manager'])}</span></div></div>",
                    unsafe_allow_html=True,
                )
                st.markdown(formation_pitch(team), unsafe_allow_html=True)
                with st.expander("Substitutes", expanded=False):
                    st.write(" · ".join(info["subs"]))

st.markdown("<div class='proto-rule'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-kicker'>Match analysis</div>", unsafe_allow_html=True)

if stats.get("status") == "AVAILABLE":
    home_core = stats["home"]["core"]
    away_core = stats["away"]["core"]
    labels = [
        ("Possession", home_core.get("Possession"), away_core.get("Possession")),
        ("Shots", home_core.get("Shots"), away_core.get("Shots")),
        ("Shots on target", home_core.get("Shots on target"), away_core.get("Shots on target")),
        ("Passes", home_core.get("Passes"), away_core.get("Passes")),
        ("Accurate passes", home_core.get("Accurate passes"), away_core.get("Accurate passes")),
        ("Corners", home_core.get("Corners"), away_core.get("Corners")),
        ("Tackles", home_core.get("Tackles"), away_core.get("Tackles")),
        ("Interceptions", home_core.get("Interceptions"), away_core.get("Interceptions")),
        ("Clearances", home_core.get("Clearances"), away_core.get("Clearances")),
        ("Yellow cards", home_core.get("Yellow cards"), away_core.get("Yellow cards")),
    ]
    df = pd.DataFrame([
        {"": label, home: h if h is not None else "—", away: a if a is not None else "—"}
        for label, h, a in labels
    ])
    st.dataframe(df, width="stretch", hide_index=True)
else:
    st.info("Historical match statistics are not available for this fixture.")

with st.expander("Context & provenance", expanded=False):
    st.write({
        "Canonical fixture ID": fixture.get("fixture_id"),
        "Source match ID": stats.get("source_match_id"),
        "Canonical fixture source": detail.get("provenance", {}).get("canonical_source"),
        "Identity source": detail.get("provenance", {}).get("identity_source"),
        "Correction source": detail.get("provenance", {}).get("correction_source"),
    })

st.caption("FRL experiment · standalone prototype · existing Fixtures Explorer is unchanged")
