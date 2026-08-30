"use client";

import { useRouter } from "next/navigation";
import styles from "./TeamStats.module.css";

type TeamOption = {
  persistent_team_code: string | null;
  display_name: string;
  season: string;
  local_team_id: string;
};

export function TeamStatsControls({
  seasons,
  teams,
  currentSeason,
  currentTeam,
}: {
  seasons: string[];
  teams: TeamOption[];
  currentSeason: string;
  currentTeam: string;
}) {
  const router = useRouter();

  function changeSeason(season: string) {
    router.push(
      `/team-stats?season=${encodeURIComponent(season)}`
    );
  }

  function changeTeam(team: string) {
    router.push(
      `/team-stats?season=${encodeURIComponent(
        currentSeason
      )}&team=${encodeURIComponent(team)}`
    );
  }

  return (
    <div className={styles.controls}>
      <label>
        <span>Season</span>
        <select
          value={currentSeason}
          onChange={(event) =>
            changeSeason(event.target.value)
          }
        >
          {seasons.map((season) => (
            <option key={season} value={season}>
              {season}
            </option>
          ))}
        </select>
      </label>

      <label>
        <span>Team</span>
        <select
          value={currentTeam}
          onChange={(event) =>
            changeTeam(event.target.value)
          }
        >
          {teams
            .filter(
              (
                team
              ): team is TeamOption & {
                persistent_team_code: string;
              } => Boolean(team.persistent_team_code)
            )
            .map((team) => (
              <option
                key={team.persistent_team_code}
                value={team.persistent_team_code}
              >
                {team.display_name}
              </option>
            ))}
        </select>
      </label>
    </div>
  );
}
