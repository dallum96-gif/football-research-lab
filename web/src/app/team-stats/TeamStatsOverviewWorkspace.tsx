import Link from "next/link";
import styles from "./TeamStats.module.css";
import refinementStyles from "./TeamStatsRefinement.module.css";

export type Metric = {
  key: string;
  label: string;
  value: number;
  unit: string;
  rank: number;
  out_of: number;
  percentile: number;
  higher_is_better: boolean;
};

export type MetricAvailability = {
  key: string;
  label: string;
  status: "AVAILABLE" | "PARTIAL" | "UNAVAILABLE" | "REVIEW_REQUIRED";
  observed_matches: number;
  eligible_matches: number;
  representation: string;
  note: string | null;
};

export type Split = {
  label: string;
  matches: number;
  points_per_match: number | null;
  goals_for_per_match: number | null;
  goals_against_per_match: number | null;
};

export type TrendPoint = {
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

export type TeamStatsOverview = {
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

const OVERVIEW_KEYS = [
  "goals_for_per_match",
  "Shots on target_per_match",
  "shot_accuracy",
  "pass_accuracy",
  "goals_against_per_match",
  "clean_sheet_rate",
];

const METRIC_FAMILY: Record<string, "attack" | "passing" | "defence"> = {
  goals_for_per_match: "attack",
  "Shots on target_per_match": "attack",
  shot_accuracy: "attack",
  pass_accuracy: "passing",
  goals_against_per_match: "defence",
  clean_sheet_rate: "defence",
};

function trim(value: number, decimals: number) {
  const fixed = value.toFixed(decimals);
  return fixed.includes(".")
    ? fixed.replace(/0+$/, "").replace(/\.$/, "")
    : fixed;
}

function formatMetric(metric: Metric) {
  if (metric.unit === "%") {
    return `${trim(metric.value, 1)}%`;
  }

  if (
    metric.key === "goals_for_per_match" ||
    metric.key === "goals_against_per_match"
  ) {
    return trim(metric.value, 1);
  }

  return trim(metric.value, 0);
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

function topPercent(metric: Metric) {
  return Math.max(1, Math.ceil((metric.rank / metric.out_of) * 100));
}

function percentileLabel(value: number) {
  return `${Math.round(value)}th percentile`;
}

function rankingsHref(overview: TeamStatsOverview, metric: Metric) {
  const params = new URLSearchParams({
    season: overview.season,
    family: METRIC_FAMILY[metric.key] ?? "overview",
    metric: metric.key,
    team: overview.persistent_team_code,
  });
  return `/team-stats/rankings?${params.toString()}`;
}

export function TeamStatsOverviewWorkspace({
  overview,
}: {
  overview: TeamStatsOverview;
}) {
  const overviewMetrics = OVERVIEW_KEYS
    .map((key) => overview.metrics.find((metric) => metric.key === key))
    .filter((metric): metric is Metric => Boolean(metric))
    .sort((a, b) => a.rank - b.rank || b.percentile - a.percentile);

  const strongest = overviewMetrics[0] ?? null;
  const weakest = overviewMetrics[overviewMetrics.length - 1] ?? null;

  const home = overview.splits.find((split) => split.label === "Home");
  const away = overview.splits.find((split) => split.label === "Away");

  return (
    <main className={styles.workspace}>
      <section className={`${styles.metricGrid} ${refinementStyles.overviewMetricGrid}`}>
        {overviewMetrics.map((metric) => (
          <Link
            className={`${styles.metricCard} ${refinementStyles.metricCardLink}`}
            key={metric.key}
            href={rankingsHref(overview, metric)}
            aria-label={`Open ${metric.label} league ranking`}
          >
            <div className={styles.metricTop}>
              <span>{metric.label}</span>
              <small>{ordinal(metric.rank)} / {metric.out_of}</small>
            </div>

            <strong>{formatMetric(metric)}</strong>

            <div
              className={`${styles.percentileTrack} ${refinementStyles.metricPercentileTrack}`}
              aria-label={`${metric.label}: ${percentileLabel(metric.percentile)}`}
            >
              <span style={{ width: `${metric.percentile}%` }} />
            </div>

            <footer className={refinementStyles.metricContext}>
              <span>{percentileLabel(metric.percentile)}</span>
              <span>Top {topPercent(metric)}%</span>
            </footer>
          </Link>
        ))}
      </section>

      <section className={`${styles.analysisGrid} ${refinementStyles.analysisGrid}`}>
        <article className={styles.profilePanel}>
          <header className={styles.sectionHeading}>
            <div>
              <p className={styles.kicker}>League profile</p>
              <h2>Percentile profile</h2>
            </div>
            <span className={styles.profilePopulation}>
              {overview.matches} matches · Premier League
            </span>
          </header>

          {overviewMetrics.length > 0 ? (
            <div className={styles.profileViz}>
              <div className={`${styles.profileScale} ${refinementStyles.profileScale}`} aria-hidden="true">
                <span>Worst</span>
                <span>25</span>
                <span>50</span>
                <span>75</span>
                <span>Best</span>
              </div>

              <div className={styles.profileRows}>
                {overviewMetrics.map((metric) => (
                  <div className={`${styles.profileRow} ${refinementStyles.profileRow}`} key={metric.key}>
                    <div className={styles.profileMetric}>
                      <span>{metric.label}</span>
                      <strong>{formatMetric(metric)}</strong>
                    </div>

                    <div className={styles.profileBarWrap}>
                      <div
                        className={`${styles.profileBar} ${refinementStyles.performanceScale}`}
                        aria-label={`${metric.label}: ${percentileLabel(metric.percentile)}`}
                      >
                        <i className={styles.profileQuarter} style={{ left: "25%" }} />
                        <i className={styles.profileQuarter} style={{ left: "50%" }} />
                        <i className={styles.profileQuarter} style={{ left: "75%" }} />
                        <b
                          className={`${styles.profileMarker} ${refinementStyles.profileMarker}`}
                          style={{ left: `${metric.percentile}%` }}
                        />
                      </div>
                    </div>

                    <div className={`${styles.profileRank} ${refinementStyles.profileRank}`}>
                      <strong>Top {topPercent(metric)}%</strong>
                      <span>{ordinal(metric.rank)} of {metric.out_of}</span>
                      <small>{percentileLabel(metric.percentile)}</small>
                    </div>
                  </div>
                ))}
              </div>

              <footer className={`${styles.profileFooter} ${refinementStyles.profileFooter}`}>
                <span>0 · worst</span>
                <span>League percentile · red → green</span>
                <span>100 · best</span>
              </footer>
            </div>
          ) : (
            <div className={styles.profileEmpty}>
              No rankable governed metrics are available for this season.
            </div>
          )}
        </article>

        <article className={`${styles.venuePanel} ${refinementStyles.compactVenuePanel}`}>
          <header className={styles.sectionHeading}>
            <div>
              <p className={styles.kicker}>Venue split</p>
              <h2>Home / Away</h2>
            </div>
          </header>

          {[home, away].map(
            (split) =>
              split && (
                <div className={`${styles.splitRow} ${refinementStyles.compactSplitRow}`} key={split.label}>
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
                    <strong>{split.goals_for_per_match == null ? "—" : trim(split.goals_for_per_match, 1)}</strong>
                    <span>GF / match</span>
                  </div>

                  <div className={styles.splitStat}>
                    <strong>{split.goals_against_per_match == null ? "—" : trim(split.goals_against_per_match, 1)}</strong>
                    <span>GA / match</span>
                  </div>
                </div>
              )
          )}
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
                  ? `${ordinal(strongest.rank)} of ${strongest.out_of} · ${percentileLabel(strongest.percentile)}.`
                  : "Unavailable."}
              </p>
            </div>

            <div>
              <span>Relative soft spot</span>
              <strong>{weakest?.label ?? "—"}</strong>
              <p>
                {weakest
                  ? `${ordinal(weakest.rank)} of ${weakest.out_of} · ${percentileLabel(weakest.percentile)}.`
                  : "Unavailable."}
              </p>
            </div>
          </div>
        </article>

        <article className={styles.secondaryPanel}>
          <p className={styles.kicker}>Overview logic</p>
          <div className={styles.secondaryGrid}>
            <div>
              <span>Headline metrics</span>
              <strong>{overviewMetrics.length}</strong>
            </div>
            <div>
              <span>League population</span>
              <strong>{overviewMetrics[0]?.out_of ?? "—"}</strong>
            </div>
            <div>
              <span>Best rank</span>
              <strong>{strongest ? ordinal(strongest.rank) : "—"}</strong>
            </div>
            <div>
              <span>Lowest rank</span>
              <strong>{weakest ? ordinal(weakest.rank) : "—"}</strong>
            </div>
          </div>
          <footer>
            Headline tiles are curated for signal variety and ordered by this team’s current league rank.
          </footer>
        </article>
      </section>
    </main>
  );
}
