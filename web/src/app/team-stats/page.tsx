import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { TeamKit } from "../teams/TeamKit";
import { TeamStatsControls } from "./TeamStatsControls";
import {
  TeamStatsOverviewWorkspace,
  type TeamStatsOverview,
} from "./TeamStatsOverviewWorkspace";
import {
  TeamFamilyMetricTiles,
  type TeamFamilyTileMetric,
} from "./TeamFamilyMetricTiles";
import styles from "./TeamStats.module.css";

type TeamOption = {
  persistent_team_code: string | null;
  display_name: string;
  season: string;
  local_team_id: string;
};

type SeasonResponse = {
  seasons: string[];
};

type RankingCoverage = {
  eligible_matches: number;
  observed_matches: number;
  missing_matches: number;
  coverage_status: string;
};

type RankingEntry = {
  persistent_team_code: string;
  display_name: string;
  local_team_id: string;
  value: number | null;
  rank: number | null;
  out_of: number;
  percentile: number | null;
  coverage: RankingCoverage;
};

type RankingMetric = {
  key: string;
  label: string;
  unit: string;
  higher_is_better: boolean;
  representation: string;
  ranking_policy: string;
  percentile_policy: string;
  entries: RankingEntry[];
};

type LeagueRankingsResponse = {
  analysis_version: string;
  season: string;
  population_size: number;
  ranking_policy: string;
  percentile_policy: string;
  metrics: RankingMetric[];
};

type FamilyKey = "overview" | "attack" | "passing" | "defence" | "discipline";
type AnalyticalFamily = Exclude<FamilyKey, "overview">;

const API_BASE =
  process.env.NEXT_PUBLIC_FRL_API_URL ?? "http://127.0.0.1:8000";

const tabs: { key: FamilyKey; label: string }[] = [
  { key: "overview", label: "Overview" },
  { key: "attack", label: "Attack" },
  { key: "passing", label: "Passing" },
  { key: "defence", label: "Defence" },
  { key: "discipline", label: "Discipline" },
];

const FAMILY_CONFIG: Record<
  AnalyticalFamily,
  { label: string; metricKeys: string[]; description: string }
> = {
  attack: {
    label: "Attack",
    metricKeys: [
      "goals_for_per_match",
      "Shots_per_match",
      "Shots on target_per_match",
      "Shots off target_per_match",
      "Blocked shots_per_match",
      "Shots inside box_per_match",
      "Shots outside box_per_match",
      "Hit woodwork_per_match",
      "Corners_per_match",
      "Offsides_per_match",
      "Big chances created_per_match",
      "Big chances missed_per_match",
      "Big chances scored_per_match",
      "Final third entries_per_match",
      "Penalty area entries_per_match",
      "Touches in opposition box_per_match",
      "Open-play assists_per_match",
      "Set-piece assists_per_match",
      "shot_accuracy",
      "goals_per_shot",
      "failed_to_score_rate",
    ],
    description:
      "Goals, shooting, chance quality, attacking territory and finishing outcomes from the governed Team Stats analysis.",
  },
  passing: {
    label: "Passing",
    metricKeys: [
      "Possession_per_match",
      "Passes_per_match",
      "Accurate passes_per_match",
      "Forward passes_per_match",
      "Long balls_per_match",
      "Accurate long balls_per_match",
      "Final third passes_per_match",
      "Successful final third passes_per_match",
      "Through balls_per_match",
      "Accurate through balls_per_match",
      "Crosses_per_match",
      "Touches_per_match",
      "Possession lost_per_match",
      "Possession won attacking third_per_match",
      "Possession won middle third_per_match",
      "Possession won defensive third_per_match",
      "Ball recoveries_per_match",
      "pass_accuracy",
    ],
    description:
      "Possession, circulation, progression and ball-use measures. Possession lives here rather than as a separate analytical family.",
  },
  defence: {
    label: "Defence",
    metricKeys: [
      "goals_against_per_match",
      "Tackles_per_match",
      "Tackles won_per_match",
      "Interceptions_per_match",
      "Interceptions won_per_match",
      "Interceptions in box_per_match",
      "Clearances_per_match",
      "Effective clearances_per_match",
      "Blocks_per_match",
      "Duels won_per_match",
      "Duels lost_per_match",
      "Aerial duels won_per_match",
      "Aerial duels lost_per_match",
      "Contests won_per_match",
      "Shots conceded inside box_per_match",
      "Shots conceded outside box_per_match",
      "Errors leading to shot_per_match",
      "Errors leading to goal_per_match",
      "Saves_per_match",
      "Saves inside box_per_match",
      "Saves outside box_per_match",
      "High claims_per_match",
      "Keeper sweeper actions_per_match",
      "Accurate keeper sweeper actions_per_match",
      "clean_sheet_rate",
    ],
    description:
      "Defensive outcomes, duels, shot suppression, errors and goalkeeper actions. High action counts are rankings, not automatic claims of better defending.",
  },
  discipline: {
    label: "Discipline",
    metricKeys: [
      "Fouls conceded_per_match",
      "Fouls won_per_match",
      "Yellow cards_per_match",
      "Red cards_per_match",
    ],
    description:
      "Foul and card measures, with ranking direction kept explicit rather than interpreted as a universal quality score.",
  },
};

async function getJson<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

function metricAvailableForSeason(metric: RankingMetric) {
  return metric.entries.some(
    (entry) => entry.value !== null && entry.value !== undefined
  );
}

function teamStatsHref(season: string, team: string, family: FamilyKey) {
  const params = new URLSearchParams({ season, team });
  if (family !== "overview") params.set("family", family);
  return `/team-stats?${params.toString()}`;
}

function rankingsHref(
  season: string,
  family: AnalyticalFamily,
  metric?: string,
  team?: string
) {
  const params = new URLSearchParams({ season, family });
  if (metric) params.set("metric", metric);
  if (team) params.set("team", team);
  return `/team-stats/rankings?${params.toString()}`;
}

function FamilyWorkspace({
  overview,
  rankings,
  teamCode,
  family,
}: {
  overview: TeamStatsOverview;
  rankings: LeagueRankingsResponse | null;
  teamCode: string;
  family: AnalyticalFamily;
}) {
  const config = FAMILY_CONFIG[family];
  const metrics = config.metricKeys
    .map((key) => rankings?.metrics.find((metric) => metric.key === key))
    .filter((metric): metric is RankingMetric => Boolean(metric))
    .filter(metricAvailableForSeason);

  const tileMetrics: TeamFamilyTileMetric[] = metrics.map((metric) => {
    const entry = metric.entries.find(
      (candidate) => candidate.persistent_team_code === teamCode
    );
    return {
      key: metric.key,
      label: metric.label,
      unit: metric.unit,
      value: entry?.value ?? null,
      rank: entry?.rank ?? null,
      outOf: entry?.out_of ?? rankings?.population_size ?? 0,
      percentile: entry?.percentile ?? null,
      observedMatches: entry?.coverage.observed_matches ?? 0,
      eligibleMatches: entry?.coverage.eligible_matches ?? overview.matches,
      href: rankingsHref(overview.season, family, metric.key, teamCode),
    };
  });

  const availableMetrics = tileMetrics.filter((metric) => metric.value !== null);

  return (
    <main className={styles.workspace}>
      <section className={styles.secondaryPanel}>
        <header className={styles.sectionHeading}>
          <div>
            <p className={styles.kicker}>Analytical family</p>
            <h2>{config.label}</h2>
          </div>
          <Link
            className={styles.kicker}
            style={{ textDecoration: "none" }}
            href={rankingsHref(overview.season, family, undefined, teamCode)}
          >
            League rankings →
          </Link>
        </header>
        <p className={styles.context}>
          {config.description} The vertical-list tiles keep the Team View focused on one club across many measures, while every row opens the equivalent population ranking.
        </p>
      </section>

      <TeamFamilyMetricTiles
        family={family}
        teamName={overview.display_name}
        metrics={tileMetrics}
      />

      <section className={styles.bottomGrid}>
        <article className={styles.readPanel}>
          <p className={styles.kicker}>What this view means</p>
          <div className={styles.readItems}>
            <div>
              <span>Grain</span>
              <strong>Team · season</strong>
              <p>Fixture observations aggregated through the governed kernel.</p>
            </div>
            <div>
              <span>Comparison</span>
              <strong>Premier League</strong>
              <p>
                Ranks and percentiles use the same eligible population as League Rankings.
              </p>
            </div>
          </div>
        </article>

        <article className={styles.secondaryPanel}>
          <p className={styles.kicker}>Current boundary</p>
          <div className={styles.secondaryGrid}>
            <div>
              <span>Team observations</span>
              <strong>{availableMetrics.length}/{tileMetrics.length}</strong>
            </div>
            <div>
              <span>Family metrics</span>
              <strong>{tileMetrics.length}</strong>
            </div>
            <div>
              <span>League population</span>
              <strong>{rankings?.population_size ?? "—"}</strong>
            </div>
            <div>
              <span>Layout</span>
              <strong>Vertical lists</strong>
            </div>
          </div>
          <footer>
            The catalogue is broader than any one season. Fully unavailable season metrics are hidden; partial and team-specific gaps remain explicit.
          </footer>
        </article>
      </section>
    </main>
  );
}

export default async function TeamStatsPage({
  searchParams,
}: {
  searchParams: Promise<{ season?: string; team?: string; family?: string }>;
}) {
  const query = await searchParams;
  const activeFamily =
    tabs.find((tab) => tab.key === query.family)?.key ?? "overview";

  const seasonResponse = await getJson<SeasonResponse>("/api/v1/seasons");
  const seasons = seasonResponse?.seasons ?? [];
  const season =
    query.season && seasons.includes(query.season) ? query.season : seasons[0];

  const teams = season
    ? (await getJson<TeamOption[]>(`/api/v1/teams/${encodeURIComponent(season)}`)) ?? []
    : [];
  const governedTeams = teams.filter(
    (team): team is TeamOption & { persistent_team_code: string } =>
      Boolean(team.persistent_team_code)
  );

  const requestedTeam =
    query.team && governedTeams.some((team) => team.persistent_team_code === query.team)
      ? query.team
      : governedTeams[0]?.persistent_team_code;
  const selectedTeam = governedTeams.find(
    (team) => team.persistent_team_code === requestedTeam
  );

  const overview =
    season && requestedTeam
      ? await getJson<TeamStatsOverview>(
          `/api/v1/team-stats/${encodeURIComponent(season)}/${encodeURIComponent(requestedTeam)}/overview`
        )
      : null;

  const rankings =
    activeFamily !== "overview" && season
      ? await getJson<LeagueRankingsResponse>(
          `/api/v1/team-stats/${encodeURIComponent(season)}/rankings`
        )
      : null;

  return (
    <AppShell>
      <div className={styles.page}>
        <header className={styles.profileHeader}>
          <div className={styles.identity}>
            <div className={styles.kit}>
              {selectedTeam ? (
                <TeamKit teamName={selectedTeam.display_name} />
              ) : (
                <span className={styles.placeholder}>TS</span>
              )}
            </div>
            <div>
              <p className={styles.eyebrow}>Analysis · Team Stats</p>
              <h1>{selectedTeam?.display_name ?? "Team Stats"}</h1>
              <p className={styles.context}>
                Premier League · {season ?? "Season unavailable"}
                {overview ? ` · ${overview.matches} matches` : ""}
              </p>
            </div>
          </div>

          {season && requestedTeam && (
            <TeamStatsControls
              seasons={seasons}
              teams={teams}
              currentSeason={season}
              currentTeam={requestedTeam}
              currentFamily={activeFamily}
            />
          )}
        </header>

        <nav className={styles.tabs} aria-label="Team Stats sections">
          {tabs.map((tab) => {
            if (!season || !requestedTeam) {
              return (
                <span key={tab.key} className={styles.futureTab}>{tab.label}</span>
              );
            }
            return (
              <span
                key={tab.key}
                className={tab.key === activeFamily ? styles.activeTab : styles.futureTab}
              >
                <Link
                  href={teamStatsHref(season, requestedTeam, tab.key)}
                  style={{
                    color: "inherit",
                    textDecoration: "none",
                    display: "inline-flex",
                    alignItems: "center",
                    height: "100%",
                  }}
                >
                  {tab.label}
                </Link>
              </span>
            );
          })}
        </nav>

        {overview ? (
          activeFamily === "overview" ? (
            <TeamStatsOverviewWorkspace overview={overview} />
          ) : requestedTeam ? (
            <FamilyWorkspace
              overview={overview}
              rankings={rankings}
              teamCode={requestedTeam}
              family={activeFamily}
            />
          ) : null
        ) : (
          <div className={styles.empty}>Team Stats data is unavailable for this selection.</div>
        )}
      </div>
    </AppShell>
  );
}