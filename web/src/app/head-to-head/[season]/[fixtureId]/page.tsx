import Link from "next/link";
import { notFound } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { TeamKit } from "@/app/teams/TeamKit";
import styles from "./HeadToHead.module.css";

const API_BASE = (process.env.NEXT_PUBLIC_FRL_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

type RateSummary = {
  hits: number;
  observed_matches: number;
  eligible_matches: number;
  hit_rate: number | null;
  coverage_status: string;
};

type BetBuilderEntry = {
  id: string;
  side: "home" | "away";
  team_name: string;
  opponent_name: string;
  market_label: string;
  evidence_label: string;
  evidence_index: number | null;
  team_recent: RateSummary;
  opponent_allowance: RateSummary;
};

type Metric = {
  key: string;
  label: string;
  unit: string;
  value: number | null;
  observed_matches: number;
  eligible_matches: number;
};

type TeamProfile = {
  team_name: string;
  persistent_team_code: string;
  sample_size: number;
  current_season_sample_size: number;
  form: Array<"W" | "D" | "L">;
  points: number;
  metrics: Metric[];
};

type PlayerRow = {
  rank: number;
  player_code: string;
  player_name: string;
  position: string;
  appearances: number;
  minutes: number;
  value: number;
};

type Leaderboard = {
  key: string;
  label: string;
  unit: string;
  players: PlayerRow[];
};

type PlayerSide = {
  team_name: string;
  player_count: number;
  fixture_evidence_count: number;
  leaderboards: Leaderboard[];
};

type H2HPack = {
  pack_version: string;
  fixture: {
    season: string;
    fixture_id: string;
    gameweek: number | null;
    kickoff_time: string | null;
    home_team_name: string;
    away_team_name: string;
  };
  forecast: {
    status: string;
    model?: string;
    control_status?: string;
    training_fixtures?: number;
    expected_goals?: { home: number; away: number };
    probabilities?: Record<string, number>;
    correct_scores?: Array<{ home: number; away: number; probability: number }>;
  };
  profiles: { home: TeamProfile; away: TeamProfile };
  players: { home: PlayerSide; away: PlayerSide };
  betbuilder: {
    status: string;
    threshold_policy: string;
    index_definition: string;
    entries: BetBuilderEntry[];
  };
  data_maturity?: {
    status: string;
    note: string;
  };
  limitations: string[];
};

type PageProps = { params: Promise<{ season: string; fixtureId: string }> };

export const dynamic = "force-dynamic";

async function getPack(season: string, fixtureId: string): Promise<H2HPack | null> {
  try {
    const response = await fetch(
      `${API_BASE}/api/v1/head-to-head/${encodeURIComponent(season)}/${encodeURIComponent(fixtureId)}`,
      { cache: "no-store" },
    );
    if (response.status === 404) return null;
    if (!response.ok) throw new Error(`FRL API request failed: ${response.status}`);
    return await response.json() as H2HPack;
  } catch {
    return null;
  }
}

function pct(value: number | null | undefined) {
  return value == null ? "—" : `${(value * 100).toFixed(0)}%`;
}

function decimal(value: number | null | undefined) {
  return value == null ? "—" : value.toFixed(2);
}

function metricValue(metric: Metric) {
  if (metric.value == null) return "—";
  return metric.value.toFixed(Math.abs(metric.value) >= 10 ? 1 : 2);
}

function fixtureDate(value: string | null) {
  if (!value) return "Kickoff TBC";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Kickoff TBC";
  return date.toLocaleString("en-GB", {
    timeZone: "Europe/London",
    weekday: "short",
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function RateLine({ label, summary }: { label: string; summary: RateSummary }) {
  const width = summary.hit_rate == null ? 0 : Math.max(0, Math.min(100, summary.hit_rate * 100));
  return (
    <div className={styles.evidenceLine}>
      <span>{label}</span>
      <div className={styles.track} aria-hidden="true">
        <div className={styles.fill} style={{ width: `${width}%` }} />
      </div>
      <b>{pct(summary.hit_rate)}</b>
    </div>
  );
}

function EvidenceCard({ entry }: { entry: BetBuilderEntry }) {
  return (
    <article className={styles.evidenceCard} data-evidence={entry.evidence_label}>
      <div className={styles.evidenceTitle}>
        <div>
          <small>{entry.team_name} · fixed V1 threshold</small>
          <strong>{entry.market_label}</strong>
        </div>
        <span className={styles.badge}>{entry.evidence_label}</span>
      </div>
      <div className={styles.evidenceBars}>
        <RateLine label={`${entry.team_name} recent`} summary={entry.team_recent} />
        <RateLine label={`${entry.opponent_name} allowed`} summary={entry.opponent_allowance} />
      </div>
      <div className={styles.evidenceMeta}>
        <span>Evidence index {pct(entry.evidence_index)} · descriptive, not probability</span>
        <span>{entry.team_recent.observed_matches}+{entry.opponent_allowance.observed_matches} observed samples</span>
      </div>
    </article>
  );
}

function ProfileCard({ side, season }: { side: TeamProfile; season: string }) {
  return (
    <article className={styles.profile}>
      <div className={styles.profileHead}>
        <div>
          <small>Recent analytical profile · up to {side.sample_size}</small>
          <h3>{side.team_name}</h3>
        </div>
        <Link className={styles.profileLink} href={`/teams/${season}/${encodeURIComponent(side.persistent_team_code)}`}>
          Full profile ↗
        </Link>
      </div>
      <div className={styles.form} aria-label={`${side.team_name} recent form`}>
        {side.form.map((result, index) => <span key={`${result}-${index}`} data-result={result}>{result}</span>)}
      </div>
      <div className={styles.metricGrid}>
        {side.metrics.map((metric) => (
          <div className={styles.metric} key={metric.key}>
            <span title={metric.label}>{metric.label}</span>
            <strong>{metricValue(metric)}</strong>
            <small>{metric.observed_matches}/{metric.eligible_matches} observed</small>
          </div>
        ))}
      </div>
    </article>
  );
}

function PlayerWatchlist({ side }: { side: PlayerSide }) {
  const keys = new Set(["xg", "goals", "cards", "tackles"]);
  const boards = side.leaderboards.filter((board) => keys.has(board.key));
  return (
    <article className={styles.playerCard}>
      <h3>{side.team_name}</h3>
      {boards.map((board) => (
        <div className={styles.playerGroup} key={board.key}>
          <span>{board.label}</span>
          {board.players.slice(0, 3).map((player) => (
            <div className={styles.playerRow} key={`${board.key}-${player.player_code}-${player.rank}`}>
              <strong>{player.player_name}</strong>
              <small>{player.appearances} apps · {Math.round(player.minutes)} min</small>
              <b>{player.value.toFixed(player.value % 1 === 0 ? 0 : 2)}</b>
            </div>
          ))}
          {!board.players.length && <div className={styles.muted}>No observed evidence yet.</div>}
        </div>
      ))}
    </article>
  );
}

export default async function HeadToHeadPage({ params }: PageProps) {
  const { season, fixtureId } = await params;
  const data = await getPack(season, fixtureId);
  if (!data) notFound();

  const probs = data.forecast.probabilities ?? {};
  const homeEntries = data.betbuilder.entries.filter((entry) => entry.side === "home");
  const awayEntries = data.betbuilder.entries.filter((entry) => entry.side === "away");
  const scores = data.forecast.correct_scores ?? [];

  return (
    <AppShell>
      <div className={styles.page}>
        <section className={styles.hero}>
          <div className={styles.heroTop}>
            <div>
              <span className={styles.kicker}>Head-to-Head Intelligence · {data.pack_version}</span>
              <small>Premier League · {season}{data.fixture.gameweek ? ` · GW ${data.fixture.gameweek}` : ""} · {fixtureDate(data.fixture.kickoff_time)}</small>
            </div>
            <div className={styles.heroActions}>
              <Link className={styles.action} href={`/matchday/${season}/${fixtureId}`}>Matchday workspace</Link>
              <Link className={styles.action} href={`/fixtures/${season}/${fixtureId}`}>Fixture evidence</Link>
            </div>
          </div>

          <div className={styles.fixture}>
            <div className={styles.team}>
              <div className={styles.kit}><TeamKit teamName={data.fixture.home_team_name} /></div>
              <strong>{data.fixture.home_team_name}</strong>
            </div>
            <div className={styles.vs}>VERSUS</div>
            <div className={styles.team}>
              <div className={styles.kit}><TeamKit teamName={data.fixture.away_team_name} /></div>
              <strong>{data.fixture.away_team_name}</strong>
            </div>
          </div>

          {data.forecast.status === "AVAILABLE" ? (
            <div className={styles.forecast}>
              <article><span>{data.fixture.home_team_name}</span><strong>{pct(probs.home_win)}</strong></article>
              <article><span>Draw</span><strong>{pct(probs.draw)}</strong></article>
              <article><span>{data.fixture.away_team_name}</span><strong>{pct(probs.away_win)}</strong></article>
            </div>
          ) : <div className={styles.notice}>Adaptive DC forecast is unavailable for this fixture.</div>}
          <div className={styles.heroFooter}>
            {data.forecast.model ?? "Adaptive control"} · λ {decimal(data.forecast.expected_goals?.home)}–{decimal(data.forecast.expected_goals?.away)} · frozen experimental control · trained only on completed fixtures before kickoff
          </div>
        </section>

        {data.data_maturity?.status === "EARLY_SEASON" && (
          <div className={styles.notice}><strong>Early-season evidence:</strong> {data.data_maturity.note}</div>
        )}

        <section className={styles.section}>
          <div className={styles.sectionHeading}>
            <div><span className={styles.kicker}>Heart of the page</span><h2>BetBuilder Stat Pack</h2></div>
            <p>Two-sided evidence, not picks. Each leg pairs recent team hit frequency with the opponent&apos;s recent allowance frequency on a fixed threshold.</p>
          </div>
          <div className={styles.betGrid}>
            {[...homeEntries, ...awayEntries].map((entry) => <EvidenceCard key={entry.id} entry={entry} />)}
          </div>
        </section>

        <section className={styles.section}>
          <div className={styles.sectionHeading}>
            <div><span className={styles.kicker}>Profiles collide</span><h2>Analytical matchup</h2></div>
            <p>The same governed recent evidence viewed as two team profiles. This is the bridge into the deeper Team Scouting workspace.</p>
          </div>
          <div className={styles.profileGrid}>
            <ProfileCard side={data.profiles.home} season={season} />
            <ProfileCard side={data.profiles.away} season={season} />
          </div>
        </section>

        <section className={styles.section}>
          <div className={styles.sectionHeading}>
            <div><span className={styles.kicker}>Independent forecast evidence</span><h2>Model picture</h2></div>
            <p>Adaptive DC stays separate from the stat pack so model probabilities cannot magically turn descriptive hit rates into betting probabilities.</p>
          </div>
          <div className={styles.marketPanel}>
            <article className={styles.marketCard}>
              <h3>Match markets</h3>
              <div className={styles.marketRows}>
                <div className={styles.marketRow}><span>Home win</span><b>{pct(probs.home_win)}</b></div>
                <div className={styles.marketRow}><span>Draw</span><b>{pct(probs.draw)}</b></div>
                <div className={styles.marketRow}><span>Away win</span><b>{pct(probs.away_win)}</b></div>
                <div className={styles.marketRow}><span>Over 2.5 goals</span><b>{pct(probs.over_2_5)}</b></div>
                <div className={styles.marketRow}><span>Both teams to score</span><b>{pct(probs.btts)}</b></div>
              </div>
            </article>
            <article className={styles.scoreCard}>
              <h3>Most likely exact scores</h3>
              <div className={styles.scores}>
                {scores.map((score) => (
                  <div className={styles.score} key={`${score.home}-${score.away}`}>
                    <strong>{score.home}–{score.away}</strong><span>{pct(score.probability)}</span>
                  </div>
                ))}
              </div>
            </article>
          </div>
        </section>

        <section className={styles.section}>
          <div className={styles.sectionHeading}>
            <div><span className={styles.kicker}>Player evidence</span><h2>Watchlists</h2></div>
            <p>Current-season player evidence only in V1. Thin samples stay visible rather than being silently bulked out with incompatible history.</p>
          </div>
          <div className={styles.playerGrid}>
            <PlayerWatchlist side={data.players.home} />
            <PlayerWatchlist side={data.players.away} />
          </div>
        </section>

        <div className={styles.notice}>
          <strong>Research boundary.</strong> {data.betbuilder.index_definition} Fouls-drawn/fouls-committed and referee-adjusted card modelling remain deliberately withheld until governed.
        </div>
      </div>
    </AppShell>
  );
}
