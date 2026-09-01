"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
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
  currentPlayer,
  currentFamily,
  position,
}: {
  seasons: string[];
  players: PlayerOption[];
  currentSeason: string;
  currentPlayer: string;
  currentFamily: string;
  position: string;
}) {
  const router = useRouter();

  function changeSeason(season: string) {
    const params = new URLSearchParams({ season });
    if (currentFamily !== "overview") params.set("family", currentFamily);
    router.push(`/player-stats?${params.toString()}`);
  }

  function changePlayer(player: string) {
    const params = new URLSearchParams({
      season: currentSeason,
      player,
    });
    if (currentFamily !== "overview") params.set("family", currentFamily);
    router.push(`/player-stats?${params.toString()}`);
  }

  const rankingParams = new URLSearchParams({
    season: currentSeason,
    position,
    family: currentFamily,
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

      <label>
        <span>Player</span>
        <select
          value={currentPlayer}
          onChange={(event) => changePlayer(event.target.value)}
        >
          {players
            .filter((player) => player.minutes > 0)
            .map((player) => (
              <option key={player.player_code} value={player.player_code}>
                {player.player_name}
              </option>
            ))}
        </select>
      </label>
    </div>
  );
}
