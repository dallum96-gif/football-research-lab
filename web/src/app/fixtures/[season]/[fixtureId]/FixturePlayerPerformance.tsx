"use client";

import { useEffect, useState } from "react";
import styles from "./FixturePlayerPerformance.module.css";

type PlayerPerformance = {
  player_id: string | null;
  player_name: string | null;
  position: string | null;
  minutes: number | null;
  value: number | null;
};

type PerformanceMetric = {
  key: string;
  label: string;
  unit: string;
  player: PlayerPerformance | null;
};

type FixturePlayerPerformanceSide = {
  side: "home" | "away";
  team_name: string;
  metrics: PerformanceMetric[];
  status: "AVAILABLE" | "UNAVAILABLE" | "KNOWN_EXCEPTION";
  limitations: string[];
};

type FixturePlayerPerformanceResponse = {
  season: string;
  fixture_id: string;
  home: FixturePlayerPerformanceSide;
  away: FixturePlayerPerformanceSide;
};

type Props = {
  season: string;
  fixtureId: string;
};

const runtimeEnv = (globalThis as typeof globalThis & {
  process?: { env?: Record<string, string | undefined> };
}).process?.env;

const API_BASE = runtimeEnv?.NEXT_PUBLIC_FRL_API_URL ?? "http://127.0.0.1:8000";

function formatValue(metric: PerformanceMetric): string {
  const value = metric.player?.value;
  if (value == null || Number.isNaN(value)) return "—";
  if (metric.unit === "%") return `${value.toFixed(1)}%`;
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

function PlayerPerformancePanel({ side }: { side: FixturePlayerPerformanceSide }) {
  const home = side.side === "home";

  return (
    <section className={`${styles.panel} ${home ? styles.home : styles.away}`} aria-label={`${side.team_name} player performance`}>
      <div className={styles.heading}>
        <span className={styles.kicker}>Player performance</span>
        <span className={styles.teamName}>{side.team_name}</span>
      </div>

      <div className={styles.metrics}>
        {side.metrics.map((metric) => (
          <div className={styles.metricRow} key={metric.key}>
            <div className={styles.metricCopy}>
              <span className={styles.metricLabel}>{metric.label}</span>
              <span className={styles.playerLine}>
                {metric.player?.player_name ?? "No player recorded"}
                {metric.player?.position ? <span className={styles.position}>{metric.player.position}</span> : null}
              </span>
            </div>
            <span className={styles.metricValue}>{formatValue(metric)}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

export function FixturePlayerPerformance({ season, fixtureId }: Props) {
  const [data, setData] = useState<FixturePlayerPerformanceResponse | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    let mounted = true;

    fetch(`${API_BASE}/api/v1/fixtures/${encodeURIComponent(season)}/${encodeURIComponent(fixtureId)}/player-performance`, {
      signal: controller.signal,
      cache: "no-store",
    })
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
      <PlayerPerformancePanel side={data.home} />
      <PlayerPerformancePanel side={data.away} />
    </div>
  );
}
