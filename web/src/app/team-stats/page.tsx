import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { TeamKit } from "../teams/TeamKit";
import { TeamStatsControls } from "./TeamStatsControls";
import {
  TeamStatsOverviewWorkspace,
  type TeamStatsOverview,
} from "./TeamStatsOverviewWorkspace";
import styles from "./TeamStats.module.css";

type TeamOption = {
  persistent_team_code: string | null;
  display_name: string;
  season: string;
  local_team_id: string;
};

type SeasonResponse = {
  seasons: string[];
};

type RankingCoverage = {
  eligible_matches: number;
  observed_matches: number;
  missing_matches: number;
  coverage_status: string;
};

type RankingEntry = {
  persistent_team_code: string;
  display_name: string;
  local_team_id: string;
  value: number | null;
  rank: number | null;
  out_of: number;
  percentile: number | null;
  coverage: RankingCoverage;
};

type RankingMetric = {
  key: string;
  label: string;
  unit: string;
  higher_is_better: boolean;
  representation: string;
  ranking_policy: string;
  percentile_policy: string;
  entries: RankingEntry[];
};

type LeagueRankingsResponse = {
  analysis_version: string;
  season: string;
  population_size: number;
  ranking_policy: string;
  percentile_policy: string;
  metrics: RankingMetric[];
};

type FamilyKey =
  | "overview"
  | "attack"
  | "passing"
  | "defence"
  | "discipline";

type AnalyticalFamily = Exclude<FamilyKey, "overview">;

const API_BASE =
  process.env.NEXT_PUBLIC_FRL_API_URL ??
  "http://127.0.0.1:8000";

const tabs: { key: FamilyKey; label: string }[] = [
  { key: "overview", label: "Overview" },
  { key: "attack", label: "Attack" },
  { key: "passing", label: "Passing" },
  { key: "defence", label: "Defence" },
  { key: "discipline", label: "Discipline" },
];

const FAMILY_CONFIG: Record<
  AnalyticalFamily,
  {
    label: string;
    metricKeys: string[];
    description: string;
  }
> = {
  attack: {
    label: "Attack",
    metricKeys: [
      "goals_for_per_match",
      "Shots_per_match",
      "Shots on target_per_match",
      "Corners_per_match",
    ],
    description:
      "Goals and attacking volume from the shared governed Team Stats analysis.",
  },
  passing: {
    label: "Passing",
    metricKeys: [
      "Possession_per_match",
      "Passes_per_match",
      "Accurate passes_per_match",
      "Crosses_per_match",
    ],
    description:
      "Possession and passing-volume measures. Possession lives here rather than as a separate analytical family.",
  },
  defence: {
    label: "Defence",
    metricKeys: [
      "goals_against_per_match",
      "Tackles_per_match",
      "Interceptions_per_match",
      "Clearances_per_match",
    ],
    description:
      "Defensive outcomes and action volume, kept distinct so high action counts are not automatically interpreted as better defending.",
  },
  discipline: {
    label: "Discipline",
    metricKeys: [
      "Fouls conceded_per_match",
      "Yellow cards_per_match",
      "Red cards_per_match",
    ],
    description:
      "Fouls and card rates, ranked with lower values first.",
  },
};

async function getJson<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      cache: "no-store",
    });

    if (!response.ok) {
      return null;
    }

    return (await response.json()) as T;
  } catch {
    return null;
  }
}

function formatRankingMetric(metric: RankingMetric, value: number | null) {
  if (value === null) {
    return "—";
  }

  if (metric.unit === "%") {
    return `${value.toFixed(1)}%`;
  }

  if (
    metric.key === "points_per_match" ||
    metric.key.includes("goals")
  ) {
    return value.toFixed(2);
  }

  return value.toFixed(1);
}

function ordinal(value: number) {
  const mod100 = value % 100;

  if (mod100 >= 11 && mod100 <= 13) {
    return `${value}th`;
  }

  const suffix =
    value % 10 === 1
      ? "st"
      : value % 10 === 2
        ? "nd"
        : value % 10 === 3
          ? "rd"
          : "th";

  return `${value}${suffix}`;
}

function teamStatsHref(
  season: string,
  team: string,
  family: FamilyKey
) {
  const params = new URLSearchParams({ season, team });
  if (family !== "overview") {
    params.set("family", family);
  }
  return `/team-stats?${params.toString()}`;
}

function rankingsHref(season: string, family: AnalyticalFamily) {
  const params = new URLSearchParams({ season, family });
  return `/team-stats/rankings?${params.toString()}`;
}

function FamilyWorkspace({
  overview,
  rankings,
  teamCode,
  family,
}: {
  overview: TeamStatsOverview;
  rankings: LeagueRankingsResponse | null;
  teamCode: string;
  family: AnalyticalFamily;
}) {
  const config = FAMILY_CONFIG[family];
  const metrics = config.metricKeys
    .map((key) => rankings?.metrics.find((metric) => metric.key === key))
    .filter((metric): metric is RankingMetric => Boolean(metric));

  const availableMetrics = metrics.filter((metric) => {
    const entry = metric.entries.find(
      (candidate) => candidate.persistent_team_code === teamCode
    );
    return entry?.value !== null && entry?.value !== undefined;
  });

  return (
    <main className={styles.workspace}>
      <section className={styles.secondaryPanel}>
        <header className={styles.sectionHeading}>
          <div>
            <p className={styles.kicker}>Analytical family</p>
            <h2>{config.label}</h2>
          </div>
          <Link
            className={styles.kicker}
            style={{ textDecoration: "none" }}
            href={rankingsHref(overview.season, family)}
          >
            League rankings →
          </Link>
        </header>
        <p className={styles.context}>
          {config.description} Missing current-season observations remain
          unavailable rather than becoming zero.
        </p>
      </section>

      <section className={styles.metricGrid}>
        {metrics.map((metric) => {
          const entry = metric.entries.find(
            (candidate) => candidate.persistent_team_code === teamCode
          );
          const available =
            entry?.value !== null &&
            entry?.value !== undefined &&
            entry.rank !== null &&
            entry.percentile !== null;

          return (
            <article className={styles.metricCard} key={metric.key}>
              <div className={styles.metricTop}>
                <span>{metric.label}</span>
                <small>
                  {available && entry?.rank !== null
                    ? `${ordinal(entry.rank)} / ${entry.out_of}`
                    : "Unavailable"}
                </small>
              </div>

              <strong>
                {entry ? formatRankingMetric(metric, entry.value) : "—"}
              </strong>

              <div
                className={styles.percentileTrack}
                aria-label={
                  available && entry?.percentile !== null
                    ? `${entry.percentile} percentile`
                    : `${metric.label} unavailable for this season`
                }
              >
                <span
                  style={{
                    width:
                      available && entry?.percentile !== null
                        ? `${entry.percentile}%`
                        : "0%",
                  }}
                />
              </div>

              <footer>
                <span>
                  {available && entry?.percentile !== null
                    ? `P${Math.round(entry.percentile)}`
                    : `${entry?.coverage.observed_matches ?? 0}/${entry?.coverage.eligible_matches ?? overview.matches}`}
                </span>
                <span>
                  {available
                    ? metric.higher_is_better
                      ? "Higher values rank first"
                      : "Lower values rank first"
                    : "No governed observation"}
                </span>
              </footer>
            </article>
          );
        })}
      </section>

      {metrics.length === 0 && (
        <div className={styles.empty}>
          {config.label} analysis is unavailable for this selection.
        </div>
      )}

      <section className={styles.bottomGrid}>
        <article className={styles.readPanel}>
          <p className={styles.kicker}>What this view means</p>
          <div className={styles.readItems}>
            <div>
              <span>Grain</span>
              <strong>Team · season</strong>
              <p>Fixture observations aggregated through the governed kernel.</p>
            </div>
            <div>
              <span>Comparison</span>
              <strong>Premier League</strong>
              <p>
                Ranks and percentiles use the same eligible population as
                League Rankings.
              </p>
            </div>
          </div>
        </article>

        <article className={styles.secondaryPanel}>
          <p className={styles.kicker}>Current boundary</p>
          <div className={styles.secondaryGrid}>
            <div>
              <span>Observed metrics</span>
              <strong>
                {availableMetrics.length}/{metrics.length}
              </strong>
            </div>
            <div>
              <span>Matches</span>
              <strong>{overview.matches}</strong>
            </div>
            <div>
              <span>League population</span>
              <strong>{rankings?.population_size ?? "—"}</strong>
            </div>
            <div>
              <span>New data</span>
              <strong>None</strong>
            </div>
          </div>
          <footer>
            Family views project the existing governed analysis; they do not
            create substitute observations for missing source evidence.
          </footer>
        </article>
      </section>
    </main>
  );
}

export default async function TeamStatsPage({
  searchParams,
}: {
  searchParams: Promise<{
    season?: string;
    team?: string;
    family?: string;
  }>;
}) {
  const query = await searchParams;
  const activeFamily =
    tabs.find((tab) => tab.key === query.family)?.key ?? "overview";

  const seasonResponse = await getJson<SeasonResponse>("/api/v1/seasons");
  const seasons = seasonResponse?.seasons ?? [];

  const season =
    query.season && seasons.includes(query.season)
      ? query.season
      : seasons[0];

  const teams = season
    ? (await getJson<TeamOption[]>(
        `/api/v1/teams/${encodeURIComponent(season)}`
      )) ?? []
    : [];

  const governedTeams = teams.filter(
    (
      team
    ): team is TeamOption & {
      persistent_team_code: string;
    } => Boolean(team.persistent_team_code)
  );

  const requestedTeam =
    query.team &&
    governedTeams.some(
      (team) => team.persistent_team_code === query.team
    )
      ? query.team
      : governedTeams[0]?.persistent_team_code;

  const selectedTeam = governedTeams.find(
    (team) => team.persistent_team_code === requestedTeam
  );

  const overview =
    season && requestedTeam
      ? await getJson<TeamStatsOverview>(
          `/api/v1/team-stats/${encodeURIComponent(
            season
          )}/${encodeURIComponent(requestedTeam)}/overview`
        )
      : null;

  const rankings =
    activeFamily !== "overview" && season
      ? await getJson<LeagueRankingsResponse>(
          `/api/v1/team-stats/${encodeURIComponent(season)}/rankings`
        )
      : null;

  return (
    <AppShell>
      <div className={styles.page}>
        <header className={styles.profileHeader}>
          <div className={styles.identity}>
            <div className={styles.kit}>
              {selectedTeam ? (
                <TeamKit teamName={selectedTeam.display_name} />
              ) : (
                <span className={styles.placeholder}>TS</span>
              )}
            </div>

            <div>
              <p className={styles.eyebrow}>Analysis · Team Stats</p>
              <h1>{selectedTeam?.display_name ?? "Team Stats"}</h1>
              <p className={styles.context}>
                Premier League · {season ?? "Season unavailable"}
                {overview ? ` · ${overview.matches} matches` : ""}
              </p>
            </div>
          </div>

          {season && requestedTeam && (
            <TeamStatsControls
              seasons={seasons}
              teams={teams}
              currentSeason={season}
              currentTeam={requestedTeam}
              currentFamily={activeFamily}
            />
          )}
        </header>

        <nav className={styles.tabs} aria-label="Team Stats sections">
          {tabs.map((tab) => {
            if (!season || !requestedTeam) {
              return (
                <span key={tab.key} className={styles.futureTab}>
                  {tab.label}
                </span>
              );
            }

            return (
              <span
                key={tab.key}
                className={
                  tab.key === activeFamily
                    ? styles.activeTab
                    : styles.futureTab
                }
              >
                <Link
                  href={teamStatsHref(season, requestedTeam, tab.key)}
                  style={{
                    color: "inherit",
                    textDecoration: "none",
                    display: "inline-flex",
                    alignItems: "center",
                    height: "100%",
                  }}
                >
                  {tab.label}
                </Link>
              </span>
            );
          })}
        </nav>

        {overview ? (
          activeFamily === "overview" ? (
            <TeamStatsOverviewWorkspace overview={overview} />
          ) : requestedTeam ? (
            <FamilyWorkspace
              overview={overview}
              rankings={rankings}
              teamCode={requestedTeam}
              family={activeFamily}
            />
          ) : null
        ) : (
          <div className={styles.empty}>
            Team Stats data is unavailable for this selection.
          </div>
        )}
      </div>
    </AppShell>
  );
}
