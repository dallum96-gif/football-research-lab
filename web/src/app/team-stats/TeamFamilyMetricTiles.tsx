import Link from "next/link";
import tileStyles from "./StatsListTiles.module.css";
import {
  TEAM_STATS_FAMILY_CONFIG,
  type TeamStatsAnalyticalFamily,
} from "./teamMetricFamilies";

export type TeamFamilyTileMetric = {
  key: string;
  label: string;
  unit: string;
  value: number | null;
  rank: number | null;
  outOf: number;
  percentile: number | null;
  observedMatches: number;
  eligibleMatches: number;
  href: string;
};

export type TeamFamilyTileKey = TeamStatsAnalyticalFamily;

const TILE_TONES = ["coral", "green", "gold", "blue"] as const;

function trim(value: number, decimals: number) {
  const fixed = value.toFixed(decimals);
  return fixed.includes(".")
    ? fixed.replace(/0+$/, "").replace(/\.$/, "")
    : fixed;
}

function formatMetric(metric: TeamFamilyTileMetric) {
  if (metric.value === null) return "—";
  if (metric.unit === "%") return `${trim(metric.value, 1)}%`;
  if (
    metric.key === "goals_for_per_match" ||
    metric.key === "goals_against_per_match" ||
    metric.key === "points_per_match"
  ) {
    return trim(metric.value, 1);
  }
  return trim(metric.value, Number.isInteger(metric.value) ? 0 : 2);
}

function ordinal(value: number) {
  const mod100 = value % 100;
  if (mod100 >= 11 && mod100 <= 13) return `${value}th`;
  const suffix =
    value % 10 === 1 ? "st" : value % 10 === 2 ? "nd" : value % 10 === 3 ? "rd" : "th";
  return `${value}${suffix}`;
}

export function TeamFamilyMetricTiles({
  family,
  teamName,
  metrics,
}: {
  family: TeamFamilyTileKey;
  teamName: string;
  metrics: TeamFamilyTileMetric[];
}) {
  const byKey = new Map(metrics.map((metric) => [metric.key, metric]));
  const groups = TEAM_STATS_FAMILY_CONFIG[family].groups
    .map((group) => ({
      ...group,
      metrics: group.metricKeys
        .map((key) => byKey.get(key))
        .filter((metric): metric is TeamFamilyTileMetric => Boolean(metric)),
    }))
    .filter((group) => group.metrics.length > 0);

  if (!groups.length) {
    return (
      <div className={tileStyles.noTiles}>
        No governed metrics are available for this team and season.
      </div>
    );
  }

  return (
    <section className={tileStyles.leaderboardSection}>
      <header className={tileStyles.leaderboardHeading}>
        <div>
          <p className={tileStyles.familyKicker}>Team view</p>
          <h2>{teamName} · metric profile</h2>
        </div>
        <span>
          Read vertically through one team. Every row links to the matching league ranking.
        </span>
      </header>

      <div className={tileStyles.leaderboardGrid}>
        {groups.map((group, tileIndex) => (
          <article
            className={tileStyles.leaderboardCard}
            data-tone={TILE_TONES[tileIndex % TILE_TONES.length]}
            key={group.key}
          >
            <header className={tileStyles.cardHeader}>
              <div>
                <span>Team metrics</span>
                <h3>{group.label}</h3>
              </div>
              <strong>{group.metrics.length} stats</strong>
            </header>

            <ol className={tileStyles.leaderboardList}>
              {group.metrics.map((metric) => {
                const available = metric.value !== null && metric.rank !== null;
                return (
                  <li key={metric.key}>
                    <Link
                      href={metric.href}
                      className={tileStyles.teamMetricRow}
                      title={`Open ${metric.label} league ranking`}
                    >
                      <span className={tileStyles.metricIdentity}>
                        <strong>{metric.label}</strong>
                        <small>
                          {available && metric.rank !== null
                            ? `${ordinal(metric.rank)} of ${metric.outOf}`
                            : `${metric.observedMatches}/${metric.eligibleMatches} matches observed`}
                        </small>
                      </span>
                      <span className={tileStyles.teamMetricValue}>
                        {formatMetric(metric)}
                      </span>
                      <span className={tileStyles.teamMetricContext}>
                        {available && metric.percentile !== null
                          ? `P${Math.round(metric.percentile)}`
                          : "—"}
                      </span>
                    </Link>
                  </li>
                );
              })}
            </ol>

            <footer>
              <span>{group.label}</span>
              <span>{group.metrics.length}</span>
            </footer>
          </article>
        ))}
      </div>
    </section>
  );
}
