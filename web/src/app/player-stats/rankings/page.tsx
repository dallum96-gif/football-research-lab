import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { AllPlayersRankingsOverview, type PositionRankingData } from "./AllPlayersRankingsOverview";
import { PlayerRankingsControls } from "./PlayerRankingsControls";
import { PlayerRankingsOverview } from "./PlayerRankingsOverview";
import { PlayerRankingsFamilyTable } from "./PlayerRankingsFamilyTable";
import type { RankingMetric } from "../PlayerVisuals";
import styles from "../PlayerStats.module.css";

type SeasonResponse = { seasons: string[] };

type PlayerRankingsResult = Omit<PositionRankingData, "metrics"> & {
  metrics: RankingMetric[];
};

type TeamOption = {
  persistent_team_code: string | null;
  display_name: string;
};

type TeamOverviewResult = {
  persistent_team_code: string;
  display_name: string;
  season: string;
  played: number;
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

const POSITION_VALUES = ["GKP", "DEF", "MID", "FWD"] as const;
const POSITIONS = new Set<string>(POSITION_VALUES);
const POSITION_LABELS: Record<(typeof POSITION_VALUES)[number], string> = {
  GKP: "Goalkeepers",
  DEF: "Defenders",
  MID: "Midfielders",
  FWD: "Forwards",
};
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

async function getPositionRankings(season: string, position: string) {
  return getJson<PlayerRankingsResult>(
    `/api/v1/player-stats/${encodeURIComponent(season)}/rankings/${encodeURIComponent(position)}`
  );
}

async function getPossibleMinutesByClub(season: string) {
  const teams =
    (await getJson<TeamOption[]>(`/api/v1/teams/${encodeURIComponent(season)}`)) ?? [];

  const rows = await Promise.all(
    teams.map(async (team) => {
      if (!team.persistent_team_code) {
        return [team.display_name, 0] as const;
      }

      const overview = await getJson<TeamOverviewResult>(
        `/api/v1/teams/${encodeURIComponent(season)}/${encodeURIComponent(
          team.persistent_team_code
        )}/overview`
      );

      return [team.display_name, Math.max(0, overview?.played ?? 0) * 90] as const;
    })
  );

  return Object.fromEntries(rows) as Record<string, number>;
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

  const requestedPosition = query.position?.toUpperCase();
  const position =
    requestedPosition && POSITIONS.has(requestedPosition)
      ? requestedPosition
      : "ALL";

  const allPlayerData =
    season && position === "ALL"
      ? await Promise.all([
          Promise.all(
            POSITION_VALUES.map(
              async (item) => [item, await getPositionRankings(season, item)] as const
            )
          ),
          getPossibleMinutesByClub(season),
        ])
      : null;

  const rankingsByPosition: Record<string, PositionRankingData | null> =
    Object.fromEntries(allPlayerData?.[0] ?? []);
  const possibleMinutesByClub = allPlayerData?.[1] ?? {};

  const rankings =
    season && position !== "ALL"
      ? await getPositionRankings(season, position)
      : null;

  const availableFamilies: FamilyKey[] = FAMILY_ORDER.filter((family) => {
    if (position === "ALL") {
      return Object.values(rankingsByPosition).some((item) => {
        if (!item) return false;
        if (family === "overview") {
          return (OVERVIEW_KEYS[item.position] ?? []).some((key) =>
            item.metrics.some((metric) => metric.key === key)
          );
        }
        return item.metrics.some((metric) => metric.family === family);
      });
    }

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

  const familyPossibleMinutesByClub =
    season && position !== "ALL" && family !== "overview"
      ? await getPossibleMinutesByClub(season)
      : {};

  const isOverview = family === "overview";
  const hasAllPlayerData =
    position === "ALL" &&
    Object.values(rankingsByPosition).some((item) => item?.metrics.length);
  const familyPositions =
    position === "ALL" && !isOverview
      ? POSITION_VALUES.flatMap((item) => {
          const positionRankings = rankingsByPosition[item];
          if (!positionRankings) return [];
          const metricCount = positionRankings.metrics.filter(
            (metric) => metric.family === family
          ).length;
          return metricCount > 0
            ? [{ position: item, rankings: positionRankings, metricCount }]
            : [];
        })
      : [];

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
                Premier League · {season ?? "Season unavailable"} · {position === "ALL" ? "All Players" : position}
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

        {position === "ALL" && isOverview && hasAllPlayerData ? (
          <main className={styles.workspace}>
            <AllPlayersRankingsOverview
              season={season ?? ""}
              rankingsByPosition={rankingsByPosition}
              possibleMinutesByClub={possibleMinutesByClub}
            />
          </main>
        ) : position === "ALL" && familyPositions.length > 0 ? (
          <main className={styles.workspace}>
            <section className={styles.familyPositionChooser}>
              <header>
                <div>
                  <p className={styles.kicker}>League Rankings · {FAMILY_LABELS[family]}</p>
                  <h2>Choose the comparison population</h2>
                </div>
                <p>
                  Player rankings remain position-specific so unlike roles are not
                  presented as one comparable league table.
                </p>
              </header>

              <div className={styles.familyPositionGrid}>
                {familyPositions.map(
                  ({ position: item, rankings: itemRankings, metricCount }) => (
                    <Link
                      key={item}
                      href={familyHref(season ?? "", item, family)}
                      className={styles.familyPositionCard}
                    >
                      <span>{item}</span>
                      <strong>{POSITION_LABELS[item]}</strong>
                      <small>
                        {itemRankings.population_size} players · {metricCount}{" "}
                        governed {metricCount === 1 ? "metric" : "metrics"}
                      </small>
                      <b>Open {FAMILY_LABELS[family]} rankings →</b>
                    </Link>
                  )
                )}
              </div>

              <footer>
                Select a position here to open its governed comparison population.
                The family selection is preserved in the analytical table.
              </footer>
            </section>
          </main>
        ) : rankings && (isOverview || familyMetrics.length > 0) ? (
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
                possibleMinutesByClub={familyPossibleMinutesByClub}
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
