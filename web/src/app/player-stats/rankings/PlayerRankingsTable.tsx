"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { RankingMetric } from "../PlayerVisuals";
import rankingStyles from "./PlayerRankings.module.css";

const FAMILY_ORDER = [
  "shooting",
  "creation",
  "possession",
  "defending",
  "discipline",
  "goalkeeping",
  "fpl",
];

const FAMILY_LABELS: Record<string, string> = {
  shooting: "Shooting",
  creation: "Creation",
  possession: "Possession",
  defending: "Defending",
  discipline: "Discipline",
  goalkeeping: "Goalkeeping",
  fpl: "FPL",
};

type SortDirection = "asc" | "desc";
type FixedSortKey = "player" | "club" | "minutes";

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

export function PlayerRankingsTable({
  season,
  metrics,
  overviewKeys,
  cohortDescription,
}: {
  season: string;
  metrics: RankingMetric[];
  overviewKeys: string[];
  cohortDescription: string;
}) {
  const availableMetrics = useMemo(
    () => metrics.filter((metric) => metric.availability !== "UNAVAILABLE"),
    [metrics]
  );

  const initialKeys = useMemo(() => {
    const available = new Set(availableMetrics.map((metric) => metric.key));
    const overview = overviewKeys.filter((key) => available.has(key));
    return overview.length ? overview : availableMetrics.slice(0, 6).map((metric) => metric.key);
  }, [availableMetrics, overviewKeys]);

  const [visibleKeys, setVisibleKeys] = useState<string[]>(initialKeys);
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
    return metric.entries.find((entry) => entry.player_code === playerCode)?.value ?? null;
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

  function changeSort(key: FixedSortKey | string, numeric = false) {
    if (sortKey === key) {
      setSortDirection((current) => (current === "asc" ? "desc" : "asc"));
      return;
    }

    setSortKey(key);
    setSortDirection(numeric ? "desc" : "asc");
  }

  function toggleMetric(key: string) {
    setVisibleKeys((current) =>
      current.includes(key)
        ? current.filter((candidate) => candidate !== key)
        : [...current, key]
    );
  }

  function resetOverview() {
    setVisibleKeys(initialKeys);
  }

  const groupedMetrics = FAMILY_ORDER.map((family) => ({
    family,
    metrics: availableMetrics.filter((metric) => metric.family === family),
  })).filter((group) => group.metrics.length > 0);

  const gridTemplateColumns = `42px minmax(180px, 1.35fr) minmax(125px, .9fr) 78px ${visibleMetrics
    .map(() => "minmax(105px, .8fr)")
    .join(" ")}`;

  return (
    <>
      <section className={rankingStyles.columnControlPanel}>
        <div className={rankingStyles.columnControlIntro}>
          <div>
            <p className={rankingStyles.controlKicker}>Table columns</p>
            <h2>Build the ranking view</h2>
          </div>
          <div className={rankingStyles.controlMeta}>
            <span>{visibleMetrics.length} metric columns visible</span>
            <button type="button" onClick={resetOverview}>
              Reset overview
            </button>
          </div>
        </div>

        <div className={rankingStyles.metricToggleGroups}>
          {groupedMetrics.map(({ family, metrics: familyMetrics }) => (
            <div className={rankingStyles.metricToggleGroup} key={family}>
              <span>{FAMILY_LABELS[family] ?? family}</span>
              <div>
                {familyMetrics.map((metric) => {
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
            </div>
          ))}
        </div>
      </section>

      <section className={rankingStyles.unifiedRankingPanel}>
        <header className={rankingStyles.unifiedRankingHeading}>
          <div>
            <p className={rankingStyles.controlKicker}>League rankings</p>
            <h2>Sortable player table</h2>
          </div>
          <span>{cohortDescription}</span>
        </header>

        <div className={rankingStyles.unifiedTableScroll}>
          <div
            className={rankingStyles.unifiedTable}
            style={{ minWidth: `${520 + visibleMetrics.length * 112}px` }}
          >
            <div
              className={rankingStyles.unifiedHeader}
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
                className={rankingStyles.unifiedRow}
                style={{ gridTemplateColumns }}
                key={row.player_code}
              >
                <span className={rankingStyles.rowNumber}>{index + 1}</span>
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
                    <span className={rankingStyles.metricCell} key={metric.key}>
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
