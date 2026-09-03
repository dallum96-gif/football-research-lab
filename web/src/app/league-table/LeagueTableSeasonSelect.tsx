"use client";

import { useRouter } from "next/navigation";
import styles from "./LeagueTable.module.css";

export function LeagueTableSeasonSelect({
  seasons,
  currentSeason,
}: {
  seasons: string[];
  currentSeason: string;
}) {
  const router = useRouter();

  return (
    <label className={styles.seasonControl}>
      <span>Season</span>
      <select
        value={currentSeason}
        onChange={(event) => {
          const params = new URLSearchParams({ season: event.target.value });
          router.push(`/league-table?${params.toString()}`);
        }}
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
