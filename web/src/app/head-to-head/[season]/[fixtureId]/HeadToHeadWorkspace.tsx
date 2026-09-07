"use client";

import { useState } from "react";
import Link from "next/link";
import { TeamKit } from "@/app/teams/TeamKit";
import { CategoryTabs, EvidenceDrawer, FormStrip, PanelHeading } from "@/components/analyst/AnalystUI";
import type { H2HPack } from "./page";
import styles from "./HeadToHead.module.css";

type Entry = H2HPack["betbuilder"]["entries"][number];
type Rate = Entry["team_recent"];
const percent = (n: number | null | undefined) => n == null ? "—" : `${Math.round(n * 100)}%`;
const number = (n: number | null | undefined) => n == null ? "—" : n.toFixed(1);
const friendly = (s: string) => s.toLowerCase().replaceAll("_", " ");
const group = (e: Entry) => e.id.includes("corners") ? "corners" : e.id.includes("cards") ? "cards" : e.id.includes("shots") || e.id.includes("sot") ? "shots" : "goals";
const categories = ["all", "goals", "shots", "corners", "cards"];

function RateBar({ label, rate, away = false }: { label: string; rate: Rate; away?: boolean }) {
  return <div className={styles.rate} data-away={away}><div><span>{label}</span><strong>{rate.observed_matches ? `${rate.hits}/${rate.observed_matches}` : "Unavailable"}</strong></div><div className={styles.track}><i style={{ width: rate.hit_rate == null ? "0%" : percent(rate.hit_rate) }} /></div><small>{rate.observed_matches}/{rate.eligible_matches} observed · {friendly(rate.coverage_status)}</small></div>;
}

function Badge({ entry }: { entry: Entry }) {
  return <span className={styles.badge} data-tone={entry.evidence_label}>{friendly(entry.evidence_label)}{entry.evidence_label === "STRONG" ? " evidence" : ""}</span>;
}

export default function HeadToHeadWorkspace({ data }: { data: H2HPack }) {
  const ranked = [...data.betbuilder.entries].sort((a,b) => (b.evidence_index ?? -1) - (a.evidence_index ?? -1));
  const [selectedId, setSelectedId] = useState(ranked[0]?.id ?? "");
  const [tab, setTab] = useState("angles");
  const [category, setCategory] = useState("all");
  const [drawer, setDrawer] = useState(false);
  const [playerMetric, setPlayerMetric] = useState("xg");
  const selected = data.betbuilder.entries.find(e => e.id === selectedId);
  const visible = ranked.filter(e => category === "all" || group(e) === category);
  const top = ranked.filter(e => e.evidence_index != null).slice(0, 3);
  const f = data.fixture;
  const p = data.forecast.probabilities ?? {};
  const fixtureHref = `/fixtures/${f.season}/${f.fixture_id}`;
  const chooseCategory = (id: string) => {
    setCategory(id);
    const first = ranked.find(e => id === "all" || group(e) === id);
    if (first) setSelectedId(first.id);
  };
  const date = f.kickoff_time ? new Date(f.kickoff_time).toLocaleString("en-GB", { timeZone: "Europe/London", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }) : "Kickoff TBC";
  return <div className={styles.workspace}>
    <header className={styles.heading}><div><span className={styles.eyebrow}>Matchup intelligence</span><h1>Head-to-Head <span>/ BetBuilder</span></h1></div><nav><Link href={`/matchday/${f.season}/${f.fixture_id}`}>Matchday ↗</Link><button onClick={() => setDrawer(true)}>Evidence desk ↗</button></nav></header>
    <section className={styles.fixture}>
      {(["home", "away"] as const).map(side => <div key={side} className={styles.team} data-side={side}><div className={styles.kit}><TeamKit teamName={data.profiles[side].team_name} /></div><div><small>{side} · {f.season}</small><Link href={`/teams/${f.season}/${data.profiles[side].persistent_team_code}`}>{data.profiles[side].team_name}</Link><FormStrip results={data.profiles[side].form} /></div></div>)}
      <div className={styles.fixtureStamp}><b>VS</b><span>{date}</span><small>Premier League {f.gameweek ? `· GW ${f.gameweek}` : ""}</small></div>
    </section>
    <section className={styles.picks}>
      <div className={styles.pickHeading}><span className={styles.eyebrow}>Start here</span><h2>Best supported<br/> angles</h2><small>Fixed thresholds · recent 5<br/>Descriptive, not probabilities</small></div>
      {top.map(entry => <button className={styles.angleCard} key={entry.id} data-active={selectedId === entry.id && tab === "angles"} onClick={() => { setSelectedId(entry.id); setCategory("all"); setTab("angles"); }}><div><Badge entry={entry}/><span className={styles.arrow}>↗</span></div><strong>{entry.market_label}</strong><div className={styles.cardRates}><span><b>{entry.team_recent.hits}/{entry.team_recent.observed_matches}</b> team</span><span><b>{entry.opponent_allowance.hits}/{entry.opponent_allowance.observed_matches}</b> opponent allows</span></div><small>{Math.min(entry.team_recent.observed_matches, entry.opponent_allowance.observed_matches) < 5 ? "Limited sample · inspect coverage" : "Two-sided recent evidence"}</small></button>)}
      {!top.length && <div className={styles.empty}>No observed matchup angles. Open the evidence desk for coverage.</div>}
    </section>
    <CategoryTabs items={[{id:"angles",label:"BetBuilder evidence"},{id:"profiles",label:"Team matchup"},{id:"players",label:"Player watch"},{id:"forecast",label:"Model picture"}]} value={tab} onChange={setTab}/>
    <section className={styles.bench} aria-label="Interactive evidence workspace">
      {tab === "angles" && <><aside className={styles.rail}><div className={styles.filters}>{categories.map(c => <button key={c} aria-pressed={category===c} onClick={() => chooseCategory(c)}>{c}</button>)}</div><div className={styles.angleList}>{visible.map(entry => <button key={entry.id} className={styles.angleRow} aria-pressed={selectedId === entry.id} onClick={() => setSelectedId(entry.id)}><span>{entry.market_label}<small>{friendly(entry.evidence_label)}</small></span><b>{entry.evidence_index == null ? "—" : Math.round(entry.evidence_index * 100)}<small>index</small></b></button>)}</div></aside>
      {selected ? <article className={styles.detail}><PanelHeading eyebrow="Team tendency × opponent allowance" title={selected.market_label} action={<button className={styles.detailLink} onClick={() => setDrawer(true)}>Inspect evidence ↗</button>}/><div className={styles.comparison}><div><RateBar label={selected.team_name + " · hit frequency"} rate={selected.team_recent}/><RateBar label={selected.opponent_name + " · opponent allowance"} rate={selected.opponent_allowance} away/></div><div className={styles.index}><span>Evidence index</span><strong>{selected.evidence_index == null ? "—" : Math.round(selected.evidence_index*100)}<small>/100</small></strong><Badge entry={selected}/><small>Not a forecast probability</small></div></div><div className={styles.detailFoot}><span>Up to five prior completed fixtures. Each bar retains its own observed population.</span><Link href={fixtureHref}>Open fixture →</Link></div></article> : <div className={styles.empty}>No evidence for this category.</div>}</>}
      {tab === "profiles" && <div className={styles.twoPanels}>{(["home","away"] as const).map(side => <article key={side} className={styles.scrollPanel}><PanelHeading eyebrow="Recent pre-match profile" title={data.profiles[side].team_name} action={<Link href={`/teams/${f.season}/${data.profiles[side].persistent_team_code}`}>Scout ↗</Link>}/><div className={styles.metricGrid}>{data.profiles[side].metrics.map(m => <div key={m.key}><span>{m.label}</span><strong>{number(m.value)}<small>{m.unit}</small></strong><small>{m.observed_matches}/{m.eligible_matches} observed</small></div>)}</div></article>)}</div>}
      {tab === "players" && <div className={styles.playerBench}><CategoryTabs items={Array.from(new Map([...data.players.home.leaderboards,...data.players.away.leaderboards].map(b=>[b.key,{id:b.key,label:b.label}])).values())} value={playerMetric} onChange={setPlayerMetric} label="Player metric"/><div className={styles.twoPanels}>{(["home","away"] as const).map(side => { const board=data.players[side].leaderboards.find(b=>b.key===playerMetric); return <article key={side} className={styles.scrollPanel}><PanelHeading eyebrow="Current-season FPL · prior fixtures" title={data.players[side].team_name}/>{board?.players.map(row=><Link className={styles.player} key={row.player_code} href={`/players/${f.season}/${row.player_code}`}><span className={styles.playerRank}>{row.rank}</span><span><strong>{row.player_name}</strong><small>{row.position} · {row.appearances} apps · {Math.round(row.minutes)} min</small></span><b>{number(row.value)}</b></Link>)}{!board?.players.length && <p className={styles.empty}>No observed player evidence for this metric.</p>}</article>})}</div></div>}
      {tab === "forecast" && <div className={styles.twoPanels}><article className={styles.scrollPanel}><PanelHeading eyebrow="Independent probability layer" title="Frozen experimental forecast"/><div className={styles.marketRows}>{[["home_win",f.home_team_name],["draw","Draw"],["away_win",f.away_team_name],["over_2_5","Over 2.5 goals"],["btts","Both teams to score"]].map(([key,label])=><div key={key}><span>{label}</span><b>{data.forecast.status==="AVAILABLE" ? percent(p[key]) : "Unavailable"}</b></div>)}</div></article><article className={styles.scrollPanel}><PanelHeading eyebrow={data.forecast.model ?? "Model unavailable"} title="Scoreline distribution"/><div className={styles.scoreRows}>{data.forecast.correct_scores?.map(s=><div key={`${s.home}-${s.away}`}><b>{s.home}–{s.away}</b><div className={styles.track}><i style={{width:percent(s.probability)}}/></div><strong>{percent(s.probability)}</strong></div>)}</div><p className={styles.footnote}>Shown scorelines are a subset of the model distribution. Model outputs do not set the evidence index.</p></article></div>}
    </section>
    <footer className={styles.pulse}><span><i/> MODEL PULSE <small>Experimental · separate from stat pack</small></span><b>{data.forecast.status==="AVAILABLE" ? `${f.home_team_name} ${percent(p.home_win)} · Draw ${percent(p.draw)} · ${f.away_team_name} ${percent(p.away_win)}` : "Forecast unavailable"}</b><span>Model λ <strong>{number(data.forecast.expected_goals?.home)}–{number(data.forecast.expected_goals?.away)}</strong></span></footer>
    <EvidenceDrawer open={drawer} onClose={() => setDrawer(false)} title={selected?.market_label ?? "Fixture evidence"}>
      {selected && <><Badge entry={selected}/><p>Up to five completed fixtures before {date}. Frequencies are descriptive; they are not independent betting probabilities.</p><RateBar label="Team recent evidence" rate={selected.team_recent}/><RateBar label="Opponent allowance evidence" rate={selected.opponent_allowance} away/><h3>Index definition</h3><p>{data.betbuilder.index_definition}</p><details><summary>Exact evidence record</summary><pre>{JSON.stringify(selected,null,2)}</pre></details></>}
      <h3>Population & limitations</h3>{data.data_maturity && <p>{data.data_maturity.note}</p>}<ul>{data.limitations.map(l=><li key={l}>{l}</li>)}</ul><p>{data.betbuilder.threshold_policy}</p><Link href={fixtureHref}>Canonical fixture and evidence →</Link>
    </EvidenceDrawer>
  </div>;
}
