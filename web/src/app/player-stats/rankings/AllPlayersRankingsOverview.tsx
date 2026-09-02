"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import styles from "./AllPlayersRankingsOverview.module.css";

type RankingEntry = {
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

type RankingMetric = {
  key: string;
  label: string;
  unit: string;
  family: string;
  higher_is_better: boolean;
  representation: string;
  entries: RankingEntry[];
};

export type PositionRankingData = {
  analysis_version: string;
  season: string;
  position: string;
  population_size: number;
  cohort: {
    competition: string;
    season: string;
    position: string;
    minimum_minutes: number;
    description: string;
  };
  ranking_policy: string;
  percentile_policy: string;
  metrics: RankingMetric[];
};

type ScatterPosition = "DEF" | "MID" | "FWD";
type MinuteQualifier = 0 | 0.1 | 0.25 | 0.5 | 0.75;

type ScatterPoint = {
  player: RankingEntry;
  x: number;
  y: number;
  xPercentile: number;
  yPercentile: number;
  signal: "balanced" | "x-led" | "y-led" | null;
};

const SCATTER_CONFIG: Record<
  ScatterPosition,
  {
    xKey: string;
    yKey: string;
    kicker: string;
    title: string;
    description: string;
    xLed: string;
    yLed: string;
    balanced: string;
  }
> = {
  DEF: {
    xKey: "defensive_contribution_per_90",
    yKey: "xgi_per_90",
    kicker: "Two-way defenders",
    title: "Defensive work vs attacking contribution",
    description: "Defensive contribution / 90 against xGI / 90 for Premier League defenders.",
    xLed: "Defensive-first profile",
    yLed: "Attack-first profile",
    balanced: "Two-way standout",
  },
  MID: {
    xKey: "xa_per_90",
    yKey: "xg_per_90",
    kicker: "Midfield threat",
    title: "Creation vs goal threat",
    description: "xA / 90 against xG / 90 for Premier League midfielders.",
    xLed: "Creator-first profile",
    yLed: "Goal-threat profile",
    balanced: "Dual-threat midfielder",
  },
  FWD: {
    xKey: "xg_per_90",
    yKey: "goals_per_90",
    kicker: "Scoring process",
    title: "xG / 90 vs Goals / 90",
    description: "Expected-goal process against actual scoring output for Premier League forwards.",
    xLed: "High process · lower output",
    yLed: "Output ahead of process",
    balanced: "Process + output",
  },
};

const MINUTE_OPTIONS: Array<{ value: MinuteQualifier; label: string }> = [
  { value: 0, label: "All minutes" },
  { value: 0.1, label: "10%+ possible" },
  { value: 0.25, label: "25%+ possible" },
  { value: 0.5, label: "50%+ possible" },
  { value: 0.75, label: "75%+ possible" },
];
const OUTFIELD: ScatterPosition[] = ["DEF", "MID", "FWD"];

function trim(value: number, decimals = 2) {
  const fixed = value.toFixed(decimals);
  return fixed.includes(".")
    ? fixed.replace(/0+$/, "").replace(/\.$/, "")
    : fixed;
}

function formatValue(metric: RankingMetric, value: number | null) {
  if (value == null) return "—";
  if (metric.unit === "%") return `${trim(value, 1)}%`;
  return trim(value, Number.isInteger(value) ? 0 : 2);
}

function playerHref(season: string, playerCode: string) {
  return `/player-stats?season=${encodeURIComponent(season)}&player=${encodeURIComponent(playerCode)}`;
}

function metric(data: PositionRankingData | null | undefined, key: string) {
  return data?.metrics.find((item) => item.key === key) ?? null;
}

function possibleMinutes(
  entry: RankingEntry,
  possibleMinutesByClub: Record<string, number>
) {
  return Math.max(
    0,
    ...entry.clubs.map((club) => possibleMinutesByClub[club] ?? 0)
  );
}

function eligible(
  entry: RankingEntry,
  club: string,
  minuteQualifier: MinuteQualifier,
  possibleMinutesByClub: Record<string, number>
) {
  if (club !== "ALL" && !entry.clubs.includes(club)) return false;
  if (minuteQualifier === 0) return true;

  const availableMinutes = possibleMinutes(entry, possibleMinutesByClub);
  if (availableMinutes <= 0) return true;
  return entry.minutes >= availableMinutes * minuteQualifier;
}

function xPosition(value: number, max: number) {
  return 52 + (value / max) * 520;
}

function yPosition(value: number, max: number) {
  return 238 - (value / max) * 190;
}

function signalFor(xPercentile: number, yPercentile: number): ScatterPoint["signal"] {
  if (xPercentile >= 70 && yPercentile >= 70) return "balanced";
  if (xPercentile >= 70 && yPercentile <= 50) return "x-led";
  if (xPercentile <= 50 && yPercentile >= 70) return "y-led";
  return null;
}

function leaderAcross(
  datasets: Array<PositionRankingData | null | undefined>,
  key: string,
  club: string,
  minuteQualifier: MinuteQualifier,
  possibleMinutesByClub: Record<string, number>
) {
  const candidates: Array<{ metric: RankingMetric; entry: RankingEntry }> = [];

  datasets.forEach((data) => {
    const current = metric(data, key);
    if (!current) return;
    current.entries.forEach((entry) => {
      if (
        entry.value == null ||
        !eligible(entry, club, minuteQualifier, possibleMinutesByClub)
      ) return;
      candidates.push({ metric: current, entry });
    });
  });

  if (!candidates.length) return null;

  return candidates.sort((a, b) => {
    const left = Number(a.entry.value ?? 0);
    const right = Number(b.entry.value ?? 0);
    return a.metric.higher_is_better ? right - left : left - right;
  })[0];
}

export function AllPlayersRankingsOverview({
  season,
  rankingsByPosition,
  possibleMinutesByClub,
}: {
  season: string;
  rankingsByPosition: Record<string, PositionRankingData | null>;
  possibleMinutesByClub: Record<string, number>;
}) {
  const [scatterPosition, setScatterPosition] = useState<ScatterPosition>("FWD");
  const [club, setClub] = useState("ALL");
  const [minuteQualifier, setMinuteQualifier] = useState<MinuteQualifier>(0.25);

  const clubs = useMemo(() => {
    const values = new Set<string>();
    Object.values(rankingsByPosition).forEach((data) => {
      data?.metrics.forEach((item) => {
        item.entries.forEach((entry) => entry.clubs.forEach((name) => values.add(name)));
      });
    });
    return [...values].sort((a, b) => a.localeCompare(b));
  }, [rankingsByPosition]);

  const signalCards = useMemo(() => {
    const outfield = OUTFIELD.map((position) => rankingsByPosition[position]);
    return [
      {
        label: "Scoring leader",
        note: "Goals",
        result: leaderAcross(outfield, "goals", club, minuteQualifier, possibleMinutesByClub),
      },
      {
        label: "Creative leader",
        note: "xA / 90",
        result: leaderAcross(outfield, "xa_per_90", club, minuteQualifier, possibleMinutesByClub),
      },
      {
        label: "Defensive engine",
        note: "Defensive contribution / 90",
        result: leaderAcross(outfield, "defensive_contribution_per_90", club, minuteQualifier, possibleMinutesByClub),
      },
      {
        label: "Keeper workload",
        note: "Saves / 90",
        result: leaderAcross([rankingsByPosition.GKP], "saves_per_90", club, minuteQualifier, possibleMinutesByClub),
      },
    ];
  }, [rankingsByPosition, club, minuteQualifier, possibleMinutesByClub]);

  const scatter = useMemo(() => {
    const data = rankingsByPosition[scatterPosition];
    const config = SCATTER_CONFIG[scatterPosition];
    const xMetric = metric(data, config.xKey);
    const yMetric = metric(data, config.yKey);
    if (!xMetric || !yMetric) return null;

    const points = xMetric.entries
      .filter(
        (entry) =>
          entry.value != null &&
          eligible(entry, club, minuteQualifier, possibleMinutesByClub)
      )
      .map((entry) => {
        const yEntry = yMetric.entries.find(
          (candidate) => candidate.player_code === entry.player_code
        );
        if (
          yEntry?.value == null ||
          entry.percentile == null ||
          yEntry.percentile == null
        ) {
          return null;
        }
        return {
          player: entry,
          x: Number(entry.value),
          y: Number(yEntry.value),
          xPercentile: entry.percentile,
          yPercentile: yEntry.percentile,
          signal: signalFor(entry.percentile, yEntry.percentile),
        } satisfies ScatterPoint;
      })
      .filter((point): point is ScatterPoint => Boolean(point));

    if (!points.length) return null;

    const maxX = Math.max(...points.map((point) => point.x), 0.01);
    const maxY = Math.max(...points.map((point) => point.y), 0.01);
    const averageX = points.reduce((sum, point) => sum + point.x, 0) / points.length;
    const averageY = points.reduce((sum, point) => sum + point.y, 0) / points.length;

    const candidates = points
      .filter((point) => point.signal)
      .sort((a, b) => {
        const aBalanced = a.signal === "balanced" ? 1 : 0;
        const bBalanced = b.signal === "balanced" ? 1 : 0;
        if (aBalanced !== bBalanced) return bBalanced - aBalanced;
        return Math.max(b.xPercentile, b.yPercentile) - Math.max(a.xPercentile, a.yPercentile);
      })
      .slice(0, 4);

    return { config, xMetric, yMetric, points, candidates, maxX, maxY, averageX, averageY };
  }, [rankingsByPosition, scatterPosition, club, minuteQualifier, possibleMinutesByClub]);

  const qualifierLabel =
    minuteQualifier === 0
      ? "all minutes"
      : `${Math.round(minuteQualifier * 100)}%+ possible minutes`;

  return (
    <div className={styles.landing}>
      <section className={styles.filterBar} aria-label="League discovery filters">
        <div className={styles.filterIntro}>
          <strong>Filter the view</strong>
          <span>Ranks stay anchored to each player&apos;s full positional league cohort.</span>
        </div>
        <label>
          <span>Club</span>
          <select value={club} onChange={(event) => setClub(event.target.value)}>
            <option value="ALL">All clubs</option>
            {clubs.map((name) => (
              <option key={name} value={name}>{name}</option>
            ))}
          </select>
        </label>
        <label>
          <span>Minutes qualifier</span>
          <select
            value={minuteQualifier}
            onChange={(event) => setMinuteQualifier(Number(event.target.value) as MinuteQualifier)}
          >
            {MINUTE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
        </label>
      </section>

      <section className={styles.signalGrid} aria-label="League signals">
        {signalCards.map((card) => {
          const result = card.result;
          return result ? (
            <Link
              key={card.label}
              className={styles.signalCard}
              href={playerHref(season, result.entry.player_code)}
            >
              <div>
                <span>{card.label}</span>
                <small>{card.note}</small>
              </div>
              <strong>{formatValue(result.metric, result.entry.value)}</strong>
              <h3>{result.entry.player_name}</h3>
              <p>{result.entry.clubs.join(" · ") || "Club unavailable"} · {result.entry.position}</p>
              <footer>
                <span>{result.entry.minutes} min</span>
                <span>{result.entry.rank != null ? `${result.entry.rank} / ${result.entry.out_of}` : "—"}</span>
              </footer>
            </Link>
          ) : (
            <article key={card.label} className={`${styles.signalCard} ${styles.signalEmpty}`}>
              <div><span>{card.label}</span><small>{card.note}</small></div>
              <p>No player matches the current filters.</p>
            </article>
          );
        })}
      </section>

      <section className={styles.discoveryGrid}>
        <article className={styles.scatterPanel}>
          <header className={styles.scatterHeader}>
            <div>
              <p>{scatter?.config.kicker ?? "Positional scatter"}</p>
              <h2>{scatter?.config.title ?? "No governed scatter available"}</h2>
              <span>{scatter?.config.description}</span>
            </div>
            <div className={styles.positionButtons} aria-label="Scatter plot position">
              {OUTFIELD.map((position) => (
                <button
                  type="button"
                  key={position}
                  className={position === scatterPosition ? styles.positionActive : undefined}
                  onClick={() => setScatterPosition(position)}
                  aria-pressed={position === scatterPosition}
                >
                  {position}
                </button>
              ))}
            </div>
          </header>

          {scatter ? (
            <>
              <div className={styles.scatterWrap}>
                <svg
                  className={styles.scatter}
                  viewBox="0 0 620 275"
                  role="img"
                  aria-label={`${scatter.yMetric.label} against ${scatter.xMetric.label} for ${scatterPosition} players`}
                >
                  <line
                    x1={xPosition(scatter.averageX, scatter.maxX)}
                    x2={xPosition(scatter.averageX, scatter.maxX)}
                    y1="35"
                    y2="238"
                    className={styles.averageLine}
                  />
                  <line
                    x1="52"
                    x2="572"
                    y1={yPosition(scatter.averageY, scatter.maxY)}
                    y2={yPosition(scatter.averageY, scatter.maxY)}
                    className={styles.averageLine}
                  />
                  <line x1="52" x2="572" y1="238" y2="238" className={styles.axisLine} />
                  <line x1="52" x2="52" y1="35" y2="238" className={styles.axisLine} />

                  {scatter.points.map((point) => (
                    <a
                      key={point.player.player_code}
                      href={playerHref(season, point.player.player_code)}
                      aria-label={`Open ${point.player.player_name}`}
                    >
                      <circle
                        cx={xPosition(point.x, scatter.maxX)}
                        cy={yPosition(point.y, scatter.maxY)}
                        r={point.signal ? 6 : 4.5}
                        className={
                          point.signal === "balanced"
                            ? styles.dotBalanced
                            : point.signal === "x-led"
                              ? styles.dotXLed
                              : point.signal === "y-led"
                                ? styles.dotYLed
                                : styles.dot
                        }
                      >
                        <title>
                          {`${point.player.player_name} · ${scatter.xMetric.label} ${trim(point.x)} · ${scatter.yMetric.label} ${trim(point.y)}`}
                        </title>
                      </circle>
                    </a>
                  ))}

                  <text x="312" y="267" className={styles.axisLabel}>{scatter.xMetric.label} →</text>
                  <text x="9" y="137" className={styles.axisLabel} transform="rotate(-90 9 137)">{scatter.yMetric.label} →</text>
                </svg>
              </div>
              <footer className={styles.scatterFooter}>
                <span>{scatter.points.length} players shown · {qualifierLabel}{club !== "ALL" ? ` · ${club}` : ""}</span>
                <span>Dashed lines = filtered-view averages</span>
              </footer>
            </>
          ) : (
            <div className={styles.emptyScatter}>No players match these filters for this scatter.</div>
          )}
        </article>

        <article className={styles.profilePanel}>
          <header>
            <p>Profiles to inspect</p>
            <h2>Why these dots stand out</h2>
            <span>Every label below is generated directly from the two plotted positional percentiles.</span>
          </header>

          {scatter?.candidates.length ? (
            <div className={styles.profileList}>
              {scatter.candidates.map((point) => {
                const label = point.signal
                  ? scatter.config[
                      point.signal === "balanced"
                        ? "balanced"
                        : point.signal === "x-led"
                          ? "xLed"
                          : "yLed"
                    ]
                  : "Notable profile";
                return (
                  <Link href={playerHref(season, point.player.player_code)} key={point.player.player_code}>
                    <div className={styles.profileIdentity}>
                      <strong>{point.player.player_name}</strong>
                      <span>{point.player.clubs.join(" · ") || "Club unavailable"} · {point.player.minutes} min</span>
                    </div>
                    <div className={styles.profileSignal} data-signal={point.signal ?? undefined}>
                      <strong>{label}</strong>
                      <span>P{Math.round(point.xPercentile)} {scatter.xMetric.label} · P{Math.round(point.yPercentile)} {scatter.yMetric.label}</span>
                    </div>
                  </Link>
                );
              })}
            </div>
          ) : (
            <div className={styles.emptyProfiles}>No clear high-contrast profile is visible under the current filters.</div>
          )}

          <footer>
            <strong>Interpretation rule</strong>
            <span>Green = strong on both axes. Amber = x-axis led. Coral = y-axis led. These are descriptive prompts, not model recommendations.</span>
          </footer>
        </article>
      </section>

      <section className={styles.methodStrip}>
        <div>
          <strong>All Players is a discovery view, not one universal ranking.</strong>
          <span>DEF, MID, FWD and GKP rankings remain position-specific underneath.</span>
        </div>
        <p>Club and minutes controls filter what is visible. The minutes qualifier uses each club&apos;s completed league matches × 90; ranks and percentiles are not recalculated.</p>
      </section>
    </div>
  );
}
