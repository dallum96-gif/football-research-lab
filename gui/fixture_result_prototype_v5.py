from __future__ import annotations

import html
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import query_api
from gui.theme import apply_theme, render_sidebar_controls

st.set_page_config(page_title="FRL — Fixture Result Prototype", page_icon="⚽", layout="wide")
apply_theme()
render_sidebar_controls()

SEASON = st.query_params.get("season", "2016-17")
FIXTURE_ID = st.query_params.get("fixture", "8")

LINEUPS = {
    "Arsenal": {
        "formation": "4–2–3–1", "manager": "Arsène Wenger",
        "players": [("Petr Cech","GK","gk"),("Héctor Bellerín","RB","d"),("Rob Holding","CB","d"),("Calum Chambers","CB","d"),("Nacho Monreal","LB","d"),("Mohamed Elneny","DM","m"),("Francis Coquelin","DM","m"),("Theo Walcott","RW","a"),("Aaron Ramsey","AM","m"),("Alex Iwobi","LW","a"),("Alexis Sánchez","ST","a")],
        "subs": ["David Ospina","Kieran Gibbs","Alex Oxlade-Chamberlain","Granit Xhaka","Santi Cazorla","Jack Wilshere","Chuba Akpom"],
    },
    "Liverpool": {
        "formation": "4–3–3", "manager": "Jürgen Klopp",
        "players": [("Simon Mignolet","GK","gk"),("Nathaniel Clyne","RB","d"),("Dejan Lovren","CB","d"),("Ragnar Klavan","CB","d"),("Alberto Moreno","LB","d"),("Jordan Henderson","CM","m"),("Georginio Wijnaldum","CM","m"),("Adam Lallana","CM","m"),("Sadio Mané","RW","a"),("Roberto Firmino","CF","a"),("Philippe Coutinho","LW","a")],
        "subs": ["Alexander Manninger","Joël Matip","Trent Alexander-Arnold","Marko Grujic","Emre Can","Kevin Stewart","Divock Origi"],
    },
}

TIMELINE = [("26'","LIV","card","Adam Lallana","Yellow card"),("31'","ARS","goal","Theo Walcott","Assist: Alex Iwobi · 1–0"),("37'","ARS","card","Francis Coquelin","Yellow card"),("45+1'","LIV","goal","Philippe Coutinho","Free-kick · 1–1"),("49'","LIV","goal","Adam Lallana","Assist: Georginio Wijnaldum · 1–2"),("56'","LIV","goal","Philippe Coutinho","Assist: Nathaniel Clyne · 1–3"),("57'","ARS","card","Alex Iwobi","Yellow card"),("59'","ARS","sub","Alex Oxlade-Chamberlain","On for Alex Iwobi"),("61'","ARS","sub","Santi Cazorla","On for Aaron Ramsey"),("63'","LIV","goal","Sadio Mané","Assist: Adam Lallana · 1–4"),("64'","ARS","goal","Alex Oxlade-Chamberlain","Assist: Santi Cazorla · 2–4"),("70'","LIV","sub","Emre Can","On for Philippe Coutinho"),("75'","ARS","goal","Calum Chambers","Assist: Santi Cazorla · 3–4"),("76'","LIV","sub","Divock Origi","On for Adam Lallana")]

@st.cache_data
def get_fixture(season: str, fixture_id: str):
    return query_api.fixture_detail(season=season, fixture_id=fixture_id)


def kit_svg(team: str) -> str:
    if team == "Arsenal":
        body, sleeve, collar, sock = "#d71920", "#ffffff", "#ffffff", "#ffffff"
    else:
        body, sleeve, collar, sock = "#d71920", "#f3f3f3", "#f3f3f3", "#d71920"
    return f"""<svg width='48' height='58' viewBox='0 0 52 64' aria-label='{html.escape(team)} kit'><path d='M17 4 L5 12 L10 24 L17 20 L17 45 Q26 51 35 45 L35 20 L42 24 L47 12 L35 4 L31 8 L21 8 Z' fill='{body}' stroke='rgba(24,23,20,.16)' stroke-width='1.5'/><path d='M17 4 L21 8 L17 16 L10 20 L5 12 Z' fill='{sleeve}'/><path d='M35 4 L31 8 L35 16 L42 20 L47 12 Z' fill='{sleeve}'/><path d='M20 8 Q26 13 32 8' fill='none' stroke='{collar}' stroke-width='3'/><rect x='17' y='45' width='7' height='14' rx='2' fill='{sock}'/><rect x='28' y='45' width='7' height='14' rx='2' fill='{sock}'/></svg>"""


def pitch(team: str) -> str:
    info = LINEUPS[team]
    pos = ([(50,89),(88,72),(62,75),(38,75),(12,72),(34,57),(66,57),(85,38),(50,39),(15,38),(50,17)]
           if team == "Arsenal" else
           [(50,89),(88,72),(62,75),(38,75),(12,72),(25,54),(50,58),(75,54),(84,32),(50,25),(16,32)])
    tokens=[]
    for (name, role, kind),(x,y) in zip(info["players"],pos):
        accent = "#68645c" if kind=="gk" else "#9aaa42" if kind=="m" else "#e85d3f"
        tokens.append(f"<div class='player-token' style='left:{x}%;top:{y}%'><div class='player-shirt' style='--accent:{accent}'><span>{html.escape(role)}</span></div><div class='player-name'>{html.escape(name)}</div></div>")
    return "<div class='pitch-wrap'><div class='pitch'><div class='pitch-mid'></div><div class='pitch-circle'></div><div class='pitch-box top'></div><div class='pitch-box bottom'></div>"+"".join(tokens)+"</div></div>"


def num(v):
    try: return float(v)
    except Exception: return None


def pretty(v):
    if v in (None, ""): return "—"
    n=num(v)
    if n is None: return str(v)
    return str(int(n)) if n.is_integer() else f"{n:.1f}"


def ratio_bar(label: str, home_v, away_v, suffix: str = "") -> str:
    h = num(home_v) or 0.0
    a = num(away_v) or 0.0
    total = h + a
    hp = 50.0 if total <= 0 else 100.0 * h / total
    ap = 100.0 - hp
    return f"<div class='viz-row'><div class='viz-label'><span>{html.escape(label)}</span><strong>{pretty(home_v)}{suffix} · {pretty(away_v)}{suffix}</strong></div><div class='bar'><div class='home-bar' style='width:{hp:.1f}%'></div><div class='away-bar' style='width:{ap:.1f}%'></div></div></div>"


def stat_tile(label: str, value: str, note: str = "") -> str:
    return f"<div class='stat-tile'><div class='label'>{html.escape(label)}</div><div class='value'>{html.escape(value)}</div><div class='note'>{html.escape(note)}</div></div>"


st.markdown("""<style>
.fixture-head{display:grid;grid-template-columns:1fr 170px 1fr;gap:1.5rem;align-items:center;margin:1rem auto 1.2rem;max-width:980px}.fixture-team{text-align:center}.fixture-kit{height:58px;display:flex;justify-content:center;align-items:center}.fixture-team-name{color:var(--frl-text);font-size:1.22rem;font-weight:850;letter-spacing:-.03em}.fixture-team-meta{color:var(--frl-muted-soft);font-size:.63rem;text-transform:uppercase;letter-spacing:.1em;margin-top:.2rem}.fixture-score{text-align:center}.fixture-scoreline{color:var(--frl-text);font-size:4rem;font-weight:900;letter-spacing:-.07em;line-height:.9}.fixture-status{color:var(--frl-muted);font-size:.65rem;font-weight:800;text-transform:uppercase;letter-spacing:.12em;margin-top:.45rem}.proto-kicker,.section-kicker{color:var(--frl-accent);font-size:.61rem;font-weight:800;letter-spacing:.15em;text-transform:uppercase}.proto-meta{color:var(--frl-muted);font-size:.73rem}.proto-rule{height:2px;background:var(--frl-text);opacity:.88;margin:1rem auto 1.15rem;max-width:980px}.timeline{border-top:1px solid var(--frl-border)}.event{display:grid;grid-template-columns:46px 30px 1fr 40px;gap:.6rem;align-items:center;padding:.48rem 0;border-bottom:1px solid var(--frl-border)}.event-minute{font-size:.65rem;color:var(--frl-muted-soft);font-weight:800;text-align:right}.event-icon{width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:var(--frl-surface-raised);border:1px solid var(--frl-border);font-size:.62rem}.event-main{font-size:.74rem;color:var(--frl-text);font-weight:800}.event-copy{font-size:.65rem;color:var(--frl-muted)}.event-side{font-size:.59rem;font-weight:900;text-align:right;color:var(--frl-muted)}.goal-event{margin:.42rem 0;padding:.7rem .75rem;border:1px solid rgba(232,93,63,.24);border-radius:12px;background:rgba(232,93,63,.055);display:grid;grid-template-columns:46px 30px 1fr 45px;gap:.6rem;align-items:center}.goal-event .event-icon{width:28px;height:28px;background:rgba(154,170,66,.18);border-color:rgba(154,170,66,.35);font-size:.75rem}.goal-event .event-main{font-size:.82rem}.goal-score{font-size:.72rem;font-weight:900;color:var(--frl-accent);text-align:right}.pitch-wrap{background:#eef0dd;border:1px solid rgba(24,23,20,.1);border-radius:16px;padding:.7rem}.pitch{position:relative;height:480px;border-radius:11px;overflow:hidden;background:#dfe6c3;border:2px solid rgba(255,255,255,.75)}.pitch-mid{position:absolute;left:0;right:0;top:50%;border-top:2px solid rgba(255,255,255,.72)}.pitch-circle{position:absolute;left:50%;top:50%;width:88px;height:88px;margin:-44px;border:2px solid rgba(255,255,255,.72);border-radius:50%}.pitch-box{position:absolute;left:50%;transform:translateX(-50%);width:180px;height:92px;border:2px solid rgba(255,255,255,.72)}.pitch-box.top{top:0;border-top:0;border-radius:0 0 70px 70px}.pitch-box.bottom{bottom:0;border-bottom:0;border-radius:70px 70px 0 0}.player-token{position:absolute;transform:translate(-50%,-50%);width:82px;text-align:center}.player-shirt{width:28px;height:30px;margin:auto;border-radius:8px;border:1px solid rgba(24,23,20,.15);position:relative;background:#fffdf8;box-shadow:0 3px 8px rgba(24,23,20,.08)}.player-shirt:before,.player-shirt:after{content:'';position:absolute;top:2px;width:9px;height:14px;background:var(--accent);border-radius:3px}.player-shirt:before{left:-6px}.player-shirt:after{right:-6px}.player-shirt span{font-size:.46rem;font-weight:900;color:#37352f;position:absolute;left:0;right:0;top:9px}.player-name{font-size:.53rem;line-height:1.03;font-weight:800;color:#26251f;margin-top:.14rem;text-shadow:0 1px 0 rgba(255,255,255,.45)}.kit-inline{display:flex;align-items:center;gap:.65rem}.kit-copy strong{display:block;color:var(--frl-text);font-size:1rem;font-weight:850}.kit-copy span{display:block;color:var(--frl-muted-soft);font-size:.61rem;text-transform:uppercase;letter-spacing:.1em}.analysis-wrap{max-width:980px;margin:0 auto}.stat-tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:.65rem;margin:.8rem 0 1rem}.stat-tile{background:var(--frl-surface);border:1px solid var(--frl-border);border-radius:12px;padding:.8rem .85rem;min-height:82px}.stat-tile .label{color:var(--frl-muted-soft);font-size:.57rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}.stat-tile .value{color:var(--frl-text);font-size:1.45rem;font-weight:900;letter-spacing:-.04em;margin-top:.22rem}.stat-tile .note{color:var(--frl-muted);font-size:.61rem;margin-top:.1rem}.viz-grid{display:grid;grid-template-columns:1fr 1fr;gap:.7rem}.viz-card{background:var(--frl-surface);border:1px solid var(--frl-border);border-radius:13px;padding:.85rem .9rem}.viz-title{color:var(--frl-text);font-size:.76rem;font-weight:850;margin-bottom:.7rem}.viz-row{margin:.6rem 0 .78rem}.viz-label{display:flex;justify-content:space-between;font-size:.62rem;color:var(--frl-muted)}.viz-label strong{color:var(--frl-text);font-weight:800}.bar{display:flex;height:8px;background:#eee9dd;border-radius:99px;overflow:hidden;margin-top:.3rem}.home-bar{background:var(--frl-accent)}.away-bar{background:var(--frl-secondary)}.insight{margin-top:.65rem;padding:.52rem .65rem;border-left:3px solid var(--frl-accent);background:rgba(232,93,63,.05);border-radius:0 8px 8px 0;color:var(--frl-muted);font-size:.65rem;line-height:1.45}
</style>""", unsafe_allow_html=True)

try:
    detail=get_fixture(SEASON,FIXTURE_ID)
except Exception as exc:
    st.error(f"Unable to load fixture: {exc}")
    st.stop()

fixture,stats=detail["fixture"],detail["stats"]
home,away=fixture["home_team_name"],fixture["away_team_name"]
hs,as_=fixture.get("home_score") or "—",fixture.get("away_score") or "—"

st.markdown("<div class='proto-kicker'>Fixture · Result</div>",unsafe_allow_html=True)
st.markdown(f"<div class='proto-meta'>{html.escape(fixture['season'])} · Matchweek {html.escape(str(fixture['gameweek']))} · {html.escape(fixture['kickoff_time'][:10])} · Emirates Stadium</div>",unsafe_allow_html=True)
st.markdown(f"<div class='fixture-head'><div class='fixture-team'><div class='fixture-kit'>{kit_svg(home)}</div><div class='fixture-team-name'>{html.escape(home)}</div><div class='fixture-team-meta'>{html.escape(LINEUPS[home]['formation'])} · {html.escape(LINEUPS[home]['manager'])}</div></div><div class='fixture-score'><div class='fixture-scoreline'>{hs}–{as_}</div><div class='fixture-status'>Full time</div></div><div class='fixture-team'><div class='fixture-kit'>{kit_svg(away)}</div><div class='fixture-team-name'>{html.escape(away)}</div><div class='fixture-team-meta'>{html.escape(LINEUPS[away]['formation'])} · {html.escape(LINEUPS[away]['manager'])}</div></div></div>",unsafe_allow_html=True)
st.markdown("<div class='proto-rule'></div>",unsafe_allow_html=True)

left,right=st.columns([1.0,1.35],gap="large")
with left:
    st.markdown("<div class='section-kicker'>Match story</div>",unsafe_allow_html=True)
    st.markdown("<div style='font-size:1.08rem;font-weight:850;margin:.2rem 0 .7rem'>A seven-goal classic</div>",unsafe_allow_html=True)
    st.markdown("<div class='timeline'>",unsafe_allow_html=True)
    for minute,side,kind,title,copy in TIMELINE:
        icon={'goal':'⚽','card':'▮','sub':'↕'}[kind]
        cls='goal-event' if kind=='goal' else 'event'
        score=copy.split('·')[-1].strip() if kind=='goal' else ''
        st.markdown(f"<div class='{cls}'><div class='event-minute'>{html.escape(minute)}</div><div class='event-icon'>{icon}</div><div><div class='event-main'>{html.escape(title)}</div><div class='event-copy'>{html.escape(copy)}</div></div><div class='goal-score'>{html.escape(score) if score else side}</div></div>",unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)

with right:
    st.markdown("<div class='section-kicker'>Starting XI</div>",unsafe_allow_html=True)
    tabs=st.tabs([home,away])
    for tab,team in zip(tabs,[home,away]):
        with tab:
            info=LINEUPS[team]
            st.markdown(f"<div class='kit-inline'>{kit_svg(team)}<div class='kit-copy'><strong>{html.escape(team)}</strong><span>{html.escape(info['formation'])} · {html.escape(info['manager'])}</span></div></div>",unsafe_allow_html=True)
            st.markdown(pitch(team),unsafe_allow_html=True)
            with st.expander("Substitutes",expanded=False): st.write(" · ".join(info['subs']))

st.markdown("<div class='proto-rule'></div>",unsafe_allow_html=True)
st.markdown("<div class='analysis-wrap'><div class='section-kicker'>Match analysis</div>",unsafe_allow_html=True)

if stats.get('status')=='AVAILABLE':
    hc,ac=stats['home']['core'],stats['away']['core']
    st.markdown("<div class='stat-tiles'>"+stat_tile('Possession',f"{pretty(hc.get('Possession'))}% · {pretty(ac.get('Possession'))}%",f"{home} · {away}")+stat_tile('Shots',f"{pretty(hc.get('Shots'))} · {pretty(ac.get('Shots'))}","total attempts")+stat_tile('On target',f"{pretty(hc.get('Shots on target'))} · {pretty(ac.get('Shots on target'))}","shots on target")+stat_tile('Corners',f"{pretty(hc.get('Corners'))} · {pretty(ac.get('Corners'))}","set-piece pressure")+"</div>",unsafe_allow_html=True)
    st.markdown("<div class='viz-grid'>",unsafe_allow_html=True)
    st.markdown("<div class='viz-card'><div class='viz-title'>Territory & rhythm</div>"+ratio_bar('Possession',hc.get('Possession'),ac.get('Possession'),'%')+ratio_bar('Passes',hc.get('Passes'),ac.get('Passes'))+ratio_bar('Accurate passes',hc.get('Accurate passes'),ac.get('Accurate passes'))+"</div>",unsafe_allow_html=True)
    st.markdown("<div class='viz-card'><div class='viz-title'>Defensive workload</div>"+ratio_bar('Tackles',hc.get('Tackles'),ac.get('Tackles'))+ratio_bar('Interceptions',hc.get('Interceptions'),ac.get('Interceptions'))+ratio_bar('Clearances',hc.get('Clearances'),ac.get('Clearances'))+"</div>",unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)
else:
    st.info('Historical match statistics are not available for this fixture.')

with st.expander('Context & provenance',expanded=False):
    st.write({'Canonical fixture ID':fixture.get('fixture_id'),'Source match ID':stats.get('source_match_id'),'Canonical fixture source':detail.get('provenance',{}).get('canonical_source'),'Identity source':detail.get('provenance',{}).get('identity_source'),'Correction source':detail.get('provenance',{}).get('correction_source')})

st.caption('FRL experiment · standalone prototype · existing Fixtures Explorer is unchanged')
