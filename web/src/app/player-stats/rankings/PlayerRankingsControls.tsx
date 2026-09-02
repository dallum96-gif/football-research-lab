"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import styles from "../PlayerStats.module.css";

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

  function route(nextSeason: string) {
    const params = new URLSearchParams({
      season: nextSeason,
      position,
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
        <Link
          href={`/player-stats/rankings?season=${encodeURIComponent(currentSeason)}&position=ALL&family=overview`}
          className={styles.viewActive}
        >
          League Rankings
        </Link>
      </div>

      <label className={styles.rankingsSeasonControl}>
        <span>Season</span>
        <select
          value={currentSeason}
          onChange={(event) => route(event.target.value)}
        >
          {seasons.map((season) => (
            <option key={season} value={season}>{season}</option>
          ))}
        </select>
      </label>
    </div>
  );
}
