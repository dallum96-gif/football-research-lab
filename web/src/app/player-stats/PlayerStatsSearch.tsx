"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import styles from "./PlayerStatsDiscovery.module.css";

type PlayerOption = {
  player_code: string;
  player_name: string;
  position: string;
  clubs: string[];
  minutes: number;
  appearances: number;
  starts: number;
};

export function PlayerStatsSearch({
  season,
  players,
  currentFamily = "overview",
  size = "large",
}: {
  season: string;
  players: PlayerOption[];
  currentFamily?: string;
  size?: "large" | "compact";
}) {
  const [query, setQuery] = useState("");

  const results = useMemo(() => {
    const normalised = query.trim().toLocaleLowerCase("en-GB");
    if (!normalised) return [];

    return players
      .filter((player) => {
        const haystack = [player.player_name, player.position, ...player.clubs]
          .join(" ")
          .toLocaleLowerCase("en-GB");
        return haystack.includes(normalised);
      })
      .sort((a, b) => {
        const aName = a.player_name.toLocaleLowerCase("en-GB");
        const bName = b.player_name.toLocaleLowerCase("en-GB");
        const aStarts = aName.startsWith(normalised) ? 0 : 1;
        const bStarts = bName.startsWith(normalised) ? 0 : 1;
        return aStarts - bStarts || a.player_name.localeCompare(b.player_name);
      })
      .slice(0, 8);
  }, [players, query]);

  return (
    <div className={styles.searchShell} data-size={size}>
      <label className={styles.searchLabel}>
        <span>{size === "large" ? "Find a player" : "Player search"}</span>
        <span className={styles.searchInputWrap}>
          <span className={styles.searchIcon} aria-hidden="true">⌕</span>
          <input
            className={styles.searchInput}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search player or club..."
            autoComplete="off"
            role="combobox"
            aria-expanded={results.length > 0}
            aria-autocomplete="list"
          />
        </span>
      </label>

      {results.length > 0 && (
        <div className={styles.searchResults} role="listbox">
          {results.map((player) => {
            const params = new URLSearchParams({
              season,
              player: player.player_code,
            });
            if (currentFamily !== "overview") params.set("family", currentFamily);

            return (
              <Link
                role="option"
                aria-selected="false"
                key={player.player_code}
                href={`/player-stats?${params.toString()}`}
              >
                <span className={styles.resultIdentity}>
                  <strong>{player.player_name}</strong>
                  <span>{player.clubs.join(" · ") || "Club unavailable"} · {player.position}</span>
                </span>
                <span className={styles.resultMeta}>{player.minutes} min</span>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
