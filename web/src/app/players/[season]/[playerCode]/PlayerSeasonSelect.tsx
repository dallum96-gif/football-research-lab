"use client";

import { useRouter } from "next/navigation";
import styles from "./PlayerProfile.module.css";

type PlayerSeasonOption = {
  season: string;
  player_code: string;
  player_name: string;
  position: string;
  clubs: string[];
  identity_status?: string;
};

export function PlayerSeasonSelect({
  currentSeason,
  seasons,
}: {
  currentSeason: string;
  seasons: PlayerSeasonOption[];
}) {
  const router = useRouter();

  return (
    <label className={styles.selectControl}>
      <span>Season</span>
      <select
        value={currentSeason}
        onChange={(event) => {
          const selected = seasons.find(
            (option) => option.season === event.target.value
          );
          if (!selected) return;
          router.push(
            `/players/${encodeURIComponent(selected.season)}/${encodeURIComponent(
              selected.player_code
            )}`
          );
        }}
      >
        {seasons.map((option) => (
          <option key={`${option.season}-${option.player_code}`} value={option.season}>
            {option.season}
          </option>
        ))}
      </select>
    </label>
  );
}
