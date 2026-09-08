"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { TeamKit } from "@/app/teams/TeamKit";
import { EvidenceDrawer, FormStrip } from "@/components/analyst/AnalystUI";
import { MatchdayFixtureNavigator } from "./MatchdayFixtureNavigator";
import styles from "./MatchdayDeskV6.module.css";

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
  sample_size: number;
  current_season_sample_size: number;
  form: Array<"W" | "D" | "L">;
  matches: RecentMatch[];
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
  fixture_evidence_count: number;
  leaderboards: PlayerLeaderboard[];
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
  data_maturity?: {
    status: "EARLY_SEASON" | "RECENT_WINDOW_MATURE";
    note: string;
  };
  teams: { home: TeamSide; away: TeamSide };
  players: { home: PlayerSide; away: PlayerSide };
  limitations: string[];
};

type ThresholdObservation = {
  season: string;
  fixture_id: string;
  kickoff_time: string | null;
  opponent: string;
  venue: "Home" | "Away" | null;
  value: number;
  hit: boolean;
};

type ThresholdSummary = {
  hits: number;
  observed_matches: number;
  eligible_matches: number;
  hit_rate: number | null;
  average: number | null;
  coverage_status: "COMPLETE" | "PARTIAL" | "UNAVAILABLE";
  sequence_order: "MOST_RECENT_FIRST";
  observations: ThresholdObservation[];
};

type MarketLaneSide = {
  team_name: string;
  opponent_name: string;
  attack: ThresholdSummary;
  defence_allowance: ThresholdSummary;
  evidence_label: "STRONG" | "FAVOURABLE" | "MIXED" | "WEAK" | "UNAVAILABLE";
  evidence_index: number | null;
};

type MarketLane = {
  key: string;
  family: string;
  market_line: {
    label: string;
    threshold: number;
    unit: string;
    source_key: string;
  };
  home_lane: MarketLaneSide;
  away_lane: MarketLaneSide;
};

type Forecast = {
  status: string;
  model?: string;
  control_status?: string;
  reason?: string;
  probabilities?: Record<string, number>;
  expected_goals?: { home: number; away: number };
};

type HeadToHeadPack = {
  pack_version: string;
  market_lanes: MarketLane[];
  forecast: Forecast;
  limitations: string[];
  betbuilder?: {
    threshold_policy?: string;
    index_definition?: string;
  };
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
  marketPack: Record<string, unknown> | null;
  fixtureOptions: Array<Record<string, unknown>>;
};

const QUESTION_ORDER = ["Goals", "Corners", "Shots", "SOT", "Fouls", "Cards", "Players"] as const;
const PLAYER_BOARD_KEYS = ["goals", "xg", "cards", "tackles"];

function fixtureDate(value: string | null | undefined) {
  if (!value) return "Date TBC";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "Date TBC";
  return parsed.toLocaleDateString("en-GB", {
    timeZone: "Europe/London",
    weekday: "short",
    day: "numeric",
    month: "short",
  });
}

function fixtureTime(value: string | null | undefined) {
  if (!value) return "TBC";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "TBC";
  return parsed.toLocaleTimeString("en-GB", {
    timeZone: "Europe/London",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function number(value: number | null | undefined, digits = 1) {
  if (value == null || Number.isNaN(value)) return "—";
  if (Math.abs(value - Math.round(value)) < 1e-9) return Math.round(value).toLocaleString("en-GB");
  return value.toFixed(digits);
}

function percent(value: number | null | undefined) {
  return value == null || Number.isNaN(value) ? "—" : `${Math.round(value * 100)}%`;
}

function latestLabel(value: string | null) {
  if (!value) return "fixture";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "fixture";
  return parsed.toLocaleDateString("en-GB", { timeZone: "Europe/London", day: "numeric", month: "short" });
}

function EvidenceStrip({ summary, label }: { summary: ThresholdSummary; label: string }) {
  return (
    <div className={styles.evidenceStrip} aria-label={`${label}: ${summary.hits} hits from ${summary.observed_matches} observed matches`}>
      {summary.observations.map((observation) => (
        <span
          key={`${observation.season}-${observation.fixture_id}`}
          className={styles.evidenceCell}
          data-hit={observation.hit ? "true" : "false"}
          title={`${latestLabel(observation.kickoff_time)} · ${observation.opponent} · ${number(observation.value)}`}
        >
          <b>{number(observation.value)}</b>
          <small>{observation.opponent.slice(0, 3).toUpperCase()}</small>
        </span>
      ))}
      {!summary.observations.length && <span className={styles.noSequence}>No observed values</span>}
    </div>
  );
}

function EvidenceHalf({
  teamName,
  summary,
  kind,
  align,
}: {
  teamName: string;
  summary: ThresholdSummary;
  kind: "attack" | "defence";
  align: "left" | "right";
}) {
  const description = kind === "attack" ? "cleared the line" : "opponents cleared";
  return (
    <div className={styles.evidenceHalf} data-align={align}>
      <div className={styles.evidenceHalfTop}>
        <div>
          <span>{kind === "attack" ? "ATTACK OUTPUT" : "DEFENCE ALLOWANCE"}</span>
          <strong>{teamName}</strong>
        </div>
        <div className={styles.hitCount}>
          <strong>{summary.hits}/{summary.observed_matches || "—"}</strong>
          <span>{description}</span>
        </div>
      </div>
      <EvidenceStrip summary={summary} label={`${teamName} ${description}`} />
      <div className={styles.evidenceMeta}>
        <span>avg <b>{number(summary.average)}</b></span>
        <span>{summary.observed_matches}/{summary.eligible_matches} observed</span>
        {summary.coverage_status === "PARTIAL" && <em>partial coverage</em>}
      </div>
    </div>
  );
}

function DirectionLane({ lane, tone }: { lane: MarketLaneSide; tone: "home" | "away" }) {
  return (
    <article className={styles.directionLane} data-tone={tone}>
      <div className={styles.axisLabel}>
        <span>{lane.team_name} attack</span>
        <i>→</i>
        <strong>MARKET LINE</strong>
        <i>←</i>
        <span>{lane.opponent_name} defence</span>
      </div>
      <div className={styles.directionBody}>
        <EvidenceHalf teamName={lane.team_name} summary={lane.attack} kind="attack" align="left" />
        <div className={styles.axisSpine} aria-hidden="true"><span /></div>
        <EvidenceHalf teamName={lane.opponent_name} summary={lane.defence_allowance} kind="defence" align="right" />
      </div>
      <div className={styles.directionFooter}>
        <span className={styles.signalLabel} data-signal={lane.evidence_label.toLowerCase()}>{lane.evidence_label} evidence</span>
        <small>Paired recent hit evidence · descriptive, not a model probability</small>
      </div>
    </article>
  );
}

function MarketFamilyDesk({ lane }: { lane: MarketLane }) {
  return (
    <section className={styles.marketDesk}>
      <header className={styles.marketHeading}>
        <div>
          <span>MARKET QUESTION · LAST FIVE</span>
          <h2>{lane.market_line.label}</h2>
          <p>Recent attacking output against what the opponent has recently allowed at the same fixed line.</p>
        </div>
        <div className={styles.lineStamp}>
          <span>FIXED LINE</span>
          <strong>{lane.market_line.label}</strong>
          <small>{lane.market_line.source_key}</small>
        </div>
      </header>
      <div className={styles.directionStack}>
        <DirectionLane lane={lane.home_lane} tone="home" />
        <DirectionLane lane={lane.away_lane} tone="away" />
      </div>
      <footer className={styles.marketFoot}>
        <span>Latest match is shown first in each sequence.</span>
        <span>Missing observations stay missing and reduce the displayed denominator.</span>
      </footer>
    </section>
  );
}

function PlayerBoard({ home, away }: { home: PlayerLeaderboard; away: PlayerLeaderboard }) {
  return (
    <article className={styles.playerBoard}>
      <div className={styles.playerSide}>
        {home.players.slice(0, 3).map((player) => (
          <div className={styles.playerLine} key={`${home.key}-${player.player_code}`}>
            <span><b>{player.player_name}</b><small>{player.position || "—"} · {player.appearances} apps</small></span>
            <strong>{number(player.value)}</strong>
          </div>
        ))}
      </div>
      <div className={styles.playerMetric}>
        <span>PLAYER WATCH</span>
        <strong>{home.label}</strong>
        <small>{home.unit}</small>
      </div>
      <div className={`${styles.playerSide} ${styles.playerSideAway}`}>
        {away.players.slice(0, 3).map((player) => (
          <div className={styles.playerLine} key={`${away.key}-${player.player_code}`}>
            <strong>{number(player.value)}</strong>
            <span><b>{player.player_name}</b><small>{player.position || "—"} · {player.appearances} apps</small></span>
          </div>
        ))}
      </div>
    </article>
  );
}

function PlayersDesk({ home, away }: { home: PlayerSide; away: PlayerSide }) {
  const pairs = PLAYER_BOARD_KEYS.map((key) => ({
    home: home.leaderboards.find((board) => board.key === key),
    away: away.leaderboards.find((board) => board.key === key),
  })).filter((pair): pair is { home: PlayerLeaderboard; away: PlayerLeaderboard } => Boolean(pair.home && pair.away));

  return (
    <section className={styles.playersDesk}>
      <header className={styles.marketHeading}>
        <div>
          <span>PLAYER QUESTION · RECENT EVIDENCE</span>
          <h2>Who is carrying the individual volume?</h2>
          <p>Current-season player evidence, kept separate from team threshold lines until player-market semantics are explicitly promoted.</p>
        </div>
        <div className={styles.playerSample}>
          <span>FIXTURE EVIDENCE</span>
          <strong>{home.fixture_evidence_count} / {away.fixture_evidence_count}</strong>
          <small>home / away fixtures</small>
        </div>
      </header>
      <div className={styles.playerTeamLabels}><strong>{home.team_name}</strong><span>RECENT LEADERS</span><strong>{away.team_name}</strong></div>
      <div className={styles.playerBoardStack}>
        {pairs.map(({ home: homeBoard, away: awayBoard }) => <PlayerBoard key={homeBoard.key} home={homeBoard} away={awayBoard} />)}
        {!pairs.length && <p className={styles.empty}>No directly comparable player boards are available for this fixture.</p>}
      </div>
      <footer className={styles.marketFoot}><span>{home.sample_definition}.</span><span>No player betting probability is inferred from these totals.</span></footer>
    </section>
  );
}

function FoulsBoundary() {
  return (
    <section className={styles.boundaryDesk}>
      <span className={styles.boundaryMark}>FRL BOUNDARY</span>
      <h2>Fouls are not promoted into this matchup lane yet.</h2>
      <p>FRL is deliberately withholding foul-committed versus foul-drawn opponent pairing until the source semantics and coverage are governed strongly enough for fixture-specific use.</p>
      <div><strong>Not zero. Not guessed. Not silently substituted.</strong><span>The question stays visible because it is analytically useful; the evidence stays withheld because it is not ready.</span></div>
    </section>
  );
}

function ModelStrip({ forecast, home, away }: { forecast: Forecast | undefined; home: string; away: string }) {
  if (!forecast || forecast.status !== "AVAILABLE") return null;
  const probabilities = forecast.probabilities ?? {};
  return (
    <section className={styles.modelStrip}>
      <div className={styles.modelIdentity}>
        <span>SEPARATE MODEL LAYER</span>
        <strong>{forecast.model ?? "Forecast"}</strong>
        <small>{forecast.control_status?.replaceAll("_", " ").toLowerCase()}</small>
      </div>
      <div><span>{home}</span><strong>{percent(probabilities.home_win)}</strong><small>win</small></div>
      <div><span>Draw</span><strong>{percent(probabilities.draw)}</strong><small>match</small></div>
      <div><span>{away}</span><strong>{percent(probabilities.away_win)}</strong><small>win</small></div>
      <div><span>Over 2.5</span><strong>{percent(probabilities.over_2_5)}</strong><small>goals</small></div>
      <div><span>BTTS</span><strong>{percent(probabilities.btts)}</strong><small>yes</small></div>
      <div className={styles.modelXg}><span>Expected goals</span><strong>{number(forecast.expected_goals?.home)} <i>/</i> {number(forecast.expected_goals?.away)}</strong><small>home / away</small></div>
    </section>
  );
}

export function MatchdayDeskV6({ pack, marketPack, fixtureOptions }: Props) {
  const data = pack as unknown as MatchdayPack;
  const marketData = marketPack as unknown as HeadToHeadPack | null;
  const fixtures = fixtureOptions as unknown as FixtureOption[];
  const lanes = marketData?.market_lanes ?? [];
  const laneByFamily = useMemo(() => new Map(lanes.map((lane) => [lane.family, lane])), [lanes]);
  const firstQuestion = QUESTION_ORDER.find((question) => laneByFamily.has(question)) ?? "Players";
  const [question, setQuestion] = useState<string>(firstQuestion);
  const [evidenceOpen, setEvidenceOpen] = useState(false);
  const activeLane = laneByFamily.get(question);
  const h2hHref = `/head-to-head/${encodeURIComponent(data.fixture.season)}/${encodeURIComponent(data.fixture.fixture_id)}`;

  return (
    <div className={styles.workspace}>
      <div className={styles.topbar}>
        <div><span>MATCHDAY</span><strong>{data.fixture.gameweek ? `GW ${data.fixture.gameweek}` : data.fixture.season}</strong></div>
        <details className={styles.fixtureChooser}>
          <summary>Change fixture <span>⌄</span></summary>
          <MatchdayFixtureNavigator season={data.fixture.season} currentFixtureId={data.fixture.fixture_id} currentGameweek={data.fixture.gameweek} currentHome={data.fixture.home_team_name} currentAway={data.fixture.away_team_name} fixtures={fixtures} />
        </details>
        <Link href={`/fixtures/${data.fixture.season}/${data.fixture.fixture_id}`}>Match report ↗</Link>
        <Link href={h2hHref}>Full H2H pack ↗</Link>
        <button type="button" onClick={() => setEvidenceOpen(true)}>Sources & method</button>
      </div>

      <header className={styles.fixtureHeader}>
        <div className={styles.fixtureTeam}>
          <span className={styles.heroKit}><TeamKit teamName={data.fixture.home_team_name} /></span>
          <div>
            <strong>{data.fixture.home_team_name}</strong>
            <span className={styles.formLine}><FormStrip results={data.teams.home.form.slice(0, 5)} /><small>last {data.teams.home.sample_size}</small></span>
          </div>
        </div>
        <div className={styles.fixtureCentre}>
          <span>{fixtureDate(data.fixture.kickoff_time)}</span>
          <strong>{fixtureTime(data.fixture.kickoff_time)}</strong>
          <small>Premier League · {data.fixture.gameweek ? `GW ${data.fixture.gameweek}` : data.fixture.season}</small>
        </div>
        <div className={`${styles.fixtureTeam} ${styles.fixtureTeamAway}`}>
          <span className={styles.heroKit}><TeamKit teamName={data.fixture.away_team_name} /></span>
          <div>
            <strong>{data.fixture.away_team_name}</strong>
            <span className={`${styles.formLine} ${styles.formLineAway}`}><small>last {data.teams.away.sample_size}</small><FormStrip results={data.teams.away.form.slice(0, 5)} /></span>
          </div>
        </div>
      </header>

      <section className={styles.questionIntro}>
        <div><span>FIXTURE EVIDENCE DESK</span><h1>What does this matchup say about the market?</h1></div>
        <p>Start with the betting question. Then put recent attack against recent opponent allowance at the exact same line.</p>
      </section>

      <nav className={styles.questionNav} aria-label="Market questions">
        {QUESTION_ORDER.map((item) => {
          const governedLane = laneByFamily.has(item);
          const available = governedLane || item === "Players";
          return (
            <button
              type="button"
              key={item}
              data-active={question === item ? "true" : "false"}
              data-available={available ? "true" : "false"}
              onClick={() => setQuestion(item)}
            >
              {item}<span>{governedLane ? "●" : item === "Players" ? "◆" : "○"}</span>
            </button>
          );
        })}
      </nav>

      <main className={styles.questionPanel}>
        {activeLane && <MarketFamilyDesk lane={activeLane} />}
        {question === "Players" && <PlayersDesk home={data.players.home} away={data.players.away} />}
        {question === "Fouls" && <FoulsBoundary />}
        {!activeLane && question !== "Players" && question !== "Fouls" && (
          <section className={styles.boundaryDesk}><span className={styles.boundaryMark}>UNAVAILABLE</span><h2>This market lane has no governed evidence for the selected fixture.</h2><p>The interface will not convert missing evidence into a zero or substitute a neighbouring metric.</p></section>
        )}
      </main>

      <ModelStrip forecast={marketData?.forecast} home={data.fixture.home_team_name} away={data.fixture.away_team_name} />

      <section className={styles.methodRail}>
        <div><span>READING RULE</span><strong>Hit rate is evidence, not probability.</strong></div>
        <p>The lane asks two descriptive questions: how often did the attacking side clear the line, and how often did opponents clear that line against the defence? Price and calibrated probability remain separate analytical layers.</p>
        <button type="button" onClick={() => setEvidenceOpen(true)}>Inspect coverage & limitations →</button>
      </section>

      <EvidenceDrawer open={evidenceOpen} onClose={() => setEvidenceOpen(false)} title="Matchday evidence & method">
        <div className={styles.evidenceDrawerContent}>
          <h3>Fixture cutoff</h3>
          <p>{fixtureDate(data.fixture.kickoff_time)} · {fixtureTime(data.fixture.kickoff_time)} London time. Recent evidence uses completed fixtures before this kickoff.</p>
          {data.data_maturity && <><h3>Sample maturity</h3><p>{data.data_maturity.note}</p></>}
          <h3>Market lanes</h3>
          <p>{marketData?.betbuilder?.threshold_policy ?? "Fixed market thresholds are unavailable for this fixture."}</p>
          <p>{marketData?.betbuilder?.index_definition ?? "No descriptive evidence index is available."}</p>
          <h3>Player evidence</h3>
          <p>{data.players.home.sample_definition}. {data.players.away.sample_definition}.</p>
          <h3>Limitations</h3>
          <ul>{[...data.limitations, ...(marketData?.limitations ?? [])].map((note, index) => <li key={index}>{note}</li>)}</ul>
          <p>Matchday pack: {data.pack_version}{marketData?.pack_version ? ` · matchup pack: ${marketData.pack_version}` : ""}</p>
        </div>
      </EvidenceDrawer>
    </div>
  );
}