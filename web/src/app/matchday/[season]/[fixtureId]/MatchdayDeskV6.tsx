"use client";

import Link from "next/link";
import { useState } from "react";
import { TeamKit } from "@/app/teams/TeamKit";
import { EvidenceDrawer, FormStrip } from "@/components/analyst/AnalystUI";
import { MatchdayFixtureNavigator } from "./MatchdayFixtureNavigator";
import styles from "./MatchdayDeskV6.module.css";

type TeamSide = {
  team_name: string;
  sample_size: number;
  form: Array<"W" | "D" | "L">;
};

type LeaderPlayer = {
  rank: number;
  player_code: string;
  player_name: string;
  position: string;
  appearances: number;
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
  data_maturity?: { note: string };
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
  coverage_status: "COMPLETE" | "PARTIAL" | "UNAVAILABLE";
  observations: ThresholdObservation[];
};

type MarketLaneSide = {
  team_name: string;
  opponent_name: string;
  attack: ThresholdSummary;
  defence_allowance: ThresholdSummary;
  evidence_label: "STRONG" | "FAVOURABLE" | "MIXED" | "WEAK" | "UNAVAILABLE";
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
  probabilities?: Record<string, number>;
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

const QUESTIONS = ["Goals", "Corners", "Shots", "SOT", "Cards", "Players", "Fouls"] as const;
const PLAYER_KEYS = ["goals", "cards", "tackles", "recoveries"];

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

function whole(value: number | null | undefined) {
  if (value == null || Number.isNaN(value)) return "—";
  return Math.round(value).toLocaleString("en-GB");
}

function supportText(label: MarketLaneSide["evidence_label"]) {
  if (label === "STRONG") return "Both sides support this line";
  if (label === "FAVOURABLE") return "Recent evidence leans this way";
  if (label === "MIXED") return "The evidence is mixed";
  if (label === "WEAK") return "Little recent support";
  return "Not enough evidence";
}

function sampleNote(summary: ThresholdSummary) {
  if (!summary.eligible_matches) return "No matches available";
  if (summary.eligible_matches < 5) return `Last ${summary.eligible_matches} available`;
  if (summary.observed_matches < summary.eligible_matches) return `${summary.observed_matches}/${summary.eligible_matches} stat observations`;
  return "Last 5";
}

function HitSequence({ summary }: { summary: ThresholdSummary }) {
  return (
    <div className={styles.hitSequence}>
      {summary.observations.map((observation) => (
        <span
          key={`${observation.season}-${observation.fixture_id}`}
          data-hit={observation.hit ? "true" : "false"}
          title={`${observation.opponent}: ${whole(observation.value)}`}
        >
          <b>{whole(observation.value)}</b>
          <small>{observation.hit ? "✓" : "×"}</small>
        </span>
      ))}
      {!summary.observations.length && <em>No data</em>}
    </div>
  );
}

function EvidenceRow({
  label,
  summary,
}: {
  label: string;
  summary: ThresholdSummary;
}) {
  return (
    <div className={styles.evidenceRow}>
      <div className={styles.evidenceLabel}>
        <strong>{label}</strong>
        <span>{sampleNote(summary)}</span>
      </div>
      <HitSequence summary={summary} />
      <div className={styles.hitScore}>
        <strong>{summary.hits}/{summary.observed_matches || "—"}</strong>
        <span>hit</span>
      </div>
    </div>
  );
}

function MarketCard({ lane, side }: { lane: MarketLaneSide; side: "home" | "away" }) {
  return (
    <article className={styles.marketCard} data-side={side}>
      <header className={styles.marketCardHeader}>
        <div>
          <span>{side === "home" ? "HOME MARKET" : "AWAY MARKET"}</span>
          <h3>{lane.team_name}</h3>
        </div>
        <div className={styles.supportPill} data-signal={lane.evidence_label.toLowerCase()}>
          {supportText(lane.evidence_label)}
        </div>
      </header>

      <EvidenceRow label={`${lane.team_name} did it`} summary={lane.attack} />
      <EvidenceRow label={`${lane.opponent_name} allowed it`} summary={lane.defence_allowance} />
    </article>
  );
}

function MarketDesk({ lane }: { lane: MarketLane }) {
  return (
    <section className={styles.marketDesk}>
      <header className={styles.marketTitle}>
        <div>
          <span>LAST-FIVE MARKET CHECK</span>
          <h2>{lane.market_line.label}</h2>
        </div>
        <p>Did the team hit the line — and did its opponent recently allow the same thing?</p>
      </header>
      <div className={styles.marketCards}>
        <MarketCard lane={lane.home_lane} side="home" />
        <MarketCard lane={lane.away_lane} side="away" />
      </div>
      <footer className={styles.marketFooter}>
        <span>Numbers are individual match values, newest first.</span>
        <span>Green = line hit · cream = line missed.</span>
      </footer>
    </section>
  );
}

function PlayerDesk({ home, away }: { home: PlayerSide; away: PlayerSide }) {
  const pairs = PLAYER_KEYS.map((key) => ({
    home: home.leaderboards.find((board) => board.key === key),
    away: away.leaderboards.find((board) => board.key === key),
  })).filter((pair): pair is { home: PlayerLeaderboard; away: PlayerLeaderboard } => Boolean(pair.home && pair.away));

  return (
    <section className={styles.playerDesk}>
      <header className={styles.marketTitle}>
        <div><span>PLAYER WATCH</span><h2>Who is producing the numbers?</h2></div>
        <p>Recent player totals only. No player betting probability is inferred here.</p>
      </header>
      <div className={styles.playerHead}><strong>{home.team_name}</strong><span>RECENT LEADERS</span><strong>{away.team_name}</strong></div>
      <div className={styles.playerBoards}>
        {pairs.map(({ home: homeBoard, away: awayBoard }) => (
          <article className={styles.playerBoard} key={homeBoard.key}>
            <div className={styles.playerList}>
              {homeBoard.players.slice(0, 4).map((player) => (
                <div key={`${homeBoard.key}-${player.player_code}`}><span><b>{player.player_name}</b><small>{player.position || "—"}</small></span><strong>{whole(player.value)}</strong></div>
              ))}
            </div>
            <div className={styles.playerMetric}><span>{homeBoard.label}</span></div>
            <div className={`${styles.playerList} ${styles.playerListAway}`}>
              {awayBoard.players.slice(0, 4).map((player) => (
                <div key={`${awayBoard.key}-${player.player_code}`}><strong>{whole(player.value)}</strong><span><b>{player.player_name}</b><small>{player.position || "—"}</small></span></div>
              ))}
            </div>
          </article>
        ))}
        {!pairs.length && <p className={styles.empty}>No comparable player boards are available.</p>}
      </div>
    </section>
  );
}

function FoulsDesk() {
  return (
    <section className={styles.simpleBoundary}>
      <span>FOULS</span>
      <h2>Useful question. Evidence not promoted yet.</h2>
      <p>FRL is not yet presenting foul-won against foul-committed matchup evidence here because that pairing has not passed the required semantic and coverage checks.</p>
    </section>
  );
}

export function MatchdayDeskV6({ pack, marketPack, fixtureOptions }: Props) {
  const data = pack as unknown as MatchdayPack;
  const marketData = marketPack as unknown as HeadToHeadPack | null;
  const fixtures = fixtureOptions as unknown as FixtureOption[];
  const laneByFamily = new Map((marketData?.market_lanes ?? []).map((lane) => [lane.family, lane]));
  const firstQuestion = QUESTIONS.find((item) => laneByFamily.has(item)) ?? "Players";
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
        <Link href={h2hHref}>Full H2H ↗</Link>
        <button type="button" onClick={() => setEvidenceOpen(true)}>Sources & method</button>
      </div>

      <header className={styles.fixtureHeader}>
        <div className={styles.fixtureTeam}>
          <span className={styles.heroKit}><TeamKit teamName={data.fixture.home_team_name} /></span>
          <div><strong>{data.fixture.home_team_name}</strong><span className={styles.formLine}><FormStrip results={data.teams.home.form.slice(0, 5)} /><small>last {data.teams.home.sample_size}</small></span></div>
        </div>
        <div className={styles.fixtureCentre}><span>{fixtureDate(data.fixture.kickoff_time)}</span><strong>{fixtureTime(data.fixture.kickoff_time)}</strong><small>{data.fixture.gameweek ? `GW ${data.fixture.gameweek}` : data.fixture.season}</small></div>
        <div className={`${styles.fixtureTeam} ${styles.fixtureTeamAway}`}>
          <span className={styles.heroKit}><TeamKit teamName={data.fixture.away_team_name} /></span>
          <div><strong>{data.fixture.away_team_name}</strong><span className={`${styles.formLine} ${styles.formLineAway}`}><small>last {data.teams.away.sample_size}</small><FormStrip results={data.teams.away.form.slice(0, 5)} /></span></div>
        </div>
      </header>

      <nav className={styles.questionNav} aria-label="Betting market evidence">
        {QUESTIONS.map((item) => {
          const available = laneByFamily.has(item) || item === "Players" || item === "Fouls";
          return <button type="button" key={item} data-active={question === item ? "true" : "false"} data-available={available ? "true" : "false"} onClick={() => setQuestion(item)}>{item}</button>;
        })}
      </nav>

      <main className={styles.questionPanel}>
        {activeLane && <MarketDesk lane={activeLane} />}
        {question === "Players" && <PlayerDesk home={data.players.home} away={data.players.away} />}
        {question === "Fouls" && <FoulsDesk />}
        {!activeLane && question !== "Players" && question !== "Fouls" && <section className={styles.simpleBoundary}><span>{question}</span><h2>No governed matchup evidence for this fixture.</h2><p>FRL will not replace missing evidence with zero or a neighbouring statistic.</p></section>}
      </main>

      <EvidenceDrawer open={evidenceOpen} onClose={() => setEvidenceOpen(false)} title="Matchday evidence & method">
        <div className={styles.evidenceDrawerContent}>
          <h3>How to read this</h3>
          <p>Each market card combines two descriptive checks from matches before kickoff: whether the selected team cleared the fixed line, and whether opponents cleared that same line against the team they now face.</p>
          <p>Hit frequencies are evidence to investigate, not calibrated betting probabilities.</p>
          {data.data_maturity && <><h3>Sample</h3><p>{data.data_maturity.note}</p></>}
          <h3>Threshold policy</h3><p>{marketData?.betbuilder?.threshold_policy ?? "No market threshold pack is available."}</p>
          <h3>Player evidence</h3><p>{data.players.home.sample_definition}. {data.players.away.sample_definition}.</p>
          <h3>Limitations</h3><ul>{[...data.limitations, ...(marketData?.limitations ?? [])].map((note, index) => <li key={index}>{note}</li>)}</ul>
          <p>Matchday pack: {data.pack_version}{marketData?.pack_version ? ` · matchup pack: ${marketData.pack_version}` : ""}</p>
        </div>
      </EvidenceDrawer>
    </div>
  );
}
