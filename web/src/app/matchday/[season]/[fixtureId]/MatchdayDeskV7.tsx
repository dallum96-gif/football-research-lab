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

type PlayerSide = {
  team_name: string;
  sample_definition: string;
  fixture_evidence_count: number;
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

type BttsObservation = {
  season: string;
  fixture_id: string;
  kickoff_time: string | null;
  opponent: string;
  venue: "Home" | "Away" | null;
  goals_for: number;
  goals_against: number;
  hit: boolean;
};

type BttsSummary = {
  hits: number;
  observed_matches: number;
  eligible_matches: number;
  hit_rate: number | null;
  coverage_status: "COMPLETE" | "PARTIAL" | "UNAVAILABLE";
  observations: BttsObservation[];
};

type BttsMarket = {
  key: string;
  family: "BTTS";
  label: string;
  home_team_name: string;
  away_team_name: string;
  home_recent: BttsSummary;
  away_recent: BttsSummary;
};

type PlayerMarketObservation = {
  season: string;
  fixture_id: string;
  kickoff_time: string | null;
  opponent: string;
  value: number;
  hit: boolean;
};

type PlayerMarketPlayer = {
  player_code: string;
  player_name: string;
  position: string;
  hits: number;
  observed_appearances: number;
  eligible_team_matches: number;
  total: number;
  observations: PlayerMarketObservation[];
};

type PlayerMarketSide = {
  team_name: string;
  eligible_team_matches: number;
  players: PlayerMarketPlayer[];
};

type PlayerMarket = {
  key: string;
  family: string;
  label: string;
  threshold: number;
  unit: string;
  source: string;
  home: PlayerMarketSide;
  away: PlayerMarketSide;
  sample_definition: string;
};

type HeadToHeadPack = {
  pack_version: string;
  market_lanes: MarketLane[];
  fixture_markets?: { btts?: BttsMarket };
  player_markets?: PlayerMarket[];
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
const PLAYER_MARKET_ORDER = ["Shots", "SOT", "Fouls won", "Fouls committed", "Goals", "Cards"];

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
  if (family === "Corners" || family === "Fouls won") return "gold";
  if (family === "Shots") return "blue";
  if (family === "SOT") return "teal";
  if (family === "Cards" || family === "Fouls committed") return "violet";
  if (family === "BTTS") return "olive";
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

function BttsCells({ summary }: { summary: BttsSummary }) {
  const cells: Array<BttsObservation | null> = summary.observations.slice(0, 5);
  while (cells.length < 5) cells.push(null);
  return (
    <div className={styles.cells}>
      {cells.map((observation, index) => observation ? (
        <span key={`${observation.season}-${observation.fixture_id}`} data-hit={observation.hit ? "true" : "false"} title={`${observation.opponent}: ${whole(observation.goals_for)}-${whole(observation.goals_against)}`}>
          <b>{whole(observation.goals_for)}-{whole(observation.goals_against)}</b>
          <small>{shortOpponent(observation.opponent)}</small>
        </span>
      ) : <span key={`btts-empty-${index}`} data-empty="true"><b>—</b><small>—</small></span>)}
    </div>
  );
}

function BttsSide({ teamName, summary }: { teamName: string; summary: BttsSummary }) {
  return (
    <section className={`${styles.sideMarket} ${styles.bttsSide}`}>
      <header><strong>{teamName}</strong><span>{summary.hits}/{summary.observed_matches || "—"} BTTS</span></header>
      <div className={styles.evidenceLine}>
        <strong>Both scored</strong>
        <BttsCells summary={summary} />
        <b className={styles.hitRate}>{summary.hits}/{summary.observed_matches || "—"}</b>
      </div>
    </section>
  );
}

function BttsFamily({ market }: { market: BttsMarket }) {
  return (
    <article className={`${styles.marketFamily} ${styles.bttsFamily}`} data-tone="olive">
      <header className={styles.familyHeader}>
        <div><span>BTTS</span><strong>Both teams to score</strong></div>
        <small>SCORELINES · NEWEST FIRST</small>
      </header>
      <BttsSide teamName={market.home_team_name} summary={market.home_recent} />
      <BttsSide teamName={market.away_team_name} summary={market.away_recent} />
    </article>
  );
}

function MarketsDesk({ lanes, btts }: { lanes: MarketLane[]; btts?: BttsMarket }) {
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
        {btts && <BttsFamily market={btts} />}
        {!ordered.length && !btts && <div className={styles.empty}>No governed team-market evidence is available for this fixture.</div>}
      </div>
    </section>
  );
}

function PlayerCells({ player }: { player: PlayerMarketPlayer }) {
  const cells: Array<PlayerMarketObservation | null> = player.observations.slice(0, 5);
  while (cells.length < 5) cells.push(null);
  return (
    <div className={styles.playerCells}>
      {cells.map((observation, index) => observation ? (
        <span key={`${player.player_code}-${observation.season}-${observation.fixture_id}`} data-hit={observation.hit ? "true" : "false"} title={`${observation.opponent}: ${whole(observation.value)}`}>
          <b>{whole(observation.value)}</b>
          <small>{shortOpponent(observation.opponent)}</small>
        </span>
      ) : <span key={`${player.player_code}-empty-${index}`} data-empty="true"><b>—</b><small>—</small></span>)}
    </div>
  );
}

function PlayerMarketTeam({ side }: { side: PlayerMarketSide }) {
  return (
    <section className={styles.playerMarketTeam}>
      <header><strong>{side.team_name}</strong><span>last {side.eligible_team_matches} team games</span></header>
      {side.players.slice(0, 3).map((player) => (
        <div className={styles.playerPropRow} key={player.player_code}>
          <span className={styles.playerPropName}><b>{player.player_name}</b><small>{player.position || "—"}</small></span>
          <PlayerCells player={player} />
          <strong className={styles.playerHitRate}>{player.hits}/{player.observed_appearances || "—"}</strong>
        </div>
      ))}
      {!side.players.length && <span className={styles.playerNoData}>No observed player evidence</span>}
    </section>
  );
}

function PlayerMarketFamily({ market }: { market: PlayerMarket }) {
  return (
    <article className={styles.playerMarketFamily} data-tone={familyTone(market.family)}>
      <header className={styles.familyHeader}>
        <div><span>{market.family}</span><strong>{market.label}</strong></div>
        <small>PLAYER LAST FIVE</small>
      </header>
      <PlayerMarketTeam side={market.home} />
      <PlayerMarketTeam side={market.away} />
    </article>
  );
}

function PlayerDesk({ markets }: { markets: PlayerMarket[] }) {
  const byFamily = new Map(markets.map((market) => [market.family, market]));
  const ordered = PLAYER_MARKET_ORDER.map((family) => byFamily.get(family)).filter((market): market is PlayerMarket => Boolean(market));
  return (
    <section className={styles.playerDesk}>
      <div className={styles.cheatSheetHeading}>
        <div><span>PLAYER BETTING CHEAT SHEET</span><strong>Recent prop-line evidence</strong></div>
        <p>Actual values from current-season appearances before kickoff. Green means the player cleared the displayed line.</p>
      </div>
      <div className={styles.playerMarketGrid}>
        {ordered.map((market) => <PlayerMarketFamily key={market.key} market={market} />)}
        {!ordered.length && <div className={styles.empty}>No governed player-market evidence is available for this fixture.</div>}
      </div>
    </section>
  );
}

function FoulsDesk() {
  return (
    <section className={styles.boundaryDesk}>
      <span>TEAM FOULS</span>
      <h2>Player fouls are now in the Players cheat sheet.</h2>
      <p>The separate team-level foul-won against foul-committed matchup lane remains withheld until that pairing has passed the required semantic and coverage checks.</p>
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
        <button type="button" data-active={view === "players"} onClick={() => setView("players")}>Player markets</button>
        <button type="button" data-active={view === "fouls"} onClick={() => setView("fouls")}>Team fouls</button>
      </nav>

      <main className={styles.desk}>
        {view === "markets" && <MarketsDesk lanes={marketData?.market_lanes ?? []} btts={marketData?.fixture_markets?.btts} />}
        {view === "players" && <PlayerDesk markets={marketData?.player_markets ?? []} />}
        {view === "fouls" && <FoulsDesk />}
      </main>

      <EvidenceDrawer open={evidenceOpen} onClose={() => setEvidenceOpen(false)} title="Matchday evidence & method">
        <div className={styles.evidenceDrawerContent}>
          <h3>How to read the cheat sheet</h3>
          <p>For each team market, FRL pairs the team’s recent threshold results with how often the upcoming opponent allowed the same threshold in its own recent fixtures.</p>
          <p>Player markets use current-season pre-kickoff appearances and fixed common prop-like lines. Hit frequencies are descriptive evidence, not calibrated betting probabilities.</p>
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
