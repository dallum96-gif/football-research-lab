import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { TeamDirectorySelect } from "./TeamDirectorySelect";
import { TeamKit } from "./TeamKit";
import styles from "./TeamsDirectory.module.css";

type TeamOption = {
  persistent_team_code: string | null;
  display_name: string;
  season: string;
  local_team_id: string;
};

type SeasonResponse = {
  seasons: string[];
};

const API_BASE =
  process.env.NEXT_PUBLIC_FRL_API_URL ?? "http://127.0.0.1:8000";

async function getJson<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      cache: "no-store",
    });

    if (!response.ok) {
      return null;
    }

    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export default async function TeamsPage({
  searchParams,
}: {
  searchParams: Promise<{ season?: string }>;
}) {
  const query = await searchParams;

  const seasonResponse =
    await getJson<SeasonResponse>("/api/v1/seasons");

  const seasons = seasonResponse?.seasons ?? [];

  const season =
    query.season && seasons.includes(query.season)
      ? query.season
      : seasons[0];

  const teams = season
    ? (
        await getJson<TeamOption[]>(
          `/api/v1/teams/${encodeURIComponent(season)}`
        )
      ) ?? []
    : [];

  const governedTeams = teams.filter(
    (
      team
    ): team is TeamOption & {
      persistent_team_code: string;
    } => Boolean(team.persistent_team_code)
  );

  const midpoint = Math.ceil(governedTeams.length / 2);

  const columns = [
    governedTeams.slice(0, midpoint),
    governedTeams.slice(midpoint),
  ];

  return (
    <AppShell>
      <div className={styles.page}>
        <header className={styles.profileHeader}>
          <div className={styles.identity}>
            <span className={styles.monogram}>T</span>

            <div>
              <p className={styles.eyebrow}>Explore</p>
              <h1>Teams</h1>
              <p className={styles.context}>
                Premier League · {season ?? "Season unavailable"}
              </p>
            </div>
          </div>

          {season && (
            <div className={styles.headerControls}>
              <TeamDirectorySelect
                currentSeason={season}
                seasons={seasons}
              />
            </div>
          )}
        </header>

        <nav
          className={styles.tabs}
          aria-label="Team workspace"
        >
          <span className={styles.activeTab}>
            Team profiles
          </span>
        </nav>

        <main className={styles.workspace}>
          {season && governedTeams.length > 0 ? (
            <section className={styles.clubIndex}>
              <header className={styles.sectionHeading}>
                <div>
                  <p className={styles.sectionKicker}>
                    {season} Premier League
                  </p>
                  <h2>Choose a club</h2>
                </div>

                <p>
                  {governedTeams.length} governed profiles
                </p>
              </header>

              <div className={styles.clubColumns}>
                {columns.map((column, columnIndex) => (
                  <div
                    className={styles.clubColumn}
                    key={columnIndex}
                  >
                    {column.map((team) => (
                      <Link
                        key={team.persistent_team_code}
                        href={`/teams/${encodeURIComponent(
                          season
                        )}/${encodeURIComponent(
                          team.persistent_team_code
                        )}?view=overview`}
                        className={styles.clubLink}
                      >
                        <TeamKit teamName={team.display_name} />

                        <span className={styles.clubName}>
                          {team.display_name}
                        </span>

                        <span className={styles.clubAction}>
                          Profile <i>→</i>
                        </span>
                      </Link>
                    ))}
                  </div>
                ))}
              </div>

              <footer className={styles.indexFooter}>
                <span>
                  Club identity follows the governed FRL
                  team registry.
                </span>

                <span>
                  Select a team to enter its season
                  workspace.
                </span>
              </footer>
            </section>
          ) : (
            <div className="frl-empty-state">
              No governed team profiles are available.
            </div>
          )}
        </main>
      </div>
    </AppShell>
  );
}
