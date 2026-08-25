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
        "players": [
            ("Petr Cech", "GK", "gk"), ("Héctor Bellerín", "RB", "d"), ("Rob Holding", "CB", "d"),
            ("Calum Chambers", "CB", "d"), ("Nacho Monreal", "LB", "d"), ("Mohamed Elneny", "DM", "m"),
            ("Francis Coquelin", "DM", "m"), ("Theo Walcott", "RW", "a"), ("Aaron Ramsey", "AM", "m"),
            ("Alex Iwobi", "LW", "a"), ("Alexis Sánchez", "ST", "a"),
        ],
        "subs": ["David Ospina", "Kieran Gibbs", "Alex Oxlade-Chamberlain", "Granit Xhaka", "Santi Cazorla", "Jack Wilshere", "Chuba Akpom"],
    },
    "Liverpool": {
        "formation": "4–3–3", "manager": "Jürgen Klopp",
        "players": [
            ("Simon Mignolet", "GK", "gk"), ("Nathaniel Clyne", "RB", "d"), ("Dejan Lovren", "CB", "d"),
            ("Ragnar Klavan", "CB", "d"), ("Alberto Moreno", "LB", "d"), ("Jordan Henderson", "CM", "m"),
            ("Georginio Wijnaldum", "CM", "m"), ("Adam Lallana", "CM", "m"), ("Sadio Mané", "RW", "a"),
            ("Roberto Firmino", "CF", "a"), ("Philippe Coutinho", "LW", "a"),
        ],
        "subs": ["Alexander Manninger", "Joël Matip", "Trent Alexander-Arnold", "Marko Grujic", "Emre Can", "Kevin Stewart", "Divock Origi"],
    },
}

TIMELINE = [
    ("26'", "LIV", "card", "Adam Lallana", "Yellow card"),
    ("31'", "ARS", "goal", "Theo Walcott", "Assist: Alex Iwobi · 1–0"),
    ("37'", "ARS", "card", "Francis Coquelin", "Yellow card"),
    ("45+1'", "LIV", "goal", "Philippe Coutinho", "Free-kick · 1–1"),
    ("49'", "LIV", "goal", "Adam Lallana", "Assist: Georginio Wijnaldum · 1–2"),
    ("56'", "LIV", "goal", "Philippe Coutinho", "Assist: Nathaniel Clyne · 1–3"),
    ("57'", "ARS", "card", "Alex Iwobi", "Yellow card"),
    ("59'", "ARS", "sub", "Alex Oxlade-Chamberlain", "On for Alex Iwobi"),
    ("61'", "ARS", "sub", "Santi Cazorla", "On for Aaron Ramsey"),
    ("63'", "LIV", "goal", "Sadio Mané", "Assist: Adam Lallana · 1–4"),
    ("64'", "ARS", "goal", "Alex Oxlade-Chamberlain", "Assist: Santi Cazorla · 2–4"),
    ("70'", "LIV", "sub", "Emre Can", "On for Philippe Coutinho"),
    ("75'", "ARS", "goal", "Calum Chambers", "Assist: Santi Cazorla · 3–4"),
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
    return f"""<svg width='52' height='64' viewBox='0 0 52 64' aria-label='{html.escape(team)} kit'><path d='M17 4 L5 12 L10 24 L17 20 L17 45 Q26 51 35 45 L35 20 L42 24 L47 12 L35 4 L31 8 L21 8 Z' fill='{body}' stroke='rgba(24,23,20,.16)' stroke-width='1.5'/><path d='M17 4 L21 8 L17 16 L10 20 L5 12 Z' fill='{sleeve}'/><path d='M35 4 L31 8 L35 16 L42 20 L47 12 Z' fill='{sleeve}'/><path d='M20 8 Q26 13 32 8' fill='none' stroke='{collar}' stroke-width='3'/><rect x='17' y='45' width='7' height='14' rx='2' fill='{sock}'/><rect x='28' y='45' width='7' height='14' rx='2' fill='{sock}'/></svg>"""


def pitch(team: str) -> str:
    info = LINEUPS[team]
    positions = [(50,89),(12,72),(38,75),(62,75),(88,72),(34,57),(66,57),(15,38),(50,39),(85,38),(50,17)] if team == "Arsenal" else [(50,89),(12,72),(38,75),(62,75),(88,72),(25,54),(50,58),(75,54),(16,32),(50,25),(84,32)]
    tokens = []
    for (name, role, kind), (x, y) in zip(info["players"], positions):
        accent = "#68645c" if kind == "gk" else "#9aaa42" if kind == "m" else "#e85d3f"
        tokens.append(f"<div class='player-token' style='left:{x}%;top:{y}%'><div class='player-shirt' style='--accent:{accent}'><span>{html.escape(role)}</span></div><div class='player-name'>{html.escape(name)}</div></div>")
    return "<div class='pitch-wrap'><div class='pitch'><div class='pitch-mid'></div><div class='pitch-circle'></div><div class='pitch-box top'></div><div class='pitch-box bottom'></div>" + "".join(tokens) + "</div></div>"


def metric_value(side: dict, key: str, fallback=0):
    value = side.get(key)
    return fallback if value in (None, "") else value


def pct(value):
    try:
        return float(value)
    except Exception:
        return 0.0


def pretty_num(value):
    if value in (None, ""):
        return "—"
    try:
        n = float(value)
        return str(int(n)) if n.is_integer() else f"{n:.1f}"
    except Exception:
        return str(value)


def bar_row(label, home, away, suffix=""):
    h, a = pct(home), pct(away)
    total = h + a
    hp = 50 if total <= 0 else (h / total) * 100
    ap = 50 if total <= 0 else (a / total) * 100
    return f"""<div class='viz-row'><div class='viz-label'><span>{html.escape(label)}</span><strong>{pretty_num(home)}{suffix} — {pretty_num(away)}{suffix}</strong></div><div class='bar'><div class='bar-home' style='width:{hp:.1f}%'></div><div class='bar-away' style='width:{ap:.1f}%'></div></div></div>"""


def stat_card(label, value, note="", wide=False):
    cls = "stat-card wide" if wide else "stat-card"
    return f"<div class='{cls}'><div class='stat-label'>{html.escape(label)}</div><div class='stat-value'>{html.escape(str(value))}</div><div class='stat-note'>{html.escape(note)}</div></div>"


st.markdown("""<style>
.proto-kicker{color:var(--frl-accent);font-size:.62rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase;margin-bottom:.45rem}.proto-meta{color:var(--frl-muted);font-size:.74rem}.fixture-head{display:grid;grid-template-columns:1fr 170px 1fr;gap:1.5rem;align-items:center;margin:1rem 0 1.5rem}.fixture-team{text-align:center}.fixture-kit{height:66px;display:flex;justify-content:center;align-items:center}.fixture-team-name{color:var(--frl-text);font-size:1.25rem;font-weight:850}.fixture-team-meta{color:var(--frl-muted-soft);font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;margin-top:.25rem}.fixture-score{text-align:center}.fixture-scoreline{color:var(--frl-text);font-size:4.2rem;font-weight:900;letter-spacing:-.07em;line-height:.9}.fixture-status{color:var(--frl-muted);font-size:.67rem;font-weight:800;text-transform:uppercase;letter-spacing:.12em;margin-top:.5rem}.proto-rule{height:2px;background:var(--frl-text);opacity:.9;margin:1rem 0 1.3rem}.section-kicker{color:var(--frl-accent);font-size:.61rem;font-weight:800;letter-spacing:.15em;text-transform:uppercase;margin-bottom:.55rem}.timeline{border-top:1px solid var(--frl-border)}.event{display:grid;grid-template-columns:50px 28px 1fr 45px;gap:.65rem;align-items:center;padding:.58rem 0;border-bottom:1px solid var(--frl-border)}.event-minute{font-size:.67rem;color:var(--frl-muted-soft);font-weight:800;text-align:right}.event-icon{width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:var(--frl-surface-raised);border:1px solid var(--frl-border);font-size:.65rem}.event-main{font-size:.75rem;color:var(--frl-text);font-weight:800}.event-copy{font-size:.68rem;color:var(--frl-muted)}.event-side{font-size:.62rem;font-weight:900;text-align:right;color:var(--frl-muted)}.pitch-wrap{background:#eef0dd;border:1px solid rgba(24,23,20,.1);border-radius:17px;padding:.8rem}.pitch{position:relative;height:500px;border-radius:12px;overflow:hidden;background:#dfe6c3;border:2px solid rgba(255,255,255,.75)}.pitch-mid{position:absolute;left:0;right:0;top:50%;border-top:2px solid rgba(255,255,255,.72)}.pitch-circle{position:absolute;left:50%;top:50%;width:92px;height:92px;margin:-46px;border:2px solid rgba(255,255,255,.72);border-radius:50%}.pitch-box{position:absolute;left:50%;transform:translateX(-50%);width:190px;height:94px;border:2px solid rgba(255,255,255,.72)}.pitch-box.top{top:0;border-top:0;border-radius:0 0 75px 75px}.pitch-box.bottom{bottom:0;border-bottom:0;border-radius:75px 75px 0 0}.player-token{position:absolute;transform:translate(-50%,-50%);width:84px;text-align:center}.player-shirt{width:28px;height:30px;margin:auto;border-radius:8px;border:1px solid rgba(24,23,20,.15);position:relative;background:#fffdf8;box-shadow:0 3px 9px rgba(24,23,20,.1)}.player-shirt:before,.player-shirt:after{content:'';position:absolute;top:2px;width:9px;height:14px;background:var(--accent);border-radius:3px}.player-shirt:before{left:-6px}.player-shirt:after{right:-6px}.player-shirt span{font-size:.48rem;font-weight:900;color:#37352f;position:absolute;left:0;right:0;top:9px}.player-name{font-size:.55rem;line-height:1.05;font-weight:800;color:#26251f;margin-top:.16rem;text-shadow:0 1px 0 rgba(255,255,255,.45)}.kit-inline{display:flex;align-items:center;gap:.7rem}.kit-copy strong{display:block;color:var(--frl-text);font-size:1.05rem;font-weight:850}.kit-copy span{display:block;color:var(--frl-muted-soft);font-size:.63rem;text-transform:uppercase;letter-spacing:.1em}.stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:.7rem;margin:.8rem 0 1rem}.stat-card{background:var(--frl-surface);border:1px solid var(--frl-border);border-radius:13px;padding:.9rem .95rem;min-height:90px}.stat-card.wide{grid-column:span 2}.stat-label{color:var(--frl-muted-soft);font-size:.59rem;font-weight:800;text-transform:uppercase;letter-spacing:.11em}.stat-value{color:var(--frl-text);font-size:1.65rem;font-weight:900;letter-spacing:-.04em;margin-top:.2rem}.stat-note{color:var(--frl-muted);font-size:.65rem;margin-top:.15rem}.viz-panel{background:var(--frl-surface);border:1px solid var(--frl-border);border-radius:15px;padding:1rem 1.05rem;margin-bottom:.8rem}.viz-head{display:flex;justify-content:space-between;align-items:baseline;gap:1rem;margin-bottom:.7rem}.viz-head strong{font-size:.86rem;color:var(--frl-text)}.viz-head span{font-size:.64rem;color:var(--frl-muted-soft)}.viz-row{margin:.68rem 0 1rem}.viz-label{display:flex;justify-content:space-between;gap:1rem;font-size:.67rem;color:var(--frl-muted)}.viz-label strong{font-weight:800;color:var(--frl-text)}.bar{height:9px;background:#eee9dd;border-radius:999px;overflow:hidden;display:flex;margin-top:.38rem}.bar-home{background:var(--frl-accent);height:100%}.bar-away{background:var(--frl-secondary);height:100%}.mini-legend{display:flex;gap:1rem;font-size:.6rem;color:var(--frl-muted);margin-top:.3rem}.dot-home,.dot-away{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:.3rem}.dot-home{background:var(--frl-accent)}.dot-away{background:var(--frl-secondary)}
</style>""", unsafe_allow_html=True)

try:
    detail = get_fixture(SEASON, FIXTURE_ID)
except Exception as exc:
    st.error(f"Unable to load fixture: {exc}")
    st.stop()

fixture, stats = detail["fixture"], detail["stats"]
home, away = fixture["home_team_name"], fixture["away_team_name"]
home_score = fixture.get("home_score") or "—"
away_score = fixture.get("away_score") or "—"

st.markdown("<div class='proto-kicker'>Fixture · Result</div>", unsafe_allow_html=True)
st.markdown(f"<div class='proto-meta'>{html.escape(fixture['season'])} · Matchweek {html.escape(str(fixture['gameweek']))} · {html.escape(fixture['kickoff_time'][:10])} · Emirates Stadium</div>", unsafe_allow_html=True)
st.markdown(f"<div class='fixture-head'><div class='fixture-team'><div class='fixture-kit'>{kit_svg(home)}</div><div class='fixture-team-name'>{html.escape(home)}</div><div class='fixture-team-meta'>{html.escape(LINEUPS.get(home,{}).get('formation',''))} · {html.escape(LINEUPS.get(home,{}).get('manager',''))}</div></div><div class='fixture-score'><div class='fixture-scoreline'>{home_score}–{away_score}</div><div class='fixture-status'>Full time</div></div><div class='fixture-team'><div class='fixture-kit'>{kit_svg(away)}</div><div class='fixture-team-name'>{html.escape(away)}</div><div class='fixture-team-meta'>{html.escape(LINEUPS.get(away,{}).get('formation',''))} · {html.escape(LINEUPS.get(away,{}).get('manager',''))}</div></div></div>", unsafe_allow_html=True)
st.markdown("<div class='proto-rule'></div>", unsafe_allow_html=True)

left, right = st.columns([1.05, 1.45], gap="large")
with left:
    st.markdown("<div class='section-kicker'>Match story</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:1.1rem;font-weight:800'>A seven-goal classic</div>", unsafe_allow_html=True)
    st.markdown("<div class='timeline'>", unsafe_allow_html=True)
    for minute, side, kind, title, copy in TIMELINE:
        st.markdown(f"<div class='event'><div class='event-minute'>{html.escape(minute)}</div><div class='event-icon'>{'⚽' if kind=='goal' else '▮' if kind=='card' else '↕'}</div><div><div class='event-main'>{html.escape(title)}</div><div class='event-copy'>{html.escape(copy)}</div></div><div class='event-side'>{side}</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
with right:
    st.markdown("<div class='section-kicker'>Starting XI</div>", unsafe_allow_html=True)
    tabs = st.tabs([home, away])
    for tab, team in zip(tabs, [home, away]):
        with tab:
            info = LINEUPS.get(team)
            if not info:
                st.info("Line-up evidence is not available for this fixture.")
            else:
                st.markdown(f"<div class='kit-inline'>{kit_svg(team)}<div class='kit-copy'><strong>{html.escape(team)}</strong><span>{html.escape(info['formation'])} · {html.escape(info['manager'])}</span></div></div>", unsafe_allow_html=True)
                st.markdown(pitch(team), unsafe_allow_html=True)
                with st.expander("Substitutes", expanded=False):
                    st.write(" · ".join(info['subs']))

st.markdown("<div class='proto-rule'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-kicker'>Match analysis</div>", unsafe_allow_html=True)

if stats.get("status") != "AVAILABLE":
    st.info("Historical match statistics are not available for this fixture.")
else:
    hc, ac = stats["home"]["core"], stats["away"]["core"]
    ho, ao = stats["home"].get("optional", {}), stats["away"].get("optional", {})

    st.markdown("<div class='stat-grid'>" +
                stat_card("Scoreline", f"{home_score}–{away_score}", "Liverpool won by one") +
                stat_card("Total goals", f"{int(float(home_score))+int(float(away_score))}", "Three Arsenal · four Liverpool") +
                stat_card("Shots", f"{pretty_num(metric_value(hc,'Shots'))} · {pretty_num(metric_value(ac,'Shots'))}", f"{home} · {away}") +
                stat_card("On target", f"{pretty_num(metric_value(hc,'Shots on target'))} · {pretty_num(metric_value(ac,'Shots on target'))}", f"{home} · {away}") +
                "</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='viz-panel'><div class='viz-head'><strong>Territory & rhythm</strong><span>share of the match total</span></div>{bar_row('Possession', metric_value(hc,'Possession'), metric_value(ac,'Possession'), '%')}{bar_row('Passes', metric_value(hc,'Passes'), metric_value(ac,'Passes'))}{bar_row('Accurate passes', metric_value(hc,'Accurate passes'), metric_value(ac,'Accurate passes'))}<div class='mini-legend'><span><i class='dot-home'></i>{html.escape(home)}</span><span><i class='dot-away'></i>{html.escape(away)}</span></div></div>", unsafe_allow_html=True)

    st.markdown(f"<div class='viz-panel'><div class='viz-head'><strong>Where the game was won</strong><span>action volume</span></div>{bar_row('Corners', metric_value(hc,'Corners'), metric_value(ac,'Corners'))}{bar_row('Tackles', metric_value(hc,'Tackles'), metric_value(ac,'Tackles'))}{bar_row('Interceptions', metric_value(hc,'Interceptions'), metric_value(ac,'Interceptions'))}{bar_row('Clearances', metric_value(hc,'Clearances'), metric_value(ac,'Clearances'))}<div class='mini-legend'><span><i class='dot-home'></i>{html.escape(home)}</span><span><i class='dot-away'></i>{html.escape(away)}</span></div></div>", unsafe_allow_html=True)

    xg_h = ho.get("Expected goals")
    xg_a = ao.get("Expected goals")
    xa_h = ho.get("Expected assists")
    xa_a = ao.get("Expected assists")
    if any(v not in (None, "") for v in [xg_h, xg_a, xa_h, xa_a]):
        xg_hs, xg_as = pretty_num(xg_h), pretty_num(xg_a)
        xa_hs, xa_as = pretty_num(xa_h), pretty_num(xa_a)
        st.markdown(f"<div class='viz-panel'><div class='viz-head'><strong>Chance quality</strong><span>where source evidence exists</span></div><div class='stat-grid'><div class='stat-card'><div class='stat-label'>Expected goals</div><div class='stat-value'>{xg_hs} · {xg_as}</div><div class='stat-note'>{html.escape(home)} · {html.escape(away)}</div></div><div class='stat-card'><div class='stat-label'>Expected assists</div><div class='stat-value'>{xa_hs} · {xa_as}</div><div class='stat-note'>{html.escape(home)} · {html.escape(away)}</div></div></div></div>", unsafe_allow_html=True)

with st.expander("Deeper statistics & provenance", expanded=False):
    st.write({
        "Canonical fixture ID": fixture.get("fixture_id"),
        "Source match ID": stats.get("source_match_id"),
        "Canonical fixture source": detail.get("provenance", {}).get("canonical_source"),
        "Identity source": detail.get("provenance", {}).get("identity_source"),
        "Correction source": detail.get("provenance", {}).get("correction_source"),
    })

st.caption("FRL experiment · standalone prototype · existing Fixtures Explorer is unchanged")
