import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { TeamKit } from "../teams/TeamKit";
import { TeamStatsControls } from "./TeamStatsControls";
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

type Metric = {
  key: string;
  label: string;
  value: number;
  unit: string;
  rank: number;
  out_of: number;
  percentile: number;
  higher_is_better: boolean;
};

type MetricAvailability = {
  key: string;
  label: string;
  status: "AVAILABLE" | "PARTIAL" | "UNAVAILABLE" | "REVIEW_REQUIRED";
  observed_matches: number;
  eligible_matches: number;
  representation: string;
  note: string | null;
};

type Split = {
  label: string;
  matches: number;
  points_per_match: number | null;
  goals_for_per_match: number | null;
  goals_against_per_match: number | null;
};

type TrendPoint = {
  fixture_id: string;
  kickoff_time: string | null;
  home: boolean;
  points: number;
  goals_for: number | null;
  goals_against: number | null;
  shots: number | null;
  shots_on_target: number | null;
  possession: number | null;
};

type TeamStatsOverview = {
  persistent_team_code: string;
  display_name: string;
  season: string;
  matches: number;
  metrics: Metric[];
  pass_accuracy: number | null;
  clean_sheet_rate: number | null;
  failed_to_score_rate: number | null;
  expected_goals_per_match: number | null;
  xg_overperformance: number | null;
  splits: Split[];
  trend: TrendPoint[];
  availability: MetricAvailability[];
  limitations: string[];
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

type FamilyKey = "overview" | "attack";

const API_BASE =
  process.env.NEXT_PUBLIC_FRL_API_URL ??
  "http://127.0.0.1:8000";

const tabs: {
  key: string;
  label: string;
  enabled: boolean;
}[] = [
  { key: "overview", label: "Overview", enabled: true },
  { key: "attack", label: "Attack", enabled: true },
  { key: "passing", label: "Passing", enabled: false },
  { key: "defence", label: "Defence", enabled: false },
  { key: "discipline", label: "Discipline", enabled: false },
];

const ATTACK_METRIC_KEYS = [
  "goals_for_per_match",
  "Shots_per_match",
  "Shots on target_per_match",
  "Corners_per_match",
];

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

function formatMetric(metric: Metric) {
  if (metric.unit === "%") {
    return `${metric.value.toFixed(1)}%`;
  }

  if (
    metric.key === "points_per_match" ||
    metric.key.includes("goals")
  ) {
    return metric.value.toFixed(2);
  }

  return metric.value.toFixed(1);
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

function rollingPpg(points: TrendPoint[]) {
  return points.map((_, index) => {
    const start = Math.max(0, index - 4);
    const window = points.slice(start, index + 1);

    return (
      window.reduce(
        (total, point) => total + point.points,
        0
      ) / window.length
    );
  });
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

function rankingsHref(season: string, family: FamilyKey, metric?: string) {
  const params = new URLSearchParams({ season, family });
  if (metric) {
    params.set("metric", metric);
  }
  return `/team-stats/rankings?${params.toString()}`;
}

function OverviewWorkspace({ overview }: { overview: TeamStatsOverview }) {
  const trend = rollingPpg(overview.trend);
  const trendPoints = trend
    .map((value, index) => {
      const x =
        trend.length <= 1
          ? 0
          : (index / (trend.length - 1)) * 100;
      const y =
        100 -
        Math.min(3, Math.max(0, value)) / 3 * 100;
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");

  const strongest =
    overview.metrics.reduce<Metric | null>(
      (best, metric) =>
        !best || metric.percentile > best.percentile ? metric : best,
      null
    );

  const weakest =
    overview.metrics.reduce<Metric | null>(
      (worst, metric) =>
        !worst || metric.percentile < worst.percentile ? metric : worst,
      null
    );

  const home = overview.splits.find((split) => split.label === "Home");
  const away = overview.splits.find((split) => split.label === "Away");
  const latestRolling = trend.length > 0 ? trend[trend.length - 1] : null;
  const seasonPpg =
    overview.metrics.find((metric) => metric.key === "points_per_match")
      ?.value ?? null;

  return (
    <main className={styles.workspace}>
      <section className={styles.metricGrid}>
        {overview.availability
          .filter(
            (availability) =>
              availability.key !== "expected_goals_per_match"
          )
          .map((availability) => {
            const metric = overview.metrics.find(
              (candidate) => candidate.key === availability.key
            );

            return (
              <article className={styles.metricCard} key={availability.key}>
                <div className={styles.metricTop}>
                  <span>{availability.label}</span>
                  <small>
                    {metric
                      ? `${ordinal(metric.rank)} / ${metric.out_of}`
                      : "Unavailable"}
                  </small>
                </div>

                <strong>{metric ? formatMetric(metric) : "—"}</strong>

                <div
                  className={styles.percentileTrack}
                  aria-label={
                    metric
                      ? `${metric.percentile} percentile`
                      : `${availability.label} unavailable for this season`
                  }
                >
                  <span
                    style={{
                      width: metric ? `${metric.percentile}%` : "0%",
                    }}
                  />
                </div>

                <footer>
                  <span>
                    {metric
                      ? `P${Math.round(metric.percentile)}`
                      : `${availability.observed_matches}/${availability.eligible_matches}`}
                  </span>
                  <span>
                    {metric
                      ? "League percentile"
                      : availability.note ?? "Unavailable for this season"}
                  </span>
                </footer>
              </article>
            );
          })}
      </section>

      <section className={styles.analysisGrid}>
        <article className={styles.trendPanel}>
          <header className={styles.sectionHeading}>
            <div>
              <p className={styles.kicker}>Season pulse</p>
              <h2>Five-match rolling PPG</h2>
            </div>

            <div className={styles.trendReadout}>
              <span>Latest five</span>
              <strong>
                {latestRolling !== null ? latestRolling.toFixed(2) : "—"}
              </strong>
              <small>
                Season {seasonPpg !== null ? seasonPpg.toFixed(2) : "—"}
              </small>
            </div>
          </header>

          <div className={styles.chart}>
            <div className={styles.chartLabels}>
              <span>3.0</span>
              <span>2.0</span>
              <span>1.0</span>
              <span>0.0</span>
            </div>

            <div className={styles.chartCanvas}>
              <i className={styles.gridLine} style={{ top: "0%" }} />
              <i className={styles.gridLine} style={{ top: "33.333%" }} />
              <i className={styles.gridLine} style={{ top: "66.666%" }} />
              <i className={styles.gridLine} style={{ top: "100%" }} />

              <svg
                viewBox="0 0 100 100"
                preserveAspectRatio="none"
                role="img"
                aria-label="Five-match rolling points per game"
              >
                <polyline
                  points={trendPoints}
                  vectorEffect="non-scaling-stroke"
                />
              </svg>
            </div>
          </div>

          <footer className={styles.chartFooter}>
            <span>Season start</span>
            <span>Form moves. Baselines matter.</span>
            <span>Season end</span>
          </footer>
        </article>

        <article className={styles.venuePanel}>
          <header className={styles.sectionHeading}>
            <div>
              <p className={styles.kicker}>Venue split</p>
              <h2>Home / Away</h2>
            </div>
          </header>

          {[home, away].map(
            (split) =>
              split && (
                <div className={styles.splitRow} key={split.label}>
                  <div
                    className={
                      split.label === "Home"
                        ? styles.homeMarker
                        : styles.awayMarker
                    }
                  >
                    {split.label.charAt(0)}
                  </div>

                  <div className={styles.splitName}>
                    <strong>{split.label}</strong>
                    <span>{split.matches} matches</span>
                  </div>

                  <div className={styles.splitStat}>
                    <strong>
                      {split.points_per_match?.toFixed(2) ?? "—"}
                    </strong>
                    <span>PPG</span>
                  </div>

                  <div className={styles.splitStat}>
                    <strong>
                      {split.goals_for_per_match?.toFixed(2) ?? "—"}
                    </strong>
                    <span>GF</span>
                  </div>

                  <div className={styles.splitStat}>
                    <strong>
                      {split.goals_against_per_match?.toFixed(2) ?? "—"}
                    </strong>
                    <span>GA</span>
                  </div>
                </div>
              )
          )}

          <div className={styles.venueNote}>
            {home?.points_per_match != null && away?.points_per_match != null ? (
              <>
                <span>Venue effect</span>
                <strong>
                  {Math.abs(
                    home.points_per_match - away.points_per_match
                  ).toFixed(2)}{" "}
                  PPG
                </strong>
                <p>
                  {home.points_per_match > away.points_per_match
                    ? "Stronger home return."
                    : home.points_per_match < away.points_per_match
                      ? "Stronger away return."
                      : "No PPG difference."}
                </p>
              </>
            ) : (
              <p>Venue comparison unavailable.</p>
            )}
          </div>
        </article>
      </section>

      <section className={styles.bottomGrid}>
        <article className={styles.readPanel}>
          <p className={styles.kicker}>Read the team</p>

          <div className={styles.readItems}>
            <div>
              <span>Strongest signal</span>
              <strong>{strongest?.label ?? "—"}</strong>
              <p>
                {strongest
                  ? `${ordinal(strongest.rank)} of ${strongest.out_of} in the league.`
                  : "Unavailable."}
              </p>
            </div>

            <div>
              <span>Relative soft spot</span>
              <strong>{weakest?.label ?? "—"}</strong>
              <p>
                {weakest
                  ? `${ordinal(weakest.rank)} of ${weakest.out_of} in the league.`
                  : "Unavailable."}
              </p>
            </div>
          </div>
        </article>

        <article className={styles.secondaryPanel}>
          <p className={styles.kicker}>Secondary signals</p>

          <div className={styles.secondaryGrid}>
            <div>
              <span>Pass accuracy</span>
              <strong>
                {overview.pass_accuracy !== null
                  ? `${(overview.pass_accuracy * 100).toFixed(1)}%`
                  : "—"}
              </strong>
            </div>

            <div>
              <span>Clean sheets</span>
              <strong>
                {overview.clean_sheet_rate !== null
                  ? `${(overview.clean_sheet_rate * 100).toFixed(0)}%`
                  : "—"}
              </strong>
            </div>

            <div>
              <span>Failed to score</span>
              <strong>
                {overview.failed_to_score_rate !== null
                  ? `${(overview.failed_to_score_rate * 100).toFixed(0)}%`
                  : "—"}
              </strong>
            </div>

            <div>
              <span>xG / match</span>
              <strong>
                {overview.expected_goals_per_match !== null
                  ? overview.expected_goals_per_match.toFixed(2)
                  : "—"}
              </strong>
            </div>
          </div>

          <footer>League context, not a prediction model.</footer>
        </article>
      </section>
    </main>
  );
}

function AttackWorkspace({
  overview,
  rankings,
  teamCode,
}: {
  overview: TeamStatsOverview;
  rankings: LeagueRankingsResponse | null;
  teamCode: string;
}) {
  const metrics = ATTACK_METRIC_KEYS.map((key) =>
    rankings?.metrics.find((metric) => metric.key === key)
  ).filter((metric): metric is RankingMetric => Boolean(metric));

  return (
    <main className={styles.workspace}>
      <section className={styles.secondaryPanel}>
        <header className={styles.sectionHeading}>
          <div>
            <p className={styles.kicker}>Analytical family</p>
            <h2>Attack</h2>
          </div>
          <Link
            className={styles.kicker}
            style={{ textDecoration: "none" }}
            href={rankingsHref(overview.season, "attack")}
          >
            League rankings →
          </Link>
        </header>
        <p className={styles.context}>
          Goals, shot volume, shots on target and corners from the same governed
          season analysis used by League Rankings. Missing current-season
          observations remain unavailable rather than becoming zero.
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
                    ? "League percentile"
                    : "No governed observation"}
                </span>
              </footer>
            </article>
          );
        })}
      </section>

      {metrics.length === 0 && (
        <div className={styles.empty}>
          Attack analysis is unavailable for this selection.
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
              <p>Ranks and percentiles use the same eligible population as Rankings.</p>
            </div>
          </div>
        </article>

        <article className={styles.secondaryPanel}>
          <p className={styles.kicker}>Current boundary</p>
          <div className={styles.secondaryGrid}>
            <div>
              <span>xG / match</span>
              <strong>
                {overview.expected_goals_per_match !== null
                  ? overview.expected_goals_per_match.toFixed(2)
                  : "—"}
              </strong>
            </div>
            <div>
              <span>Matches</span>
              <strong>{overview.matches}</strong>
            </div>
            <div>
              <span>Family status</span>
              <strong>Governed</strong>
            </div>
            <div>
              <span>New data</span>
              <strong>None</strong>
            </div>
          </div>
          <footer>
            xG remains a separately governed observation and is not silently
            ranked here.
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
  const activeFamily: FamilyKey =
    query.family === "attack" ? "attack" : "overview";

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
    activeFamily === "attack" && season
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
            />
          )}
        </header>

        <nav className={styles.tabs} aria-label="Team Stats sections">
          {tabs.map((tab) => {
            if (!tab.enabled || !season || !requestedTeam) {
              return (
                <span key={tab.key} className={styles.futureTab}>
                  {tab.label}
                </span>
              );
            }

            const family = tab.key as FamilyKey;
            return (
              <span
                key={tab.key}
                className={
                  family === activeFamily
                    ? styles.activeTab
                    : styles.futureTab
                }
              >
                <Link
                  href={teamStatsHref(season, requestedTeam, family)}
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
          activeFamily === "attack" && requestedTeam ? (
            <AttackWorkspace
              overview={overview}
              rankings={rankings}
              teamCode={requestedTeam}
            />
          ) : (
            <OverviewWorkspace overview={overview} />
          )
        ) : (
          <div className={styles.empty}>
            Team Stats data is unavailable for this selection.
          </div>
        )}
      </div>
    </AppShell>
  );
}
