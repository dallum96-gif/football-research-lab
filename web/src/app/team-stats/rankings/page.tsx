import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { TeamKit } from "../../teams/TeamKit";
import { TeamStatsControls } from "../TeamStatsControls";
import teamStyles from "../TeamStats.module.css";
import styles from "./LeagueRankings.module.css";

type TeamOption = {
  persistent_team_code: string | null;
  display_name: string;
  season: string;
  local_team_id: string;
};

type SeasonResponse = {
  seasons: string[];
};

type RankingEntry = {
  persistent_team_code: string;
  display_name: string;
  local_team_id: string;
  value: number | null;
  rank: number | null;
  out_of: number;
  percentile: number | null;
  coverage: Record<string, unknown>;
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

const API_BASE =
  process.env.NEXT_PUBLIC_FRL_API_URL ??
  "http://127.0.0.1:8000";

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

function formatValue(metric: RankingMetric, value: number | null) {
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

function ordinal(value: number | null) {
  if (value === null) {
    return "—";
  }

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

function representationLabel(value: string) {
  return value
    .toLowerCase()
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export default async function TeamStatsRankingsPage({
  searchParams,
}: {
  searchParams: Promise<{
    season?: string;
    metric?: string;
  }>;
}) {
  const query = await searchParams;
  const seasonResponse =
    await getJson<SeasonResponse>("/api/v1/seasons");
  const seasons = seasonResponse?.seasons ?? [];
  const season =
    query.season && seasons.includes(query.season)
      ? query.season
      : seasons[0];

  const [teams, rankings] = season
    ? await Promise.all([
        getJson<TeamOption[]>(
          `/api/v1/teams/${encodeURIComponent(season)}`
        ),
        getJson<LeagueRankingsResponse>(
          `/api/v1/team-stats/${encodeURIComponent(season)}/rankings`
        ),
      ])
    : [null, null];

  const governedTeams = (teams ?? []).filter(
    (
      team
    ): team is TeamOption & {
      persistent_team_code: string;
    } => Boolean(team.persistent_team_code)
  );

  const selectedMetric =
    rankings?.metrics.find((metric) => metric.key === query.metric) ??
    rankings?.metrics[0] ??
    null;

  const teamViewCode = governedTeams[0]?.persistent_team_code;

  return (
    <AppShell>
      <div className={teamStyles.page}>
        <header className={teamStyles.profileHeader}>
          <div className={teamStyles.identity}>
            <div className={teamStyles.kit}>
              <span className={teamStyles.placeholder}>LR</span>
            </div>

            <div>
              <p className={teamStyles.eyebrow}>
                Analysis · Team Stats
              </p>
              <h1>League Rankings</h1>
              <p className={teamStyles.context}>
                Premier League · {season ?? "Season unavailable"}
                {rankings
                  ? ` · ${rankings.population_size} teams`
                  : ""}
              </p>
            </div>
          </div>

          {season && (
            <TeamStatsControls
              seasons={seasons}
              teams={teams ?? []}
              currentSeason={season}
              currentTeam={teamViewCode}
              currentView="rankings"
            />
          )}
        </header>

        {rankings && selectedMetric ? (
          <main className={styles.workspace}>
            <nav
              className={styles.metricNav}
              aria-label="League ranking metric"
            >
              {rankings.metrics.map((metric) => {
                const params = new URLSearchParams({
                  season: rankings.season,
                  metric: metric.key,
                });

                return (
                  <Link
                    key={metric.key}
                    href={`/team-stats/rankings?${params.toString()}`}
                    className={
                      metric.key === selectedMetric.key
                        ? styles.activeMetric
                        : styles.metricLink
                    }
                  >
                    {metric.label}
                  </Link>
                );
              })}
            </nav>

            <section className={styles.summary}>
              <div>
                <p className={teamStyles.kicker}>League table</p>
                <h2>{selectedMetric.label}</h2>
                <p>
                  Ranked across the governed {rankings.season} Premier
                  League population. Ties use competition ranking.
                </p>
              </div>

              <dl>
                <div>
                  <dt>Population</dt>
                  <dd>{rankings.population_size}</dd>
                </div>
                <div>
                  <dt>Direction</dt>
                  <dd>
                    {selectedMetric.higher_is_better
                      ? "Higher is better"
                      : "Lower is better"}
                  </dd>
                </div>
                <div>
                  <dt>Representation</dt>
                  <dd>
                    {representationLabel(selectedMetric.representation)}
                  </dd>
                </div>
              </dl>
            </section>

            <section className={styles.tablePanel}>
              <div className={styles.tableHeader}>
                <span>Rank</span>
                <span>Team</span>
                <span>Value</span>
                <span>Percentile</span>
              </div>

              <div className={styles.rows}>
                {selectedMetric.entries.map((entry) => {
                  const teamParams = new URLSearchParams({
                    season: rankings.season,
                    team: entry.persistent_team_code,
                  });

                  return (
                    <Link
                      className={styles.row}
                      key={entry.persistent_team_code}
                      href={`/team-stats?${teamParams.toString()}`}
                      aria-label={`Analyse ${entry.display_name}`}
                    >
                      <strong className={styles.rank}>
                        {ordinal(entry.rank)}
                      </strong>

                      <div className={styles.team}>
                        <span className={styles.teamKit}>
                          <TeamKit teamName={entry.display_name} />
                        </span>
                        <div>
                          <strong>{entry.display_name}</strong>
                          <small>{entry.persistent_team_code}</small>
                        </div>
                      </div>

                      <strong className={styles.value}>
                        {formatValue(selectedMetric, entry.value)}
                      </strong>

                      <div className={styles.percentile}>
                        <div
                          className={styles.percentileTrack}
                          aria-label={
                            entry.percentile === null
                              ? "Percentile unavailable"
                              : `${entry.percentile} percentile`
                          }
                        >
                          <span
                            style={{
                              width: `${entry.percentile ?? 0}%`,
                            }}
                          />
                        </div>
                        <span>
                          {entry.percentile === null
                            ? "—"
                            : `P${Math.round(entry.percentile)}`}
                        </span>
                      </div>
                    </Link>
                  );
                })}
              </div>
            </section>

            <footer className={styles.methodNote}>
              <span>{rankings.analysis_version}</span>
              <span>
                Values, ranks and percentiles are supplied by the shared
                Team Stats analytical kernel.
              </span>
            </footer>
          </main>
        ) : (
          <section className={styles.emptyState}>
            <p className={teamStyles.kicker}>League Rankings</p>
            <h2>Ranking data is unavailable.</h2>
            <p>
              FRL could not resolve a governed league population for this
              season.
            </p>
          </section>
        )}
      </div>
    </AppShell>
  );
}
