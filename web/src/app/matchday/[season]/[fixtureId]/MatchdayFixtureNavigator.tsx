"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import styles from "./MatchdayWorkspace.module.css";

type FixtureOption = {
  fixture_id?: string;
  gameweek?: number | null;
  kickoff_time?: string | null;
  home_team_name?: string;
  away_team_name?: string;
  completed?: boolean;
};

type Props = {
  season: string;
  currentFixtureId: string;
  currentGameweek: number | null;
  currentHome: string;
  currentAway: string;
  fixtures: FixtureOption[];
};

function fixtureDate(value: string | null | undefined) {
  if (!value) return "date TBC";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "date TBC";
  return parsed.toLocaleDateString("en-GB", {
    timeZone: "Europe/London",
    weekday: "short",
    day: "numeric",
    month: "short",
  });
}

export function MatchdayFixtureNavigator({
  season,
  currentFixtureId,
  currentGameweek,
  currentHome,
  currentAway,
  fixtures,
}: Props) {
  const router = useRouter();
  const [mode, setMode] = useState<"gameweek" | "teams">("gameweek");
  const [gameweek, setGameweek] = useState<number | null>(currentGameweek);
  const [teamA, setTeamA] = useState(currentHome);
  const [teamB, setTeamB] = useState(currentAway);

  const sortedFixtures = useMemo(
    () => [...fixtures].sort((a, b) => String(a.kickoff_time ?? "").localeCompare(String(b.kickoff_time ?? ""))),
    [fixtures],
  );

  const gameweeks = useMemo(
    () => [...new Set(sortedFixtures.map((fixture) => fixture.gameweek).filter((value): value is number => typeof value === "number"))].sort((a, b) => a - b),
    [sortedFixtures],
  );

  const gameweekFixtures = useMemo(
    () => sortedFixtures.filter((fixture) => fixture.gameweek === gameweek),
    [gameweek, sortedFixtures],
  );

  const teams = useMemo(
    () => [...new Set(sortedFixtures.flatMap((fixture) => [fixture.home_team_name, fixture.away_team_name]).filter((value): value is string => Boolean(value)))].sort((a, b) => a.localeCompare(b)),
    [sortedFixtures],
  );

  const selectedMeeting = useMemo(() => {
    if (!teamA || !teamB || teamA === teamB) return null;
    const meetings = sortedFixtures.filter((fixture) => {
      const home = fixture.home_team_name;
      const away = fixture.away_team_name;
      return (home === teamA && away === teamB) || (home === teamB && away === teamA);
    });
    if (!meetings.length) return null;

    const now = Date.now();
    return meetings.find((fixture) => {
      if (fixture.completed || !fixture.kickoff_time) return false;
      const kickoff = new Date(fixture.kickoff_time).getTime();
      return Number.isFinite(kickoff) && kickoff >= now;
    }) ?? meetings.find((fixture) => !fixture.completed) ?? meetings.at(-1) ?? null;
  }, [sortedFixtures, teamA, teamB]);

  function openFixture(fixtureId: string | undefined) {
    if (!fixtureId) return;
    router.push(`/matchday/${season}/${fixtureId}`);
  }

  return (
    <div className={styles.heroActions}>
      <div className={styles.segmented} aria-label="Choose fixture navigation mode">
        <button type="button" data-active={mode === "gameweek" ? "true" : "false"} onClick={() => setMode("gameweek")}>
          By gameweek
        </button>
        <button type="button" data-active={mode === "teams" ? "true" : "false"} onClick={() => setMode("teams")}>
          Pick two teams
        </button>
      </div>

      {mode === "gameweek" ? (
        <>
          <label className={styles.fixtureSelect}>
            <span>Gameweek</span>
            <select value={gameweek ?? ""} onChange={(event) => setGameweek(Number(event.target.value))}>
              {gameweeks.map((value) => <option key={value} value={value}>GW {value}</option>)}
            </select>
          </label>
          <label className={styles.fixtureSelect}>
            <span>Fixture</span>
            <select
              value={gameweekFixtures.some((fixture) => String(fixture.fixture_id) === currentFixtureId) ? currentFixtureId : ""}
              onChange={(event) => openFixture(event.target.value)}
            >
              {!gameweekFixtures.some((fixture) => String(fixture.fixture_id) === currentFixtureId) && <option value="">Choose fixture</option>}
              {gameweekFixtures.map((fixture) => (
                <option key={String(fixture.fixture_id)} value={String(fixture.fixture_id)}>
                  {fixture.home_team_name} v {fixture.away_team_name}
                </option>
              ))}
            </select>
          </label>
        </>
      ) : (
        <>
          <label className={styles.fixtureSelect}>
            <span>Team A</span>
            <select value={teamA} onChange={(event) => setTeamA(event.target.value)}>
              {teams.map((team) => <option key={team}>{team}</option>)}
            </select>
          </label>
          <label className={styles.fixtureSelect}>
            <span>Team B</span>
            <select value={teamB} onChange={(event) => setTeamB(event.target.value)}>
              {teams.map((team) => <option key={team} disabled={team === teamA}>{team}</option>)}
            </select>
          </label>
          <button
            type="button"
            className={styles.reportLink}
            disabled={!selectedMeeting || teamA === teamB}
            onClick={() => openFixture(selectedMeeting?.fixture_id)}
            title={selectedMeeting ? `${selectedMeeting.home_team_name} v ${selectedMeeting.away_team_name}` : "Choose two different teams"}
          >
            {selectedMeeting ? `Open ${selectedMeeting.gameweek ? `GW${selectedMeeting.gameweek} · ` : ""}${fixtureDate(selectedMeeting.kickoff_time)}` : "Choose two teams"}
          </button>
        </>
      )}
    </div>
  );
}
