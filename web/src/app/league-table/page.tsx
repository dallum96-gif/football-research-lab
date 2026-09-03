import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { ClubKit } from "@/components/ClubKit";
import { LeagueTableSeasonSelect } from "./LeagueTableSeasonSelect";
import styles from "./LeagueTable.module.css";

type SeasonResponse = {
  seasons: string[];
};

type LeagueTableRow = {
  position: number;
  persistent_team_code: string;
  display_name: string;
  local_team_id: string;
  played: number;
  wins: number;
  draws: number;
  losses: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  points: number;
  form: Array<"W" | "D" | "L">;
};

type LeagueTableResult = {
  season: string;
  competition: string;
  rows: LeagueTableRow[];
  completed_fixtures: number;
  scheduled_fixtures: number;
  total_fixtures: number;
  latest_completed_kickoff: string | null;
  information_available_as_of: string | null;
  source_release_sha: string | null;
  query_version: string;
  limitations: string[];
};

const API_BASE =
  process.env.NEXT_PUBLIC_FRL_API_URL ?? "http://127.0.0.1:8000";

async function getJson<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

function boundaryLabel(value: string | null) {
  if (!value) return "Release boundary unavailable";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
    timeZoneName: "short",
  }).format(parsed);
}

function goalDifference(value: number) {
  return value > 0 ? `+${value}` : String(value);
}

export default async function LeagueTablePage({
  searchParams,
}: {
  searchParams: Promise<{ season?: string }>;
}) {
  const query = await searchParams;
  const seasonResponse = await getJson<SeasonResponse>("/api/v1/seasons");
  const seasons = seasonResponse?.seasons ?? [];
  const season =
    query.season && seasons.includes(query.season) ? query.season : seasons[0];
  const table = season
    ? await getJson<LeagueTableResult>(
        `/api/v1/league-table/${encodeURIComponent(season)}`
      )
    : null;

  return (
    <AppShell>
      <div className={styles.page}>
        <header className={styles.header}>
          <div>
            <p className={styles.eyebrow}>Explore · League Table</p>
            <h1>Premier League Table</h1>
            <p className={styles.context}>
              {season ?? "Season unavailable"}
              {table
                ? ` · ${table.completed_fixtures} of ${table.total_fixtures} fixtures completed`
                : " · governed table unavailable"}
            </p>
          </div>
          {season && (
            <LeagueTableSeasonSelect
              seasons={seasons}
              currentSeason={season}
            />
          )}
        </header>

        {table ? (
          <>
            <section className={styles.summary} aria-label="League table state">
              <div>
                <span>Completed</span>
                <strong>{table.completed_fixtures} fixtures</strong>
                <small>{table.rows.reduce((sum, row) => sum + row.played, 0)} team appearances</small>
              </div>
              <div>
                <span>Still scheduled</span>
                <strong>{table.scheduled_fixtures} fixtures</strong>
                <small>Unplayed fixtures do not enter the table.</small>
              </div>
              <div>
                <span>Information boundary</span>
                <strong>{boundaryLabel(table.information_available_as_of)}</strong>
                <small>
                  {table.latest_completed_kickoff
                    ? `Latest represented result: ${boundaryLabel(table.latest_completed_kickoff)}`
                    : "No completed result boundary available."}
                </small>
              </div>
            </section>

            <section className={styles.tablePanel}>
              <header className={styles.tableHeading}>
                <div>
                  <p className={styles.kicker}>Current standings</p>
                  <h2>{table.competition} · {table.season}</h2>
                </div>
                <span>P · W · D · L · GF · GA · GD · Pts · last five</span>
              </header>

              <div className={styles.tableScroll}>
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th scope="col">Pos</th>
                      <th scope="col">Club</th>
                      <th scope="col">P</th>
                      <th scope="col">W</th>
                      <th scope="col">D</th>
                      <th scope="col">L</th>
                      <th scope="col">GF</th>
                      <th scope="col">GA</th>
                      <th scope="col">GD</th>
                      <th scope="col">Pts</th>
                      <th scope="col">Form</th>
                    </tr>
                  </thead>
                  <tbody>
                    {table.rows.map((row) => (
                      <tr key={row.persistent_team_code || row.local_team_id}>
                        <td><span className={styles.position}>{row.position}</span></td>
                        <td>
                          {row.persistent_team_code ? (
                            <Link
                              className={styles.teamLink}
                              href={`/teams/${encodeURIComponent(table.season)}/${encodeURIComponent(row.persistent_team_code)}`}
                            >
                              <ClubKit club={row.display_name} size="small" />
                              <span>{row.display_name}</span>
                            </Link>
                          ) : (
                            <span className={styles.teamLink}>
                              <ClubKit club={row.display_name} size="small" />
                              <span>{row.display_name}</span>
                            </span>
                          )}
                        </td>
                        <td>{row.played}</td>
                        <td>{row.wins}</td>
                        <td>{row.draws}</td>
                        <td>{row.losses}</td>
                        <td>{row.goals_for}</td>
                        <td>{row.goals_against}</td>
                        <td className={row.goal_difference > 0 ? styles.positive : row.goal_difference < 0 ? styles.negative : undefined}>
                          {goalDifference(row.goal_difference)}
                        </td>
                        <td className={styles.points}>{row.points}</td>
                        <td>
                          <span className={styles.form} aria-label={`${row.display_name} recent form`}>
                            {row.form.length
                              ? row.form.map((result, index) => (
                                  <span
                                    className={styles.formMark}
                                    data-result={result}
                                    key={`${row.local_team_id}-${index}-${result}`}
                                  >
                                    {result}
                                  </span>
                                ))
                              : "—"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <section className={styles.boundary}>
              <article>
                <p className={styles.kicker}>Living-season interpretation</p>
                <h3>Partial-season state, not a completed-season claim</h3>
                <p>
                  FRL derives this table only from completed canonical results. Scheduled fixtures remain outside points, goals and form until their completed result is represented.
                </p>
              </article>
              <article>
                <p className={styles.kicker}>Provenance</p>
                <h3>Canonical fixtures + governed team identity</h3>
                <p>Query version {table.query_version}</p>
                {table.source_release_sha && (
                  <div className={styles.releaseCode}>Release {table.source_release_sha}</div>
                )}
              </article>
            </section>
          </>
        ) : (
          <div className="frl-empty-state">
            No governed league table is available for this season.
          </div>
        )}
      </div>
    </AppShell>
  );
}
