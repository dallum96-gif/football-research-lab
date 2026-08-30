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

type FamilyKey =
  | "overview"
  | "attack"
  | "possession"
  | "passing"
  | "defence"
  | "discipline";

const API_BASE =
  process.env.NEXT_PUBLIC_FRL_API_URL ??
  "http://127.0.0.1:8000";

const families: { key: FamilyKey; label: string }[] = [
  { key: "overview", label: "Overview" },
  { key: "attack", label: "Attack" },
  { key: "possession", label: "Possession" },
  { key: "passing", label: "Passing" },
  { key: "defence", label: "Defence" },
  { key: "discipline", label: "Discipline" },
];

const familyMetricKeys: Record<FamilyKey, string[]> = {
  overview: [
    "points_per_match",
    "goals_for_per_match",
    "goals_against_per_match",
    "Shots_per_match",
    "Shots on target_per_match",
    "Possession_per_match",
  ],
  attack: [
    "goals_for_per_match",
    "Shots_per_match",
    "Shots on target_per_match",
  ],
  possession: ["Possession_per_match"],
  passing: [],
  defence: ["goals_against_per_match"],
  discipline: [],
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

function rankingsHref(
  season: string,
  family: FamilyKey,
  metric?: string
) {
  const params = new URLSearchParams({ season, family });
  if (metric) {
    params.set("metric", metric);
  }
  return `/team-stats/rankings?${params.toString()}`;
}

function teamHref(season: string, entry: RankingEntry) {
  const params = new URLSearchParams({
    season,
    team: entry.persistent_team_code,
  });
  return `/team-stats?${params.toString()}`;
}

function RankingCard({
  metric,
  season,
}: {
  metric: RankingMetric;
  season: string;
}) {
  const leaders = metric.entries
    .filter((entry) => entry.rank !== null)
    .slice(0, 5);

  return (
    <article className={styles.rankingCard}>
      <header className={styles.cardHeader}>
        <div>
          <span>{metric.label}</span>
          <small>{metric.unit}</small>
        </div>
        <Link href={rankingsHref(season, "overview", metric.key)}>
          Full ranking
        </Link>
      </header>

      <div className={styles.cardLeaders}>
        {leaders.map((entry) => (
          <Link
            key={entry.persistent_team_code}
            href={teamHref(season, entry)}
            className={styles.cardRow}
          >
            <strong className={styles.cardRank}>{entry.rank}</strong>
            <span className={styles.cardKit}>
              <TeamKit teamName={entry.display_name} />
            </span>
            <span className={styles.cardTeam}>{entry.display_name}</span>
            <strong className={styles.cardValue}>
              {formatValue(metric, entry.value)}
            </strong>
          </Link>
        ))}
      </div>

      <footer className={styles.cardFooter}>
        <span>{metric.higher_is_better ? "Higher" : "Lower"} is better</span>
        <span>{metric.entries.length} teams</span>
      </footer>
    </article>
  );
}

function FullRanking({
  metric,
  rankings,
}: {
  metric: RankingMetric;
  rankings: LeagueRankingsResponse;
}) {
  return (
    <section className={styles.tablePanel}>
      <div className={styles.tableHeader}>
        <span>Rank</span>
        <span>Team</span>
        <span>Value</span>
        <span>Percentile</span>
      </div>

      <div className={styles.rows}>
        {metric.entries.map((entry) => (
          <Link
            className={styles.row}
            key={entry.persistent_team_code}
            href={teamHref(rankings.season, entry)}
            aria-label={`Analyse ${entry.display_name}`}
          >
            <strong className={styles.rank}>{ordinal(entry.rank)}</strong>

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
              {formatValue(metric, entry.value)}
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
                <span style={{ width: `${entry.percentile ?? 0}%` }} />
              </div>
              <span>
                {entry.percentile === null
                  ? "—"
                  : `P${Math.round(entry.percentile)}`}
              </span>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}

export default async function TeamStatsRankingsPage({
  searchParams,
}: {
  searchParams: Promise<{
    season?: string;
    family?: string;
    metric?: string;
  }>;
}) {
  const query = await searchParams;
  const seasonResponse = await getJson<SeasonResponse>("/api/v1/seasons");
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

  const requestedFamily = families.find(
    (family) => family.key === query.family
  )?.key;
  const activeFamily: FamilyKey = requestedFamily ?? "overview";
  const activeFamilyLabel =
    families.find((family) => family.key === activeFamily)?.label ??
    "Overview";
  const activeFamilyMetrics = familyMetricKeys[activeFamily]
    .map((key) => rankings?.metrics.find((metric) => metric.key === key))
    .filter((metric): metric is RankingMetric => Boolean(metric));
  const activeMetric =
    activeFamilyMetrics.find((metric) => metric.key === query.metric) ??
    activeFamilyMetrics[0] ??
    null;
  const overviewMetric =
    activeFamily === "overview" && query.metric
      ? rankings?.metrics.find((metric) => metric.key === query.metric) ?? null
      : null;
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
              <p className={teamStyles.eyebrow}>Analysis · Team Stats</p>
              <h1>League Rankings</h1>
              <p className={teamStyles.context}>
                Premier League · {season ?? "Season unavailable"}
                {rankings ? ` · ${rankings.population_size} teams` : ""}
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

        {rankings ? (
          <main className={styles.workspace}>
            <nav
              className={styles.familyNav}
              aria-label="League Rankings sections"
            >
              {families.map((family) => (
                <Link
                  key={family.key}
                  href={rankingsHref(rankings.season, family.key)}
                  className={
                    family.key === activeFamily
                      ? styles.activeFamily
                      : styles.familyLink
                  }
                >
                  {family.label}
                </Link>
              ))}
            </nav>

            {activeFamily === "overview" ? (
              <>
                <section className={styles.familyIntro}>
                  <div>
                    <p className={teamStyles.kicker}>League Rankings</p>
                    <h2>Overview</h2>
                    <p>
                      A compact snapshot of the six governed rankings shared
                      with Team View.
                    </p>
                  </div>
                  <span className={styles.populationBadge}>
                    {rankings.population_size} team population
                  </span>
                </section>

                <section className={styles.familySection}>
                  <div className={styles.cardGrid}>
                    {rankings.metrics.map((metric) => (
                      <RankingCard
                        key={metric.key}
                        metric={metric}
                        season={rankings.season}
                      />
                    ))}
                  </div>
                </section>

                {overviewMetric && (
                  <section className={styles.fullRanking}>
                    <header className={styles.fullRankingHeader}>
                      <div>
                        <p className={teamStyles.kicker}>Full ranking</p>
                        <h2>{overviewMetric.label}</h2>
                        <p>
                          Ranked across the governed {rankings.season} Premier
                          League population. Ties use competition ranking.
                        </p>
                      </div>
                      <Link href={rankingsHref(rankings.season, "overview")}>
                        Close
                      </Link>
                    </header>
                    <FullRanking metric={overviewMetric} rankings={rankings} />
                  </section>
                )}
              </>
            ) : (
              <section className={styles.familyRankingWorkspace}>
                <header className={styles.familyRankingHeader}>
                  <div>
                    <p className={teamStyles.kicker}>League Rankings</p>
                    <h2>{activeFamilyLabel}</h2>
                  </div>
                  <span className={styles.populationBadge}>
                    {rankings.population_size} team population
                  </span>
                </header>

                {activeFamilyMetrics.length > 0 ? (
                  <>
                    <nav
                      className={styles.metricSubheadings}
                      aria-label={`${activeFamilyLabel} ranking metrics`}
                    >
                      {activeFamilyMetrics.map((metric) => (
                        <Link
                          key={metric.key}
                          href={rankingsHref(
                            rankings.season,
                            activeFamily,
                            metric.key
                          )}
                          className={
                            metric.key === activeMetric?.key
                              ? styles.activeMetricSubheading
                              : styles.metricSubheading
                          }
                        >
                          {metric.label}
                        </Link>
                      ))}
                    </nav>

                    {activeMetric && (
                      <>
                        <div className={styles.rankingTitleRow}>
                          <div>
                            <h3>{activeMetric.label}</h3>
                            <p>
                              Full {rankings.season} Premier League ranking.
                            </p>
                          </div>
                          <span>
                            {activeMetric.higher_is_better
                              ? "Higher is better"
                              : "Lower is better"}
                          </span>
                        </div>
                        <FullRanking
                          metric={activeMetric}
                          rankings={rankings}
                        />
                        <footer className={styles.detailMeta}>
                          <span>
                            {representationLabel(activeMetric.representation)}
                          </span>
                          <span>{rankings.ranking_policy}</span>
                        </footer>
                      </>
                    )}
                  </>
                ) : (
                  <div className={styles.unavailableFamily}>
                    <strong>No governed ranking metric here yet.</strong>
                    <span>
                      FRL will populate this family only when the underlying
                      metrics are analytically ready.
                    </span>
                  </div>
                )}
              </section>
            )}

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
