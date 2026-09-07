"use client";

import Link from "next/link";
import { useState } from "react";
import { TeamKit } from "@/app/teams/TeamKit";
import { EvidenceDrawer, FormStrip } from "@/components/analyst/AnalystUI";
import { MatchdayFixtureNavigator } from "./MatchdayFixtureNavigator";
import styles from "./MatchdayWorkspace.module.css";

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

type PlayerLeaderboard = {
  key: string;
  label: string;
  unit: string;
  players: Array<{
    rank: number;
    player_code: string;
    player_name: string;
    position: string;
    appearances: number;
    minutes: number;
    value: number;
  }>;
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

function percent(value: number | undefined) {
  return value == null ? "—" : `${(value * 100).toFixed(1)}%`;
}

function decimal(value: number | null | undefined, digits = 2) {
  return value == null || Number.isNaN(value) ? "—" : value.toFixed(digits);
}

function metricValue(metric: Metric) {
  if (metric.value == null) return "—";
  return metric.value.toFixed(Math.abs(metric.value) >= 10 ? 1 : 2);
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

function TeamRecentCard({ side }: { side: TeamSide }) {
  return (
    <section className={styles.teamRecentCard}>
      <div className={styles.cardHeader}>
        <div>
          <span className={styles.kicker}>Last {side.sample_size} · {side.current_season_sample_size} this season</span>
          <h3>{side.team_name}</h3>
        </div>
        <FormStrip results={side.form} />
      </div>
      <div className={styles.recentMatches}>
        {side.matches.slice(0, 3).map((match) => (
          <Link href={`/fixtures/${match.season}/${match.fixture_id}`} className={styles.recentMatch} key={`${match.season}-${match.fixture_id}`}>
            <span data-result={match.result}>{match.result}</span><strong>{match.opponent}</strong><small>{match.venue}</small><b>{match.goals_for}–{match.goals_against}</b>
          </Link>
        ))}
      </div>
      <div className={styles.miniMetricGrid}>
        {side.metrics.slice(0, 4).map((metric) => (
          <div className={styles.miniMetric} key={metric.key}>
            <span>{metric.label}</span>
            <strong>{metricValue(metric)}</strong>
            <small>{metric.observed_matches}/{metric.eligible_matches} observed</small>
          </div>
        ))}
      </div>
    </section>
  );
}

function TeamPanel({ side }: { side: TeamSide }) {
  return (
    <section className={styles.sidePanel}>
      <div className={styles.sidePanelHeader}>
        <div>
          <span className={styles.kicker}>As-of form · {side.current_season_sample_size} current-season matches</span>
          <h2>{side.team_name}</h2>
        </div>
        <div className={styles.pointsBlock}>
          <strong>{side.points}</strong>
          <span>points from {side.sample_size}</span>
        </div>
      </div>
      <FormStrip results={side.form} />
      <div className={styles.teamMetrics}>
        {side.metrics.map((metric) => (
          <article className={styles.metricTile} key={metric.key}>
            <span>{metric.label}</span>
            <strong>{metricValue(metric)}</strong>
            <small>per observed match · {metric.observed_matches}/{metric.eligible_matches}</small>
          </article>
        ))}
      </div>
      <div className={styles.recentMatches}>
        {side.matches.map((match) => (
          <Link href={`/fixtures/${match.season}/${match.fixture_id}`} className={styles.recentMatch} key={`${match.season}-${match.fixture_id}`}>
            <span data-result={match.result}>{match.result}</span>
            <strong>{match.opponent}</strong>
            <small>{match.venue}</small>
            <b>{match.goals_for}–{match.goals_against}</b>
          </Link>
        ))}
      </div>
    </section>
  );
}

function PlayerTile({ leaderboard }: { leaderboard: PlayerLeaderboard }) {
  return (
    <article className={styles.leaderTile}>
      <div className={styles.leaderTileHeader}>
        <span>{leaderboard.label}</span>
        <small>Last 5 apps max</small>
      </div>
      <div className={styles.leaderList}>
        {leaderboard.players.length ? leaderboard.players.map((player) => (
          <div className={styles.leaderRow} key={`${leaderboard.key}-${player.player_code}-${player.rank}`}>
            <span className={styles.rank}>{player.rank}</span>
            <div>
              <strong>{player.player_name}</strong>
              <small>{player.position || "—"} · {player.appearances} apps</small>
            </div>
            <b>{player.value.toFixed(player.value % 1 === 0 ? 0 : 2)}</b>
          </div>
        )) : <div className={styles.emptyTile}>No observed player data yet.</div>}
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
      <div><span>{label}</span><strong>{percent(probability)}</strong></div>
      <div className={styles.marketFair}><span>FRL fair</span><b>{decimal(fairOdds)}</b></div>
      <label>
        <span>Bookmaker</span>
        <input inputMode="decimal" placeholder="e.g. 2.40" value={value} onChange={(event) => onChange(event.target.value)} />
      </label>
      <div className={styles.marketEdge} data-positive={ev != null && ev > 0 ? "true" : "false"}>
        <span>Model EV</span>
        <b>{ev == null ? "—" : `${ev >= 0 ? "+" : ""}${(ev * 100).toFixed(1)}%`}</b>
      </div>
    </article>
  );
}

export function MatchdayWorkspaceV2({ pack, fixtureOptions }: Props) {
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
          <MatchdayFixtureNavigator
            season={data.fixture.season}
            currentFixtureId={data.fixture.fixture_id}
            currentGameweek={data.fixture.gameweek}
            currentHome={data.fixture.home_team_name}
            currentAway={data.fixture.away_team_name}
            fixtures={fixtures}
          />
        </details>
        <Link className={styles.reportLink} href={`/fixtures/${data.fixture.season}/${data.fixture.fixture_id}`}>Match report ↗</Link>
        <button type="button" className={styles.evidenceButton} onClick={() => setEvidenceOpen(true)}>Evidence & sources</button>
      </div>
      <header className={styles.hero}>
        <div className={styles.heroMeta}>
          <span className={styles.kicker}>Premier League · {data.fixture.season}</span>
          <strong>{data.fixture.gameweek ? `Gameweek ${data.fixture.gameweek}` : "Fixture workspace"}</strong>
          <small>{fixtureDate(data.fixture.kickoff_time)} · {fixtureTime(data.fixture.kickoff_time)}</small>
        </div>

        <div className={styles.fixtureHero}>
          <div className={styles.heroTeam}>
            <span className={styles.heroKit}><TeamKit teamName={data.fixture.home_team_name} /></span>
            <strong>{data.fixture.home_team_name}</strong>
          </div>
          <div className={styles.vsBlock}><span>Kickoff</span><b>{fixtureTime(data.fixture.kickoff_time)}</b><small>London time</small></div>
          <div className={`${styles.heroTeam} ${styles.heroTeamAway}`}>
            <span className={styles.heroKit}><TeamKit teamName={data.fixture.away_team_name} /></span>
            <strong>{data.fixture.away_team_name}</strong>
          </div>
        </div>

      </header>

      <section className={styles.modelPulse} aria-label="Current fixture model probabilities">
        <div className={styles.pulseLabel}><span className={styles.kicker}>Model pulse</span><strong>{prediction.model ?? "Model unavailable"}</strong><small>{prediction.status === "AVAILABLE" ? "Experimental forecast" : "No forecast for this fixture"}</small></div>
        <div className={styles.pulseValue}><span>Home win</span><strong>{percent(probabilities.home_win)}</strong><small>fair {decimal(fairOdds.home_win)}</small></div>
        <div className={styles.pulseValue}><span>Draw</span><strong>{percent(probabilities.draw)}</strong><small>fair {decimal(fairOdds.draw)}</small></div>
        <div className={styles.pulseValue}><span>Away win</span><strong>{percent(probabilities.away_win)}</strong><small>fair {decimal(fairOdds.away_win)}</small></div>
        <div className={styles.pulseValue}><span>Expected goals · home / away</span><strong>{decimal(prediction.expected_goals?.home)} <i>/</i> {decimal(prediction.expected_goals?.away)}</strong><small>Model goal rates</small></div>
        <button type="button" className={styles.pulseAction} onClick={() => setTab("Model")}>Model detail ↗</button>
      </section>

      {prediction.status !== "AVAILABLE" && <div className={styles.notice} role="status">{prediction.reason ?? "Prediction unavailable for this fixture."}</div>}

      <nav className={styles.primaryTabs} aria-label="Matchday research sections">
        {PRIMARY_TABS.map((item) => (
          <button type="button" key={item} aria-pressed={tab === item} data-active={tab === item ? "true" : "false"} onClick={() => setTab(item)}>{item === "Markets" ? "Odds notebook" : item === "Model" ? "Model & info" : item === "Overview" ? "Fixture desk" : item}</button>
        ))}
      </nav>

      {data.data_maturity?.status === "EARLY_SEASON" && (
        <div className={styles.notice} role="status">
          <strong>Early-season sample</strong><span>Team matches: {data.data_maturity.team_current_season_matches.home} home / {data.data_maturity.team_current_season_matches.away} away · Player evidence: {data.data_maturity.player_fixture_evidence_matches.home} / {data.data_maturity.player_fixture_evidence_matches.away} fixtures</span><button type="button" onClick={() => setEvidenceOpen(true)}>Sample notes ↗</button>
        </div>
      )}

      <section className={styles.panel} aria-label={`${tab} analysis`}>
        {tab === "Overview" && (
          <div className={styles.overviewGrid}>
            <TeamRecentCard side={data.teams.home} />
            <section className={styles.matchupEntry}>
              <span className={styles.kicker}>The matchup workspace</span>
              <h2>Head-to-Head<br /><em>+ BetBuilder</em></h2>
              <p>Put each team’s recent output alongside what their opponent allows.</p>
              <div className={styles.entryCategories}><span>Goals</span><span>Shots</span><span>Corners</span><span>Cards</span></div>
              <Link className={styles.primaryAction} href={h2hHref}>Open the stat pack <span>→</span></Link>
              <small>Observed hit frequencies · coverage at every threshold</small>
              <div className={styles.goalPictureHeading}>Separate model picture</div>
              <div className={styles.goalGrid}>
                <article><span>Over 2.5</span><strong>{percent(probabilities.over_2_5)}</strong></article>
                <article><span>BTTS</span><strong>{percent(probabilities.btts)}</strong></article>
              </div>
            </section>
            <TeamRecentCard side={data.teams.away} />
            <div className={styles.deskFooter}><span>Recent team metrics are per observed match. Form reads oldest → newest.</span><button type="button" onClick={() => setTab("Teams")}>Compare all team evidence →</button></div>
          </div>
        )}

        {tab === "Teams" && <div className={styles.twoColumn}><TeamPanel side={data.teams.home} /><TeamPanel side={data.teams.away} /></div>}

        {tab === "Players" && (
          <div>
            <div className={styles.subnavRow}>
              <div className={styles.segmented}>
                {(["home", "away"] as const).map((side) => (
                  <button type="button" key={side} data-active={playerSide === side ? "true" : "false"} onClick={() => setPlayerSide(side)}>{data.players[side].team_name}</button>
                ))}
              </div>
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
            <section className={styles.featureCard}>
              <span className={styles.kicker}>Cards watch · V1</span><h2>Player card & tackle context</h2>
              <div className={styles.matchupColumns}>
                {(["home", "away"] as const).map((side) => {
                  const cardBoard = data.players[side].leaderboards.find((item) => item.key === "cards");
                  const tackleBoard = data.players[side].leaderboards.find((item) => item.key === "tackles");
                  return (
                    <div key={side}>
                      <h3>{data.players[side].team_name}</h3><strong>Cards</strong>
                      {(cardBoard?.players ?? []).slice(0, 3).map((player) => <p key={`card-${player.player_code}`}>{player.player_name}<b>{player.value.toFixed(0)}</b></p>)}
                      <strong>Tackles</strong>
                      {(tackleBoard?.players ?? []).slice(0, 3).map((player) => <p key={`tackle-${player.player_code}`}>{player.player_name}<b>{player.value.toFixed(0)}</b></p>)}
                    </div>
                  );
                })}
              </div>
            </section>
            <section className={`${styles.featureCard} ${styles.researchBoundary}`}>
              <span className={styles.kicker}>Availability</span><h2>Matchup coverage</h2><p>{data.matchups.cards.note}</p>
              <div>{data.matchups.cards.withheld.map((item) => <span key={item}>○ {item}</span>)}</div>
              <Link className={styles.reportLink} href={h2hHref}>Open team threshold evidence →</Link>
            </section>
          </div>
        )}

        {tab === "Markets" && (
          <div>
            <div className={styles.sectionHeading}><div><span className={styles.kicker}>Odds notebook</span><h2>Compare your price with the model</h2></div><small>Manual decimal odds · held on this page</small></div>
            <div className={styles.marketGrid}>
              <MarketCard label={data.fixture.home_team_name} probability={probabilities.home_win} fairOdds={fairOdds.home_win} value={odds.home_win ?? ""} onChange={(value) => setOdds((current) => ({ ...current, home_win: value }))} />
              <MarketCard label="Draw" probability={probabilities.draw} fairOdds={fairOdds.draw} value={odds.draw ?? ""} onChange={(value) => setOdds((current) => ({ ...current, draw: value }))} />
              <MarketCard label={data.fixture.away_team_name} probability={probabilities.away_win} fairOdds={fairOdds.away_win} value={odds.away_win ?? ""} onChange={(value) => setOdds((current) => ({ ...current, away_win: value }))} />
              <MarketCard label="Over 2.5" probability={probabilities.over_2_5} fairOdds={fairOdds.over_2_5} value={odds.over_2_5 ?? ""} onChange={(value) => setOdds((current) => ({ ...current, over_2_5: value }))} />
              <MarketCard label="BTTS yes" probability={probabilities.btts} fairOdds={fairOdds.btts} value={odds.btts ?? ""} onChange={(value) => setOdds((current) => ({ ...current, btts: value }))} />
            </div>
            <p className={styles.footnote}>Positive model EV means the entered price is longer than FRL’s fair price. It is a model disagreement to investigate, not a betting instruction.</p>
          </div>
        )}

        {tab === "Model" && (
          <div className={styles.modelGrid}>
            <section className={styles.featureCard}>
              <span className={styles.kicker}>Transparent inputs</span><h2>Why these λ values?</h2>
              <div className={styles.inputGrid}>
                {[
                  ["Home attack", prediction.inputs?.home_strength?.home_attack],
                  ["Home defence", prediction.inputs?.home_strength?.home_defence],
                  ["Away attack", prediction.inputs?.away_strength?.away_attack],
                  ["Away defence", prediction.inputs?.away_strength?.away_defence],
                ].map(([label, value]) => (
                  <article key={String(label)}><span>{label}</span><strong>{typeof value === "number" ? `${value.toFixed(2)}×` : "—"}</strong><small>league rate</small></article>
                ))}
              </div>
              <p className={styles.explainer}>Above 1.00 means more than the relevant league scoring/conceding average; below 1.00 means less. FRL combines the two teams’ strengths with the league home/away scoring environment to create the expected-goal rates.</p>
            </section>
            <section className={styles.featureCard}>
              <span className={styles.kicker}>Correct score</span><h2>Most likely scorelines</h2>
              <div className={styles.scoreGrid}>
                {(prediction.correct_scores ?? []).slice(0, 8).map((score) => <article key={`${score.home}-${score.away}`}><strong>{score.home}–{score.away}</strong><span>{percent(score.probability)}</span><small>fair {decimal(score.fair_odds)}</small></article>)}
              </div>
            </section>
          </div>
        )}
      </section>

      <EvidenceDrawer open={evidenceOpen} onClose={() => setEvidenceOpen(false)} title="Matchday evidence & sources">
        <div className={styles.evidenceContent}>
          <h3>Fixture cutoff</h3><p>{fixtureDate(data.fixture.kickoff_time)} · {fixtureTime(data.fixture.kickoff_time)} London time. Recent-form views use completed fixtures before this kickoff.</p>
          <h3>Sample & coverage</h3>{data.data_maturity && <p>{data.data_maturity.note}</p>}
          <p>Home player sample: {data.players.home.sample_definition}. Away player sample: {data.players.away.sample_definition}.</p>
          <h3>Model</h3><p>{prediction.model ?? "Unavailable"}{prediction.source_season ? ` · source season ${prediction.source_season}` : ""}. {prediction.research_status?.replaceAll("_", " ").toLowerCase()}</p>
          {prediction.reason && <p>{prediction.reason}</p>}
          <h3>Limitations</h3><ul>{[...data.limitations, ...(prediction.limitations ?? [])].map((note, index) => <li key={index}>{note}</li>)}</ul>
          <p>Pack version: {data.pack_version}</p>
        </div>
      </EvidenceDrawer>
    </div>
  );
}
