"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { TeamKit } from "@/app/teams/TeamKit";
import { EvidenceDrawer, FormStrip } from "@/components/analyst/AnalystUI";
import { MatchdayFixtureNavigator } from "./MatchdayFixtureNavigator";
import styles from "./MatchdayDeskV5.module.css";

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
  source_season?: string;
  reason?: string;
  limitations?: string[];
  probabilities?: Record<string, number>;
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

type DeskView = "last5" | "teams" | "players" | "probabilities";

type PlayerCategory = {
  key: string;
  label: string;
  tone: "sun" | "blue" | "olive" | "violet" | "coral" | "teal";
  matches: (board: PlayerLeaderboard) => boolean;
};

const TEAM_METRIC_PRIORITY = [
  "goals_for",
  "goals",
  "shots_on_target",
  "shots",
  "corners",
  "fouls",
  "cards",
  "possession",
  "tackles",
];

const PLAYER_CATEGORIES: PlayerCategory[] = [
  { key: "shooting", label: "Shooting", tone: "sun", matches: (board) => /shot|target|goal/i.test(`${board.key} ${board.label}`) && !/against|conced/i.test(`${board.key} ${board.label}`) },
  { key: "creation", label: "Creation", tone: "blue", matches: (board) => /assist|chance|key.?pass|creation/i.test(`${board.key} ${board.label}`) },
  { key: "defending", label: "Defending", tone: "olive", matches: (board) => /tackle|interception|clearance|block|duel|recover/i.test(`${board.key} ${board.label}`) },
  { key: "fouls", label: "Fouls", tone: "violet", matches: (board) => /foul|drawn|won/i.test(`${board.key} ${board.label}`) },
  { key: "discipline", label: "Cards", tone: "coral", matches: (board) => /card|yellow|red|booking/i.test(`${board.key} ${board.label}`) },
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
  const text = `${metric.key} ${metric.label}`.toLowerCase();
  if (/shot|goal|attack/.test(text)) return "coral";
  if (/corner|set.?piece/.test(text)) return "sun";
  if (/foul|card|yellow|red/.test(text)) return "violet";
  if (/tackle|interception|clearance|defen|duel/.test(text)) return "olive";
  if (/pass|possession|chance|assist|creation/.test(text)) return "blue";
  return "teal";
}

function sharedTeamMetrics(home: TeamSide, away: TeamSide) {
  const awayByKey = new Map(away.metrics.map((metric) => [metric.key, metric]));
  return home.metrics
    .map((homeMetric) => ({ home: homeMetric, away: awayByKey.get(homeMetric.key) }))
    .filter((pair): pair is { home: Metric; away: Metric } => Boolean(pair.away))
    .sort((a, b) => {
      const aText = `${a.home.key} ${a.home.label}`.toLowerCase();
      const bText = `${b.home.key} ${b.home.label}`.toLowerCase();
      const aIndex = TEAM_METRIC_PRIORITY.findIndex((key) => aText.includes(key));
      const bIndex = TEAM_METRIC_PRIORITY.findIndex((key) => bText.includes(key));
      return (aIndex === -1 ? 99 : aIndex) - (bIndex === -1 ? 99 : bIndex);
    });
}

function recentSummary(matches: RecentMatch[]) {
  const recent = matches.slice(0, 5);
  const wins = recent.filter((match) => match.result === "W").length;
  const draws = recent.filter((match) => match.result === "D").length;
  const losses = recent.filter((match) => match.result === "L").length;
  const goalsFor = recent.reduce((sum, match) => sum + match.goals_for, 0);
  const goalsAgainst = recent.reduce((sum, match) => sum + match.goals_against, 0);
  return { recent, wins, draws, losses, goalsFor, goalsAgainst };
}

function availablePlayerCategories(home: PlayerSide, away: PlayerSide) {
  const allBoards = [...home.leaderboards, ...away.leaderboards];
  const matched = PLAYER_CATEGORIES.filter((category) => allBoards.some(category.matches));
  return matched.length ? matched : [{ key: "leaders", label: "Leaders", tone: "teal" as const, matches: (_board: PlayerLeaderboard) => true }];
}

function pairedBoards(home: PlayerSide, away: PlayerSide, category: PlayerCategory) {
  const awayByKey = new Map(away.leaderboards.filter(category.matches).map((board) => [board.key, board]));
  return home.leaderboards
    .filter(category.matches)
    .map((homeBoard) => ({ home: homeBoard, away: awayByKey.get(homeBoard.key) }))
    .filter((pair): pair is { home: PlayerLeaderboard; away: PlayerLeaderboard } => Boolean(pair.away))
    .slice(0, 3);
}

function RecentTeam({ side, tone }: { side: TeamSide; tone: "home" | "away" }) {
  const summary = recentSummary(side.matches);
  return (
    <section className={styles.recentTeam} data-side={tone}>
      <header className={styles.recentTeamHeader}>
        <div className={styles.recentIdentity}>
          <span className={styles.miniKit}><TeamKit teamName={side.team_name} /></span>
          <div><strong>{side.team_name}</strong><FormStrip results={side.form.slice(0, 5)} /></div>
        </div>
        <div className={styles.recentRecord}>
          <strong>{summary.wins}-{summary.draws}-{summary.losses}</strong>
          <span>W-D-L</span>
        </div>
        <div className={styles.recentGoals}>
          <strong>{summary.goalsFor}-{summary.goalsAgainst}</strong>
          <span>goals</span>
        </div>
      </header>

      <div className={styles.matchRows}>
        {summary.recent.map((match) => (
          <Link href={`/fixtures/${match.season}/${match.fixture_id}`} key={`${match.season}-${match.fixture_id}`} className={styles.matchRow}>
            <span className={styles.resultBadge} data-result={match.result}>{match.result}</span>
            <strong>{match.opponent}</strong>
            <small>{match.venue === "Home" ? "H" : "A"}</small>
            <b>{match.goals_for}-{match.goals_against}</b>
          </Link>
        ))}
        {!summary.recent.length && <span className={styles.empty}>No completed matches before kickoff.</span>}
      </div>
    </section>
  );
}

function CompactMetricRow({ home, away }: { home: Metric; away: Metric }) {
  const tone = metricTone(home);
  const max = Math.max(Math.abs(home.value ?? 0), Math.abs(away.value ?? 0), 1);
  const homeWidth = home.value == null ? 0 : Math.max(6, Math.min(100, Math.abs(home.value) / max * 100));
  const awayWidth = away.value == null ? 0 : Math.max(6, Math.min(100, Math.abs(away.value) / max * 100));
  return (
    <div className={styles.metricRow} data-tone={tone}>
      <strong>{metricValue(home)}</strong>
      <div className={styles.metricTrackHome}><i style={{ width: `${homeWidth}%` }} /></div>
      <span>{home.label}</span>
      <div className={styles.metricTrackAway}><i style={{ width: `${awayWidth}%` }} /></div>
      <strong>{metricValue(away)}</strong>
    </div>
  );
}

function PlayerBoardPair({ home, away, tone }: { home: PlayerLeaderboard; away: PlayerLeaderboard; tone: PlayerCategory["tone"] }) {
  return (
    <article className={styles.playerBoard} data-tone={tone}>
      <header>{home.label}</header>
      <div className={styles.playerBoardColumns}>
        <div>
          {home.players.slice(0, 3).map((player) => (
            <div className={styles.playerLine} key={`${home.key}-${player.player_code}`}>
              <span><b>{player.player_name}</b><small>{player.position || "—"}</small></span>
              <strong>{playerValue(home, player)}</strong>
            </div>
          ))}
        </div>
        <div className={styles.playerAway}>
          {away.players.slice(0, 3).map((player) => (
            <div className={styles.playerLine} key={`${away.key}-${player.player_code}`}>
              <strong>{playerValue(away, player)}</strong>
              <span><b>{player.player_name}</b><small>{player.position || "—"}</small></span>
            </div>
          ))}
        </div>
      </div>
    </article>
  );
}

export function MatchdayDeskV5({ pack, fixtureOptions }: Props) {
  const data = pack as unknown as MatchdayPack;
  const fixtures = fixtureOptions as unknown as FixtureOption[];
  const [view, setView] = useState<DeskView>("last5");
  const [evidenceOpen, setEvidenceOpen] = useState(false);

  const teamMetrics = useMemo(() => sharedTeamMetrics(data.teams.home, data.teams.away), [data.teams.home, data.teams.away]);
  const categories = useMemo(() => availablePlayerCategories(data.players.home, data.players.away), [data.players.home, data.players.away]);
  const [playerCategoryKey, setPlayerCategoryKey] = useState(categories[0]?.key ?? "leaders");
  const activeCategory = categories.find((category) => category.key === playerCategoryKey) ?? categories[0];
  const playerBoards = activeCategory ? pairedBoards(data.players.home, data.players.away, activeCategory) : [];
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
          <small>Premier League · {data.fixture.gameweek ? `GW ${data.fixture.gameweek}` : data.fixture.season}</small>
        </div>
        <div className={`${styles.fixtureTeam} ${styles.fixtureTeamAway}`}>
          <span className={styles.heroKit}><TeamKit teamName={data.fixture.away_team_name} /></span>
          <strong>{data.fixture.away_team_name}</strong>
        </div>
      </header>

      <nav className={styles.viewNav} aria-label="Matchday evidence views">
        <button type="button" data-active={view === "last5"} onClick={() => setView("last5")}>Last 5</button>
        <button type="button" data-active={view === "teams"} onClick={() => setView("teams")}>Team numbers</button>
        <button type="button" data-active={view === "players"} onClick={() => setView("players")}>Player leaders</button>
        <Link href={h2hHref}>H2H ↗</Link>
        <button type="button" data-active={view === "probabilities"} onClick={() => setView("probabilities")}>Probabilities</button>
      </nav>

      <main className={styles.deskPanel}>
        {view === "last5" && (
          <div className={styles.lastFiveView}>
            <div className={styles.panelHeading}>
              <div><span>FORM AT KICKOFF</span><h2>What happened in the last five</h2></div>
              <small>Most recent completed fixtures before this match</small>
            </div>
            <div className={styles.lastFiveLayout}>
              <div className={styles.recentPair}>
                <RecentTeam side={data.teams.home} tone="home" />
                <RecentTeam side={data.teams.away} tone="away" />
              </div>
              <aside className={styles.quickNumbers}>
                <header><span>RECENT NUMBERS</span><strong>Across the same window</strong></header>
                <div className={styles.metricRows}>
                  {teamMetrics.slice(0, 5).map(({ home, away }) => <CompactMetricRow key={home.key} home={home} away={away} />)}
                </div>
              </aside>
            </div>
          </div>
        )}

        {view === "teams" && (
          <div className={styles.teamNumbersView}>
            <div className={styles.panelHeading}>
              <div><span>TEAM EVIDENCE</span><h2>Recent team numbers</h2></div>
              <small>{data.teams.home.team_name} vs {data.teams.away.team_name}</small>
            </div>
            <div className={styles.teamIdentityRow}>
              <div><span className={styles.miniKit}><TeamKit teamName={data.teams.home.team_name} /></span><strong>{data.teams.home.team_name}</strong><FormStrip results={data.teams.home.form.slice(0, 5)} /></div>
              <span>RECENT WINDOW</span>
              <div><FormStrip results={data.teams.away.form.slice(0, 5)} /><strong>{data.teams.away.team_name}</strong><span className={styles.miniKit}><TeamKit teamName={data.teams.away.team_name} /></span></div>
            </div>
            <div className={styles.fullMetricRows}>
              {teamMetrics.slice(0, 9).map(({ home, away }) => <CompactMetricRow key={home.key} home={home} away={away} />)}
            </div>
          </div>
        )}

        {view === "players" && (
          <div className={styles.playersView}>
            <div className={styles.panelHeading}>
              <div><span>PLAYER EVIDENCE</span><h2>Recent player leaders</h2></div>
              <small>Choose a stat family</small>
            </div>
            <div className={styles.categoryTabs}>
              {categories.map((category) => (
                <button type="button" key={category.key} data-active={activeCategory?.key === category.key} data-tone={category.tone} onClick={() => setPlayerCategoryKey(category.key)}>{category.label}</button>
              ))}
            </div>
            <div className={styles.playerTeamHead}>
              <strong>{data.players.home.team_name}</strong><span>{activeCategory?.label ?? "Players"}</span><strong>{data.players.away.team_name}</strong>
            </div>
            <div className={styles.playerBoards}>
              {playerBoards.length ? playerBoards.map(({ home, away }) => <PlayerBoardPair key={home.key} home={home} away={away} tone={activeCategory?.tone ?? "teal"} />) : <p className={styles.empty}>No directly comparable player leaderboard is available in this category yet.</p>}
            </div>
          </div>
        )}

        {view === "probabilities" && (
          <div className={styles.probabilityView}>
            <div className={styles.panelHeading}>
              <div><span>MODEL OUTPUT</span><h2>Match probabilities</h2></div>
              <button type="button" onClick={() => setEvidenceOpen(true)}>How FRL calculated this →</button>
            </div>
            {data.prediction.status === "AVAILABLE" ? (
              <div className={styles.probabilityGrid}>
                <article data-tone="coral"><span>{data.fixture.home_team_name}</span><strong>{probability(probabilities.home_win)}</strong></article>
                <article data-tone="sun"><span>Draw</span><strong>{probability(probabilities.draw)}</strong></article>
                <article data-tone="olive"><span>{data.fixture.away_team_name}</span><strong>{probability(probabilities.away_win)}</strong></article>
                {probabilities.over_2_5 != null && <article data-tone="blue"><span>Over 2.5</span><strong>{probability(probabilities.over_2_5)}</strong></article>}
                {probabilities.btts != null && <article data-tone="violet"><span>BTTS</span><strong>{probability(probabilities.btts)}</strong></article>}
              </div>
            ) : <p className={styles.empty}>{data.prediction.reason ?? "No match probabilities are available for this fixture."}</p>}
          </div>
        )}
      </main>

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
