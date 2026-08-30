"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import styles from "./TeamStats.module.css";
import viewStyles from "./TeamStatsViewSwitch.module.css";

type TeamOption = {
  persistent_team_code: string | null;
  display_name: string;
  season: string;
  local_team_id: string;
};

type TeamStatsView = "team" | "rankings";

export function TeamStatsControls({
  seasons,
  teams,
  currentSeason,
  currentTeam,
  currentView = "team",
}: {
  seasons: string[];
  teams: TeamOption[];
  currentSeason: string;
  currentTeam?: string;
  currentView?: TeamStatsView;
}) {
  const router = useRouter();

  function changeSeason(season: string) {
    const path =
      currentView === "rankings"
        ? "/team-stats/rankings"
        : "/team-stats";
    const params = new URLSearchParams({ season });

    if (currentView === "team" && currentTeam) {
      params.set("team", currentTeam);
    }

    router.push(`${path}?${params.toString()}`);
  }

  function changeTeam(team: string) {
    router.push(
      `/team-stats?season=${encodeURIComponent(
        currentSeason
      )}&team=${encodeURIComponent(team)}`
    );
  }

  const teamViewParams = new URLSearchParams({
    season: currentSeason,
  });
  if (currentTeam) {
    teamViewParams.set("team", currentTeam);
  }

  const rankingsParams = new URLSearchParams({
    season: currentSeason,
  });

  return (
    <div className={styles.controls}>
      <div
        className={viewStyles.switch}
        aria-label="Team Stats view"
      >
        <Link
          href={`/team-stats?${teamViewParams.toString()}`}
          className={
            currentView === "team"
              ? viewStyles.active
              : viewStyles.inactive
          }
        >
          Team View
        </Link>
        <Link
          href={`/team-stats/rankings?${rankingsParams.toString()}`}
          className={
            currentView === "rankings"
              ? viewStyles.active
              : viewStyles.inactive
          }
        >
          League Rankings
        </Link>
      </div>

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

      {currentView === "team" && currentTeam && (
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
      )}
    </div>
  );
}
