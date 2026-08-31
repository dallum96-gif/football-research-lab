import styles from "./TeamStats.module.css";

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

export function TeamStatsOverviewWorkspace({
  overview,
}: {
  overview: TeamStatsOverview;
}) {
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
  const seasonAvailableMetrics = overview.availability.filter(
    (availability) =>
      availability.key !== "expected_goals_per_match" &&
      availability.status !== "UNAVAILABLE"
  );
  const hasSecondarySignals =
    overview.pass_accuracy !== null ||
    overview.clean_sheet_rate !== null ||
    overview.failed_to_score_rate !== null ||
    overview.expected_goals_per_match !== null;

  return (
    <main className={styles.workspace}>
      <section className={styles.metricGrid}>
        {seasonAvailableMetrics.map((availability) => {
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
                    : availability.status}
                </small>
              </div>

              <strong>{metric ? formatMetric(metric) : "—"}</strong>

              <div
                className={styles.percentileTrack}
                aria-label={
                  metric
                    ? `${metric.percentile} percentile`
                    : `${availability.label} has partial or review-required coverage`
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
                    : availability.note ?? availability.status}
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

        {hasSecondarySignals && (
          <article className={styles.secondaryPanel}>
            <p className={styles.kicker}>Secondary signals</p>

            <div className={styles.secondaryGrid}>
              {overview.pass_accuracy !== null && (
                <div>
                  <span>Pass accuracy</span>
                  <strong>
                    {(overview.pass_accuracy * 100).toFixed(1)}%
                  </strong>
                </div>
              )}

              {overview.clean_sheet_rate !== null && (
                <div>
                  <span>Clean sheets</span>
                  <strong>
                    {(overview.clean_sheet_rate * 100).toFixed(0)}%
                  </strong>
                </div>
              )}

              {overview.failed_to_score_rate !== null && (
                <div>
                  <span>Failed to score</span>
                  <strong>
                    {(overview.failed_to_score_rate * 100).toFixed(0)}%
                  </strong>
                </div>
              )}

              {overview.expected_goals_per_match !== null && (
                <div>
                  <span>xG / match</span>
                  <strong>
                    {overview.expected_goals_per_match.toFixed(2)}
                  </strong>
                </div>
              )}
            </div>

            <footer>
              Only signals available in the selected season are shown.
            </footer>
          </article>
        )}
      </section>
    </main>
  );
}
