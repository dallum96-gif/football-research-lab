import { AppShell } from "@/components/AppShell";
import { PlayerRankingsControls } from "./PlayerRankingsControls";
import { PlayerRankingsTable } from "./PlayerRankingsTable";
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

export default async function PlayerRankingsPage({
  searchParams,
}: {
  searchParams: Promise<{ season?: string; position?: string }>;
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
              family="overview"
            />
          )}
        </header>

        <nav className={styles.tabs} aria-label="Player ranking workspace">
          <span className={styles.activeTab}>League table</span>
        </nav>

        {rankings ? (
          <main className={styles.workspace}>
            <PlayerRankingsTable
              season={season ?? ""}
              metrics={rankings.metrics}
              overviewKeys={OVERVIEW_KEYS[position] ?? []}
              cohortDescription={rankings.cohort.description}
            />
          </main>
        ) : (
          <div className="frl-empty-state">
            No governed player ranking population is available for this selection.
          </div>
        )}
      </div>
    </AppShell>
  );
}
