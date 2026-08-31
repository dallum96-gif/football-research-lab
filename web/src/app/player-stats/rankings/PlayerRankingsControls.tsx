"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import styles from "../PlayerStats.module.css";

const POSITIONS = ["GKP", "DEF", "MID", "FWD"];

export function PlayerRankingsControls({
  seasons,
  currentSeason,
  position,
  family,
}: {
  seasons: string[];
  currentSeason: string;
  position: string;
  family: string;
}) {
  const router = useRouter();

  function route(nextSeason: string, nextPosition: string) {
    const params = new URLSearchParams({
      season: nextSeason,
      position: nextPosition,
      family,
    });
    router.push(`/player-stats/rankings?${params.toString()}`);
  }

  return (
    <div className={styles.controls}>
      <div className={styles.viewSwitch} aria-label="Player Stats view">
        <Link href={`/player-stats?season=${encodeURIComponent(currentSeason)}`}>
          Player View
        </Link>
        <span className={styles.viewActive}>League Rankings</span>
      </div>

      <label>
        <span>Season</span>
        <select
          value={currentSeason}
          onChange={(event) => route(event.target.value, position)}
        >
          {seasons.map((season) => (
            <option key={season} value={season}>{season}</option>
          ))}
        </select>
      </label>

      <label>
        <span>Position</span>
        <select
          value={position}
          onChange={(event) => route(currentSeason, event.target.value)}
        >
          {POSITIONS.map((value) => (
            <option key={value} value={value}>{value}</option>
          ))}
        </select>
      </label>
    </div>
  );
}
