import Link from "next/link";
import { notFound } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { TeamSeasonSelect } from "./TeamSeasonSelect";
import { TeamKit } from "../../TeamKit";
import { OverviewDetailTabs } from "./OverviewDetailTabs";
import styles from "./TeamProfile.module.css";

type TeamProfileProps = {
  params: Promise<{
    season: string;
    teamCode: string;
  }>;
  searchParams: Promise<{
    view?: string | string[];
  }>;
};

type TeamOverview = {
  persistent_team_code: string;
  display_name: string;
  season: string;
  local_team_id: string;
  competition: string;
  position: number;
  played: number;
  wins: number;
  draws: number;
  losses: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  points: number;
};

type TeamEraRecordItem = {
  label: string;
  value: string;
  detail: string | null;
};

type TeamEraOverview = {
  persistent_team_code: string;
  display_name: string;
  first_season: string;
  last_season: string;
  season_count: number;
  across_seasons: TeamEraRecordItem[];
  team_records: TeamEraRecordItem[];
  player_records_status: "UNAVAILABLE";
  player_records_note: string;
};

type SeasonOption = {
  persistent_team_code: string;
  display_name: string;
  season: string;
  local_team_id: string;
};

type Fixture = {
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

type FixtureResponse = {
  data: Fixture[];
};

const API_BASE = (
  process.env.NEXT_PUBLIC_FRL_API_URL ?? "http://127.0.0.1:8000"
).replace(/\/$/, "");

const VIEWS = ["overview", "records", "xi", "fixtures", "stats"] as const;
type View = (typeof VIEWS)[number];

async function getJson<T>(path: string): Promise<{ ok: boolean; status: number; data?: T }> {
  try {
    const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
    if (!response.ok) return { ok: false, status: response.status };
    return {
      ok: true,
      status: response.status,
      data: (await response.json()) as T,
    };
  } catch {
    return { ok: false, status: 503 };
  }
}

function ordinal(value: number): string {
  const mod100 = value % 100;
  if (mod100 >= 11 && mod100 <= 13) return `${value}th`;

  switch (value % 10) {
    case 1:
      return `${value}st`;
    case 2:
      return `${value}nd`;
    case 3:
      return `${value}rd`;
    default:
      return `${value}th`;
  }
}

function signed(value: number): string {
  return value > 0 ? `+${value}` : String(value);
}

function shortDate(value: string | null): string {
  if (!value) return "Date unavailable";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Date unavailable";

  return new Intl.DateTimeFormat("en-GB", {
    timeZone: "Europe/London",
    day: "numeric",
    month: "short",
  }).format(date);
}

function fixtureLabel(fixture: Fixture, teamName: string): string {
  const opponent =
    fixture.home_team_name === teamName
      ? fixture.away_team_name
      : fixture.home_team_name;

  const score =
    fixture.home_score == null || fixture.away_score == null
      ? "unplayed"
      : `${fixture.home_score}–${fixture.away_score}`;

  return `${shortDate(fixture.kickoff_time)} · ${opponent} · ${score}`;
}

function opponentName(fixture: Fixture, teamName: string): string {
  return fixture.home_team_name === teamName
    ? fixture.away_team_name
    : fixture.home_team_name;
}

function fixtureScore(fixture: Fixture): string {
  if (fixture.home_score == null || fixture.away_score == null) return "?";
  return `${fixture.home_score}?${fixture.away_score}`;
}


function EmptyView({ view }: { view: Exclude<View, "overview"> }) {
  const labels: Record<Exclude<View, "overview">, [string, string]> = {
    records: [
      "Season records",
      "Results, streaks, goals, player records and matchday records will live here.",
    ],
    xi: [
      "Most played XI",
      "A football-native season XI visual will occupy this workspace.",
    ],
    fixtures: [
      "Season fixtures",
      "The complete compact fixture record will live here with links into Fixture Workspace.",
    ],
    stats: [
      "Team stats",
      "The analytical layer will use focused sub-views rather than one enormous statistics page.",
    ],
  };

  const [title, description] = labels[view];

  return (
    <section className={styles.pendingView}>
      <p className={styles.sectionKicker}>Coming next</p>
      <h2>{title}</h2>
      <p>{description}</p>
    </section>
  );
}

export const dynamic = "force-dynamic";

export default async function TeamProfilePage({
  params,
  searchParams,
}: TeamProfileProps) {
  const { season, teamCode } = await params;
  const query = await searchParams;

  const requestedView = Array.isArray(query.view) ? query.view[0] : query.view;
  const activeView: View = VIEWS.includes(requestedView as View)
    ? (requestedView as View)
    : "overview";

  const overviewResult = await getJson<TeamOverview>(
    `/api/v1/teams/${encodeURIComponent(season)}/${encodeURIComponent(teamCode)}/overview`
  );

  if (!overviewResult.ok || !overviewResult.data) {
    if (overviewResult.status === 404) notFound();
    throw new Error(`FRL Team Overview request failed: ${overviewResult.status}`);
  }

  const overview = overviewResult.data;

  const [seasonResult, fixtureResult, eraResult] = await Promise.all([
    getJson<SeasonOption[]>(
      `/api/v1/team-seasons?persistent_team_code=${encodeURIComponent(teamCode)}`
    ),
    getJson<FixtureResponse>(
      `/api/v1/fixtures/${encodeURIComponent(season)}?team=${encodeURIComponent(
        overview.display_name
      )}&limit=100`
    ),
    getJson<TeamEraOverview>(
      `/api/v1/teams/${encodeURIComponent(teamCode)}/era-overview`
    ),
  ]);

  const seasonOptions = seasonResult.ok && seasonResult.data
    ? seasonResult.data
    : [
        {
          persistent_team_code: teamCode,
          display_name: overview.display_name,
          season,
          local_team_id: overview.local_team_id,
        },
      ];

  const fixtures =
    fixtureResult.ok && fixtureResult.data
      ? fixtureResult.data.data.filter((fixture) => fixture.result !== "UNPLAYED")
      : [];

  const finalFive = fixtures.slice(-5);
  const era = eraResult.ok ? eraResult.data ?? null : null;

  return (
    <AppShell>
      <div className={styles.profile}>
        <header className={styles.profileHeader}>
          <div className={styles.identity}>
            <div className={styles.profileKit}>
              <TeamKit teamName={overview.display_name} />
            </div>

            <div>
              <p className={styles.eyebrow}>Team profile</p>
              <h1>{overview.display_name}</h1>
              <p className={styles.context}>
                {overview.competition} · {overview.season}
              </p>
            </div>
          </div>

          <div className={styles.headerControls}>
            <TeamSeasonSelect
              currentSeason={season}
              teamCode={teamCode}
              currentView={activeView}
              seasons={seasonOptions}
            />
          </div>
        </header>

        <nav className={styles.tabs} aria-label="Team profile views">
          {VIEWS.map((view) => (
            <Link
              key={view}
              href={`/teams/${encodeURIComponent(season)}/${encodeURIComponent(
                teamCode
              )}?view=${view}`}
              className={styles.tab}
              data-active={activeView === view ? "true" : "false"}
            >
              {view === "xi"
                ? "XI"
                : view.charAt(0).toUpperCase() + view.slice(1)}
            </Link>
          ))}
        </nav>

        <main className={styles.workspace}>
          {activeView === "overview" ? (
            <div className={styles.overview}>
              <section
                className={styles.headlineStrip}
                aria-label={`${overview.display_name} ${overview.season} season record`}
              >
                <div className={styles.headlineMetric}>
                  <strong>{ordinal(overview.position)}</strong>
                  <span>League finish</span>
                </div>

                <div className={styles.headlineMetric}>
                  <strong>{overview.points}</strong>
                  <span>Points</span>
                </div>

                <div className={styles.headlineMetric}>
                  <strong>
                    {overview.wins}–{overview.draws}–{overview.losses}
                  </strong>
                  <span>W–D–L</span>
                </div>

                <div className={styles.headlineMetric}>
                  <strong>{signed(overview.goal_difference)}</strong>
                  <span>Goal difference</span>
                </div>

                <div className={styles.headlineMetric}>
                  <strong>
                    {overview.goals_for}
                    <small> : </small>
                    {overview.goals_against}
                  </strong>
                  <span>Goals for : against</span>
                </div>
              </section>

              <section className={styles.seasonPulse}>
                <div className={styles.sectionHeading}>
                  <div>
                    <p className={styles.sectionKicker}>Season at a glance</p>
                    <h2>The shape of the season</h2>
                  </div>

                  <div className={styles.legend} aria-label="Result legend">
                    <span><i data-result="W" /> Win</span>
                    <span><i data-result="D" /> Draw</span>
                    <span><i data-result="L" /> Loss</span>
                  </div>
                </div>

                {fixtures.length ? (
                  <>
                    <div
                      className={styles.formRibbon}
                      style={{ gridTemplateColumns: `repeat(${fixtures.length}, minmax(4px, 1fr))` }}
                    >
                      {fixtures.map((fixture) => (
                        <Link
                          key={fixture.fixture_id}
                          href={`/fixtures/${encodeURIComponent(
                            fixture.season
                          )}/${encodeURIComponent(fixture.fixture_id)}`}
                          className={styles.formResult}
                          data-result={fixture.result}
                          aria-label={`${fixture.result}: ${fixtureLabel(
                            fixture,
                            overview.display_name
                          )}`}
                          title={`${fixture.result} · ${fixtureLabel(
                            fixture,
                            overview.display_name
                          )}`}
                        >
                          <span className={styles.formResultLetter}>{fixture.result}</span>
                          <span className={styles.fixtureTooltip}>
                            <strong>
                              {opponentName(fixture, overview.display_name)}
                            </strong>
                            <small>
                              {shortDate(fixture.kickoff_time)} ?{" "}
                              {fixture.venue ?? "Venue unavailable"}
                            </small>
                            <b>{fixtureScore(fixture)}</b>
                          </span>
                        </Link>
                      ))}
                    </div>

                    <div className={styles.ribbonAxis}>
                      <span>{shortDate(fixtures[0]?.kickoff_time ?? null)}</span>
                      <span>{overview.played} league matches</span>
                      <span>
                        {shortDate(fixtures[fixtures.length - 1]?.kickoff_time ?? null)}
                      </span>
                    </div>
                  </>
                ) : (
                  <p className={styles.unavailable}>
                    Season result sequence unavailable.
                  </p>
                )}
              </section>
              <OverviewDetailTabs
                position={ordinal(overview.position)}
                played={overview.played}
                points={overview.points}
                wins={overview.wins}
                draws={overview.draws}
                losses={overview.losses}
                goalsFor={overview.goals_for}
                goalsAgainst={overview.goals_against}
                goalDifference={overview.goal_difference}
                closingFixtures={finalFive.map((fixture) => ({
                  href: `/fixtures/${encodeURIComponent(
                    fixture.season
                  )}/${encodeURIComponent(fixture.fixture_id)}`,
                  result: fixture.result ?? "?",
                  opponent: opponentName(fixture, overview.display_name),
                  score: fixtureScore(fixture),
                  venue: fixture.venue ?? "Venue unavailable",
                  date: shortDate(fixture.kickoff_time),
                }))}
              />

              {era && (
                <section className={styles.eraSection}>
                  <header className={styles.eraHeading}>
                    <div>
                      <p className={styles.sectionKicker}>Across the FRL era</p>
                      <h2>{era.first_season} to {era.last_season}</h2>
                    </div>
                    <span>{era.season_count} Premier League seasons</span>
                  </header>

                  <div className={styles.eraGrid}>
                    <article className={styles.eraPanel}>
                      <div className={styles.eraPanelHeader}>
                        <span>01</span>
                        <div>
                          <p>Across seasons</p>
                          <small>Best single-season marks</small>
                        </div>
                      </div>

                      <div className={styles.eraRecords}>
                        {era.across_seasons.map((record) => (
                          <div className={styles.eraRecord} key={record.label}>
                            <span>{record.label}</span>
                            <strong>{record.value}</strong>
                            <small>{record.detail}</small>
                          </div>
                        ))}
                      </div>
                    </article>

                    <article className={styles.eraPanel}>
                      <div className={styles.eraPanelHeader}>
                        <span>02</span>
                        <div>
                          <p>Team records</p>
                          <small>Results and runs across our dataset</small>
                        </div>
                      </div>

                      <div className={styles.eraRecords}>
                        {era.team_records.map((record) => (
                          <div className={styles.eraRecord} key={record.label}>
                            <span>{record.label}</span>
                            <strong>{record.value.replaceAll("?", "-")}</strong>
                            <small>{record.detail?.replaceAll("?", "/")}</small>
                          </div>
                        ))}
                      </div>

                      <Link
                        className={styles.eraPanelLink}
                        href={`/teams/${encodeURIComponent(season)}/${encodeURIComponent(
                          teamCode
                        )}?view=records`}
                      >
                        Open record book <span>?</span>
                      </Link>
                    </article>

                    <article className={`${styles.eraPanel} ${styles.playerEraPanel}`}>
                      <div className={styles.eraPanelHeader}>
                        <span>03</span>
                        <div>
                          <p>Player records</p>
                          <small>Across Arsenal's FRL-era seasons</small>
                        </div>
                      </div>

                      <div className={styles.playerEraPreview}>
                        <strong>Player record book</strong>
                        <p>
                          Goals, appearances, starts, minutes and other
                          cross-season player records will live here once
                          team-scoped identity comparison is governed.
                        </p>
                      </div>

                      <span className={styles.evidenceLabel}>
                        Evidence boundary preserved
                      </span>
                    </article>
                  </div>
                </section>
              )}
            </div>
          ) : (
            <EmptyView view={activeView} />
          )}
        </main>
      </div>
    </AppShell>
  );
}
