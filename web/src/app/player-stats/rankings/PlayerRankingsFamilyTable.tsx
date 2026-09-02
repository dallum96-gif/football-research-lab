"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import type { RankingMetric } from "../PlayerVisuals";
import familyStyles from "./PlayerRankingsFamilyTable.module.css";

type MinutesShare = 0 | 10 | 25 | 50 | 75;
type NormalizationView = "RAW" | "PER_90";

type NormalizedRankingMetric = RankingMetric & {
  concept_key?: string;
  normalization?: string;
  supported_normalizations?: string[];
};

type PlayerRow = {
  player_code: string;
  player_name: string;
  clubs: string[];
  minutes: number;
};

const MINUTES_OPTIONS: MinutesShare[] = [0, 10, 25, 50, 75];
const NORMALIZATION_OPTIONS: Array<{
  value: NormalizationView;
  label: string;
}> = [
  { value: "RAW", label: "Raw" },
  { value: "PER_90", label: "Per 90" },
];
const MAX_VISIBLE_METRICS = 4;
const TILE_TONES = ["coral", "green", "gold", "blue"] as const;

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

function conceptKey(metric: NormalizedRankingMetric) {
  return metric.concept_key ?? metric.key;
}

function normalization(metric: NormalizedRankingMetric) {
  return metric.normalization ?? (metric.key.endsWith("_per_90") ? "PER_90" : "RAW");
}

function conceptLabel(metrics: NormalizedRankingMetric[]) {
  const raw = metrics.find((metric) => normalization(metric) === "RAW");
  if (raw) return raw.label;
  const rate = metrics.find((metric) => normalization(metric) === "RATE");
  if (rate) return rate.label;
  return (metrics[0]?.label ?? "").replace(/\s*\/\s*90$/i, "");
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
    () =>
      metrics.filter(
        (metric) => metric.availability !== "UNAVAILABLE"
      ) as NormalizedRankingMetric[],
    [metrics]
  );

  const conceptGroups = useMemo(() => {
    const groups = new Map<string, NormalizedRankingMetric[]>();
    for (const metric of availableMetrics) {
      const key = conceptKey(metric);
      const group = groups.get(key) ?? [];
      group.push(metric);
      groups.set(key, group);
    }
    return groups;
  }, [availableMetrics]);

  const [normalizationView, setNormalizationView] =
    useState<NormalizationView>("RAW");

  const selectableMetrics = useMemo(() => {
    const selected: Array<{
      concept: string;
      label: string;
      metric: NormalizedRankingMetric;
    }> = [];

    for (const [concept, group] of conceptGroups) {
      const invariantRate = group.find(
        (metric) => normalization(metric) === "RATE"
      );
      const metric =
        invariantRate ??
        group.find((candidate) => normalization(candidate) === normalizationView);

      if (metric) {
        selected.push({
          concept,
          label: conceptLabel(group),
          metric,
        });
      }
    }

    return selected;
  }, [conceptGroups, normalizationView]);

  const selectableConceptKeys = useMemo(
    () => selectableMetrics.map((item) => item.concept),
    [selectableMetrics]
  );

  const [visibleConcepts, setVisibleConcepts] = useState<string[]>(() =>
    selectableMetrics
      .slice(0, MAX_VISIBLE_METRICS)
      .map((item) => item.concept)
  );
  const [club, setClub] = useState("ALL");
  const [minutesShare, setMinutesShare] = useState<MinutesShare>(25);

  useEffect(() => {
    setVisibleConcepts((current) => {
      const next = current
        .filter((key) => selectableConceptKeys.includes(key))
        .slice(0, MAX_VISIBLE_METRICS);

      for (const key of selectableConceptKeys) {
        if (next.length >= MAX_VISIBLE_METRICS) break;
        if (!next.includes(key)) next.push(key);
      }

      return next.length === current.length &&
        next.every((key, index) => key === current[index])
        ? current
        : next;
    });
  }, [selectableConceptKeys]);

  const metricByConcept = useMemo(
    () =>
      new Map(
        selectableMetrics.map(({ concept, metric }) => [concept, metric])
      ),
    [selectableMetrics]
  );

  const entriesByMetric = useMemo(
    () =>
      new Map(
        availableMetrics.map((metric) => [
          metric.key,
          new Map(
            metric.entries.map((entry) => [entry.player_code, entry])
          ),
        ])
      ),
    [availableMetrics]
  );

  const visibleMetrics = useMemo(
    () =>
      visibleConcepts
        .map((key) => metricByConcept.get(key))
        .filter(
          (metric): metric is NormalizedRankingMetric => Boolean(metric)
        ),
    [metricByConcept, visibleConcepts]
  );

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

  const filteredRows = useMemo(
    () =>
      rows.filter((row) => {
        if (club !== "ALL" && !row.clubs.includes(club)) return false;
        if (minutesShare === 0) return true;

        const possibleMinutes = row.clubs.reduce<number | null>(
          (found, playerClub) =>
            found ??
            possibleMinutesLookup.get(
              playerClub.toLocaleLowerCase("en-GB")
            ) ??
            null,
          null
        );

        if (possibleMinutes == null || possibleMinutes <= 0) return false;
        return row.minutes >= possibleMinutes * (minutesShare / 100);
      }),
    [club, minutesShare, possibleMinutesLookup, rows]
  );

  const leaderboards = useMemo(
    () =>
      visibleMetrics.map((metric) => {
        const entries = entriesByMetric.get(metric.key);
        const players = filteredRows
          .flatMap((row) => {
            const entry = entries?.get(row.player_code);
            return entry && entry.value != null ? [{ row, entry }] : [];
          })
          .sort((a, b) => {
            const aRank = a.entry.rank ?? Number.POSITIVE_INFINITY;
            const bRank = b.entry.rank ?? Number.POSITIVE_INFINITY;
            if (aRank !== bRank) return aRank - bRank;

            const aPercentile = a.entry.percentile ?? -1;
            const bPercentile = b.entry.percentile ?? -1;
            if (aPercentile !== bPercentile) return bPercentile - aPercentile;

            if (a.entry.value !== b.entry.value) {
              return metric.higher_is_better
                ? (b.entry.value ?? 0) - (a.entry.value ?? 0)
                : (a.entry.value ?? 0) - (b.entry.value ?? 0);
            }

            return a.row.player_name.localeCompare(b.row.player_name, "en-GB", {
              sensitivity: "base",
            });
          })
          .slice(0, 10);

        return { metric, players };
      }),
    [entriesByMetric, filteredRows, visibleMetrics]
  );

  function toggleMetric(concept: string) {
    setVisibleConcepts((current) => {
      if (current.includes(concept)) {
        return current.filter((candidate) => candidate !== concept);
      }
      if (current.length >= MAX_VISIBLE_METRICS) return current;
      return [...current, concept];
    });
  }

  const selectionIsFull = visibleConcepts.length >= MAX_VISIBLE_METRICS;

  return (
    <>
      <section className={familyStyles.familyControlsPanel}>
        <div className={familyStyles.familyControlsHeading}>
          <div>
            <p className={familyStyles.familyKicker}>Build your leaderboards</p>
            <h2>{familyLabel} rankings</h2>
          </div>
          <span>
            Club and minutes filters change who appears. The underlying order
            remains governed against the full {position} cohort.
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

          <div className={familyStyles.minutesFilter}>
            <span>Stat view</span>
            <div>
              {NORMALIZATION_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  data-active={
                    normalizationView === option.value ? "true" : "false"
                  }
                  aria-pressed={normalizationView === option.value}
                  onClick={() => setNormalizationView(option.value)}
                >
                  {option.label}
                </button>
              ))}
            </div>
            <small>Rates such as pass completion stay unchanged</small>
          </div>
        </div>

        <div className={familyStyles.metricChooser}>
          <div className={familyStyles.metricChooserHeading}>
            <div>
              <span>Leaderboard tiles</span>
              <strong aria-live="polite">
                {visibleConcepts.length} of {MAX_VISIBLE_METRICS} selected
              </strong>
            </div>
            <p>
              {selectionIsFull
                ? "Remove one tile to choose another."
                : `Choose ${MAX_VISIBLE_METRICS - visibleConcepts.length} more.`}
            </p>
          </div>
          <div className={familyStyles.familyMetricPills}>
            {selectableMetrics.map(({ concept, label }) => {
              const active = visibleConcepts.includes(concept);
              const disabled = selectionIsFull && !active;
              return (
                <button
                  key={concept}
                  type="button"
                  data-active={active ? "true" : "false"}
                  aria-pressed={active}
                  disabled={disabled}
                  title={disabled ? "Remove a selected metric first" : undefined}
                  onClick={() => toggleMetric(concept)}
                >
                  {label}
                </button>
              );
            })}
          </div>
        </div>
      </section>

      <section className={familyStyles.leaderboardSection}>
        <header className={familyStyles.leaderboardHeading}>
          <div>
            <p className={familyStyles.familyKicker}>Top ten</p>
            <h2>{familyLabel} · {position}</h2>
          </div>
          <span>
            {filteredRows.length} of {rows.length} players visible · {cohortDescription}
          </span>
        </header>

        {leaderboards.length > 0 ? (
          <div className={familyStyles.leaderboardGrid}>
            {leaderboards.map(({ metric, players }, tileIndex) => (
              <article
                className={familyStyles.leaderboardCard}
                data-tone={TILE_TONES[tileIndex % TILE_TONES.length]}
                key={metric.key}
              >
                <header className={familyStyles.cardHeader}>
                  <div>
                    <span>
                      Top 10 · {position} ·{" "}
                      {normalization(metric) === "PER_90"
                        ? "Per 90"
                        : normalization(metric) === "RAW"
                        ? "Raw"
                        : "Rate"}
                    </span>
                    <h3>{metric.label}</h3>
                  </div>
                  <strong>{metric.unit || "Value"}</strong>
                </header>

                {players.length > 0 ? (
                  <ol className={familyStyles.leaderboardList}>
                    {players.map(({ row, entry }, index) => (
                      <li key={row.player_code}>
                        <Link
                          href={`/player-stats?season=${encodeURIComponent(
                            season
                          )}&player=${encodeURIComponent(row.player_code)}`}
                          title={
                            entry.rank != null
                              ? `League rank ${entry.rank} of ${entry.out_of}`
                              : `Open ${row.player_name} in Player Stats`
                          }
                        >
                          <span
                            className={familyStyles.listRank}
                            data-podium={index < 3 ? String(index + 1) : undefined}
                          >
                            {String(index + 1).padStart(2, "0")}
                          </span>
                          <span className={familyStyles.playerIdentity}>
                            <strong>{row.player_name}</strong>
                            <small>
                              {row.clubs.join(" · ") || "No club"} · {row.minutes} min
                            </small>
                          </span>
                          <span className={familyStyles.metricValue}>
                            {formatMetric(metric, entry.value)}
                          </span>
                        </Link>
                      </li>
                    ))}
                  </ol>
                ) : (
                  <div className={familyStyles.cardEmpty}>
                    No players meet the current filters.
                  </div>
                )}

                <footer>
                  Best {players.length} matching the current filters
                  <span>{players.length}/10</span>
                </footer>
              </article>
            ))}
          </div>
        ) : (
          <div className={familyStyles.noTiles}>
            Choose at least one metric to show a leaderboard.
          </div>
        )}
      </section>
    </>
  );
}
