"use client";

import { useRouter } from "next/navigation";

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

  return (
    <label
      className={`frl-context-control frl-context-control-season${
        disabled ? " frl-context-control-disabled" : ""
      }`}
      aria-disabled={disabled}
    >
      <span>Season</span>
      <select
        aria-label="Team season"
        value={currentSeason}
        disabled={disabled}
        onChange={(event) => {
          const season = event.target.value;
          router.push(
            `/teams/${encodeURIComponent(season)}/${encodeURIComponent(teamCode)}?view=${encodeURIComponent(currentView)}`
          );
        }}
      >
        {seasons.map((option) => (
          <option key={option.season} value={option.season}>
            {option.season}
          </option>
        ))}
      </select>
      <span className="frl-context-chevron">⌄</span>
    </label>
  );
}
