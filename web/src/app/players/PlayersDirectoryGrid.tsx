"use client";

import Link from "next/link";
import type { CSSProperties } from "react";
import { useMemo, useState } from "react";
import styles from "./PlayersDirectoryGrid.module.css";

type PlayerOption = {
  player_code: string;
  player_name: string;
  position: string;
  clubs: string[];
  minutes: number;
  appearances: number;
};

const POSITION_OPTIONS = [
  { value: "ALL", label: "All" },
  { value: "GKP", label: "GKP" },
  { value: "DEF", label: "DEF" },
  { value: "MID", label: "MID" },
  { value: "FWD", label: "FWD" },
];

function shirtHue(value: string) {
  let hash = 0;
  for (const char of value) hash = (hash * 31 + char.charCodeAt(0)) % 360;
  return hash;
}

export function PlayersDirectoryGrid({
  season,
  players,
}: {
  season: string;
  players: PlayerOption[];
}) {
  const [query, setQuery] = useState("");
  const [position, setPosition] = useState("ALL");

  const visible = useMemo(() => {
    const normalised = query.trim().toLocaleLowerCase("en-GB");
    return players
      .filter((player) => position === "ALL" || player.position === position)
      .filter((player) => {
        if (!normalised) return true;
        return [player.player_name, player.position, ...player.clubs]
          .join(" ")
          .toLocaleLowerCase("en-GB")
          .includes(normalised);
      })
      .sort((a, b) => a.player_name.localeCompare(b.player_name));
  }, [players, position, query]);

  return (
    <div className={styles.directory}>
      <section className={styles.toolbar} aria-label="Player directory filters">
        <label className={styles.searchWrap}>
          <span aria-hidden="true">⌕</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search player or club..."
            aria-label="Search players"
          />
        </label>

        <div className={styles.positionFilters} aria-label="Filter by position">
          {POSITION_OPTIONS.map((option) => (
            <button
              type="button"
              key={option.value}
              data-active={position === option.value ? "true" : "false"}
              aria-pressed={position === option.value}
              onClick={() => setPosition(option.value)}
            >
              {option.label}
            </button>
          ))}
        </div>
      </section>

      <header className={styles.summary}>
        <div>
          <p>Player directory</p>
          <h2>{position === "ALL" ? "All Premier League players" : `${position} players`}</h2>
        </div>
        <span>{visible.length} shown</span>
      </header>

      {visible.length > 0 ? (
        <div className={styles.grid}>
          {visible.map((player) => {
            const club = player.clubs[0] ?? "Premier League";
            const style = { "--shirt-hue": shirtHue(club) } as CSSProperties;
            return (
              <Link
                className={styles.card}
                style={style}
                key={player.player_code}
                href={`/players/${encodeURIComponent(season)}/${encodeURIComponent(player.player_code)}`}
              >
                <div className={styles.visual}>
                  <span className={styles.position}>{player.position}</span>
                  <span className={styles.shirt} aria-hidden="true" />
                </div>
                <div className={styles.body}>
                  <h3>{player.player_name}</h3>
                  <p className={styles.club}>{player.clubs.join(" · ") || "Club unavailable"}</p>
                  <div className={styles.stats}>
                    <div>
                      <strong>{player.appearances}</strong>
                      <span>Apps</span>
                    </div>
                    <div>
                      <strong>{player.minutes}</strong>
                      <span>Minutes</span>
                    </div>
                  </div>
                </div>
                <footer className={styles.footer}>
                  <span>{club}</span>
                  <span>Open profile →</span>
                </footer>
              </Link>
            );
          })}
        </div>
      ) : (
        <div className={styles.empty}>No players match those filters.</div>
      )}
    </div>
  );
}
