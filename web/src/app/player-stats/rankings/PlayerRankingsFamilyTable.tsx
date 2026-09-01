"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { RankingMetric } from "../PlayerVisuals";
import rankingStyles from "./PlayerRankings.module.css";
import familyStyles from "./PlayerRankingsFamilyTable.module.css";

type SortDirection = "asc" | "desc";
type MinutesShare = 0 | 10 | 25 | 50 | 75;

type PlayerRow = {
  player_code: string;
  player_name: string;
  clubs: string[];
  minutes: number;
};

const MINUTES_OPTIONS: MinutesShare[] = [0, 10, 25, 50, 75];

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

function ordinal(value: number) {
  const mod100 = value % 100;
  if (mod100 >= 11 && mod100 <= 13) return `${value}th`;
  const suffix =
    value % 10 === 1
      ? "st"
      : value % 10 === 2
        ? "nd"
        : value % 10 === 3
          ? "rd"
          : "th";
  return `${value}${suffix}`;
}

function sortIndicator(
  key: string,
  activeKey: string,
  direction: SortDirection
) {
  if (key !== activeKey) return "↕";
  return direction === "asc" ? "↑" : "↓";
}

function median(values: number[]) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0
    ? (sorted[middle - 1] + sorted[middle]) / 2
    : sorted[middle];
}

export function PlayerRankingsFamilyTable({
  season,
  familyLabel,
  position,
  metrics,
  cohortDescription,
  possibleMinutesByClub,
}: {
  season: string;
  familyLabel: string;
  position: string;
  metrics: RankingMetric[];
  cohortDescription: string;
  possibleMinutesByClub: Record<string, number>;
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
  const [club, setClub] = useState("ALL");
  const [minutesShare, setMinutesShare] = useState<MinutesShare>(25);

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

  const clubs = useMemo(
    () =>
      [...new Set(rows.flatMap((row) => row.clubs).filter(Boolean))].sort(
        (a, b) => a.localeCompare(b, "en-GB")
      ),
    [rows]
  );

  const possibleMinutesLookup = useMemo(
    () =>
      new Map(
        Object.entries(possibleMinutesByClub).map(([name, value]) => [
          name.toLocaleLowerCase("en-GB"),
          value,
        ])
      ),
    [possibleMinutesByClub]
  );

  function metricEntry(metricKey: string, playerCode: string) {
    return metricsByKey
      .get(metricKey)
      ?.entries.find((entry) => entry.player_code === playerCode);
  }

  function possibleMinutes(row: PlayerRow) {
    for (const playerClub of row.clubs) {
      const value = possibleMinutesLookup.get(
        playerClub.toLocaleLowerCase("en-GB")
      );
      if (value != null && value > 0) return value;
    }
    return null;
  }

  const filteredRows = rows.filter((row) => {
    if (club !== "ALL" && !row.clubs.includes(club)) return false;
    if (minutesShare === 0) return true;
    const available = possibleMinutes(row);
    if (available == null) return false;
    return row.minutes >= available * (minutesShare / 100);
  });

  const sortedRows = [...filteredRows].sort((a, b) => {
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
      const aPercentile = metricEntry(sortKey, a.player_code)?.percentile ?? null;
      const bPercentile = metricEntry(sortKey, b.player_code)?.percentile ?? null;

      if (aPercentile == null && bPercentile == null) comparison = 0;
      else if (aPercentile == null) return 1;
      else if (bPercentile == null) return -1;
      else comparison = aPercentile - bPercentile;
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

  const primaryMetric = visibleMetrics[0] ?? availableMetrics[0] ?? null;
  const primaryEntries = primaryMetric
    ? filteredRows
        .map((row) => metricEntry(primaryMetric.key, row.player_code))
        .filter(
          (entry): entry is NonNullable<typeof entry> =>
            Boolean(entry && entry.value != null && entry.percentile != null)
        )
    : [];
  const leader = [...primaryEntries].sort(
    (a, b) => (b.percentile ?? -1) - (a.percentile ?? -1)
  )[0];
  const medianValue = primaryMetric
    ? median(
        primaryEntries
          .map((entry) => entry.value)
          .filter((value): value is number => value != null)
      )
    : null;

  const profileMetrics = visibleMetrics.length
    ? visibleMetrics
    : primaryMetric
      ? [primaryMetric]
      : [];
  const standout = filteredRows
    .map((row) => {
      const percentiles = profileMetrics
        .map((metric) => metricEntry(metric.key, row.player_code)?.percentile)
        .filter((value): value is number => value != null);
      const average = percentiles.length
        ? percentiles.reduce((sum, value) => sum + value, 0) /
          percentiles.length
        : null;
      return { row, average };
    })
    .filter(
      (item): item is { row: PlayerRow; average: number } => item.average != null
    )
    .sort((a, b) => b.average - a.average)[0];

  const gridTemplateColumns = `42px minmax(200px, 1.25fr) minmax(135px, .85fr) 82px ${visibleMetrics
    .map(() => "minmax(150px, .95fr)")
    .join(" ")}`;

  return (
    <>
      <section className={familyStyles.familyControlsPanel}>
        <div className={familyStyles.familyControlsHeading}>
          <div>
            <p className={familyStyles.familyKicker}>Explore the family</p>
            <h2>{familyLabel} rankings</h2>
          </div>
          <span>
            Filters change the visible players only. Every rank and percentile
            remains calculated against the full governed {position} cohort.
          </span>
        </div>

        <div className={familyStyles.familyFilters}>
          <label className={familyStyles.clubFilter}>
            <span>Club</span>
            <select value={club} onChange={(event) => setClub(event.target.value)}>
              <option value="ALL">All clubs</option>
              {clubs.map((item) => (
                <option value={item} key={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <div className={familyStyles.minutesFilter}>
            <span>Minutes played</span>
            <div>
              {MINUTES_OPTIONS.map((share) => (
                <button
                  key={share}
                  type="button"
                  data-active={minutesShare === share ? "true" : "false"}
                  aria-pressed={minutesShare === share}
                  onClick={() => setMinutesShare(share)}
                >
                  {share === 0 ? "All" : `${share}%+`}
                </button>
              ))}
            </div>
            <small>Share of possible club league minutes</small>
          </div>
        </div>

        <div className={familyStyles.metricChooser}>
          <div>
            <span>Metric columns</span>
            <button
              type="button"
              onClick={() =>
                setVisibleKeys(availableMetrics.map((metric) => metric.key))
              }
            >
              Show all
            </button>
          </div>
          <div className={familyStyles.familyMetricPills}>
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
        </div>
      </section>

      <section className={familyStyles.insightStrip}>
        <article>
          <span>Visible population</span>
          <strong>{filteredRows.length}</strong>
          <small>of {rows.length} {position} players</small>
        </article>
        <article>
          <span>{primaryMetric?.label ?? "Primary metric"} leader</span>
          <strong>{leader?.player_name ?? "—"}</strong>
          <small>
            {leader?.percentile != null
              ? `P${Math.round(leader.percentile)} · ${formatMetric(
                  primaryMetric!,
                  leader.value
                )}`
              : "No visible value"}
          </small>
        </article>
        <article>
          <span>Visible median</span>
          <strong>
            {primaryMetric && medianValue != null
              ? formatMetric(primaryMetric, medianValue)
              : "—"}
          </strong>
          <small>{primaryMetric?.label ?? "No metric selected"}</small>
        </article>
        <article>
          <span>Profile standout</span>
          <strong>{standout?.row.player_name ?? "—"}</strong>
          <small>
            {standout ? `P${Math.round(standout.average)} average` : "No visible profile"}
          </small>
        </article>
      </section>

      <section className={rankingStyles.rankingPanel}>
        <header className={familyStyles.familyTableHeading}>
          <div>
            <p className={familyStyles.familyKicker}>League table</p>
            <h2>{familyLabel} · {position}</h2>
          </div>
          <span>{cohortDescription}</span>
        </header>

        <div className={familyStyles.familyTableScroll}>
          <div
            className={familyStyles.familyTable}
            style={{ minWidth: `${560 + visibleMetrics.length * 156}px` }}
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
                  title={`Sort by ${metric.label} league percentile`}
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
                  className={familyStyles.playerCell}
                  href={`/player-stats?season=${encodeURIComponent(
                    season
                  )}&player=${encodeURIComponent(row.player_code)}`}
                >
                  <strong>{row.player_name}</strong>
                  <small>Open Player Stats →</small>
                </Link>
                <span className={familyStyles.clubCell}>
                  {row.clubs.join(" · ") || "—"}
                </span>
                <strong className={familyStyles.minutesCell}>{row.minutes}</strong>
                {visibleMetrics.map((metric) => {
                  const entry = metricEntry(metric.key, row.player_code);
                  const percentile = entry?.percentile ?? null;

                  return (
                    <span className={familyStyles.familyMetricCell} key={metric.key}>
                      <span className={familyStyles.metricCellTop}>
                        <strong>{formatMetric(metric, entry?.value ?? null)}</strong>
                        <span>
                          {entry?.rank != null
                            ? `${ordinal(entry.rank)} / ${entry.out_of}`
                            : "—"}
                        </span>
                        <small>
                          {percentile != null ? `P${Math.round(percentile)}` : "—"}
                        </small>
                      </span>
                    </span>
                  );
                })}
              </div>
            ))}

            {sortedRows.length === 0 && (
              <div className={familyStyles.noRows}>
                No players meet the current club and minutes filters.
              </div>
            )}
          </div>
        </div>
      </section>
    </>
  );
}
