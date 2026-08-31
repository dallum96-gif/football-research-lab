import Link from "next/link";
import type { RankingMetric, RankingEntry } from "../PlayerVisuals";
import rankingStyles from "./PlayerRankings.module.css";
import styles from "../PlayerStats.module.css";

const OVERVIEW_MIN_MINUTES = 60;

const SIGNAL_KEYS_BY_POSITION: Record<string, string[]> = {
  GKP: ["saves", "saves_per_90", "clean_sheets", "xgc_per_90"],
  DEF: ["goals", "assists", "xgi", "tackles_per_90"],
  MID: ["goals", "xg", "xa", "xgi"],
  FWD: ["goals", "xg", "xg_per_90", "xgi"],
};

function trim(value: number, decimals = 2) {
  const fixed = value.toFixed(decimals);
  return fixed.includes(".")
    ? fixed.replace(/0+$/, "").replace(/\.$/, "")
    : fixed;
}

function formatMetric(metric: RankingMetric, value: number | null) {
  if (value == null) return "—";
  if (Number.isInteger(value)) return String(value);
  if (metric.unit === "%") return `${trim(value, 1)}%`;
  return trim(value, 2);
}

function rankingHref(
  season: string,
  position: string,
  metric: RankingMetric
) {
  const params = new URLSearchParams({
    season,
    position,
    family: metric.family,
    metric: metric.key,
  });
  return `/player-stats/rankings?${params.toString()}`;
}

function eligibleEntries(metric: RankingMetric) {
  return metric.entries.filter(
    (entry) => entry.value != null && entry.minutes >= OVERVIEW_MIN_MINUTES
  );
}

function signalLeader(metric: RankingMetric) {
  const entries = eligibleEntries(metric);
  if (!entries.length) return null;

  return [...entries].sort((a, b) => {
    const left = Number(a.value ?? 0);
    const right = Number(b.value ?? 0);
    return metric.higher_is_better ? right - left : left - right;
  })[0];
}

type ScatterPoint = {
  player: RankingEntry;
  x: number;
  y: number;
  xPercentile: number;
  yPercentile: number;
};

function scoringScatter(metrics: RankingMetric[]) {
  const xg = metrics.find((metric) => metric.key === "xg_per_90");
  const goals = metrics.find((metric) => metric.key === "goals_per_90");
  if (!xg || !goals) return null;

  const points: ScatterPoint[] = xg.entries
    .filter((entry) => entry.value != null && entry.minutes >= OVERVIEW_MIN_MINUTES)
    .map((entry) => {
      const goalEntry = goals.entries.find(
        (candidate) => candidate.player_code === entry.player_code
      );
      if (
        goalEntry?.value == null ||
        entry.percentile == null ||
        goalEntry.percentile == null
      ) {
        return null;
      }
      return {
        player: entry,
        x: Number(entry.value),
        y: Number(goalEntry.value),
        xPercentile: entry.percentile,
        yPercentile: goalEntry.percentile,
      };
    })
    .filter((point): point is ScatterPoint => Boolean(point));

  if (points.length < 3) return null;

  const maxX = Math.max(...points.map((point) => point.x), 0.01);
  const maxY = Math.max(...points.map((point) => point.y), 0.01);
  const averageX = points.reduce((sum, point) => sum + point.x, 0) / points.length;
  const averageY = points.reduce((sum, point) => sum + point.y, 0) / points.length;

  return { xg, goals, points, maxX, maxY, averageX, averageY };
}

function xPosition(value: number, max: number) {
  return 50 + (value / max) * 520;
}

function yPosition(value: number, max: number) {
  return 238 - (value / max) * 190;
}

export function PlayerRankingsOverview({
  season,
  position,
  metrics,
  cohortDescription,
}: {
  season: string;
  position: string;
  metrics: RankingMetric[];
  cohortDescription: string;
}) {
  const signalMetrics = (SIGNAL_KEYS_BY_POSITION[position] ?? [])
    .map((key) => metrics.find((metric) => metric.key === key))
    .filter((metric): metric is RankingMetric => Boolean(metric))
    .filter((metric) => eligibleEntries(metric).length > 0);

  const leaders = signalMetrics
    .map((metric) => ({ metric, player: signalLeader(metric) }))
    .filter(
      (item): item is { metric: RankingMetric; player: RankingEntry } =>
        Boolean(item.player)
    );

  const scatter = scoringScatter(metrics);
  const investigation = scatter
    ? scatter.points
        .filter(
          (point) => point.xPercentile >= 70 && point.yPercentile <= 50
        )
        .sort((a, b) => b.xPercentile - a.xPercentile)
        .slice(0, 4)
    : [];

  return (
    <>
      <section className={rankingStyles.overviewIntro}>
        <div>
          <p className={styles.kicker}>League overview</p>
          <h2>Players worth investigating</h2>
        </div>
        <p>
          Discovery signals use players with {OVERVIEW_MIN_MINUTES}+ recorded
          minutes. They are descriptive research prompts, not betting
          recommendations.
        </p>
      </section>

      {leaders.length > 0 && (
        <section className={rankingStyles.leaderGrid}>
          {leaders.map(({ metric, player }) => (
            <Link
              className={rankingStyles.leaderCard}
              href={rankingHref(season, position, metric)}
              key={metric.key}
            >
              <div>
                <span>{metric.label}</span>
                <small>{OVERVIEW_MIN_MINUTES}+ min leader</small>
              </div>
              <strong>{formatMetric(metric, player.value)}</strong>
              <h3>{player.player_name}</h3>
              <p>{player.clubs.join(" · ") || "Club unavailable"}</p>
              <footer>
                <span>{player.minutes} min</span>
                <span>
                  {player.percentile != null
                    ? `P${Math.round(player.percentile)}`
                    : "—"}
                </span>
              </footer>
            </Link>
          ))}
        </section>
      )}

      {scatter && (
        <section className={rankingStyles.discoveryGrid}>
          <article className={rankingStyles.scatterPanel}>
            <header className={styles.sectionHeading}>
              <div>
                <p className={styles.kicker}>Scoring process vs output</p>
                <h2>xG / 90 against Goals / 90</h2>
              </div>
              <span>{scatter.points.length} players · {OVERVIEW_MIN_MINUTES}+ min</span>
            </header>

            <div className={rankingStyles.scatterWrap}>
              <svg
                className={rankingStyles.scatter}
                viewBox="0 0 620 275"
                role="img"
                aria-label="Goals per 90 against expected goals per 90"
              >
                <line
                  x1={xPosition(scatter.averageX, scatter.maxX)}
                  x2={xPosition(scatter.averageX, scatter.maxX)}
                  y1="35"
                  y2="238"
                  className={rankingStyles.scatterAverage}
                />
                <line
                  x1="50"
                  x2="580"
                  y1={yPosition(scatter.averageY, scatter.maxY)}
                  y2={yPosition(scatter.averageY, scatter.maxY)}
                  className={rankingStyles.scatterAverage}
                />
                <line x1="50" x2="580" y1="238" y2="238" className={rankingStyles.scatterAxis} />
                <line x1="50" x2="50" y1="35" y2="238" className={rankingStyles.scatterAxis} />

                {scatter.points.map((point) => (
                  <circle
                    key={point.player.player_code}
                    cx={xPosition(point.x, scatter.maxX)}
                    cy={yPosition(point.y, scatter.maxY)}
                    r="5"
                    className={
                      point.xPercentile >= 70 && point.yPercentile <= 50
                        ? rankingStyles.scatterCandidate
                        : rankingStyles.scatterDot
                    }
                  >
                    <title>
                      {`${point.player.player_name} · xG/90 ${trim(point.x)} · Goals/90 ${trim(point.y)}`}
                    </title>
                  </circle>
                ))}

                <text x="315" y="267" className={rankingStyles.scatterLabel}>xG / 90 →</text>
                <text x="8" y="128" className={rankingStyles.scatterLabel} transform="rotate(-90 8 128)">Goals / 90 →</text>
              </svg>
            </div>

            <footer className={rankingStyles.scatterFooter}>
              <span>Vertical line = cohort average xG/90</span>
              <span>Horizontal line = cohort average Goals/90</span>
            </footer>
          </article>

          <article className={rankingStyles.investigationPanel}>
            <header className={styles.sectionHeading}>
              <div>
                <p className={styles.kicker}>Research shortlist</p>
                <h2>High process · lower output</h2>
              </div>
            </header>

            {investigation.length > 0 ? (
              <div className={rankingStyles.investigationList}>
                {investigation.map((point) => (
                  <Link
                    href={`/player-stats?season=${encodeURIComponent(
                      season
                    )}&player=${encodeURIComponent(point.player.player_code)}`}
                    key={point.player.player_code}
                  >
                    <div>
                      <strong>{point.player.player_name}</strong>
                      <span>{point.player.clubs.join(" · ") || "Club unavailable"}</span>
                    </div>
                    <div>
                      <strong>P{Math.round(point.xPercentile)}</strong>
                      <span>xG/90</span>
                    </div>
                    <div>
                      <strong>P{Math.round(point.yPercentile)}</strong>
                      <span>Goals/90</span>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <p className={rankingStyles.investigationEmpty}>
                No clear high-xG / lower-scoring cluster is visible in this
                cohort yet.
              </p>
            )}

            <footer className={rankingStyles.investigationNote}>
              This is a candidate-generation screen only. Finishing gaps can
              persist for real football reasons and should be tested against
              role, minutes, opponent and price before any betting use.
            </footer>
          </article>
        </section>
      )}

      <section className={styles.methodPanel}>
        <div>
          <p className={styles.kicker}>Comparison population</p>
          <strong>{cohortDescription}</strong>
        </div>
        <p>
          Detailed rankings retain the full governed cohort. The Overview uses
          a {OVERVIEW_MIN_MINUTES}-minute discovery floor to reduce extreme
          small-sample per-90 leaders while the current season is still young.
        </p>
      </section>
    </>
  );
}
