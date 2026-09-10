"use client";

import { useRouter } from "next/navigation";
import styles from "./TeamProfile.module.css";

type SeasonOption = {
  season: string;
  display_name: string;
  persistent_team_code: string;
  local_team_id: string;
};

type Props = {
  currentSeason: string;
  teamCode: string;
  currentView: string;
  seasons: SeasonOption[];
  disabled?: boolean;
};

export function TeamSeasonSelect({
  currentSeason,
  teamCode,
  currentView,
  seasons,
  disabled = false,
}: Props) {
  const router = useRouter();

  const options = seasons.some(
    (option) => option.season === currentSeason,
  )
    ? seasons
    : [
        {
          season: currentSeason,
          display_name: "",
          persistent_team_code: teamCode,
          local_team_id: "",
        },
        ...seasons,
      ];

  return (
    <label
      className={styles.seasonControl}
      data-disabled={disabled ? "true" : "false"}
    >
      <span>Season</span>

      <select
        aria-label="Team season"
        value={currentSeason}
        disabled={disabled}
        onChange={(event) => {
          const selectedSeason = event.target.value;

          router.push(
            `/teams/${encodeURIComponent(
              selectedSeason,
            )}/${encodeURIComponent(
              teamCode,
            )}?view=${encodeURIComponent(currentView)}`,
          );
        }}
      >
        {options.map((option) => (
          <option
            key={option.season}
            value={option.season}
          >
            {option.season}
          </option>
        ))}
      </select>
    </label>
  );
}