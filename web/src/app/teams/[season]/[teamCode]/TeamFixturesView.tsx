"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { TeamKit } from "../../TeamKit";
import styles from "./TeamProfile.module.css";

export type TeamFixture = {
  fixture_id: string;
  season: string;
  gameweek: number | null;
  kickoff_time: string | null;
  home_team_name: string;
  away_team_name: string;
  home_score: number | null;
  away_score: number | null;
  venue: "Home" | "Away" | null;
  result: "W" | "D" | "L" | "UNPLAYED" | null;
};

type Filter = "all" | "home" | "away" | "W" | "D" | "L";

function opponent(fixture: TeamFixture, teamName: string) {
  return fixture.home_team_name === teamName
    ? fixture.away_team_name
    : fixture.home_team_name;
}

function dateLabel(value: string | null) {
  if (!value) return "Date TBC";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Date TBC";

  return new Intl.DateTimeFormat("en-GB", {
    timeZone: "Europe/London",
    weekday: "short",
    day: "numeric",
    month: "short",
  }).format(date);
}

function monthLabel(value: string | null) {
  if (!value) return "Date TBC";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Date TBC";

  return new Intl.DateTimeFormat("en-GB", {
    timeZone: "Europe/London",
    month: "long",
    year: "numeric",
  }).format(date);
}

function timeLabel(value: string | null) {
  if (!value) return "TBC";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "TBC";

  return new Intl.DateTimeFormat("en-GB", {
    timeZone: "Europe/London",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(date);
}

function isPlayed(fixture: TeamFixture) {
  return (
    fixture.result != null &&
    fixture.result !== "UNPLAYED" &&
    fixture.home_score != null &&
    fixture.away_score != null
  );
}

function score(fixture: TeamFixture) {
  if (fixture.home_score == null || fixture.away_score == null) {
    return null;
  }

  return `${fixture.home_score}-${fixture.away_score}`;
}

export function TeamFixturesView({
  fixtures,
  teamName,
  season,
}: {
  fixtures: TeamFixture[];
  teamName: string;
  season: string;
}) {
  const [filter, setFilter] = useState<Filter>("all");

  const ordered = useMemo(
    () =>
      [...fixtures].sort((a, b) => {
        const aTime = a.kickoff_time
          ? new Date(a.kickoff_time).getTime()
          : Number.MAX_SAFE_INTEGER;

        const bTime = b.kickoff_time
          ? new Date(b.kickoff_time).getTime()
          : Number.MAX_SAFE_INTEGER;

        return aTime - bTime;
      }),
    [fixtures]
  );

  const filtered = useMemo(
    () =>
      ordered.filter((fixture) => {
        if (filter === "all") return true;
        if (filter === "home") return fixture.venue === "Home";
        if (filter === "away") return fixture.venue === "Away";
        return fixture.result === filter;
      }),
    [ordered, filter]
  );

  const groups = useMemo(() => {
    const result: { label: string; fixtures: TeamFixture[] }[] = [];

    for (const fixture of filtered) {
      const label = monthLabel(fixture.kickoff_time);
      const last = result[result.length - 1];

      if (!last || last.label !== label) {
        result.push({ label, fixtures: [fixture] });
      } else {
        last.fixtures.push(fixture);
      }
    }

    return result;
  }, [filtered]);

  const completed = ordered.filter(isPlayed);

  const wins = completed.filter((fixture) => fixture.result === "W").length;
  const draws = completed.filter((fixture) => fixture.result === "D").length;
  const losses = completed.filter((fixture) => fixture.result === "L").length;
  const upcoming = ordered.length - completed.length;

  const filters: { key: Filter; label: string }[] = [
    { key: "all", label: "All" },
    { key: "home", label: "Home" },
    { key: "away", label: "Away" },
    { key: "W", label: "W" },
    { key: "D", label: "D" },
    { key: "L", label: "L" },
  ];

  return (
    <section className={styles.fixtureLedger}>
      <header className={styles.fixtureLedgerHeader}>
        <div>
          <p className={styles.sectionKicker}>Fixtures & results</p>
          <h2>{season} match ledger</h2>
          <p className={styles.fixtureLedgerIntro}>
            Scan the season here. Open any match to move into the full Fixture Workspace.
          </p>
        </div>

        <div className={styles.fixtureLedgerSummary}>
          <div>
            <strong>{completed.length}</strong>
            <span>Played</span>
          </div>

          <div>
            <strong>{wins}-{draws}-{losses}</strong>
            <span>W-D-L</span>
          </div>

          {upcoming > 0 && (
            <div>
              <strong>{upcoming}</strong>
              <span>Upcoming</span>
            </div>
          )}
        </div>
      </header>

      <div className={styles.fixtureLedgerToolbar}>
        <div className={styles.fixtureFilters}>
          {filters.map((item) => (
            <button
              key={item.key}
              type="button"
              data-active={filter === item.key ? "true" : "false"}
              data-result={
                item.key === "W" || item.key === "D" || item.key === "L"
                  ? item.key
                  : undefined
              }
              onClick={() => setFilter(item.key)}
            >
              {item.label}
            </button>
          ))}
        </div>

        <span className={styles.fixtureLedgerCount}>
          {filtered.length} {filtered.length === 1 ? "match" : "matches"}
        </span>
      </div>

      <div className={styles.fixtureLedgerScroll}>
        {groups.length > 0 ? (
          groups.map((group) => (
            <section className={styles.fixtureMonth} key={group.label}>
              <header className={styles.fixtureMonthHeading}>
                <span>{group.label}</span>
                <i />
              </header>

              <div className={styles.fixtureRows}>
                {group.fixtures.map((fixture) => {
                  const played = isPlayed(fixture);
                  const opposition = opponent(fixture, teamName);

                  return (
                    <Link
                      key={fixture.fixture_id}
                      href={`/fixtures/${encodeURIComponent(
                        fixture.season
                      )}/${encodeURIComponent(fixture.fixture_id)}`}
                      className={styles.fixtureLedgerRow}
                      data-result={played ? fixture.result : "UPCOMING"}
                    >
                      <span className={styles.fixtureResultSignature} />

                      <div className={styles.fixtureRound}>
                        <strong>
                          {fixture.gameweek != null
                            ? `GW ${fixture.gameweek}`
                            : "-"}
                        </strong>
                        <span>{dateLabel(fixture.kickoff_time)}</span>
                      </div>

                      <span
                        className={styles.fixtureVenue}
                        data-venue={fixture.venue?.toLowerCase() ?? "unknown"}
                      >
                        {fixture.venue === "Home"
                          ? "H"
                          : fixture.venue === "Away"
                            ? "A"
                            : "-"}
                      </span>

                      <div className={styles.fixtureOpponentKit}>
                        <TeamKit teamName={opposition} />
                      </div>

                      <div className={styles.fixtureOpponent}>
                        <strong>{opposition}</strong>
                        <span>
                          {played
                            ? fixture.venue === "Home"
                              ? `${teamName} at home`
                              : `${teamName} away`
                            : `${timeLabel(fixture.kickoff_time)} kickoff`}
                        </span>
                      </div>

                      <div className={styles.fixtureOutcome}>
                        {played ? (
                          <>
                            <span
                              className={styles.fixtureResultLetter}
                              data-result={fixture.result}
                            >
                              {fixture.result}
                            </span>
                            <strong>{score(fixture)}</strong>
                          </>
                        ) : (
                          <>
                            <span className={styles.fixtureUpcoming}>
                              Upcoming
                            </span>
                            <strong>{timeLabel(fixture.kickoff_time)}</strong>
                          </>
                        )}
                      </div>

                      <span className={styles.fixtureOpenCue} aria-hidden="true">
                        &rarr;
                      </span>
                    </Link>
                  );
                })}
              </div>
            </section>
          ))
        ) : (
          <div className={styles.fixtureLedgerEmpty}>
            No matches match this filter.
          </div>
        )}
      </div>

      <footer className={styles.fixtureLedgerFooter}>
        <span>Select a fixture to open its research workspace</span>
        <small>
          Match detail, lineups, events and evidence live one level deeper
        </small>
      </footer>
    </section>
  );
}
