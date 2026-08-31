import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { PlayerRankingsControls } from "./PlayerRankingsControls";
import { PlayerRankingsOverview } from "./PlayerRankingsOverview";
import { PlayerRankingsFamilyTable } from "./PlayerRankingsFamilyTable";
import type { RankingMetric } from "../PlayerVisuals";
import styles from "../PlayerStats.module.css";

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
  GKP: [
    "saves_per_90",
    "clean_sheets_per_90",
    "goals_conceded_per_90",
    "xgc_per_90",
    "penalties_saved",
    "bps_per_90",
  ],
  DEF: [
    "goals_per_90",
    "assists_per_90",
    "xgi_per_90",
    "tackles_per_90",
    "recoveries_per_90",
    "defensive_contribution_per_90",
    "cbi_per_90",
    "clean_sheets_per_90",
  ],
  MID: [
    "goals_per_90",
    "assists_per_90",
    "xg_per_90",
    "xa_per_90",
    "xgi_per_90",
    "key_passes_per_90",
    "tackles_per_90",
    "recoveries_per_90",
  ],
  FWD: [
    "goals_per_90",
    "assists_per_90",
    "xg_per_90",
    "xa_per_90",
    "xgi_per_90",
    "key_passes_per_90",
    "big_chances_created_per_90",
    "dribbles_per_90",
  ],
};

const POSITIONS = new Set(["GKP", "DEF", "MID", "FWD"]);
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

function familyHref(season: string, position: string, family: FamilyKey) {
  const params = new URLSearchParams({ season, position, family });
  return `/player-stats/rankings?${params.toString()}`;
}

export default async function PlayerRankingsPage({
  searchParams,
}: {
  searchParams: Promise<{
    season?: string;
    position?: string;
    family?: string;
  }>;
}) {
  const query = await searchParams;
  const seasonResponse = await getJson<SeasonResponse>("/api/v1/seasons");
  const seasons = seasonResponse?.seasons ?? [];
  const season =
    query.season && seasons.includes(query.season)
      ? query.season
      : seasons[0];
  const position =
    query.position && POSITIONS.has(query.position.toUpperCase())
      ? query.position.toUpperCase()
      : "FWD";

  const rankings = season
    ? await getJson<PlayerRankingsResult>(
        `/api/v1/player-stats/${encodeURIComponent(
          season
        )}/rankings/${encodeURIComponent(position)}`
      )
    : null;

  const availableFamilies = FAMILY_ORDER.filter((family) => {
    if (!rankings) return false;
    if (family === "overview") {
      return (OVERVIEW_KEYS[position] ?? []).some((key) =>
        rankings.metrics.some((metric) => metric.key === key)
      );
    }
    return rankings.metrics.some((metric) => metric.family === family);
  });

  const requestedFamily = query.family as FamilyKey | undefined;
  const family =
    requestedFamily && availableFamilies.includes(requestedFamily)
      ? requestedFamily
      : availableFamilies[0] ?? "overview";

  const familyMetrics = rankings
    ? family === "overview"
      ? (OVERVIEW_KEYS[position] ?? [])
          .map((key) => rankings.metrics.find((metric) => metric.key === key))
          .filter((metric): metric is RankingMetric => Boolean(metric))
      : rankings.metrics.filter((metric) => metric.family === family)
    : [];

  const isOverview = family === "overview";

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

        {rankings && (isOverview || familyMetrics.length > 0) ? (
          <main className={styles.workspace}>
            {isOverview ? (
              <PlayerRankingsOverview
                season={season ?? ""}
                position={position}
                metrics={rankings.metrics}
                cohortDescription={rankings.cohort.description}
              />
            ) : (
              <PlayerRankingsFamilyTable
                key={`${season}-${position}-${family}`}
                season={season ?? ""}
                familyLabel={FAMILY_LABELS[family]}
                position={position}
                metrics={familyMetrics}
                cohortDescription={rankings.cohort.description}
              />
            )}
          </main>
        ) : (
          <div className="frl-empty-state">
            No governed ranking metric is available for this selection.
          </div>
        )}
      </div>
    </AppShell>
  );
}
