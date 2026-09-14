import styles from "./PlayerProfile.module.css";

export type PlayerRadarAxis = {
  key: string;
  label: string;
  metric_label: string;
  value: number;
  unit: string;
  percentile: number;
  average_value?: number;
  average_percentile: number;
  rank: number | null;
  out_of: number;
  observed_players: number;
  eligible_players: number;
};

export type PlayerProfileRadarData = {
  available: boolean;
  position: string;
  season: string;
  player_code: string;
  axes: PlayerRadarAxis[];
  summary: string;
  cohort: {
    competition: string;
    season: string;
    position: string;
    minimum_minutes: number;
    population_size?: number;
    possible_minutes?: number;
    qualification_share?: number;
    description: string;
  } | null;
  analysis_version?: string;
  ranking_policy?: string;
  percentile_policy?: string;
  limitations: string[];
};

const WIDTH = 250;
const HEIGHT = 238;
const CX = 125;
const CY = 112;
const RADIUS = 72;

function point(
  index: number,
  count: number,
  percentage: number
) {
  const angle =
    -Math.PI / 2 +
    (Math.PI * 2 * index) / count;

  const proportion =
    Math.max(0, Math.min(100, percentage)) / 100;

  return {
    x:
      CX +
      Math.cos(angle) *
        RADIUS *
        proportion,
    y:
      CY +
      Math.sin(angle) *
        RADIUS *
        proportion,
  };
}

function polygon(values: number[]) {
  return values
    .map((value, index) => {
      const p = point(
        index,
        values.length,
        value
      );

      return `${p.x},${p.y}`;
    })
    .join(" ");
}

export function MidfielderRadar({
  radar,
  playerName,
}: {
  radar: PlayerProfileRadarData;
  playerName: string;
}) {
  const axes = radar.axes;

  if (
    !radar.available ||
    axes.length !== 6
  ) {
    return null;
  }

  const playerPoints = polygon(
    axes.map(
      (axis) => axis.percentile
    )
  );

  const averagePoints = polygon(
    axes.map(
      (axis) => axis.average_percentile
    )
  );

  return (
    <section className={styles.radarBlock}>
      <header className={styles.radarHeader}>
        <div>
          <span>Midfielder profile</span>
          <strong>
            vs qualified PL midfielders
          </strong>
        </div>

        <span className={styles.radarSample}>
          {radar.cohort?.population_size ?? "—"} players
        </span>
      </header>

      <svg
        className={styles.radar}
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        role="img"
        aria-label={`${playerName} percentile profile compared with qualified Premier League midfielders`}
      >
        {[25, 50, 75, 100].map(
          (ring) => (
            <polygon
              key={ring}
              className={
                ring === 50
                  ? styles.radarMidGrid
                  : styles.radarGrid
              }
              points={polygon(
                axes.map(() => ring)
              )}
            />
          )
        )}

        {axes.map((axis, index) => {
          const outer = point(
            index,
            axes.length,
            100
          );

          const label = point(
            index,
            axes.length,
            126
          );

          let anchor:
            | "start"
            | "middle"
            | "end" = "middle";

          if (label.x < CX - 12) {
            anchor = "end";
          } else if (
            label.x > CX + 12
          ) {
            anchor = "start";
          }

          return (
            <g key={axis.key}>
              <line
                className={styles.radarAxis}
                x1={CX}
                y1={CY}
                x2={outer.x}
                y2={outer.y}
              />

              <text
                className={styles.radarLabel}
                x={label.x}
                y={label.y}
                textAnchor={anchor}
                dominantBaseline="middle"
              >
                {axis.label}
              </text>
            </g>
          );
        })}

        <polygon
          className={styles.radarAverage}
          points={averagePoints}
        />

        <polygon
          className={styles.radarPlayer}
          points={playerPoints}
        />

        {axes.map((axis, index) => {
          const p = point(
            index,
            axes.length,
            axis.percentile
          );

          return (
            <circle
              key={axis.key}
              className={styles.radarPlayerPoint}
              cx={p.x}
              cy={p.y}
              r="2.3"
            >
              <title>
                {axis.label}:{" "}
                {axis.percentile.toFixed(0)}
                th percentile · rank{" "}
                {axis.rank ?? "—"} of{" "}
                {axis.out_of}
              </title>
            </circle>
          );
        })}
      </svg>

      <div className={styles.radarLegend}>
        <span>
          <i className={styles.radarPlayerKey} />
          {playerName.split(" ")[0]}
        </span>

        <span>
          <i className={styles.radarAverageKey} />
          MID average
        </span>
      </div>

      <p className={styles.radarCaveat}>
        Per 90 · minimum{" "}
        {radar.cohort?.minimum_minutes ?? "—"} minutes
      </p>
    </section>
  );
}
