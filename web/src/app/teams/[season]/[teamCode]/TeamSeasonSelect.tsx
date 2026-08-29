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
};

export function TeamSeasonSelect({
  currentSeason,
  teamCode,
  currentView,
  seasons,
}: Props) {
  const router = useRouter();

  return (
    <label className="frl-context-control frl-context-control-season">
      <span>Season</span>
      <select
        aria-label="Team season"
        value={currentSeason}
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
