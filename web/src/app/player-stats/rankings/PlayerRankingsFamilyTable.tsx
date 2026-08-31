"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { RankingMetric } from "../PlayerVisuals";
import rankingStyles from "./PlayerRankings.module.css";
import familyStyles from "./PlayerRankingsFamilyTable.module.css";

type SortDirection = "asc" | "desc";

type PlayerRow = {
  player_code: string;
  player_name: string;
  clubs: string[];
  minutes: number;
};

function trim(value: number, decimals: number) {
  const fixed = value.toFixed(decimals);
  return fixed.includes(".")
    ? fixed.replace(/0+$/, "").replace(/\.$/, "")
    : fixed;
}

function formatMetric(metric: RankingMetric, value: number | null) {
  if (value == null) return "—";
  if (Number.isInteger(value)) return String(value);
  if (metric.unit === "%") return `${trim(value, 1)}%`;
  if (["xG", "xA", "xGI", "xGC"].includes(metric.unit)) {
    return trim(value, 2);
  }
  return trim(value, 2);
}

function sortIndicator(
  key: string,
  activeKey: string,
  direction: SortDirection
) {
  if (key !== activeKey) return "↕";
  return direction === "asc" ? "↑" : "↓";
}

export function PlayerRankingsFamilyTable({
  season,
  familyLabel,
  position,
  metrics,
  cohortDescription,
}: {
  season: string;
  familyLabel: string;
  position: string;
  metrics: RankingMetric[];
  cohortDescription: string;
}) {
  const availableMetrics = useMemo(
    () => metrics.filter((metric) => metric.availability !== "UNAVAILABLE"),
    [metrics]
  );

  const [visibleKeys, setVisibleKeys] = useState<string[]>(
    availableMetrics.map((metric) => metric.key)
  );
  const [sortKey, setSortKey] = useState<string>("player");
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc");

  const metricsByKey = useMemo(
    () => new Map(availableMetrics.map((metric) => [metric.key, metric])),
    [availableMetrics]
  );

  const visibleMetrics = visibleKeys
    .map((key) => metricsByKey.get(key))
    .filter((metric): metric is RankingMetric => Boolean(metric));

  const rows = useMemo(() => {
    const players = new Map<string, PlayerRow>();
    for (const metric of availableMetrics) {
      for (const entry of metric.entries) {
        if (!players.has(entry.player_code)) {
          players.set(entry.player_code, {
            player_code: entry.player_code,
            player_name: entry.player_name,
            clubs: entry.clubs,
            minutes: entry.minutes,
          });
        }
      }
    }
    return [...players.values()];
  }, [availableMetrics]);

  function metricValue(metricKey: string, playerCode: string) {
    const metric = metricsByKey.get(metricKey);
    if (!metric) return null;
    return (
      metric.entries.find((entry) => entry.player_code === playerCode)?.value ??
      null
    );
  }

  const sortedRows = [...rows].sort((a, b) => {
    let comparison = 0;

    if (sortKey === "player") {
      comparison = a.player_name.localeCompare(b.player_name, "en-GB", {
        sensitivity: "base",
      });
    } else if (sortKey === "club") {
      comparison = (a.clubs.join(" · ") || "").localeCompare(
        b.clubs.join(" · ") || "",
        "en-GB",
        { sensitivity: "base" }
      );
    } else if (sortKey === "minutes") {
      comparison = a.minutes - b.minutes;
    } else {
      const aValue = metricValue(sortKey, a.player_code);
      const bValue = metricValue(sortKey, b.player_code);

      if (aValue == null && bValue == null) comparison = 0;
      else if (aValue == null) return 1;
      else if (bValue == null) return -1;
      else comparison = aValue - bValue;
    }

    if (comparison === 0) {
      comparison = a.player_name.localeCompare(b.player_name, "en-GB", {
        sensitivity: "base",
      });
    }

    return sortDirection === "asc" ? comparison : -comparison;
  });

  function changeSort(key: string, numeric = false) {
    if (sortKey === key) {
      setSortDirection((current) => (current === "asc" ? "desc" : "asc"));
      return;
    }

    setSortKey(key);
    setSortDirection(numeric ? "desc" : "asc");
  }

  function toggleMetric(key: string) {
    setVisibleKeys((current) => {
      const next = current.includes(key)
        ? current.filter((candidate) => candidate !== key)
        : [...current, key];

      if (sortKey === key && !next.includes(key)) {
        setSortKey("player");
        setSortDirection("asc");
      }

      return next;
    });
  }

  const gridTemplateColumns = `42px minmax(180px, 1.35fr) minmax(125px, .9fr) 78px ${visibleMetrics
    .map(() => "minmax(105px, .8fr)")
    .join(" ")}`;

  return (
    <>
      <section className={rankingStyles.rankingMetricNav}>
        <div>
          <p className={familyStyles.familyKicker}>Metrics</p>
          <h2>{familyLabel}</h2>
        </div>

        <div
          className={`${rankingStyles.metricPills} ${familyStyles.familyMetricPills}`}
        >
          {availableMetrics.map((metric) => {
            const active = visibleKeys.includes(metric.key);
            return (
              <button
                key={metric.key}
                type="button"
                data-active={active ? "true" : "false"}
                aria-pressed={active}
                onClick={() => toggleMetric(metric.key)}
              >
                {metric.label}
              </button>
            );
          })}
        </div>
      </section>

      <section className={rankingStyles.rankingPanel}>
        <header className={familyStyles.familyTableHeading}>
          <div>
            <p className={familyStyles.familyKicker}>{familyLabel}</p>
            <h2>{familyLabel} · {position}</h2>
          </div>
          <span>{cohortDescription}</span>
        </header>

        <div className={familyStyles.familyTableScroll}>
          <div
            className={familyStyles.familyTable}
            style={{ minWidth: `${520 + visibleMetrics.length * 112}px` }}
          >
            <div
              className={familyStyles.familyTableHeader}
              style={{ gridTemplateColumns }}
            >
              <span>#</span>
              <button type="button" onClick={() => changeSort("player")}>
                Player {sortIndicator("player", sortKey, sortDirection)}
              </button>
              <button type="button" onClick={() => changeSort("club")}>
                Club {sortIndicator("club", sortKey, sortDirection)}
              </button>
              <button type="button" onClick={() => changeSort("minutes", true)}>
                Minutes {sortIndicator("minutes", sortKey, sortDirection)}
              </button>
              {visibleMetrics.map((metric) => (
                <button
                  type="button"
                  key={metric.key}
                  onClick={() => changeSort(metric.key, true)}
                >
                  {metric.label} {sortIndicator(metric.key, sortKey, sortDirection)}
                </button>
              ))}
            </div>

            {sortedRows.map((row, index) => (
              <div
                className={familyStyles.familyTableRow}
                style={{ gridTemplateColumns }}
                key={row.player_code}
              >
                <span className={familyStyles.familyRowNumber}>{index + 1}</span>
                <Link
                  href={`/player-stats?season=${encodeURIComponent(
                    season
                  )}&player=${encodeURIComponent(row.player_code)}`}
                >
                  {row.player_name}
                </Link>
                <span>{row.clubs.join(" · ") || "—"}</span>
                <strong>{row.minutes}</strong>
                {visibleMetrics.map((metric) => {
                  const entry = metric.entries.find(
                    (candidate) => candidate.player_code === row.player_code
                  );
                  return (
                    <span className={familyStyles.familyMetricCell} key={metric.key}>
                      <strong>{formatMetric(metric, entry?.value ?? null)}</strong>
                      {entry?.percentile != null && (
                        <small>P{Math.round(entry.percentile)}</small>
                      )}
                    </span>
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
