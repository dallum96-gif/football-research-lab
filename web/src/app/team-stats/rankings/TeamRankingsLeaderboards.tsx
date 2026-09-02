"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { TeamKit } from "../../teams/TeamKit";
import tileStyles from "../StatsListTiles.module.css";

export type TeamRankingTileEntry = {
  persistent_team_code: string;
  display_name: string;
  value: number | null;
  rank: number | null;
  out_of: number;
  percentile: number | null;
};

export type TeamRankingTileMetric = {
  key: string;
  label: string;
  unit: string;
  higher_is_better: boolean;
  entries: TeamRankingTileEntry[];
};

const MAX_VISIBLE_METRICS = 4;
const TILE_TONES = ["coral", "green", "gold", "blue"] as const;

function trim(value: number, decimals: number) {
  const fixed = value.toFixed(decimals);
  return fixed.includes(".")
    ? fixed.replace(/0+$/, "").replace(/\.$/, "")
    : fixed;
}

function formatMetric(metric: TeamRankingTileMetric, value: number | null) {
  if (value === null) return "—";
  if (metric.unit === "%") return `${trim(value, 1)}%`;
  if (
    metric.key === "goals_for_per_match" ||
    metric.key === "goals_against_per_match" ||
    metric.key === "points_per_match"
  ) {
    return trim(value, 1);
  }
  return trim(value, Number.isInteger(value) ? 0 : 2);
}

function rankingHref(
  season: string,
  family: string,
  metric: string,
  selectedTeamCode?: string
) {
  const params = new URLSearchParams({ season, family, metric });
  if (selectedTeamCode) params.set("team", selectedTeamCode);
  return `/team-stats/rankings?${params.toString()}`;
}

function teamHref(season: string, family: string, teamCode: string) {
  const params = new URLSearchParams({ season, team: teamCode });
  if (family !== "overview") params.set("family", family);
  return `/team-stats?${params.toString()}`;
}

export function TeamRankingsLeaderboards({
  season,
  family,
  familyLabel,
  metrics,
  selectedTeamCode,
  populationSize,
}: {
  season: string;
  family: string;
  familyLabel: string;
  metrics: TeamRankingTileMetric[];
  selectedTeamCode?: string;
  populationSize: number;
}) {
  const availableMetricKeys = useMemo(() => metrics.map((metric) => metric.key), [metrics]);
  const [visibleKeys, setVisibleKeys] = useState<string[]>(() =>
    metrics.slice(0, MAX_VISIBLE_METRICS).map((metric) => metric.key)
  );

  useEffect(() => {
    setVisibleKeys((current) => {
      const next = current
        .filter((key) => availableMetricKeys.includes(key))
        .slice(0, MAX_VISIBLE_METRICS);
      for (const key of availableMetricKeys) {
        if (next.length >= MAX_VISIBLE_METRICS) break;
        if (!next.includes(key)) next.push(key);
      }
      return next.length === current.length && next.every((key, index) => key === current[index])
        ? current
        : next;
    });
  }, [availableMetricKeys]);

  const metricsByKey = useMemo(
    () => new Map(metrics.map((metric) => [metric.key, metric])),
    [metrics]
  );
  const visibleMetrics = useMemo(
    () =>
      visibleKeys
        .map((key) => metricsByKey.get(key))
        .filter((metric): metric is TeamRankingTileMetric => Boolean(metric)),
    [metricsByKey, visibleKeys]
  );

  function toggleMetric(key: string) {
    setVisibleKeys((current) => {
      if (current.includes(key)) return current.filter((candidate) => candidate !== key);
      if (current.length >= MAX_VISIBLE_METRICS) return current;
      return [...current, key];
    });
  }

  const selectionIsFull = visibleKeys.length >= MAX_VISIBLE_METRICS;

  return (
    <>
      <section className={tileStyles.familyControlsPanel}>
        <div className={tileStyles.familyControlsHeading}>
          <div>
            <p className={tileStyles.familyKicker}>Build your leaderboards</p>
            <h2>{familyLabel} rankings</h2>
          </div>
          <span>
            Choose up to four metrics. Each tile shows the governed top ten for the same Premier League population.
          </span>
        </div>

        <div className={tileStyles.metricChooser}>
          <div className={tileStyles.metricChooserHeading}>
            <div>
              <span>Leaderboard tiles</span>
              <strong aria-live="polite">
                {visibleKeys.length} of {MAX_VISIBLE_METRICS} selected
              </strong>
            </div>
            <p>
              {selectionIsFull
                ? "Remove one tile to choose another."
                : `Choose ${MAX_VISIBLE_METRICS - visibleKeys.length} more.`}
            </p>
          </div>
          <div className={tileStyles.familyMetricPills}>
            {metrics.map((metric) => {
              const active = visibleKeys.includes(metric.key);
              const disabled = selectionIsFull && !active;
              return (
                <button
                  key={metric.key}
                  type="button"
                  data-active={active ? "true" : "false"}
                  aria-pressed={active}
                  disabled={disabled}
                  title={disabled ? "Remove a selected metric first" : undefined}
                  onClick={() => toggleMetric(metric.key)}
                >
                  {metric.label}
                </button>
              );
            })}
          </div>
        </div>
      </section>

      <section className={tileStyles.leaderboardSection}>
        <header className={tileStyles.leaderboardHeading}>
          <div>
            <p className={tileStyles.familyKicker}>Top ten</p>
            <h2>{familyLabel} · Premier League</h2>
          </div>
          <span>{populationSize} team population · click a team to open Team View</span>
        </header>

        {visibleMetrics.length > 0 ? (
          <div className={tileStyles.leaderboardGrid}>
            {visibleMetrics.map((metric, tileIndex) => {
              const rankedEntries = metric.entries
                .filter((entry) => entry.rank !== null && entry.value !== null)
                .sort((a, b) => (a.rank ?? Number.POSITIVE_INFINITY) - (b.rank ?? Number.POSITIVE_INFINITY));
              const leaders = rankedEntries.slice(0, 10);
              const selectedEntry = selectedTeamCode
                ? rankedEntries.find((entry) => entry.persistent_team_code === selectedTeamCode)
                : undefined;

              return (
                <article
                  className={tileStyles.leaderboardCard}
                  data-tone={TILE_TONES[tileIndex % TILE_TONES.length]}
                  key={metric.key}
                >
                  <header className={tileStyles.cardHeader}>
                    <div>
                      <span>Top 10 · teams</span>
                      <h3>{metric.label}</h3>
                    </div>
                    <Link
                      className={tileStyles.fullRankingLink}
                      href={rankingHref(season, family, metric.key, selectedTeamCode)}
                    >
                      Full ranking
                    </Link>
                  </header>

                  <ol className={tileStyles.leaderboardList}>
                    {leaders.map((entry, index) => (
                      <li
                        key={entry.persistent_team_code}
                        data-selected={entry.persistent_team_code === selectedTeamCode ? "true" : "false"}
                      >
                        <Link href={teamHref(season, family, entry.persistent_team_code)}>
                          <span
                            className={tileStyles.listRank}
                            data-podium={index < 3 ? String(index + 1) : undefined}
                          >
                            {String(index + 1).padStart(2, "0")}
                          </span>
                          <span className={tileStyles.teamIdentity}>
                            <span className={tileStyles.teamKit}>
                              <TeamKit teamName={entry.display_name} />
                            </span>
                            <strong>{entry.display_name}</strong>
                          </span>
                          <span className={tileStyles.metricValue}>
                            {formatMetric(metric, entry.value)}
                          </span>
                        </Link>
                      </li>
                    ))}
                  </ol>

                  <footer>
                    <span>
                      {selectedEntry?.rank != null
                        ? `Selected: ${selectedEntry.rank}/${selectedEntry.out_of}`
                        : metric.higher_is_better
                          ? "Higher ranks first"
                          : "Lower ranks first"}
                    </span>
                    <span>{leaders.length}/10</span>
                  </footer>
                </article>
              );
            })}
          </div>
        ) : (
          <div className={tileStyles.noTiles}>Choose at least one metric to show a leaderboard.</div>
        )}
      </section>
    </>
  );
}
