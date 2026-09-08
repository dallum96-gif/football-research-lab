"use client";

import Link from "next/link";
import { useState } from "react";
import { TeamKit } from "@/app/teams/TeamKit";
import { EvidenceDrawer, FormStrip } from "@/components/analyst/AnalystUI";
import { MatchdayFixtureNavigator } from "./MatchdayFixtureNavigator";
import styles from "./MatchdayDeskV7.module.css";

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

type HeadToHeadPack = {
  pack_version: string;
  market_lanes: MarketLane[];
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

type DeskView = "markets" | "players" | "fouls";

const MARKET_ORDER = ["Goals", "Corners", "Shots", "SOT", "Cards"];
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

function shortOpponent(name: string) {
  const cleaned = name.replace(/[^A-Za-z]/g, "").toUpperCase();
  return cleaned.slice(0, 3) || "OPP";
}

function supportText(label: MarketLaneSide["evidence_label"]) {
  if (label === "STRONG") return "Strong support";
  if (label === "FAVOURABLE") return "Leans yes";
  if (label === "MIXED") return "Mixed";
  if (label === "WEAK") return "Weak support";
  return "Not enough data";
}

function familyTone(family: string) {
  if (family === "Goals") return "coral";
  if (family === "Corners") return "gold";
  if (family === "Shots") return "blue";
  if (family === "SOT") return "teal";
  if (family === "Cards") return "violet";
  return "coral";
}

function EvidenceCells({ summary }: { summary: ThresholdSummary }) {
  const cells: Array<ThresholdObservation | null> = summary.observations.slice(0, 5);
  while (cells.length < 5) cells.push(null);

  return (
    <div className={styles.cells}>
      {cells.map((observation, index) => observation ? (
        <span
          key={`${observation.season}-${observation.fixture_id}`}
          data-hit={observation.hit ? "true" : "false"}
          title={`${observation.opponent}: ${whole(observation.value)}`}
        >
          <b>{whole(observation.value)}</b>
          <small>{shortOpponent(observation.opponent)}</small>
        </span>
      ) : (
        <span key={`empty-${index}`} data-empty="true"><b>—</b><small>—</small></span>
      ))}
    </div>
  );
}

function EvidenceLine({ label, summary }: { label: string; summary: ThresholdSummary }) {
  return (
    <div className={styles.evidenceLine}>
      <strong>{label}</strong>
      <EvidenceCells summary={summary} />
      <b className={styles.hitRate}>{summary.hits}/{summary.observed_matches || "—"}</b>
    </div>
  );
}

function SideMarket({ lane, side }: { lane: MarketLaneSide; side: "home" | "away" }) {
  return (
    <section className={styles.sideMarket} data-side={side}>
      <header>
        <strong>{lane.team_name}</strong>
        <span data-signal={lane.evidence_label.toLowerCase()}>{supportText(lane.evidence_label)}</span>
      </header>
      <EvidenceLine label={`${lane.team_name} did it`} summary={lane.attack} />
      <EvidenceLine label={`${lane.opponent_name} allowed`} summary={lane.defence_allowance} />
    </section>
  );
}

function MarketFamily({ lane }: { lane: MarketLane }) {
  return (
    <article className={styles.marketFamily} data-tone={familyTone(lane.family)}>
      <header className={styles.familyHeader}>
        <div><span>{lane.family}</span><strong>{lane.market_line.label}</strong></div>
        <small>LAST FIVE · NEWEST FIRST</small>
      </header>
      <SideMarket lane={lane.home_lane} side="home" />
      <SideMarket lane={lane.away_lane} side="away" />
    </article>
  );
}

function MarketsDesk({ lanes }: { lanes: MarketLane[] }) {
  const byFamily = new Map(lanes.map((lane) => [lane.family, lane]));
  const ordered = MARKET_ORDER.map((family) => byFamily.get(family)).filter((lane): lane is MarketLane => Boolean(lane));

  return (
    <section className={styles.marketsDesk}>
      <div className={styles.cheatSheetHeading}>
        <div><span>LAST-FIVE BETTING CHEAT SHEET</span><strong>Team attack × opponent allowance</strong></div>
        <p>Green cells hit the displayed line. The number is the actual match value; the three-letter label is the opponent.</p>
      </div>
      <div className={styles.marketGrid}>
        {ordered.map((lane) => <MarketFamily key={lane.key} lane={lane} />)}
        {!ordered.length && <div className={styles.empty}>No governed team-market evidence is available for this fixture.</div>}
      </div>
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
      <div className={styles.cheatSheetHeading}>
        <div><span>PLAYER WATCH</span><strong>Who is producing the numbers?</strong></div>
        <p>Recent player totals only. These are evidence prompts, not player-prop probabilities.</p>
      </div>
      <div className={styles.playerGrid}>
        {pairs.map(({ home: homeBoard, away: awayBoard }) => (
          <article className={styles.playerBoard} key={homeBoard.key}>
            <header><strong>{homeBoard.label}</strong><span>{homeBoard.unit}</span></header>
            <div className={styles.playerColumns}>
              <div>
                {homeBoard.players.slice(0, 4).map((player) => (
                  <div className={styles.playerRow} key={`${homeBoard.key}-${player.player_code}`}>
                    <span><b>{player.player_name}</b><small>{player.position || "—"}</small></span><strong>{whole(player.value)}</strong>
                  </div>
                ))}
              </div>
              <div className={styles.playerAway}>
                {awayBoard.players.slice(0, 4).map((player) => (
                  <div className={styles.playerRow} key={`${awayBoard.key}-${player.player_code}`}>
                    <strong>{whole(player.value)}</strong><span><b>{player.player_name}</b><small>{player.position || "—"}</small></span>
                  </div>
                ))}
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function FoulsDesk() {
  return (
    <section className={styles.boundaryDesk}>
      <span>FOULS</span>
      <h2>Useful betting question. Not promoted yet.</h2>
      <p>FRL is withholding foul-won against foul-committed matchup evidence until that pairing has passed the required semantic and coverage checks.</p>
    </section>
  );
}

export function MatchdayDeskV7({ pack, marketPack, fixtureOptions }: Props) {
  const data = pack as unknown as MatchdayPack;
  const marketData = marketPack as unknown as HeadToHeadPack | null;
  const fixtures = fixtureOptions as unknown as FixtureOption[];
  const [view, setView] = useState<DeskView>("markets");
  const [evidenceOpen, setEvidenceOpen] = useState(false);
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

      <header className={styles.fixtureStrip}>
        <div className={styles.fixtureSide}>
          <span className={styles.kit}><TeamKit teamName={data.fixture.home_team_name} /></span>
          <div><strong>{data.fixture.home_team_name}</strong><span><FormStrip results={data.teams.home.form.slice(0, 5)} /><small>last {data.teams.home.sample_size}</small></span></div>
        </div>
        <div className={styles.kickoff}>
          <span>{fixtureDate(data.fixture.kickoff_time)}</span>
          <strong>{fixtureTime(data.fixture.kickoff_time)}</strong>
          <small>{data.fixture.gameweek ? `GW ${data.fixture.gameweek}` : data.fixture.season}</small>
        </div>
        <div className={`${styles.fixtureSide} ${styles.fixtureSideAway}`}>
          <span className={styles.kit}><TeamKit teamName={data.fixture.away_team_name} /></span>
          <div><strong>{data.fixture.away_team_name}</strong><span><small>last {data.teams.away.sample_size}</small><FormStrip results={data.teams.away.form.slice(0, 5)} /></span></div>
        </div>
      </header>

      <nav className={styles.viewNav}>
        <button type="button" data-active={view === "markets"} onClick={() => setView("markets")}>Team markets</button>
        <button type="button" data-active={view === "players"} onClick={() => setView("players")}>Players</button>
        <button type="button" data-active={view === "fouls"} onClick={() => setView("fouls")}>Fouls</button>
      </nav>

      <main className={styles.desk}>
        {view === "markets" && <MarketsDesk lanes={marketData?.market_lanes ?? []} />}
        {view === "players" && <PlayerDesk home={data.players.home} away={data.players.away} />}
        {view === "fouls" && <FoulsDesk />}
      </main>

      <EvidenceDrawer open={evidenceOpen} onClose={() => setEvidenceOpen(false)} title="Matchday evidence & method">
        <div className={styles.evidenceDrawerContent}>
          <h3>How to read the cheat sheet</h3>
          <p>For each team market, FRL pairs the team’s recent threshold results with how often the upcoming opponent allowed the same threshold in its own recent fixtures.</p>
          <p>Hit frequencies are descriptive evidence, not calibrated betting probabilities.</p>
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
