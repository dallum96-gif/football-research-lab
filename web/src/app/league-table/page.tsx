import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { ClubKit } from "@/components/ClubKit";
import { LeagueTableSeasonSelect } from "./LeagueTableSeasonSelect";
import styles from "./LeagueTable.module.css";

type SeasonResponse = {
  seasons: string[];
};

type LeagueTableView = "overall" | "home" | "away" | "last5";

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
  view: LeagueTableView;
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

const TABLE_VIEWS: ReadonlyArray<{
  key: LeagueTableView;
  label: string;
}> = [
  { key: "overall", label: "Overall" },
  { key: "home", label: "Home" },
  { key: "away", label: "Away" },
  { key: "last5", label: "Last 5" },
];

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
  if (!value) return "Boundary unavailable";
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

function isLeagueTableView(value: string | undefined): value is LeagueTableView {
  return TABLE_VIEWS.some((item) => item.key === value);
}

function viewHref(season: string, view: LeagueTableView) {
  const params = new URLSearchParams({ season, view });
  return `/league-table?${params.toString()}`;
}

export default async function LeagueTablePage({
  searchParams,
}: {
  searchParams: Promise<{ season?: string; view?: string }>;
}) {
  const query = await searchParams;
  const seasonResponse = await getJson<SeasonResponse>("/api/v1/seasons");
  const seasons = seasonResponse?.seasons ?? [];
  const season =
    query.season && seasons.includes(query.season) ? query.season : seasons[0];
  const view: LeagueTableView = isLeagueTableView(query.view)
    ? query.view
    : "overall";
  const table = season
    ? await getJson<LeagueTableResult>(
        `/api/v1/league-table/${encodeURIComponent(season)}?view=${encodeURIComponent(view)}`
      )
    : null;
  const viewLabel = TABLE_VIEWS.find((item) => item.key === view)?.label ?? "Overall";

  return (
    <AppShell>
      <div className={styles.page}>
        <header className={styles.header}>
          <div>
            <p className={styles.eyebrow}>Explore</p>
            <h1>League Table</h1>
            <p className={styles.context}>
              {table
                ? `${table.competition} · ${table.season}`
                : season ?? "Season unavailable"}
            </p>
          </div>
          {season && (
            <LeagueTableSeasonSelect
              seasons={seasons}
              currentSeason={season}
              currentView={view}
            />
          )}
        </header>

        {table && season ? (
          <>
            <nav className={styles.viewToggle} aria-label="League table view">
              {TABLE_VIEWS.map((item) => (
                <Link
                  key={item.key}
                  href={viewHref(season, item.key)}
                  className={`${styles.viewToggleItem} ${
                    view === item.key ? styles.viewToggleActive : ""
                  }`}
                  aria-current={view === item.key ? "page" : undefined}
                >
                  {item.label}
                </Link>
              ))}
            </nav>

            <div className={styles.tableState}>
              <span>{viewLabel}</span>
              <span>{table.completed_fixtures} fixtures completed</span>
              <span>
                {table.information_available_as_of
                  ? `Updated ${boundaryLabel(table.information_available_as_of)}`
                  : table.latest_completed_kickoff
                    ? `Latest result ${boundaryLabel(table.latest_completed_kickoff)}`
                    : "Update boundary unavailable"}
              </span>
            </div>

            <section className={styles.tablePanel} aria-label={`${table.competition} ${table.season} ${viewLabel.toLowerCase()} league table`}>
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
                        <td className={styles.position}>{row.position}</td>
                        <td>
                          {row.persistent_team_code ? (
                            <Link
                              className={styles.teamLink}
                              href={`/teams/${encodeURIComponent(table.season)}/${encodeURIComponent(row.persistent_team_code)}`}
                            >
                              <ClubKit club={row.display_name} size="tiny" />
                              <span>{row.display_name}</span>
                            </Link>
                          ) : (
                            <span className={styles.teamLink}>
                              <ClubKit club={row.display_name} size="tiny" />
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
                        <td
                          className={
                            row.goal_difference > 0
                              ? styles.positive
                              : row.goal_difference < 0
                                ? styles.negative
                                : undefined
                          }
                        >
                          {goalDifference(row.goal_difference)}
                        </td>
                        <td className={styles.points}>{row.points}</td>
                        <td>
                          <span className={styles.form} aria-label={`${row.display_name} recent form in ${viewLabel.toLowerCase()} view`}>
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

            <footer className={styles.footer}>
              <p>
                {table.limitations[0]} Reconstructed from completed canonical fixtures; scheduled fixtures remain outside the table until a completed result is represented.
              </p>
              <details className={styles.evidence}>
                <summary>Evidence & provenance</summary>
                <div>
                  <span>Canonical fixtures + governed team identity</span>
                  <span>Query {table.query_version}</span>
                  {table.latest_completed_kickoff && (
                    <span>Latest result {boundaryLabel(table.latest_completed_kickoff)}</span>
                  )}
                  {table.source_release_sha && (
                    <span className={styles.releaseCode}>Release {table.source_release_sha}</span>
                  )}
                </div>
              </details>
            </footer>
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
