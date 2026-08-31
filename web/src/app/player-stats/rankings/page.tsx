import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { PlayerRankingsControls } from "./PlayerRankingsControls";
import type { RankingMetric } from "../PlayerVisuals";
import styles from "../PlayerStats.module.css";
import rankingStyles from "./PlayerRankings.module.css";

type SeasonResponse = { seasons: string[] };

type PlayerRankingsResult = {
  analysis_version: string;
  season: string;
  position: string;
  population_size: number;
  cohort: {
    competition: string;
    season: string;
    position: string;
    minimum_minutes: number;
    description: string;
  };
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

const OVERVIEW_KEYS: Record<string, string[]> = {
  GKP: ["saves_per_90", "clean_sheets_per_90", "goals_conceded_per_90", "xgc_per_90", "penalties_saved", "bps_per_90"],
  DEF: ["goals_per_90", "assists_per_90", "xgi_per_90", "tackles_per_90", "recoveries_per_90", "defensive_contribution_per_90", "cbi_per_90", "clean_sheets_per_90"],
  MID: ["goals_per_90", "assists_per_90", "xg_per_90", "xa_per_90", "xgi_per_90", "key_passes_per_90", "tackles_per_90", "recoveries_per_90"],
  FWD: ["goals_per_90", "assists_per_90", "xg_per_90", "xa_per_90", "xgi_per_90", "key_passes_per_90", "big_chances_created_per_90", "dribbles_per_90"],
};

const POSITIONS = new Set(["GKP", "DEF", "MID", "FWD"]);
const API_BASE = process.env.NEXT_PUBLIC_FRL_API_URL ?? "http://127.0.0.1:8000";

async function getJson<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

function trim(value: number, decimals: number) {
  const fixed = value.toFixed(decimals);
  return fixed.includes(".") ? fixed.replace(/0+$/, "").replace(/\.$/, "") : fixed;
}

function formatMetric(metric: RankingMetric, value: number | null) {
  if (value == null) return "—";
  if (Number.isInteger(value)) return String(value);
  if (metric.unit === "%") return `${trim(value, 1)}%`;
  if (["xG", "xA", "xGI", "xGC"].includes(metric.unit)) return trim(value, 2);
  return trim(value, 2);
}

function familyHref(season: string, position: string, family: FamilyKey) {
  const params = new URLSearchParams({ season, position, family });
  return `/player-stats/rankings?${params.toString()}`;
}

function metricHref(season: string, position: string, family: FamilyKey, metric: string) {
  const params = new URLSearchParams({ season, position, family, metric });
  return `/player-stats/rankings?${params.toString()}`;
}

export default async function PlayerRankingsPage({
  searchParams,
}: {
  searchParams: Promise<{ season?: string; position?: string; family?: string; metric?: string }>;
}) {
  const query = await searchParams;
  const seasonResponse = await getJson<SeasonResponse>("/api/v1/seasons");
  const seasons = seasonResponse?.seasons ?? [];
  const season = query.season && seasons.includes(query.season) ? query.season : seasons[0];
  const position = query.position && POSITIONS.has(query.position.toUpperCase())
    ? query.position.toUpperCase()
    : "FWD";

  const rankings = season
    ? await getJson<PlayerRankingsResult>(
        `/api/v1/player-stats/${encodeURIComponent(season)}/rankings/${encodeURIComponent(position)}`
      )
    : null;

  const availableFamilies = FAMILY_ORDER.filter((family) => {
    if (!rankings) return false;
    if (family === "overview") {
      return (OVERVIEW_KEYS[position] ?? []).some((key) => rankings.metrics.some((metric) => metric.key === key));
    }
    return rankings.metrics.some((metric) => metric.family === family);
  });

  const requestedFamily = query.family as FamilyKey | undefined;
  const family = requestedFamily && availableFamilies.includes(requestedFamily)
    ? requestedFamily
    : availableFamilies[0] ?? "overview";

  const familyMetrics = rankings
    ? family === "overview"
      ? (OVERVIEW_KEYS[position] ?? [])
          .map((key) => rankings.metrics.find((metric) => metric.key === key))
          .filter((metric): metric is RankingMetric => Boolean(metric))
      : rankings.metrics.filter((metric) => metric.family === family)
    : [];

  const metric =
    familyMetrics.find((candidate) => candidate.key === query.metric) ?? familyMetrics[0] ?? null;

  return (
    <AppShell>
      <div className={styles.page}>
        <header className={styles.profileHeader}>
          <div className={styles.identity}>
            <span className={styles.avatar}>PR</span>
            <div>
              <p className={styles.eyebrow}>Analysis · Player Stats</p>
              <h1>League Rankings</h1>
              <p className={styles.context}>
                Premier League · {season ?? "Season unavailable"} · {position}
              </p>
            </div>
          </div>

          {season && (
            <PlayerRankingsControls
              seasons={seasons}
              currentSeason={season}
              position={position}
              family={family}
            />
          )}
        </header>

        <nav className={styles.tabs} aria-label="Player ranking families">
          {availableFamilies.map((item) => (
            <Link
              key={item}
              href={familyHref(season ?? "", position, item)}
              className={item === family ? styles.activeTab : styles.tab}
            >
              {FAMILY_LABELS[item]}
            </Link>
          ))}
        </nav>

        {rankings && metric ? (
          <main className={styles.workspace}>
            <section className={rankingStyles.rankingMetricNav}>
              <div>
                <p className={styles.kicker}>Metric</p>
                <h2>{metric.label}</h2>
              </div>
              <div className={rankingStyles.metricPills}>
                {familyMetrics.map((candidate) => (
                  <Link
                    key={candidate.key}
                    href={metricHref(season ?? "", position, family, candidate.key)}
                    data-active={candidate.key === metric.key ? "true" : "false"}
                  >
                    {candidate.label}
                  </Link>
                ))}
              </div>
            </section>

            <section className={rankingStyles.rankingPanel}>
              <header className={styles.sectionHeading}>
                <div>
                  <p className={styles.kicker}>{FAMILY_LABELS[family]}</p>
                  <h2>{metric.label} · {position}</h2>
                </div>
                <span>{rankings.cohort.description}</span>
              </header>

              <div className={rankingStyles.rankingTable}>
                <div className={rankingStyles.rankingHeader}>
                  <span>Rank</span><span>Player</span><span>Club</span><span>Minutes</span><span>Value</span><span>Percentile</span>
                </div>
                {metric.entries
                  .filter((entry) => entry.value != null)
                  .map((entry) => (
                    <div className={rankingStyles.rankingRow} key={entry.player_code}>
                      <strong>{entry.rank ?? "—"}</strong>
                      <Link
                        href={`/player-stats?season=${encodeURIComponent(
                          season ?? ""
                        )}&player=${encodeURIComponent(entry.player_code)}&family=${encodeURIComponent(family)}`}
                      >
                        {entry.player_name}
                      </Link>
                      <span>{entry.clubs.join(" · ") || "—"}</span>
                      <span>{entry.minutes}</span>
                      <strong>{formatMetric(metric, entry.value)}</strong>
                      <span className={rankingStyles.rankPercentile}>
                        <i><b style={{ width: `${entry.percentile ?? 0}%` }} /></i>
                        P{Math.round(entry.percentile ?? 0)}
                      </span>
                    </div>
                  ))}
              </div>
            </section>

            <section className={styles.methodPanel}>
              <div>
                <p className={styles.kicker}>Population</p>
                <strong>{rankings.population_size} {position} players</strong>
              </div>
              <p>
                Rankings use the same governed metric definition and same-position cohort as Player View. Players with zero recorded minutes remain available in Profiles but are not ranked.
              </p>
            </section>
          </main>
        ) : (
          <div className="frl-empty-state">No governed ranking metric is available for this selection.</div>
        )}
      </div>
    </AppShell>
  );
}
