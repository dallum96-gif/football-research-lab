import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { PlayerStatsControls } from "./PlayerStatsControls";
import { PlayerStatsLanding } from "./PlayerStatsLanding";
import {
  AverageDonuts,
  CohortDistributions,
  PercentileFingerprint,
  type RankingMetric,
} from "./PlayerVisuals";
import styles from "./PlayerStats.module.css";
import performanceStyles from "./PlayerStatsPerformance.module.css";

type SeasonResponse = { seasons: string[] };

type PlayerOption = {
  player_code: string;
  player_name: string;
  position: string;
  clubs: string[];
  minutes: number;
  appearances: number;
  starts: number;
};

type PlayerStatsMetric = {
  key: string;
  label: string;
  unit: string;
  family: string;
  higher_is_better: boolean;
  representation: string;
  value: number | null;
  rank: number | null;
  out_of: number;
  percentile: number | null;
  availability: string;
  observed_players: number;
  eligible_players: number;
};

type PlayerStatsResult = {
  analysis_version: string;
  season: string;
  player: PlayerOption;
  cohort: {
    competition: string;
    season: string;
    position: string;
    minimum_minutes: number;
    description: string;
  };
  overview_keys: string[];
  metrics: PlayerStatsMetric[];
  limitations: string[];
};

type PlayerRankingsResult = {
  analysis_version: string;
  season: string;
  position: string;
  population_size: number;
  cohort: PlayerStatsResult["cohort"];
  ranking_policy: string;
  percentile_policy: string;
  metrics: RankingMetric[];
};

type FamilyKey =
  | "overview"
  | "shooting"
  | "creation"
  | "possession"
  | "defending"
  | "discipline"
  | "goalkeeping"
  | "fpl";

const FAMILY_LABELS: Record<FamilyKey, string> = {
  overview: "Overview",
  shooting: "Shooting",
  creation: "Creation",
  possession: "Possession",
  defending: "Defending",
  discipline: "Discipline",
  goalkeeping: "Goalkeeping",
  fpl: "FPL",
};

const FAMILY_ORDER: FamilyKey[] = [
  "overview",
  "shooting",
  "creation",
  "possession",
  "defending",
  "discipline",
  "goalkeeping",
  "fpl",
];

const POSITION_VALUES = ["GKP", "DEF", "MID", "FWD"] as const;
const API_BASE =
  process.env.NEXT_PUBLIC_FRL_API_URL ?? "http://127.0.0.1:8000";

async function getJson<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

function initials(name: string) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("") || "P";
}

function ordinal(value: number) {
  const mod100 = value % 100;
  if (mod100 >= 11 && mod100 <= 13) return `${value}th`;
  const suffix =
    value % 10 === 1 ? "st" : value % 10 === 2 ? "nd" : value % 10 === 3 ? "rd" : "th";
  return `${value}${suffix}`;
}

function trim(value: number, decimals: number) {
  const fixed = value.toFixed(decimals);
  return fixed.includes(".") ? fixed.replace(/0+$/, "").replace(/\.$/, "") : fixed;
}

function formatMetric(metric: RankingMetric, value: number | null) {
  if (value == null) return "—";
  if (Number.isInteger(value)) return String(value);
  if (metric.unit === "%") return `${trim(value, 1)}%`;
  if (metric.unit === "xG" || metric.unit === "xA" || metric.unit === "xGI" || metric.unit === "xGC") {
    return trim(value, 2);
  }
  return trim(value, 2);
}

function statsHref(season: string, player: string, family: FamilyKey) {
  const params = new URLSearchParams({ season, player });
  if (family !== "overview") params.set("family", family);
  return `/player-stats?${params.toString()}`;
}

async function getPositionRankings(season: string, position: string) {
  return getJson<PlayerRankingsResult>(
    `/api/v1/player-stats/${encodeURIComponent(season)}/rankings/${encodeURIComponent(position)}`
  );
}

export default async function PlayerStatsPage({
  searchParams,
}: {
  searchParams: Promise<{ season?: string; player?: string; family?: string }>;
}) {
  const query = await searchParams;
  const seasonResponse = await getJson<SeasonResponse>("/api/v1/seasons");
  const seasons = seasonResponse?.seasons ?? [];
  const season =
    query.season && seasons.includes(query.season) ? query.season : seasons[0];

  const players = season
    ? (await getJson<PlayerOption[]>(`/api/v1/players/${encodeURIComponent(season)}`)) ?? []
    : [];
  const eligiblePlayers = players.filter((player) => player.minutes > 0);
  const playerCode =
    query.player && eligiblePlayers.some((player) => player.player_code === query.player)
      ? query.player
      : undefined;

  const landingRankings =
    season && !playerCode
      ? Object.fromEntries(
          await Promise.all(
            POSITION_VALUES.map(async (position) => [
              position,
              await getPositionRankings(season, position),
            ] as const)
          )
        ) as Record<string, PlayerRankingsResult | null>
      : {};

  const stats = season && playerCode
    ? await getJson<PlayerStatsResult>(
        `/api/v1/player-stats/${encodeURIComponent(season)}/${encodeURIComponent(playerCode)}`
      )
    : null;

  const rankings = stats
    ? await getPositionRankings(season ?? "", stats.player.position)
    : null;

  const availableFamilies = FAMILY_ORDER.filter((family) => {
    if (!rankings) return family === "overview";
    if (family === "overview") {
      return stats?.overview_keys.some((key) => rankings.metrics.some((metric) => metric.key === key));
    }
    return rankings.metrics.some((metric) => metric.family === family);
  });

  const requestedFamily = query.family as FamilyKey | undefined;
  const activeFamily =
    requestedFamily && availableFamilies.includes(requestedFamily)
      ? requestedFamily
      : availableFamilies[0] ?? "overview";

  const familyMetrics = rankings
    ? activeFamily === "overview"
      ? stats?.overview_keys
          .map((key) => rankings.metrics.find((metric) => metric.key === key))
          .filter((metric): metric is RankingMetric => Boolean(metric)) ?? []
      : rankings.metrics.filter((metric) => metric.family === activeFamily)
    : [];

  const selectedPlayer = stats?.player ?? null;

  return (
    <AppShell>
      <div className={styles.page}>
        <header className={styles.profileHeader}>
          <div className={styles.identity}>
            <span className={styles.avatar}>
              {selectedPlayer ? initials(selectedPlayer.player_name) : "PS"}
            </span>
            <div>
              <p className={styles.eyebrow}>Analysis · Player Stats</p>
              <h1>{selectedPlayer?.player_name ?? "Player Stats"}</h1>
              <p className={styles.context}>
                {selectedPlayer?.clubs.join(" · ") || "Premier League"}
                {selectedPlayer ? ` · ${selectedPlayer.position}` : ""}
                {season ? ` · ${season}` : ""}
              </p>
            </div>
          </div>

          {season && (
            <PlayerStatsControls
              seasons={seasons}
              players={eligiblePlayers}
              currentSeason={season}
              currentFamily={activeFamily}
              position={selectedPlayer?.position ?? "ALL"}
            />
          )}
        </header>

        {selectedPlayer && playerCode && (
          <nav className={styles.tabs} aria-label="Player Stats sections">
            {availableFamilies.map((family) => (
              <Link
                key={family}
                href={statsHref(season ?? "", playerCode, family)}
                className={family === activeFamily ? styles.activeTab : styles.tab}
              >
                {FAMILY_LABELS[family]}
              </Link>
            ))}
          </nav>
        )}

        {!playerCode && season ? (
          <PlayerStatsLanding
            season={season}
            players={eligiblePlayers}
            rankingsByPosition={landingRankings}
          />
        ) : stats && rankings && selectedPlayer && playerCode ? (
          <main className={styles.workspace}>
            <section className={styles.summaryStrip}>
              <div><strong>{selectedPlayer.appearances}</strong><span>Appearances</span></div>
              <div><strong>{selectedPlayer.starts}</strong><span>Starts</span></div>
              <div><strong>{selectedPlayer.minutes}</strong><span>Minutes</span></div>
              <div><strong>{rankings.population_size}</strong><span>{selectedPlayer.position} cohort</span></div>
              <Link
                href={`/players/${encodeURIComponent(season ?? "")}/${encodeURIComponent(playerCode)}`}
              >
                Player profile →
              </Link>
            </section>

            <section className={styles.metricGrid}>
              {familyMetrics.map((metric) => {
                const entry = metric.entries.find(
                  (candidate) => candidate.player_code === playerCode
                );
                return (
                  <article className={styles.metricCard} key={metric.key}>
                    <div className={styles.metricTop}>
                      <span>{metric.label}</span>
                      <small>
                        {entry?.rank != null ? `${ordinal(entry.rank)} / ${entry.out_of}` : "Unavailable"}
                      </small>
                    </div>
                    <strong>{formatMetric(metric, entry?.value ?? null)}</strong>
                    <div className={`${styles.percentileTrack} ${performanceStyles.performanceTrack}`}>
                      <span style={{ left: `${entry?.percentile ?? 0}%` }} />
                    </div>
                    <footer>
                      <span>{entry?.percentile != null ? `P${Math.round(entry.percentile)}` : "—"}</span>
                      <span>{metric.higher_is_better ? "Higher ranks first" : "Lower ranks first"}</span>
                    </footer>
                  </article>
                );
              })}
            </section>

            <section className={styles.visualGrid}>
              <PercentileFingerprint metrics={familyMetrics} playerCode={playerCode} />
              <AverageDonuts metrics={familyMetrics} playerCode={playerCode} />
            </section>

            <CohortDistributions metrics={familyMetrics} playerCode={playerCode} />

            <section className={styles.percentilePanel}>
              <header className={styles.sectionHeading}>
                <div>
                  <p className={styles.kicker}>FBref-style read</p>
                  <h2>{FAMILY_LABELS[activeFamily]} percentile profile</h2>
                </div>
                <span>{stats.cohort.description}</span>
              </header>

              <div className={styles.profileRows}>
                {familyMetrics.map((metric) => {
                  const entry = metric.entries.find(
                    (candidate) => candidate.player_code === playerCode
                  );
                  return (
                    <div className={styles.profileRow} key={metric.key}>
                      <div className={styles.profileMetric}>
                        <span>{metric.label}</span>
                        <strong>{formatMetric(metric, entry?.value ?? null)}</strong>
                      </div>
                      <div className={`${styles.profileBar} ${performanceStyles.performanceTrack} ${performanceStyles.profilePerformanceTrack}`}>
                        <span style={{ left: `${entry?.percentile ?? 0}%` }} />
                        <i style={{ left: `${entry?.percentile ?? 0}%` }} />
                      </div>
                      <div className={styles.profileRank}>
                        <strong>{entry?.percentile != null ? `P${Math.round(entry.percentile)}` : "—"}</strong>
                        <span>{entry?.rank != null ? `${ordinal(entry.rank)} of ${entry.out_of}` : "unranked"}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>

            <section className={styles.methodPanel}>
              <div>
                <p className={styles.kicker}>Comparison population</p>
                <strong>{stats.cohort.description}</strong>
              </div>
              <p>
                V1 keeps the minimum at one recorded minute so early-season analysis remains possible. The cohort is explicit; a stronger minutes threshold can be added as a user control later without changing the metric definitions.
              </p>
            </section>
          </main>
        ) : (
          <div className="frl-empty-state">
            No governed Player Stats population is available for this season.
          </div>
        )}
      </div>
    </AppShell>
  );
}
