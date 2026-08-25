"use client";

import { useEffect, useState } from "react";
import styles from "./FixturePlayerPerformance.module.css";

type PlayerPerformance = {
  player_id: string | null;
  player_name: string | null;
  position: string | null;
  minutes: number | null;
  value: number | null;
  secondary_value: number | null;
};

type PerformanceMetric = {
  key: string;
  label: string;
  unit: string;
  secondary_label: string | null;
  secondary_unit: string | null;
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

function formatValue(value: number | null, unit: string): string {
  if (value == null || Number.isNaN(value)) return "—";
  if (unit === "%") return `${value.toFixed(1)}%`;
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

function PlayerPerformancePanel({ side }: { side: FixturePlayerPerformanceSide }) {
  const home = side.side === "home";

  return (
    <section className={`${styles.panel} ${home ? styles.home : styles.away}`} aria-label={`${side.team_name} player performance`}>
      <div className={styles.heading}>
        <span className={styles.kicker}>Standout players</span>
        <span className={styles.teamName}>{side.team_name}</span>
      </div>

      <div className={styles.tiles}>
        {side.metrics.map((metric) => {
          const player = metric.player;
          const hasSecondary = metric.secondary_label != null && player?.secondary_value != null;
          const unitLabel = metric.key === "passes_completed"
            ? "completed"
            : metric.key === "tackles_won"
              ? "won"
              : metric.key === "successful_dribbles"
                ? "successful"
                : metric.key === "shots_on_target"
                  ? "on target"
                  : metric.key === "interceptions_won"
                    ? "won"
                    : "created";

          return (
            <article className={styles.tile} key={metric.key}>
              <div className={styles.tileTop}>
                <span className={styles.metricLabel}>{metric.label}</span>
                {player?.position ? <span className={styles.position}>{player.position}</span> : null}
              </div>

              <div className={styles.playerName}>{player?.player_name ?? "No player recorded"}</div>

              <div className={styles.valueLine}>
                <strong className={styles.metricValue}>{formatValue(player?.value ?? null, metric.unit)}</strong>
                <span className={styles.metricUnit}>{unitLabel}</span>
              </div>

              {hasSecondary ? (
                <div className={styles.secondaryLine}>
                  <span>{metric.secondary_label}</span>
                  <strong>{formatValue(player.secondary_value, metric.secondary_unit ?? "")}</strong>
                </div>
              ) : null}
            </article>
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
