"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { TeamKit } from "@/app/teams/TeamKit";
import { EvidenceDrawer, FormStrip } from "@/components/analyst/AnalystUI";
import { MatchdayFixtureNavigator } from "./MatchdayFixtureNavigator";
import styles from "./MatchdayStatPackV4.module.css";

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
  inputs?: {
    home_strength?: Record<string, number | string | null>;
    away_strength?: Record<string, number | string | null>;
  };
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

type PlayerCategory = {
  key: string;
  label: string;
  tone: string;
  matches: (board: PlayerLeaderboard) => boolean;
};

type DeepView = "pack" | "teams" | "players" | "markets";

const PLAYER_CATEGORIES: PlayerCategory[] = [
  {
    key: "shooting",
    label: "Shooting",
    tone: "sun",
    matches: (board) => /shot|target|goal|xg/i.test(`${board.key} ${board.label}`) && !/assist|against|conced/i.test(`${board.key} ${board.label}`),
  },
  {
    key: "creation",
    label: "Creation",
    tone: "blue",
    matches: (board) => /assist|chance|key.?pass|creation|xa/i.test(`${board.key} ${board.label}`),
  },
  {
    key: "defending",
    label: "Defending",
    tone: "olive",
    matches: (board) => /tackle|interception|clearance|block|duel|recover/i.test(`${board.key} ${board.label}`),
  },
  {
    key: "fouls",
    label: "Fouls",
    tone: "violet",
    matches: (board) => /foul|drawn|won/i.test(`${board.key} ${board.label}`),
  },
  {
    key: "discipline",
    label: "Cards",
    tone: "coral",
    matches: (board) => /card|yellow|red|booking/i.test(`${board.key} ${board.label}`),
  },
];

const TEAM_METRIC_PRIORITY = [
  "goals_for",
  "goals",
  "shots_on_target",
  "shots",
  "corners",
  "fouls_won",
  "fouls",
  "cards",
  "yellow",
  "possession",
  "tackles",
];

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

function metricValue(metric: Metric | undefined) {
  if (!metric || metric.value == null) return "—";
  const value = whole(metric.value);
  return metric.unit === "%" ? `${value}%` : value;
}

function playerValue(board: PlayerLeaderboard, player: LeaderPlayer | undefined) {
  if (!player) return "—";
  const value = whole(player.value);
  return board.unit === "%" ? `${value}%` : value;
}

function probability(value: number | undefined) {
  return value == null ? "—" : `${Math.round(value * 100)}%`;
}

function metricTone(metric: Metric) {
  const haystack = `${metric.key} ${metric.label}`.toLowerCase();
  if (/shot|goal|attack|xg/.test(haystack)) return "coral";
  if (/corner|set.?piece/.test(haystack)) return "sun";
  if (/foul|card|yellow|red/.test(haystack)) return "violet";
  if (/tackle|interception|clearance|defen|duel/.test(haystack)) return "olive";
  if (/pass|possession|chance|assist|creation/.test(haystack)) return "blue";
  return "teal";
}

function sharedTeamMetrics(home: TeamSide, away: TeamSide) {
  const awayByKey = new Map(away.metrics.map((metric) => [metric.key, metric]));
  const pairs = home.metrics
    .map((homeMetric) => ({ home: homeMetric, away: awayByKey.get(homeMetric.key) }))
    .filter((pair): pair is { home: Metric; away: Metric } => Boolean(pair.away));

  return pairs
    .sort((a, b) => {
      const aText = `${a.home.key} ${a.home.label}`.toLowerCase();
      const bText = `${b.home.key} ${b.home.label}`.toLowerCase();
      const aIndex = TEAM_METRIC_PRIORITY.findIndex((key) => aText.includes(key));
      const bIndex = TEAM_METRIC_PRIORITY.findIndex((key) => bText.includes(key));
      return (aIndex === -1 ? 99 : aIndex) - (bIndex === -1 ? 99 : bIndex);
    })
    .slice(0, 10);
}

function availablePlayerCategories(home: PlayerSide, away: PlayerSide) {
  const boards = [...home.leaderboards, ...away.leaderboards];
  const matched = PLAYER_CATEGORIES.filter((category) => boards.some(category.matches));
  if (matched.length) return matched;
  return [{
    key: "leaders",
    label: "Player leaders",
    tone: "teal",
    matches: (_board: PlayerLeaderboard) => true,
  }];
}

function pairedBoards(home: PlayerSide, away: PlayerSide, category: PlayerCategory) {
  const homeBoards = home.leaderboards.filter(category.matches);
  const awayByKey = new Map(away.leaderboards.filter(category.matches).map((board) => [board.key, board]));
  const matched = homeBoards
    .map((homeBoard) => ({ home: homeBoard, away: awayByKey.get(homeBoard.key) }))
    .filter((pair): pair is { home: PlayerLeaderboard; away: PlayerLeaderboard } => Boolean(pair.away));

  if (matched.length) return matched.slice(0, 3);

  const homeFallback = homeBoards.slice(0, 2);
  const awayFallback = away.leaderboards.filter(category.matches).slice(0, 2);
  return homeFallback.map((homeBoard, index) => ({ home: homeBoard, away: awayFallback[index] ?? homeBoard })).slice(0, 2);
}

function TeamStatRow({ home, away }: { home: Metric; away: Metric }) {
  const tone = metricTone(home);
  const max = Math.max(Math.abs(home.value ?? 0), Math.abs(away.value ?? 0), 1);
  const homeWidth = home.value == null ? 0 : Math.max(5, Math.min(100, Math.abs(home.value) / max * 100));
  const awayWidth = away.value == null ? 0 : Math.max(5, Math.min(100, Math.abs(away.value) / max * 100));

  return (
    <div className={styles.teamStatRow} data-tone={tone}>
      <strong className={styles.homeNumber}>{metricValue(home)}</strong>
      <div className={styles.homeTrack}><i style={{ width: `${homeWidth}%` }} /></div>
      <div className={styles.teamMetricLabel}><span>{home.label}</span></div>
      <div className={styles.awayTrack}><i style={{ width: `${awayWidth}%` }} /></div>
      <strong className={styles.awayNumber}>{metricValue(away)}</strong>
    </div>
  );
}

function PlayerBoardPair({ home, away, tone }: { home: PlayerLeaderboard; away: PlayerLeaderboard; tone: string }) {
  return (
    <article className={styles.playerBoard} data-tone={tone}>
      <div className={styles.playerBoardTitle}><strong>{home.label}</strong></div>
      <div className={styles.playerBoardSides}>
        <div className={styles.playerBoardSide}>
          {(home.players ?? []).slice(0, 3).map((player) => (
            <div className={styles.playerLine} key={`${home.key}-${player.player_code}`}>
              <span><b>{player.player_name}</b><small>{player.position || "—"}</small></span>
              <strong>{playerValue(home, player)}</strong>
            </div>
          ))}
          {!home.players?.length && <span className={styles.empty}>No data</span>}
        </div>
        <div className={`${styles.playerBoardSide} ${styles.playerBoardAway}`}>
          {(away.players ?? []).slice(0, 3).map((player) => (
            <div className={styles.playerLine} key={`${away.key}-${player.player_code}`}>
              <strong>{playerValue(away, player)}</strong>
              <span><b>{player.player_name}</b><small>{player.position || "—"}</small></span>
            </div>
          ))}
          {!away.players?.length && <span className={styles.empty}>No data</span>}
        </div>
      </div>
    </article>
  );
}

function FullTeamPanel({ side, tone }: { side: TeamSide; tone: "home" | "away" }) {
  return (
    <section className={styles.deepTeam} data-side={tone}>
      <div className={styles.deepTeamHead}>
        <span className={styles.deepKit}><TeamKit teamName={side.team_name} /></span>
        <div><strong>{side.team_name}</strong><FormStrip results={side.form} /></div>
      </div>
      <div className={styles.fullMetricList}>
        {side.metrics.map((metric) => (
          <div key={metric.key} data-tone={metricTone(metric)}>
            <span>{metric.label}</span><strong>{metricValue(metric)}</strong>
          </div>
        ))}
      </div>
      <div className={styles.recentMatches}>
        {side.matches.map((match) => (
          <Link href={`/fixtures/${match.season}/${match.fixture_id}`} key={`${match.season}-${match.fixture_id}`}>
            <span data-result={match.result}>{match.result}</span><strong>{match.opponent}</strong><small>{match.venue}</small><b>{match.goals_for}–{match.goals_against}</b>
          </Link>
        ))}
      </div>
    </section>
  );
}

function FullPlayerBoard({ board }: { board: PlayerLeaderboard }) {
  return (
    <article className={styles.fullPlayerBoard} data-tone={metricTone({ key: board.key, label: board.label, unit: board.unit, value: null, observed_matches: 0, eligible_matches: 0 })}>
      <header><strong>{board.label}</strong></header>
      {(board.players ?? []).slice(0, 10).map((player) => (
        <div key={`${board.key}-${player.player_code}-${player.rank}`}>
          <span className={styles.rank}>{player.rank}</span>
          <span><b>{player.player_name}</b><small>{player.position || "—"}</small></span>
          <strong>{playerValue(board, player)}</strong>
        </div>
      ))}
    </article>
  );
}

export function MatchdayStatPackV4({ pack, fixtureOptions }: Props) {
  const data = pack as unknown as MatchdayPack;
  const fixtures = fixtureOptions as unknown as FixtureOption[];
  const [view, setView] = useState<DeepView>("pack");
  const [playerSide, setPlayerSide] = useState<"home" | "away">("home");
  const [evidenceOpen, setEvidenceOpen] = useState(false);
  const categories = useMemo(() => availablePlayerCategories(data.players.home, data.players.away), [data.players.home, data.players.away]);
  const [playerCategoryKey, setPlayerCategoryKey] = useState(categories[0]?.key ?? "leaders");
  const activeCategory = categories.find((category) => category.key === playerCategoryKey) ?? categories[0];
  const teamMetrics = useMemo(() => sharedTeamMetrics(data.teams.home, data.teams.away), [data.teams.home, data.teams.away]);
  const playerBoards = activeCategory ? pairedBoards(data.players.home, data.players.away, activeCategory) : [];
  const selectedPlayerSide = data.players[playerSide];
  const probabilities = data.prediction.probabilities ?? {};
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
        <button type="button" onClick={() => setEvidenceOpen(true)}>Sources & method</button>
      </div>

      <header className={styles.fixtureHeader}>
        <div className={styles.fixtureTeam}>
          <span className={styles.heroKit}><TeamKit teamName={data.fixture.home_team_name} /></span>
          <strong>{data.fixture.home_team_name}</strong>
        </div>
        <div className={styles.fixtureCentre}>
          <span>{fixtureDate(data.fixture.kickoff_time)}</span>
          <strong>{fixtureTime(data.fixture.kickoff_time)}</strong>
          <small>Premier League · {data.fixture.gameweek ? `Gameweek ${data.fixture.gameweek}` : data.fixture.season}</small>
        </div>
        <div className={`${styles.fixtureTeam} ${styles.fixtureTeamAway}`}>
          <span className={styles.heroKit}><TeamKit teamName={data.fixture.away_team_name} /></span>
          <strong>{data.fixture.away_team_name}</strong>
        </div>
      </header>

      <nav className={styles.viewNav} aria-label="Matchday views">
        <button type="button" data-active={view === "pack"} onClick={() => setView("pack")}>Stat pack</button>
        <button type="button" data-active={view === "teams"} onClick={() => setView("teams")}>All team stats</button>
        <button type="button" data-active={view === "players"} onClick={() => setView("players")}>All player stats</button>
        <button type="button" data-active={view === "markets"} onClick={() => setView("markets")}>Match probabilities</button>
      </nav>

      {view === "pack" && (
        <main className={styles.statPack}>
          <section className={styles.teamPack}>
            <div className={styles.sectionTitle}>
              <div><span>TEAM</span><h2>Match in numbers</h2></div>
              <button type="button" onClick={() => setView("teams")}>See every team stat →</button>
            </div>

            <div className={styles.teamIdentityRow}>
              <div><span className={styles.miniKit}><TeamKit teamName={data.teams.home.team_name} /></span><strong>{data.teams.home.team_name}</strong><FormStrip results={data.teams.home.form} /></div>
              <span>LAST {Math.max(data.teams.home.sample_size, data.teams.away.sample_size)} MATCHES</span>
              <div><FormStrip results={data.teams.away.form} /><strong>{data.teams.away.team_name}</strong><span className={styles.miniKit}><TeamKit teamName={data.teams.away.team_name} /></span></div>
            </div>

            <div className={styles.teamStats}>
              {teamMetrics.length ? teamMetrics.map(({ home, away }) => <TeamStatRow key={home.key} home={home} away={away} />) : <p className={styles.empty}>No shared team statistics are available for this fixture yet.</p>}
            </div>
          </section>

          <section className={styles.playerPack}>
            <div className={styles.sectionTitle}>
              <div><span>PLAYERS</span><h2>Player stat pack</h2></div>
              <button type="button" onClick={() => setView("players")}>See every player board →</button>
            </div>

            <div className={styles.categoryTabs}>
              {categories.map((category) => (
                <button type="button" key={category.key} data-active={activeCategory?.key === category.key} data-tone={category.tone} onClick={() => setPlayerCategoryKey(category.key)}>{category.label}</button>
              ))}
            </div>

            <div className={styles.playerTeamHead}>
              <strong>{data.players.home.team_name}</strong>
              <span>{activeCategory?.label ?? "Players"}</span>
              <strong>{data.players.away.team_name}</strong>
            </div>

            <div className={styles.playerBoards}>
              {playerBoards.length ? playerBoards.map(({ home, away }) => <PlayerBoardPair key={`${activeCategory?.key}-${home.key}`} home={home} away={away} tone={activeCategory?.tone ?? "teal"} />) : <p className={styles.empty}>No player leaderboards in this category yet.</p>}
            </div>
          </section>

          <section className={styles.investigate}>
            <div className={styles.sectionTitle}><div><span>GO DEEPER</span><h2>Investigate the fixture</h2></div></div>
            <div className={styles.investigateGrid}>
              <button type="button" data-tone="coral" onClick={() => setView("teams")}><span>TEAM STATS</span><strong>Compare the full team profile</strong><b>→</b></button>
              <button type="button" data-tone="olive" onClick={() => setView("players")}><span>PLAYER STATS</span><strong>Open the full leaderboards</strong><b>→</b></button>
              <Link href={h2hHref} data-tone="blue"><span>H2H</span><strong>Opponent & threshold evidence</strong><b>↗</b></Link>
              <button type="button" data-tone="violet" onClick={() => setView("markets")}><span>PROBABILITIES</span><strong>What FRL gives each outcome</strong><b>→</b></button>
            </div>
          </section>
        </main>
      )}

      {view === "teams" && (
        <main className={styles.deepView}>
          <div className={styles.deepTitle}><div><span>TEAM STATS</span><h2>{data.teams.home.team_name} vs {data.teams.away.team_name}</h2></div><button type="button" onClick={() => setView("pack")}>← Back to stat pack</button></div>
          <div className={styles.teamColumns}><FullTeamPanel side={data.teams.home} tone="home" /><FullTeamPanel side={data.teams.away} tone="away" /></div>
        </main>
      )}

      {view === "players" && (
        <main className={styles.deepView}>
          <div className={styles.deepTitle}><div><span>PLAYER STATS</span><h2>Full player leaderboards</h2></div><button type="button" onClick={() => setView("pack")}>← Back to stat pack</button></div>
          <div className={styles.playerSideSwitch}>{(["home", "away"] as const).map((side) => <button type="button" key={side} data-active={playerSide === side} onClick={() => setPlayerSide(side)}>{data.players[side].team_name}</button>)}</div>
          <div className={styles.fullPlayerGrid}>{selectedPlayerSide.leaderboards.filter((board) => board.players.length).map((board) => <FullPlayerBoard key={board.key} board={board} />)}</div>
        </main>
      )}

      {view === "markets" && (
        <main className={styles.deepView}>
          <div className={styles.deepTitle}><div><span>MATCH PROBABILITIES</span><h2>FRL outcome view</h2></div><button type="button" onClick={() => setView("pack")}>← Back to stat pack</button></div>
          {data.prediction.status === "AVAILABLE" ? (
            <div className={styles.probabilityStrip}>
              <article data-tone="coral"><span>{data.fixture.home_team_name}</span><strong>{probability(probabilities.home_win)}</strong></article>
              <article data-tone="sun"><span>Draw</span><strong>{probability(probabilities.draw)}</strong></article>
              <article data-tone="olive"><span>{data.fixture.away_team_name}</span><strong>{probability(probabilities.away_win)}</strong></article>
              {probabilities.over_2_5 != null && <article data-tone="blue"><span>Over 2.5 goals</span><strong>{probability(probabilities.over_2_5)}</strong></article>}
              {probabilities.btts != null && <article data-tone="violet"><span>Both teams score</span><strong>{probability(probabilities.btts)}</strong></article>}
            </div>
          ) : <p className={styles.empty}>{data.prediction.reason ?? "No match probabilities are available for this fixture."}</p>}
          <button type="button" className={styles.methodLink} onClick={() => setEvidenceOpen(true)}>How FRL calculated this →</button>
        </main>
      )}

      <EvidenceDrawer open={evidenceOpen} onClose={() => setEvidenceOpen(false)} title="Matchday sources & method">
        <div className={styles.evidenceContent}>
          <h3>Fixture cutoff</h3>
          <p>{fixtureDate(data.fixture.kickoff_time)} · {fixtureTime(data.fixture.kickoff_time)} London time. Matchday statistics use evidence available before kickoff.</p>
          {data.data_maturity && <><h3>Sample</h3><p>{data.data_maturity.note}</p></>}
          <h3>Player evidence</h3>
          <p>{data.players.home.sample_definition}. {data.players.away.sample_definition}.</p>
          <h3>Model</h3>
          <p>{data.prediction.model ?? "Unavailable"}{data.prediction.source_season ? ` · source season ${data.prediction.source_season}` : ""}.</p>
          <h3>Limitations</h3>
          <ul>{[...data.limitations, ...(data.prediction.limitations ?? [])].map((note, index) => <li key={index}>{note}</li>)}</ul>
          <p>Pack version: {data.pack_version}</p>
        </div>
      </EvidenceDrawer>
    </div>
  );
}
