"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { TeamKit } from "@/app/teams/TeamKit";
import { EvidenceDrawer, FormStrip } from "@/components/analyst/AnalystUI";
import { MatchdayFixtureNavigator } from "./MatchdayFixtureNavigator";
import styles from "./MatchdayWorkspaceV3.module.css";

type Metric = {
  key: string;
  label: string;
  unit: string;
  value: number | null;
  observed_matches: number;
  eligible_matches: number;
};

type RecentMatch = {
  season: string;
  fixture_id: string;
  kickoff_time: string | null;
  opponent: string;
  venue: "Home" | "Away";
  goals_for: number;
  goals_against: number;
  result: "W" | "D" | "L";
};

type TeamSide = {
  team_name: string;
  persistent_team_code: string;
  sample_size: number;
  current_season_sample_size: number;
  form: Array<"W" | "D" | "L">;
  points: number;
  matches: RecentMatch[];
  metrics: Metric[];
};

type LeaderPlayer = {
  rank: number;
  player_code: string;
  player_name: string;
  position: string;
  appearances: number;
  minutes: number;
  value: number;
};

type PlayerLeaderboard = {
  key: string;
  label: string;
  unit: string;
  players: LeaderPlayer[];
};

type PlayerSide = {
  team_name: string;
  sample_definition: string;
  player_count: number;
  fixture_evidence_count: number;
  leaderboards: PlayerLeaderboard[];
};

type Prediction = {
  status: string;
  model?: string;
  research_status?: string;
  source_season?: string;
  limitations?: string[];
  reason?: string;
  expected_goals?: { home: number; away: number };
  probabilities?: Record<string, number>;
  fair_odds?: Record<string, number | null>;
  inputs?: {
    home_strength?: Record<string, number | string | null>;
    away_strength?: Record<string, number | string | null>;
  };
  correct_scores?: Array<{
    home: number;
    away: number;
    probability: number;
    fair_odds: number | null;
  }>;
};

type MatchdayPack = {
  pack_version: string;
  fixture: {
    season: string;
    fixture_id: string;
    gameweek: number | null;
    kickoff_time: string | null;
    home_team_name: string;
    away_team_name: string;
  };
  prediction: Prediction;
  data_maturity?: {
    status: "EARLY_SEASON" | "RECENT_WINDOW_MATURE";
    team_current_season_matches: { home: number; away: number };
    player_fixture_evidence_matches: { home: number; away: number };
    note: string;
  };
  teams: { home: TeamSide; away: TeamSide };
  players: { home: PlayerSide; away: PlayerSide };
  matchups: {
    cards: {
      note: string;
      withheld: string[];
    };
  };
  limitations: string[];
};

type FixtureOption = {
  fixture_id?: string;
  gameweek?: number | null;
  kickoff_time?: string | null;
  home_team_name?: string;
  away_team_name?: string;
  completed?: boolean;
};

type Props = {
  pack: Record<string, unknown>;
  fixtureOptions: Array<Record<string, unknown>>;
};

const PRIMARY_TABS = ["Overview", "Teams", "Players", "Matchups", "Markets", "Model"] as const;
const DEFAULT_PLAYER_METRICS = ["xg", "xa", "cards", "tackles"];
const PLAYER_OVERVIEW_PRIORITY = ["xg", "xa", "shots", "shots_on_target", "tackles", "cards"];

function percent(value: number | undefined) {
  return value == null ? "—" : `${(value * 100).toFixed(1)}%`;
}

function decimal(value: number | null | undefined, digits = 2) {
  return value == null || Number.isNaN(value) ? "—" : value.toFixed(digits);
}

function metricValue(metric: Metric | undefined) {
  if (!metric || metric.value == null) return "—";
  return metric.value.toFixed(Math.abs(metric.value) >= 10 ? 1 : 2);
}

function playerValue(leaderboard: PlayerLeaderboard, player: LeaderPlayer) {
  const value = player.value.toFixed(player.value % 1 === 0 ? 0 : 2);
  return leaderboard.unit ? `${value}${leaderboard.unit === "%" ? "%" : ""}` : value;
}

function fixtureDate(value: string | null | undefined) {
  if (!value) return "Date TBC";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "Date TBC";
  return parsed.toLocaleDateString("en-GB", {
    timeZone: "Europe/London",
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function fixtureTime(value: string | null | undefined) {
  if (!value) return "Time TBC";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "Time TBC";
  return parsed.toLocaleTimeString("en-GB", {
    timeZone: "Europe/London",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function sharedMetrics(home: TeamSide, away: TeamSide) {
  const awayByKey = new Map(away.metrics.map((metric) => [metric.key, metric]));
  return home.metrics
    .map((homeMetric) => ({ home: homeMetric, away: awayByKey.get(homeMetric.key) }))
    .filter((pair): pair is { home: Metric; away: Metric } => Boolean(pair.away))
    .slice(0, 6);
}

function overviewLeaderboards(side: PlayerSide) {
  const populated = side.leaderboards.filter((board) => board.players.length > 0);
  const ordered = [...populated].sort((a, b) => {
    const aIndex = PLAYER_OVERVIEW_PRIORITY.indexOf(a.key);
    const bIndex = PLAYER_OVERVIEW_PRIORITY.indexOf(b.key);
    const aPriority = aIndex === -1 ? 99 : aIndex;
    const bPriority = bIndex === -1 ? 99 : bIndex;
    return aPriority - bPriority;
  });
  return ordered.slice(0, 4);
}

function TeamComparisonRow({ home, away }: { home: Metric; away: Metric }) {
  const maxMagnitude = Math.max(Math.abs(home.value ?? 0), Math.abs(away.value ?? 0), 0.0001);
  const homeWidth = home.value == null ? 0 : Math.min(100, Math.abs(home.value) / maxMagnitude * 100);
  const awayWidth = away.value == null ? 0 : Math.min(100, Math.abs(away.value) / maxMagnitude * 100);

  return (
    <div className={styles.comparisonRow}>
      <div className={styles.metricReadingHome}>
        <strong>{metricValue(home)}</strong>
        <span>{home.observed_matches}/{home.eligible_matches}</span>
      </div>
      <div className={`${styles.metricBar} ${styles.metricBarHome}`} aria-hidden="true">
        <i style={{ width: `${homeWidth}%` }} />
      </div>
      <div className={styles.metricName}>
        <strong>{home.label}</strong>
        <small>{home.unit || "per observed match"}</small>
      </div>
      <div className={`${styles.metricBar} ${styles.metricBarAway}`} aria-hidden="true">
        <i style={{ width: `${awayWidth}%` }} />
      </div>
      <div className={styles.metricReadingAway}>
        <strong>{metricValue(away)}</strong>
        <span>{away.observed_matches}/{away.eligible_matches}</span>
      </div>
    </div>
  );
}

function PlayerSnapshot({ side, tone }: { side: PlayerSide; tone: "home" | "away" }) {
  const boards = overviewLeaderboards(side);
  return (
    <div className={styles.playerSnapshot} data-tone={tone}>
      <div className={styles.playerSnapshotHeader}>
        <div>
          <span>{tone === "home" ? "Home player lens" : "Away player lens"}</span>
          <strong>{side.team_name}</strong>
        </div>
        <small>{side.fixture_evidence_count} fixture evidence</small>
      </div>
      <div className={styles.playerAngleList}>
        {boards.length ? boards.map((board) => {
          const player = board.players[0];
          return (
            <div className={styles.playerAngleRow} key={`${side.team_name}-${board.key}`}>
              <div className={styles.playerAngleMetric}>
                <span>{board.label}</span>
                <b>{playerValue(board, player)}</b>
              </div>
              <div className={styles.playerAngleIdentity}>
                <strong>{player.player_name}</strong>
                <small>{player.position || "—"} · {player.appearances} apps · {player.minutes} mins</small>
              </div>
              <span className={styles.playerAngleRank}>#1</span>
            </div>
          );
        }) : <p className={styles.emptyState}>No observed player leaderboard data yet.</p>}
      </div>
    </div>
  );
}

function TeamPanel({ side }: { side: TeamSide }) {
  return (
    <section className={styles.deepPanel}>
      <div className={styles.deepPanelHeader}>
        <div>
          <span className={styles.kicker}>Team evidence · as of kickoff</span>
          <h2>{side.team_name}</h2>
        </div>
        <div className={styles.pointsBlock}><strong>{side.points}</strong><span>pts from {side.sample_size}</span></div>
      </div>
      <FormStrip results={side.form} />
      <div className={styles.teamMetricGrid}>
        {side.metrics.map((metric) => (
          <article className={styles.metricTile} key={metric.key}>
            <span>{metric.label}</span>
            <strong>{metricValue(metric)}</strong>
            <small>{metric.observed_matches}/{metric.eligible_matches} observed</small>
          </article>
        ))}
      </div>
      <div className={styles.recentMatches}>
        {side.matches.map((match) => (
          <Link href={`/fixtures/${match.season}/${match.fixture_id}`} className={styles.recentMatch} key={`${match.season}-${match.fixture_id}`}>
            <span data-result={match.result}>{match.result}</span><strong>{match.opponent}</strong><small>{match.venue}</small><b>{match.goals_for}–{match.goals_against}</b>
          </Link>
        ))}
      </div>
    </section>
  );
}

function PlayerTile({ leaderboard }: { leaderboard: PlayerLeaderboard }) {
  return (
    <article className={styles.leaderTile}>
      <div className={styles.leaderTileHeader}><span>{leaderboard.label}</span><small>Last 5 apps max</small></div>
      <div className={styles.leaderList}>
        {leaderboard.players.length ? leaderboard.players.map((player) => (
          <div className={styles.leaderRow} key={`${leaderboard.key}-${player.player_code}-${player.rank}`}>
            <span className={styles.rank}>{player.rank}</span>
            <div><strong>{player.player_name}</strong><small>{player.position || "—"} · {player.appearances} apps</small></div>
            <b>{playerValue(leaderboard, player)}</b>
          </div>
        )) : <div className={styles.emptyState}>No observed player data yet.</div>}
      </div>
    </article>
  );
}

function MarketCard({ label, probability, fairOdds, value, onChange }: {
  label: string;
  probability: number | undefined;
  fairOdds: number | null | undefined;
  value: string;
  onChange: (value: string) => void;
}) {
  const entered = Number(value);
  const valid = Number.isFinite(entered) && entered > 1 && probability != null;
  const ev = valid ? probability * entered - 1 : null;
  return (
    <article className={styles.marketCard}>
      <div className={styles.marketHeadline}><span>{label}</span><strong>{percent(probability)}</strong></div>
      <div className={styles.marketFair}><span>FRL fair</span><b>{decimal(fairOdds)}</b></div>
      <label><span>Bookmaker</span><input inputMode="decimal" placeholder="e.g. 2.40" value={value} onChange={(event) => onChange(event.target.value)} /></label>
      <div className={styles.marketEdge} data-positive={ev != null && ev > 0 ? "true" : "false"}><span>Model EV</span><b>{ev == null ? "—" : `${ev >= 0 ? "+" : ""}${(ev * 100).toFixed(1)}%`}</b></div>
    </article>
  );
}

export function MatchdayWorkspaceV3({ pack, fixtureOptions }: Props) {
  const data = pack as unknown as MatchdayPack;
  const fixtures = fixtureOptions as unknown as FixtureOption[];
  const [tab, setTab] = useState<(typeof PRIMARY_TABS)[number]>("Overview");
  const [playerSide, setPlayerSide] = useState<"home" | "away">("home");
  const [playerMetrics, setPlayerMetrics] = useState<string[]>(DEFAULT_PLAYER_METRICS);
  const [odds, setOdds] = useState<Record<string, string>>({});
  const [evidenceOpen, setEvidenceOpen] = useState(false);

  const prediction = data.prediction;
  const probabilities = prediction.probabilities ?? {};
  const fairOdds = prediction.fair_odds ?? {};
  const selectedPlayers = data.players[playerSide];
  const allPlayerMetrics = selectedPlayers.leaderboards;
  const visiblePlayerMetrics = allPlayerMetrics.filter((metric) => playerMetrics.includes(metric.key));
  const h2hHref = `/head-to-head/${encodeURIComponent(data.fixture.season)}/${encodeURIComponent(data.fixture.fixture_id)}`;
  const teamComparisons = useMemo(() => sharedMetrics(data.teams.home, data.teams.away), [data.teams.home, data.teams.away]);

  function togglePlayerMetric(key: string) {
    setPlayerMetrics((current) => {
      if (current.includes(key)) return current.length === 1 ? current : current.filter((item) => item !== key);
      if (current.length >= 4) return current;
      return [...current, key];
    });
  }

  return (
    <div className={styles.workspace}>
      <div className={styles.toolbar}>
        <div className={styles.workspaceTitle}><span className={styles.kicker}>Fixture intelligence</span><h1>Matchday</h1></div>
        <details className={styles.fixtureChooser}>
          <summary>Change fixture <span>⌄</span></summary>
          <MatchdayFixtureNavigator season={data.fixture.season} currentFixtureId={data.fixture.fixture_id} currentGameweek={data.fixture.gameweek} currentHome={data.fixture.home_team_name} currentAway={data.fixture.away_team_name} fixtures={fixtures} />
        </details>
        <Link className={styles.textAction} href={`/fixtures/${data.fixture.season}/${data.fixture.fixture_id}`}>Match report ↗</Link>
        <button type="button" className={styles.evidenceButton} onClick={() => setEvidenceOpen(true)}>Evidence & sources</button>
      </div>

      <header className={styles.hero}>
        <div className={styles.heroMeta}>
          <span className={styles.kicker}>Premier League · {data.fixture.season}</span>
          <strong>{data.fixture.gameweek ? `Gameweek ${data.fixture.gameweek}` : "Fixture workspace"}</strong>
          <small>{fixtureDate(data.fixture.kickoff_time)} · {fixtureTime(data.fixture.kickoff_time)}</small>
        </div>
        <div className={styles.fixtureHero}>
          <div className={styles.heroTeam}><span className={styles.heroKit}><TeamKit teamName={data.fixture.home_team_name} /></span><strong>{data.fixture.home_team_name}</strong></div>
          <div className={styles.vsBlock}><span>Kickoff</span><b>{fixtureTime(data.fixture.kickoff_time)}</b><small>London time</small></div>
          <div className={`${styles.heroTeam} ${styles.heroTeamAway}`}><span className={styles.heroKit}><TeamKit teamName={data.fixture.away_team_name} /></span><strong>{data.fixture.away_team_name}</strong></div>
        </div>
      </header>

      <section className={styles.modelPulse} aria-label="Current fixture model probabilities">
        <div className={styles.pulseLabel}><span className={styles.kicker}>Model pulse</span><strong>{prediction.model ?? "Model unavailable"}</strong><small>{prediction.status === "AVAILABLE" ? "Experimental forecast" : "No forecast for this fixture"}</small></div>
        <div className={styles.pulseValue}><span>Home win</span><strong>{percent(probabilities.home_win)}</strong><small>fair {decimal(fairOdds.home_win)}</small></div>
        <div className={styles.pulseValue}><span>Draw</span><strong>{percent(probabilities.draw)}</strong><small>fair {decimal(fairOdds.draw)}</small></div>
        <div className={styles.pulseValue}><span>Away win</span><strong>{percent(probabilities.away_win)}</strong><small>fair {decimal(fairOdds.away_win)}</small></div>
        <div className={styles.pulseValue}><span>Expected goals</span><strong>{decimal(prediction.expected_goals?.home)} <i>/</i> {decimal(prediction.expected_goals?.away)}</strong><small>home / away</small></div>
        <button type="button" className={styles.pulseAction} onClick={() => setTab("Model")}>Model detail →</button>
      </section>

      {prediction.status !== "AVAILABLE" && <div className={styles.notice} role="status">{prediction.reason ?? "Prediction unavailable for this fixture."}</div>}
      {data.data_maturity?.status === "EARLY_SEASON" && (
        <div className={styles.notice} role="status"><strong>Early-season sample</strong><span>Team matches: {data.data_maturity.team_current_season_matches.home} / {data.data_maturity.team_current_season_matches.away} · Player evidence: {data.data_maturity.player_fixture_evidence_matches.home} / {data.data_maturity.player_fixture_evidence_matches.away}</span><button type="button" onClick={() => setEvidenceOpen(true)}>Sample notes ↗</button></div>
      )}

      <nav className={styles.primaryTabs} aria-label="Matchday research sections">
        {PRIMARY_TABS.map((item) => <button type="button" key={item} aria-pressed={tab === item} data-active={tab === item ? "true" : "false"} onClick={() => setTab(item)}>{item === "Markets" ? "Odds notebook" : item === "Model" ? "Model & info" : item === "Overview" ? "Fixture desk" : item}</button>)}
      </nav>

      <section className={styles.panel} aria-label={`${tab} analysis`}>
        {tab === "Overview" && (
          <div className={styles.overviewStack}>
            <section className={styles.teamLens}>
              <div className={styles.sectionIntro}>
                <div><span className={styles.kicker}>Team matchup</span><h2>What each side brings into the fixture</h2><p>Paired pre-kickoff team metrics. Bar length is relative within each row; it is not a quality score.</p></div>
                <button type="button" className={styles.sectionAction} onClick={() => setTab("Teams")}>All team evidence →</button>
              </div>
              <div className={styles.teamLensHeader}>
                <div className={styles.teamLensIdentity}><span className={styles.miniKit}><TeamKit teamName={data.teams.home.team_name} /></span><div><strong>{data.teams.home.team_name}</strong><small>{data.teams.home.points} pts · last {data.teams.home.sample_size}</small></div><FormStrip results={data.teams.home.form} /></div>
                <span className={styles.compareCaption}>VALUE · COVERAGE</span>
                <div className={`${styles.teamLensIdentity} ${styles.teamLensIdentityAway}`}><span className={styles.miniKit}><TeamKit teamName={data.teams.away.team_name} /></span><div><strong>{data.teams.away.team_name}</strong><small>{data.teams.away.points} pts · last {data.teams.away.sample_size}</small></div><FormStrip results={data.teams.away.form} /></div>
              </div>
              <div className={styles.comparisonRows}>
                {teamComparisons.length ? teamComparisons.map(({ home, away }) => <TeamComparisonRow key={home.key} home={home} away={away} />) : <p className={styles.emptyState}>No directly comparable team metrics are available for this fixture.</p>}
              </div>
            </section>

            <section className={styles.playerLensSection}>
              <div className={styles.sectionIntro}>
                <div><span className={styles.kicker}>Player angles</span><h2>The individual numbers most likely to start an investigation</h2><p>Top observed player in each available leaderboard. These are evidence prompts, not projections.</p></div>
                <button type="button" className={styles.sectionAction} onClick={() => setTab("Players")}>Open player boards →</button>
              </div>
              <div className={styles.playerLensGrid}><PlayerSnapshot side={data.players.home} tone="home" /><PlayerSnapshot side={data.players.away} tone="away" /></div>
            </section>

            <section className={styles.investigationRail} aria-label="Deeper investigation routes">
              <button type="button" onClick={() => setTab("Teams")}><span>01</span><div><strong>Team evidence</strong><small>All metrics, form and observed coverage</small></div><b>→</b></button>
              <button type="button" onClick={() => setTab("Players")}><span>02</span><div><strong>Player boards</strong><small>Choose four leaderboards and compare leaders</small></div><b>→</b></button>
              <Link href={h2hHref}><span>03</span><div><strong>H2H stat pack</strong><small>Opponent allowance and threshold evidence</small></div><b>→</b></Link>
              <button type="button" onClick={() => setTab("Markets")}><span>04</span><div><strong>Market notebook</strong><small>Compare price with FRL fair probability</small></div><b>→</b></button>
            </section>
          </div>
        )}

        {tab === "Teams" && <div className={styles.twoColumn}><TeamPanel side={data.teams.home} /><TeamPanel side={data.teams.away} /></div>}

        {tab === "Players" && (
          <div>
            <div className={styles.subnavRow}>
              <div className={styles.segmented}>{(["home", "away"] as const).map((side) => <button type="button" key={side} data-active={playerSide === side ? "true" : "false"} onClick={() => setPlayerSide(side)}>{data.players[side].team_name}</button>)}</div>
              <div className={styles.metricToggles} aria-label="Choose up to four player metrics">
                {allPlayerMetrics.map((metric) => {
                  const active = playerMetrics.includes(metric.key);
                  const disabled = !active && playerMetrics.length >= 4;
                  return <button type="button" key={metric.key} data-active={active ? "true" : "false"} disabled={disabled} onClick={() => togglePlayerMetric(metric.key)}>{metric.label}</button>;
                })}
              </div>
            </div>
            <div className={styles.playerTileGrid}>{visiblePlayerMetrics.map((leaderboard) => <PlayerTile key={leaderboard.key} leaderboard={leaderboard} />)}</div>
            <p className={styles.footnote}>{selectedPlayers.sample_definition}. Current-season fixture evidence: {selectedPlayers.fixture_evidence_count}. Four metrics can be active at once.</p>
          </div>
        )}

        {tab === "Matchups" && (
          <div className={styles.matchupGrid}>
            <section className={styles.deepPanel}>
              <span className={styles.kicker}>Cards watch · V1</span><h2>Player card & tackle context</h2>
              <div className={styles.matchupColumns}>
                {(["home", "away"] as const).map((side) => {
                  const cardBoard = data.players[side].leaderboards.find((item) => item.key === "cards");
                  const tackleBoard = data.players[side].leaderboards.find((item) => item.key === "tackles");
                  return <div key={side}><h3>{data.players[side].team_name}</h3><strong>Cards</strong>{(cardBoard?.players ?? []).slice(0, 3).map((player) => <p key={`card-${player.player_code}`}>{player.player_name}<b>{player.value.toFixed(0)}</b></p>)}<strong>Tackles</strong>{(tackleBoard?.players ?? []).slice(0, 3).map((player) => <p key={`tackle-${player.player_code}`}>{player.player_name}<b>{player.value.toFixed(0)}</b></p>)}</div>;
                })}
              </div>
            </section>
            <section className={`${styles.deepPanel} ${styles.researchBoundary}`}><span className={styles.kicker}>Availability</span><h2>Matchup coverage</h2><p>{data.matchups.cards.note}</p><div>{data.matchups.cards.withheld.map((item) => <span key={item}>○ {item}</span>)}</div><Link className={styles.textAction} href={h2hHref}>Open team threshold evidence →</Link></section>
          </div>
        )}

        {tab === "Markets" && (
          <div>
            <div className={styles.sectionIntro}><div><span className={styles.kicker}>Odds notebook</span><h2>Compare your price with the model</h2><p>Manual decimal odds held on this page. Positive EV is a disagreement to investigate, not a betting instruction.</p></div></div>
            <div className={styles.marketGrid}>
              <MarketCard label={data.fixture.home_team_name} probability={probabilities.home_win} fairOdds={fairOdds.home_win} value={odds.home_win ?? ""} onChange={(value) => setOdds((current) => ({ ...current, home_win: value }))} />
              <MarketCard label="Draw" probability={probabilities.draw} fairOdds={fairOdds.draw} value={odds.draw ?? ""} onChange={(value) => setOdds((current) => ({ ...current, draw: value }))} />
              <MarketCard label={data.fixture.away_team_name} probability={probabilities.away_win} fairOdds={fairOdds.away_win} value={odds.away_win ?? ""} onChange={(value) => setOdds((current) => ({ ...current, away_win: value }))} />
              <MarketCard label="Over 2.5" probability={probabilities.over_2_5} fairOdds={fairOdds.over_2_5} value={odds.over_2_5 ?? ""} onChange={(value) => setOdds((current) => ({ ...current, over_2_5: value }))} />
              <MarketCard label="BTTS yes" probability={probabilities.btts} fairOdds={fairOdds.btts} value={odds.btts ?? ""} onChange={(value) => setOdds((current) => ({ ...current, btts: value }))} />
            </div>
          </div>
        )}

        {tab === "Model" && (
          <div className={styles.modelGrid}>
            <section className={styles.deepPanel}><span className={styles.kicker}>Transparent inputs</span><h2>Why these λ values?</h2><div className={styles.inputGrid}>{[["Home attack", prediction.inputs?.home_strength?.home_attack],["Home defence", prediction.inputs?.home_strength?.home_defence],["Away attack", prediction.inputs?.away_strength?.away_attack],["Away defence", prediction.inputs?.away_strength?.away_defence]].map(([label, value]) => <article key={String(label)}><span>{label}</span><strong>{typeof value === "number" ? `${value.toFixed(2)}×` : "—"}</strong><small>league rate</small></article>)}</div><p className={styles.footnote}>Above 1.00 means more than the relevant league scoring/conceding average; below 1.00 means less.</p></section>
            <section className={styles.deepPanel}><span className={styles.kicker}>Correct score</span><h2>Most likely scorelines</h2><div className={styles.scoreGrid}>{(prediction.correct_scores ?? []).slice(0, 8).map((score) => <article key={`${score.home}-${score.away}`}><strong>{score.home}–{score.away}</strong><span>{percent(score.probability)}</span><small>fair {decimal(score.fair_odds)}</small></article>)}</div></section>
          </div>
        )}
      </section>

      <EvidenceDrawer open={evidenceOpen} onClose={() => setEvidenceOpen(false)} title="Matchday evidence & sources">
        <div className={styles.evidenceContent}>
          <h3>Fixture cutoff</h3><p>{fixtureDate(data.fixture.kickoff_time)} · {fixtureTime(data.fixture.kickoff_time)} London time. Recent-form views use completed fixtures before this kickoff.</p>
          <h3>Sample & coverage</h3>{data.data_maturity && <p>{data.data_maturity.note}</p>}<p>Home player sample: {data.players.home.sample_definition}. Away player sample: {data.players.away.sample_definition}.</p>
          <h3>Model</h3><p>{prediction.model ?? "Unavailable"}{prediction.source_season ? ` · source season ${prediction.source_season}` : ""}. {prediction.research_status?.replaceAll("_", " ").toLowerCase()}</p>{prediction.reason && <p>{prediction.reason}</p>}
          <h3>Limitations</h3><ul>{[...data.limitations, ...(prediction.limitations ?? [])].map((note, index) => <li key={index}>{note}</li>)}</ul><p>Pack version: {data.pack_version}</p>
        </div>
      </EvidenceDrawer>
    </div>
  );
}
