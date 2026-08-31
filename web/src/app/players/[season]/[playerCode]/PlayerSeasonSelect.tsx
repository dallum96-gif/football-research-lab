"use client";

import { useRouter } from "next/navigation";
import styles from "./PlayerProfile.module.css";

type PlayerSeasonOption = {
  season: string;
  player_code: string;
  player_name: string;
  position: string;
  clubs: string[];
};

export function PlayerSeasonSelect({
  currentSeason,
  playerCode,
  seasons,
}: {
  currentSeason: string;
  playerCode: string;
  seasons: PlayerSeasonOption[];
}) {
  const router = useRouter();

  return (
    <label className={styles.selectControl}>
      <span>Season</span>
      <select
        value={currentSeason}
        onChange={(event) =>
          router.push(
            `/players/${encodeURIComponent(event.target.value)}/${encodeURIComponent(
              playerCode
            )}`
          )
        }
      >
        {seasons.map((option) => (
          <option key={option.season} value={option.season}>
            {option.season}
          </option>
        ))}
      </select>
    </label>
  );
}
