"use client";

import { useEffect, useState } from "react";
import styles from "./FixturePlayerPerformance.module.css";

type PlayerLeader = {
  player_id: string | null;
  player_name: string | null;
  position: string | null;
  minutes: number | null;
  value: number | null;
  secondary_value: number | null;
  tie_count: number;
};

type PlayerMetric = {
  key: string;
  label: string;
  unit: string;
  secondary_label: string | null;
  secondary_unit: string | null;
  player: PlayerLeader | null;
  status: string;
};

type PlayerPerformanceSide = {
  side: string;
  team_name: string;
  metrics: PlayerMetric[];
  status: string;
  limitations: string[];
};

type FixturePlayerPerformanceResponse = {
  season: string;
  fixture_id: string;
  home: PlayerPerformanceSide;
  away: PlayerPerformanceSide;
};

type Props = {
  season: string;
  fixtureId: string;
};

const API_BASE =
  (globalThis as typeof globalThis & { process?: { env?: Record<string, string | undefined> } })
    .process?.env?.NEXT_PUBLIC_FRL_API_URL ?? "http://127.0.0.1:8000";

function formatValue(value: number | null): string {
  if (value == null || Number.isNaN(value)) return "—";
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

function formatRate(value: number | null, unit: string | null): string {
  if (value == null || Number.isNaN(value) || !unit) return "";
  return `${value.toFixed(1)}${unit}`;
}

function metricUnit(metric: PlayerMetric): string {
  switch (metric.key) {
    case "passes_completed":
      return "completed";
    case "tackles_won":
      return "won";
    case "interceptions_won":
      return "won";
    case "key_passes":
      return "created";
    case "dribbles":
      return "dribbles";
    case "shots_on_target":
      return "on target";
    default:
      return metric.unit;
  }
}

function playerDisplay(metric: PlayerMetric): string {
  const player = metric.player;
  if (!player) return "Data unavailable";
  if (player.tie_count > 1) return `${player.tie_count} players`;
  return player.player_name ?? "Data unavailable";
}

function playerContext(metric: PlayerMetric): string | null {
  const player = metric.player;
  if (!player || player.tie_count > 1) return null;
  if (player.position || player.minutes != null) {
    return [player.position, player.minutes != null ? `${Math.round(player.minutes)}'` : null]
      .filter(Boolean)
      .join(" · ");
  }
  return null;
}

function PlayerPanel({ side }: { side: PlayerPerformanceSide }) {
  const home = side.side === "home";

  return (
    <section
      className={`${styles.panel} ${home ? styles.home : styles.away}`}
      aria-label={`${side.team_name} player performance`}
    >
      <div className={styles.heading}>
        <span className={styles.kicker}>Key player performance</span>
        <span className={styles.teamName}>{side.team_name}</span>
      </div>

      <div className={styles.performanceList}>
        {side.metrics.map((metric) => {
          const player = metric.player;
          const secondary =
            player?.secondary_value != null && metric.secondary_label
              ? `${metric.secondary_label} ${formatRate(player.secondary_value, metric.secondary_unit)}`
              : null;
          const context = playerContext(metric);

          return (
            <div className={styles.performanceRow} key={metric.key}>
              <div className={styles.metricLabel}>{metric.label}</div>
              <div className={styles.playerLine}>
                <div className={styles.playerIdentity}>
                  <span className={styles.playerName}>{playerDisplay(metric)}</span>
                  {context ? <span className={styles.playerContext}>{context}</span> : null}
                </div>
                <div className={styles.metricOutput}>
                  <span className={styles.metricValue}>{formatValue(player?.value ?? null)}</span>
                  <span className={styles.metricUnit}>{metricUnit(metric)}</span>
                </div>
              </div>
              {secondary ? <div className={styles.secondaryLine}>{secondary}</div> : null}
            </div>
          );
        })}
      </div>
    </section>
  );
}

export function FixturePlayerPerformance({ season, fixtureId }: Props) {
  const [data, setData] = useState<FixturePlayerPerformanceResponse | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    let mounted = true;

    fetch(
      `${API_BASE}/api/v1/fixtures/${encodeURIComponent(season)}/${encodeURIComponent(fixtureId)}/player-performance`,
      { signal: controller.signal, cache: "no-store" },
    )
      .then(async (response) => {
        if (!response.ok) throw new Error(`Player performance request failed: ${response.status}`);
        return response.json() as Promise<FixturePlayerPerformanceResponse>;
      })
      .then((payload) => {
        if (mounted) setData(payload);
      })
      .catch(() => {
        if (mounted) setData(null);
      });

    return () => {
      mounted = false;
      controller.abort();
    };
  }, [season, fixtureId]);

  if (!data) return null;

  return (
    <div className={styles.pair}>
      <PlayerPanel side={data.home} />
      <PlayerPanel side={data.away} />
    </div>
  );
}
