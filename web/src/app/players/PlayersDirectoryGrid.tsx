"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { ClubKit } from "@/components/ClubKit";
import type { RankingMetric, RankingEntry } from "../player-stats/PlayerVisuals";
import styles from "./PlayersDirectoryGrid.module.css";

type PlayerOption = {
  player_code: string;
  player_name: string;
  position: string;
  clubs: string[];
  minutes: number;
  appearances: number;
  starts: number;
};

export type PositionRankingData = {
  position: string;
  metrics: RankingMetric[];
};

type TileMetric = {
  metric: RankingMetric;
  entry: RankingEntry;
};

type ShowcasePlayer = {
  player: PlayerOption;
  position: string;
  club: string;
  score: number;
  metrics: TileMetric[];
};

type PositionKey = "GKP" | "DEF" | "MID" | "FWD";

const POSITION_OPTIONS: Array<{ value: PositionKey; label: string }> = [
  { value: "GKP", label: "Goalkeepers" },
  { value: "DEF", label: "Defenders" },
  { value: "MID", label: "Midfielders" },
  { value: "FWD", label: "Forwards" },
];

const PROFILE_KEYS: Record<PositionKey, string[]> = {
  GKP: [
    "saves_per_90",
    "clean_sheets_per_90",
    "goals_conceded_per_90",
    "xgc_per_90",
    "bps_per_90",
  ],
  DEF: [
    "defensive_contribution_per_90",
    "cbi_per_90",
    "recoveries_per_90",
    "tackles_per_90",
    "xgi_per_90",
  ],
  MID: [
    "xgi_per_90",
    "xa_per_90",
    "xg_per_90",
    "key_passes_per_90",
    "recoveries_per_90",
  ],
  FWD: [
    "goals_per_90",
    "xg_per_90",
    "xgi_per_90",
    "xa_per_90",
    "key_passes_per_90",
  ],
};

function trim(value: number, decimals = 2) {
  const fixed = value.toFixed(decimals);
  return fixed.includes(".")
    ? fixed.replace(/0+$/, "").replace(/\.$/, "")
    : fixed;
}

function formatMetric(metric: RankingMetric, value: number | null) {
  if (value == null) return "—";
  if (metric.unit === "%") return `${trim(value, 1)}%`;
  return trim(value, Number.isInteger(value) ? 0 : 2);
}

function percentileBand(percentile: number | null) {
  if (percentile == null) return "none";
  if (percentile >= 80) return "elite";
  if (percentile >= 60) return "strong";
  if (percentile >= 40) return "mid";
  return "low";
}

function candidateProfiles(
  players: PlayerOption[],
  rankingsByPosition: Record<string, PositionRankingData | null>
) {
  const playerByCode = new Map(players.map((player) => [player.player_code, player]));
  const candidates: ShowcasePlayer[] = [];

  for (const position of POSITION_OPTIONS.map((option) => option.value)) {
    const ranking = rankingsByPosition[position];
    if (!ranking) continue;

    const metrics = PROFILE_KEYS[position]
      .map((key) => ranking.metrics.find((metric) => metric.key === key))
      .filter((metric): metric is RankingMetric => Boolean(metric));

    const playerCodes = new Set<string>();
    metrics.forEach((metric) =>
      metric.entries.forEach((entry) => playerCodes.add(entry.player_code))
    );

    for (const playerCode of playerCodes) {
      const tileMetrics = metrics
        .map((metric) => {
          const entry = metric.entries.find(
            (candidate) => candidate.player_code === playerCode
          );
          return entry?.value != null && entry.percentile != null
            ? { metric, entry }
            : null;
        })
        .filter((item): item is TileMetric => Boolean(item));

      const baseEntry = tileMetrics[0]?.entry;
      if (!baseEntry || baseEntry.minutes < 90 || tileMetrics.length < 4) continue;

      const strongest = tileMetrics
        .map(({ entry }) => entry.percentile ?? 0)
        .sort((a, b) => b - a)
        .slice(0, 4);
      const score = strongest.reduce((sum, value) => sum + value, 0) / strongest.length;

      const player = playerByCode.get(playerCode) ?? {
        player_code: baseEntry.player_code,
        player_name: baseEntry.player_name,
        position: baseEntry.position,
        clubs: baseEntry.clubs,
        minutes: baseEntry.minutes,
        appearances: baseEntry.appearances,
        starts: baseEntry.starts,
      };

      candidates.push({
        player,
        position,
        club: player.clubs[0] ?? baseEntry.clubs[0] ?? "Premier League",
        score,
        metrics: tileMetrics.slice(0, 4),
      });
    }
  }

  return candidates.sort(
    (a, b) => b.score - a.score || b.player.minutes - a.player.minutes
  );
}

export function PlayersDirectoryGrid({
  season,
  players,
  rankingsByPosition,
}: {
  season: string;
  players: PlayerOption[];
  rankingsByPosition: Record<string, PositionRankingData | null>;
}) {
  const [query, setQuery] = useState("");
  const [position, setPosition] = useState<PositionKey>("MID");

  const candidates = useMemo(
    () => candidateProfiles(players, rankingsByPosition),
    [players, rankingsByPosition]
  );

  const showcase = useMemo(
    () => candidates.filter((candidate) => candidate.position === position).slice(0, 3),
    [candidates, position]
  );

  const searchResults = useMemo(() => {
    const normalised = query.trim().toLocaleLowerCase("en-GB");
    if (!normalised) return [];

    return players
      .filter((player) =>
        player.player_name.toLocaleLowerCase("en-GB").includes(normalised)
      )
      .sort((a, b) => {
        const aName = a.player_name.toLocaleLowerCase("en-GB");
        const bName = b.player_name.toLocaleLowerCase("en-GB");
        const aStarts = aName.startsWith(normalised) ? 0 : 1;
        const bStarts = bName.startsWith(normalised) ? 0 : 1;
        return aStarts - bStarts || a.player_name.localeCompare(b.player_name);
      })
      .slice(0, 8);
  }, [players, query]);

  const activePositionLabel =
    POSITION_OPTIONS.find((option) => option.value === position)?.label ?? position;

  return (
    <div className={styles.directory}>
      <section className={styles.toolbar}>
        <div className={styles.toolbarCopy}>
          <p>Curated discovery</p>
          <strong>Three unusually strong positional profiles</strong>
          <span>
            Cycle by position to surface the strongest governed percentile profiles without turning the page into a full directory.
          </span>
        </div>

        <div className={styles.searchArea}>
          <label className={styles.searchWrap}>
            <span aria-hidden="true">⌕</span>
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search player..."
              aria-label="Search player"
              autoComplete="off"
            />
          </label>

          {searchResults.length > 0 && (
            <div className={styles.searchResults}>
              {searchResults.map((player) => (
                <Link
                  key={player.player_code}
                  href={`/players/${encodeURIComponent(season)}/${encodeURIComponent(player.player_code)}`}
                >
                  <span>
                    <strong>{player.player_name}</strong>
                    <small>{player.clubs.join(" · ") || "Club unavailable"} · {player.position}</small>
                  </span>
                  <small>{player.appearances} apps</small>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>

      <header className={styles.summary}>
        <div>
          <p>Players worth checking</p>
          <h2>{activePositionLabel} · percentile standouts</h2>
        </div>

        <div className={styles.positionSelector} aria-label="Select player position">
          {POSITION_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              data-active={position === option.value ? "true" : "false"}
              aria-pressed={position === option.value}
              onClick={() => setPosition(option.value)}
            >
              {option.label}
            </button>
          ))}
        </div>

        <span>90+ min · top 3</span>
      </header>

      {showcase.length > 0 ? (
        <div className={styles.grid}>
          {showcase.map(({ player, position: playerPosition, club, score, metrics }) => (
            <Link
              className={styles.card}
              key={player.player_code}
              href={`/players/${encodeURIComponent(season)}/${encodeURIComponent(player.player_code)}`}
            >
              <div className={styles.visual}>
                <span className={styles.position}>{playerPosition}</span>
                <span className={styles.profileScore}>
                  <strong>{Math.round(score)}</strong>
                  <small>avg pctl</small>
                </span>
                <ClubKit club={club} size="medium" />
              </div>

              <div className={styles.body}>
                <div className={styles.identity}>
                  <div>
                    <h3>{player.player_name}</h3>
                    <p className={styles.club}>{club}</p>
                  </div>
                  <span>Outlier profile</span>
                </div>

                <div className={styles.profileTrack} aria-hidden="true">
                  <i style={{ left: `${Math.max(0, Math.min(100, score))}%` }} />
                </div>

                <div className={styles.appearanceStrip}>
                  <div><strong>{player.appearances}</strong><span>Matches</span></div>
                  <div><strong>{player.starts}</strong><span>Starts</span></div>
                  <div><strong>{player.minutes}</strong><span>Minutes</span></div>
                </div>

                <div className={styles.metricList}>
                  {metrics.map(({ metric, entry }) => (
                    <div className={styles.metricRow} key={metric.key}>
                      <span>{metric.label}</span>
                      <strong>{formatMetric(metric, entry.value)}</strong>
                      <small data-band={percentileBand(entry.percentile)}>
                        P{Math.round(entry.percentile ?? 0)}
                      </small>
                    </div>
                  ))}
                </div>
              </div>

              <footer className={styles.footer}>
                <span>{club}</span>
                <span>Open profile →</span>
              </footer>
            </Link>
          ))}
        </div>
      ) : (
        <div className={styles.empty}>
          Not enough governed {activePositionLabel.toLowerCase()} metrics are available to build the three-player showcase yet.
        </div>
      )}

      <p className={styles.methodNote}>
        Discovery score = mean of the four strongest available position-relevant percentiles. It is a browsing aid, not an FRL model score or cross-position ranking.
      </p>
    </div>
  );
}
