"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { PlayerStatsSearch } from "./PlayerStatsSearch";
import styles from "./PlayerStats.module.css";

type PlayerOption = {
  player_code: string;
  player_name: string;
  position: string;
  clubs: string[];
  minutes: number;
  appearances: number;
  starts: number;
};

export function PlayerStatsControls({
  seasons,
  players,
  currentSeason,
  currentFamily,
  position,
}: {
  seasons: string[];
  players: PlayerOption[];
  currentSeason: string;
  currentFamily: string;
  position: string;
}) {
  const router = useRouter();

  function changeSeason(season: string) {
    router.push(`/player-stats?season=${encodeURIComponent(season)}`);
  }

  const rankingParams = new URLSearchParams({
    season: currentSeason,
    position: position === "ALL" ? "ALL" : position,
    family: position === "ALL" ? "overview" : currentFamily,
  });

  return (
    <div className={styles.controls}>
      <div className={styles.viewSwitch} aria-label="Player Stats view">
        <span className={styles.viewActive}>Player View</span>
        <Link href={`/player-stats/rankings?${rankingParams.toString()}`}>
          League Rankings
        </Link>
      </div>

      <label>
        <span>Season</span>
        <select
          value={currentSeason}
          onChange={(event) => changeSeason(event.target.value)}
        >
          {seasons.map((season) => (
            <option key={season} value={season}>
              {season}
            </option>
          ))}
        </select>
      </label>

      <PlayerStatsSearch
        season={currentSeason}
        players={players}
        currentFamily={currentFamily}
        size="compact"
      />
    </div>
  );
}
