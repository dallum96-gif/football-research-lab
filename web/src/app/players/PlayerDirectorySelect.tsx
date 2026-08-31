"use client";

import { useRouter } from "next/navigation";
import styles from "./PlayersDirectory.module.css";

export function PlayerDirectorySelect({
  currentSeason,
  seasons,
}: {
  currentSeason: string;
  seasons: string[];
}) {
  const router = useRouter();

  return (
    <label className={styles.selectControl}>
      <span>Season</span>
      <select
        value={currentSeason}
        onChange={(event) =>
          router.push(
            `/players?season=${encodeURIComponent(event.target.value)}`
          )
        }
      >
        {seasons.map((season) => (
          <option key={season} value={season}>
            {season}
          </option>
        ))}
      </select>
    </label>
  );
}
