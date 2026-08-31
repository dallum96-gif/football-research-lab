import type { CSSProperties } from "react";
import styles from "./PlayerStats.module.css";

export type RankingEntry = {
  player_code: string;
  player_name: string;
  position: string;
  clubs: string[];
  minutes: number;
  starts: number;
  appearances: number;
  value: number | null;
  rank: number | null;
  out_of: number;
  percentile: number | null;
};

export type RankingMetric = {
  key: string;
  label: string;
  unit: string;
  family: string;
  higher_is_better: boolean;
  representation: string;
  availability: string;
  observed_players: number;
  eligible_players: number;
  ranking_policy: string;
  percentile_policy: string;
  entries: RankingEntry[];
};

function trim(value: number, decimals = 1) {
  const fixed = value.toFixed(decimals);
  return fixed.includes(".")
    ? fixed.replace(/0+$/, "").replace(/\.$/, "")
    : fixed;
}

function displayValue(metric: RankingMetric, value: number | null) {
  if (value == null) return "—";
  if (Number.isInteger(value)) return String(value);
  if (metric.unit === "%") return `${trim(value, 1)}%`;
  if (metric.unit.startsWith("xG") || metric.unit === "xA" || metric.unit === "xGI") {
    return trim(value, 2);
  }
  return trim(value, 2);
}

function polarPoint(cx: number, cy: number, radius: number, angle: number) {
  const radians = ((angle - 90) * Math.PI) / 180;
  return {
    x: cx + radius * Math.cos(radians),
    y: cy + radius * Math.sin(radians),
  };
}

function polygonPoints(count: number, radius: number, cx = 120, cy = 120) {
  return Array.from({ length: count }, (_, index) => {
    const point = polarPoint(cx, cy, radius, (360 / count) * index);
    return `${point.x},${point.y}`;
  }).join(" ");
}

export function PercentileFingerprint({
  metrics,
  playerCode,
}: {
  metrics: RankingMetric[];
  playerCode: string;
}) {
  const axes = metrics
    .map((metric) => {
      const entry = metric.entries.find((candidate) => candidate.player_code === playerCode);
      return entry?.percentile == null ? null : { metric, entry };
    })
    .filter((item): item is { metric: RankingMetric; entry: RankingEntry } => Boolean(item))
    .slice(0, 8);

  if (axes.length < 3) return null;

  const values = axes.map(({ entry }, index) => {
    const radius = 82 * ((entry.percentile ?? 0) / 100);
    const point = polarPoint(120, 120, radius, (360 / axes.length) * index);
    return `${point.x},${point.y}`;
  }).join(" ");

  return (
    <article className={styles.visualPanel}>
      <header className={styles.sectionHeading}>
        <div>
          <p className={styles.kicker}>Player fingerprint</p>
          <h2>Position percentile radar</h2>
        </div>
        <span>{axes.length} comparable metrics</span>
      </header>

      <div className={styles.radarWrap}>
        <svg className={styles.radar} viewBox="0 0 240 240" role="img" aria-label="Position percentile radar">
          {[.25, .5, .75, 1].map((scale) => (
            <polygon
              key={scale}
              points={polygonPoints(axes.length, 82 * scale)}
              className={styles.radarGrid}
            />
          ))}
          {axes.map((_, index) => {
            const edge = polarPoint(120, 120, 82, (360 / axes.length) * index);
            return (
              <line
                key={index}
                x1="120"
                y1="120"
                x2={edge.x}
                y2={edge.y}
                className={styles.radarAxis}
              />
            );
          })}
          <polygon points={values} className={styles.radarShape} />
          {axes.map(({ entry }, index) => {
            const radius = 82 * ((entry.percentile ?? 0) / 100);
            const point = polarPoint(120, 120, radius, (360 / axes.length) * index);
            return <circle key={index} cx={point.x} cy={point.y} r="3.3" className={styles.radarDot} />;
          })}
        </svg>

        <div className={styles.radarLegend}>
          {axes.map(({ metric, entry }) => (
            <div key={metric.key}>
              <span>{metric.label}</span>
              <strong>P{Math.round(entry.percentile ?? 0)}</strong>
            </div>
          ))}
        </div>
      </div>
    </article>
  );
}

export function AverageDonuts({
  metrics,
  playerCode,
}: {
  metrics: RankingMetric[];
  playerCode: string;
}) {
  const comparisons = metrics
    .filter((metric) => metric.higher_is_better)
    .map((metric) => {
      const player = metric.entries.find((entry) => entry.player_code === playerCode);
      const values = metric.entries
        .map((entry) => entry.value)
        .filter((value): value is number => value != null);
      const average = values.length
        ? values.reduce((sum, value) => sum + value, 0) / values.length
        : null;
      if (player?.value == null || average == null || average === 0) return null;
      const share = Math.max(0, Math.min(100, (player.value / (player.value + average)) * 100));
      const delta = ((player.value - average) / Math.abs(average)) * 100;
      return { metric, player, average, share, delta };
    })
    .filter((item): item is NonNullable<typeof item> => Boolean(item))
    .slice(0, 3);

  if (!comparisons.length) return null;

  return (
    <article className={styles.visualPanel}>
      <header className={styles.sectionHeading}>
        <div>
          <p className={styles.kicker}>League average</p>
          <h2>Player vs position average</h2>
        </div>
        <span>Premier League · same position</span>
      </header>

      <div className={styles.donutGrid}>
        {comparisons.map(({ metric, player, average, share, delta }) => (
          <div className={styles.donutCard} key={metric.key}>
            <div
              className={styles.donut}
              style={{ "--donut-share": `${share}%` } as CSSProperties}
              aria-label={`${metric.label}: ${trim(delta, 0)} percent versus position average`}
            >
              <div>
                <strong>{delta >= 0 ? "+" : ""}{trim(delta, 0)}%</strong>
                <span>vs avg</span>
              </div>
            </div>
            <strong className={styles.donutLabel}>{metric.label}</strong>
            <p>
              {displayValue(metric, player.value)} player · {displayValue(metric, average)} avg
            </p>
          </div>
        ))}
      </div>
    </article>
  );
}

export function CohortDistributions({
  metrics,
  playerCode,
}: {
  metrics: RankingMetric[];
  playerCode: string;
}) {
  const available = metrics
    .filter((metric) => metric.entries.filter((entry) => entry.value != null).length >= 3)
    .slice(0, 3);

  if (!available.length) return null;

  return (
    <article className={styles.visualPanel}>
      <header className={styles.sectionHeading}>
        <div>
          <p className={styles.kicker}>Cohort distribution</p>
          <h2>Where the player sits</h2>
        </div>
        <span>Each dot is one comparable player</span>
      </header>

      <div className={styles.distributionList}>
        {available.map((metric) => {
          const entries = metric.entries.filter(
            (entry): entry is RankingEntry & { value: number } => entry.value != null
          );
          const values = entries.map((entry) => entry.value);
          const min = Math.min(...values);
          const max = Math.max(...values);
          const average = values.reduce((sum, value) => sum + value, 0) / values.length;
          const spread = max - min || 1;
          const averageLeft = ((average - min) / spread) * 100;

          return (
            <div className={styles.distributionRow} key={metric.key}>
              <div className={styles.distributionHeading}>
                <strong>{metric.label}</strong>
                <span>{displayValue(metric, min)} — {displayValue(metric, max)}</span>
              </div>
              <div className={styles.distributionTrack}>
                <i className={styles.averageMarker} style={{ left: `${averageLeft}%` }} />
                {entries.map((entry) => {
                  const left = ((entry.value - min) / spread) * 100;
                  return (
                    <span
                      key={entry.player_code}
                      className={entry.player_code === playerCode ? styles.playerDistributionDot : styles.distributionDot}
                      style={{ left: `${left}%` }}
                      title={`${entry.player_name}: ${displayValue(metric, entry.value)}`}
                    />
                  );
                })}
              </div>
              <div className={styles.distributionFooter}>
                <span>Low</span>
                <span>Position average {displayValue(metric, average)}</span>
                <span>High</span>
              </div>
            </div>
          );
        })}
      </div>
    </article>
  );
}
