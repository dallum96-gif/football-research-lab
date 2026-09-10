import Link from "next/link";
import { notFound } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { TeamSeasonSelect } from "./TeamSeasonSelect";
import { TeamCrest } from "@/components/TeamCrest";
import { TeamOverviewV1, type ClubProfilePayload } from "./TeamOverviewV1";
import { TeamXIView, type TeamXIResult } from "./TeamXIView";
import { TeamFixturesView } from "./TeamFixturesView";
import { TeamFormView } from "./TeamFormView";
import {
  TeamRecordsView,
  type TeamSeasonRecords,
} from "./TeamRecordsView";
import styles from "./TeamProfile.module.css";

type TeamProfileProps = {
  params: Promise<{
    season: string;
    teamCode: string;
  }>;
  searchParams: Promise<{
    view?: string | string[];
    scope?: string | string[];
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

const VIEWS = ["overview", "records", "xi", "fixtures", "form"] as const;
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
    form: [
      "Form snapshot",
      "Recent performance and season baselines will live here.",
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


  const requestedScope = Array.isArray(query.scope)
    ? query.scope[0]
    : query.scope;

  const recordScope: "season" | "overall" =
    activeView === "records" && requestedScope === "overall"
      ? "overall"
      : "season";

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

  const allFixtures =
    fixtureResult.ok && fixtureResult.data
      ? fixtureResult.data.data
      : [];

  const fixtures = allFixtures.filter(
    (fixture) => fixture.result !== "UNPLAYED"
  );

  const finalFive = fixtures.slice(-5);
  const era = eraResult.ok ? eraResult.data ?? null : null;
  const profileResult = await getJson<ClubProfilePayload>(
    `/api/v1/teams/${encodeURIComponent(
      teamCode
    )}/profile?season=${encodeURIComponent(season)}`
  );

  const clubProfile =
    profileResult.ok && profileResult.data
      ? profileResult.data
      : null;
  // === FRL TEAM ERA TIMELINE START ===
  const eraSeasonOptions = seasonOptions
    .filter((option) => option.season <= season)
    .sort((a, b) => a.season.localeCompare(b.season))
    .slice(-5);

  const eraOverviewResults = await Promise.all(
    eraSeasonOptions.map((option) =>
      getJson<TeamOverview>(
        `/api/v1/teams/${encodeURIComponent(
          option.season
        )}/${encodeURIComponent(teamCode)}/overview`
      )
    )
  );

  const eraTimeline = eraSeasonOptions.flatMap(
    (option, index) => {
      const result = eraOverviewResults[index];

      if (!result?.ok || !result.data) {
        return [];
      }

      return [
        {
          season: option.season,
          position: result.data.position,
          points: result.data.points,
          played: result.data.played,
        },
      ];
    }
  );
  // === FRL TEAM ERA TIMELINE END ===
  
  


  const recordsResult =
    activeView === "records"
      ? await getJson<TeamSeasonRecords>(
          `/api/v1/teams/${encodeURIComponent(
            season
          )}/${encodeURIComponent(
            teamCode
          )}/records?scope=${encodeURIComponent(recordScope)}`
        )
      : null;

  const records =
    recordsResult?.ok && recordsResult.data
      ? recordsResult.data
      : null;

  const rawXiScope = Array.isArray(
    (query as { scope?: string | string[] }).scope
  )
    ? (query as { scope?: string[] }).scope?.[0]
    : (query as { scope?: string }).scope;

  const xiScope: "season" | "overall" =
    rawXiScope === "overall" ? "overall" : "season";

  const xiResult =
    activeView === "xi"
      ? await getJson<TeamXIResult>(
          `/api/v1/teams/${encodeURIComponent(
            season
          )}/${encodeURIComponent(
            teamCode
          )}/xi?scope=${xiScope}`
        )
      : null;

  if (
    activeView === "xi" &&
    (!xiResult || !xiResult.ok || !xiResult.data)
  ) {
    throw new Error(
      `FRL Team XI request failed: ${xiResult?.status ?? 503}`
    );
  }

  const xiData = xiResult?.data ?? null;

  return (
    <AppShell>
      <div className={styles.profile}>
        <header className={styles.profileHeader}>
          <div className={styles.identity}>
            <div className={styles.profileCrest}>
              <TeamCrest
                teamName={overview.display_name}
                size={56}
              />
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
              disabled={
                activeView === "records" &&
                recordScope === "overall"
              }
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
                : view === "fixtures"
                  ? "Fixtures & Results"
                  : view.charAt(0).toUpperCase() + view.slice(1)}
            </Link>
          ))}
        </nav>

        <main className={styles.workspace}>
          {activeView === "overview" ? (
            <TeamOverviewV1
              clubProfile={clubProfile}
              displayName={overview.display_name}
              competition={overview.competition}
              season={overview.season}
              position={overview.position}
              played={overview.played}
              points={overview.points}
              wins={overview.wins}
              draws={overview.draws}
              losses={overview.losses}
              goalsFor={overview.goals_for}
              goalsAgainst={overview.goals_against}
              goalDifference={overview.goal_difference}
              fixtures={fixtures}
              eraSeasons={eraTimeline}
            />
          ) : activeView === "records" ? (
            records ? (
              <TeamRecordsView
                records={records}
                teamCode={teamCode}
              />
            ) : (
              <section className={styles.pendingView}>
                <p className={styles.sectionKicker}>Season record book</p>
                <h2>Records unavailable</h2>
                <p>
                  The governed record seam could not be resolved safely for
                  this team-season.
                </p>
              </section>
            )
          ) : (
            activeView === "xi" && xiData ? (
              <TeamXIView
                data={xiData}
                season={season}
                teamCode={teamCode}
              />
            ) : activeView === "fixtures" ? (
              <TeamFixturesView
                fixtures={allFixtures}
                teamName={overview.display_name}
                season={season}
              />
            ) : activeView === "form" ? (
              <TeamFormView
                fixtures={allFixtures}
                teamName={overview.display_name}
                season={season}
              />
            ) : (
              <EmptyView view={activeView} />
            )
          )}
        </main>
      </div>
    </AppShell>
  );
}
