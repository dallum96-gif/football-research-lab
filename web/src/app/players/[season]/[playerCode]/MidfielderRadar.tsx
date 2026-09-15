import styles from "./PlayerProfile.module.css";

export type PlayerRadarAxis = {
  key: string;
  label: string;
  metric_label: string;
  value: number | null;
  unit: string;
  percentile: number | null;
  average_value?: number | null;
  average_percentile: number | null;
  rank: number | null;
  out_of: number;
  observed_players: number;
  eligible_players: number;
  availability: "AVAILABLE" | "PARTIAL" | "UNAVAILABLE";
};

export type PlayerProfileRadarData = {
  available: boolean;
  complete?: boolean;
  observed_axis_count?: number;
  required_axis_count?: number;
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
    label?: string;
  } | null;
  analysis_version?: string;
  ranking_policy?: string;
  percentile_policy?: string;
  template_key?: string;
  limitations: string[];
};

const POSITION_COPY: Record<
  string,
  { profile: string; comparison: string; average: string }
> = {
  GKP: {
    profile: "Goalkeeper profile",
    comparison: "vs qualified PL goalkeepers",
    average: "GK average",
  },
  DEF: {
    profile: "Defender profile",
    comparison: "vs qualified PL defenders",
    average: "DEF average",
  },
  MID: {
    profile: "Midfielder profile",
    comparison: "vs qualified PL midfielders",
    average: "MID average",
  },
  FWD: {
    profile: "Forward profile",
    comparison: "vs qualified PL forwards",
    average: "FWD average",
  },
};

const WIDTH = 250;
const HEIGHT = 238;
const CX = 125;
const CY = 112;
const RADIUS = 72;

function point(index: number, count: number, percentage: number) {
  const angle = -Math.PI / 2 + (Math.PI * 2 * index) / count;
  const proportion = Math.max(0, Math.min(100, percentage)) / 100;
  return {
    x: CX + Math.cos(angle) * RADIUS * proportion,
    y: CY + Math.sin(angle) * RADIUS * proportion,
  };
}

function polygon(values: number[]) {
  return values
    .map((value, index) => {
      const p = point(index, values.length, value);
      return `${p.x},${p.y}`;
    })
    .join(" ");
}

// Retain the existing export name so the approved Player Profile composition
// does not need a structural rewrite while the component becomes position-aware.
export function MidfielderRadar({
  radar,
  playerName,
}: {
  radar: PlayerProfileRadarData;
  playerName: string;
}) {
  const axes = radar.axes;
  if (!radar.available || axes.length !== 6) return null;

  const copy = POSITION_COPY[radar.position] ?? {
    profile: "Player profile",
    comparison: "vs qualified same-position PL players",
    average: "Position average",
  };

  const complete =
    radar.complete === true &&
    axes.every(
      (axis) => axis.percentile != null && axis.average_percentile != null
    );

  const playerPoints = complete
    ? polygon(axes.map((axis) => axis.percentile as number))
    : null;
  const averagePoints = complete
    ? polygon(axes.map((axis) => axis.average_percentile as number))
    : null;

  return (
    <section className={styles.radarBlock}>
      <header className={styles.radarHeader}>
        <div>
          <span>{copy.profile}</span>
          <strong>{copy.comparison}</strong>
        </div>
        <span className={styles.radarSample}>
          {radar.cohort?.population_size ?? "—"} players
        </span>
      </header>

      <svg
        className={styles.radar}
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        role="img"
        aria-label={`${playerName} percentile profile ${copy.comparison}`}
      >
        {[25, 50, 75, 100].map((ring) => (
          <polygon
            key={ring}
            className={ring === 50 ? styles.radarMidGrid : styles.radarGrid}
            points={polygon(axes.map(() => ring))}
          />
        ))}

        {axes.map((axis, index) => {
          const outer = point(index, axes.length, 100);
          const label = point(index, axes.length, 126);
          let anchor: "start" | "middle" | "end" = "middle";
          if (label.x < CX - 12) anchor = "end";
          else if (label.x > CX + 12) anchor = "start";

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
                className={
                  axis.availability === "UNAVAILABLE"
                    ? styles.radarUnavailableLabel
                    : styles.radarLabel
                }
                x={label.x}
                y={label.y}
                textAnchor={anchor}
                dominantBaseline="middle"
              >
                {axis.label}
              </text>
              {axis.availability === "UNAVAILABLE" ? (
                <text
                  className={styles.radarUnavailableValue}
                  x={label.x}
                  y={label.y + 8}
                  textAnchor={anchor}
                  dominantBaseline="middle"
                >
                  N/A
                </text>
              ) : null}
            </g>
          );
        })}

        {averagePoints ? (
          <polygon className={styles.radarAverage} points={averagePoints} />
        ) : null}
        {playerPoints ? (
          <polygon className={styles.radarPlayer} points={playerPoints} />
        ) : null}

        {axes.map((axis, index) => {
          if (axis.percentile == null) return null;
          const p = point(index, axes.length, axis.percentile);
          return (
            <g key={axis.key}>
              {!complete ? (
                <line
                  className={styles.radarPlayerRay}
                  x1={CX}
                  y1={CY}
                  x2={p.x}
                  y2={p.y}
                />
              ) : null}
              <circle
                className={styles.radarPlayerPoint}
                cx={p.x}
                cy={p.y}
                r="2.3"
              >
                <title>
                  {axis.label}: {axis.percentile.toFixed(0)}th percentile · rank{" "}
                  {axis.rank ?? "—"} of {axis.out_of}
                  {axis.availability === "PARTIAL"
                    ? " · partial source coverage"
                    : ""}
                </title>
              </circle>
            </g>
          );
        })}
      </svg>

      <div className={styles.radarLegend}>
        <span>
          <i className={styles.radarPlayerKey} />
          {playerName.split(" ")[0]}
        </span>
        {complete ? (
          <span>
            <i className={styles.radarAverageKey} />
            {copy.average}
          </span>
        ) : null}
      </div>

      <p className={styles.radarCaveat}>
        Percentile profile · {radar.observed_axis_count ?? axes.length}/
        {radar.required_axis_count ?? axes.length} dimensions · minimum{" "}
        {radar.cohort?.minimum_minutes ?? "—"} minutes
      </p>
    </section>
  );
}
