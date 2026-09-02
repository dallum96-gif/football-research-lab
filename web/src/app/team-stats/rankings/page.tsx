import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { TeamKit } from "../../teams/TeamKit";
import { TeamStatsControls } from "../TeamStatsControls";
import teamStyles from "../TeamStats.module.css";
import { TeamRankingsLeaderboards } from "./TeamRankingsLeaderboards";
import styles from "./LeagueRankings.module.css";
import refinementStyles from "./LeagueRankingsRefinement.module.css";

type TeamOption = {
  persistent_team_code: string | null;
  display_name: string;
  season: string;
  local_team_id: string;
};

type SeasonResponse = { seasons: string[] };

type RankingEntry = {
  persistent_team_code: string;
  display_name: string;
  local_team_id: string;
  value: number | null;
  rank: number | null;
  out_of: number;
  percentile: number | null;
  coverage: Record<string, unknown>;
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

const API_BASE =
  process.env.NEXT_PUBLIC_FRL_API_URL ?? "http://127.0.0.1:8000";

const families: { key: FamilyKey; label: string }[] = [
  { key: "overview", label: "Overview" },
  { key: "attack", label: "Attack" },
  { key: "passing", label: "Passing" },
  { key: "defence", label: "Defence" },
  { key: "discipline", label: "Discipline" },
];

const familyMetricKeys: Record<FamilyKey, string[]> = {
  overview: [
    "goals_for_per_match",
    "Shots on target_per_match",
    "shot_accuracy",
    "pass_accuracy",
    "goals_against_per_match",
    "clean_sheet_rate",
  ],
  attack: [
    "goals_for_per_match",
    "Shots_per_match",
    "Shots on target_per_match",
    "Shots off target_per_match",
    "Blocked shots_per_match",
    "Corners_per_match",
    "Offsides_per_match",
    "Big chances created_per_match",
    "Big chances missed_per_match",
    "shot_accuracy",
    "goals_per_shot",
    "failed_to_score_rate",
  ],
  passing: [
    "Possession_per_match",
    "Passes_per_match",
    "Accurate passes_per_match",
    "pass_accuracy",
    "Crosses_per_match",
  ],
  defence: [
    "goals_against_per_match",
    "Tackles_per_match",
    "Tackles won_per_match",
    "Interceptions_per_match",
    "Interceptions won_per_match",
    "Clearances_per_match",
    "Effective clearances_per_match",
    "Saves_per_match",
    "clean_sheet_rate",
  ],
  discipline: [
    "Fouls conceded_per_match",
    "Fouls won_per_match",
    "Yellow cards_per_match",
    "Red cards_per_match",
  ],
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

function trim(value: number, decimals: number) {
  const fixed = value.toFixed(decimals);
  return fixed.includes(".")
    ? fixed.replace(/0+$/, "").replace(/\.$/, "")
    : fixed;
}

function formatValue(metric: RankingMetric, value: number | null) {
  if (value === null) return "—";
  if (metric.unit === "%") return `${trim(value, 1)}%`;
  if (
    metric.key === "goals_for_per_match" ||
    metric.key === "goals_against_per_match" ||
    metric.key === "points_per_match"
  ) {
    return trim(value, 1);
  }
  return trim(value, Number.isInteger(value) ? 0 : 2);
}

function metricAvailableForSeason(metric: RankingMetric) {
  return metric.entries.some(
    (entry) => entry.value !== null && entry.value !== undefined
  );
}

function ordinal(value: number | null) {
  if (value === null) return "—";
  const mod100 = value % 100;
  if (mod100 >= 11 && mod100 <= 13) return `${value}th`;
  const suffix =
    value % 10 === 1 ? "st" : value % 10 === 2 ? "nd" : value % 10 === 3 ? "rd" : "th";
  return `${value}${suffix}`;
}

function topPercent(rank: number, outOf: number) {
  return Math.max(1, Math.ceil((rank / outOf) * 100));
}

function representationLabel(value: string) {
  return value
    .toLowerCase()
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function rankingsHref(
  season: string,
  family: FamilyKey,
  metric?: string,
  team?: string
) {
  const params = new URLSearchParams({ season, family });
  if (metric) params.set("metric", metric);
  if (team) params.set("team", team);
  return `/team-stats/rankings?${params.toString()}`;
}

function teamHref(season: string, entry: RankingEntry, family: FamilyKey = "overview") {
  const params = new URLSearchParams({
    season,
    team: entry.persistent_team_code,
  });
  if (family !== "overview") params.set("family", family);
  return `/team-stats?${params.toString()}`;
}

function median(values: number[]) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  if (sorted.length % 2 === 1) return sorted[middle];
  return (sorted[middle - 1] + sorted[middle]) / 2;
}

function FullRanking({
  metric,
  rankings,
  family = "overview",
  selectedTeamCode,
}: {
  metric: RankingMetric;
  rankings: LeagueRankingsResponse;
  family?: FamilyKey;
  selectedTeamCode?: string;
}) {
  const rankedEntries = metric.entries
    .filter((entry) => entry.rank !== null && entry.value !== null)
    .sort((a, b) => (a.rank ?? 999) - (b.rank ?? 999));
  const values = rankedEntries
    .map((entry) => entry.value)
    .filter((value): value is number => value !== null);
  const leader = rankedEntries[0] ?? null;
  const leagueMedian = median(values);
  const minimum = values.length ? Math.min(...values) : null;
  const maximum = values.length ? Math.max(...values) : null;
  const selectedEntry = selectedTeamCode
    ? rankedEntries.find((entry) => entry.persistent_team_code === selectedTeamCode) ?? null
    : null;

  return (
    <>
      <section
        className={refinementStyles.insightStrip}
        data-has-team={selectedEntry ? "true" : "false"}
        aria-label={`${metric.label} league context`}
      >
        <article className={refinementStyles.insightCard}>
          <span>Leader</span>
          <strong>{leader?.display_name ?? "—"}</strong>
          <small>{leader ? formatValue(metric, leader.value) : "Unavailable"}</small>
        </article>
        <article className={refinementStyles.insightCard}>
          <span>League median</span>
          <strong>{formatValue(metric, leagueMedian)}</strong>
          <small>Middle of observed team values</small>
        </article>
        <article className={refinementStyles.insightCard}>
          <span>League spread</span>
          <strong>
            {minimum === null || maximum === null
              ? "—"
              : `${formatValue(metric, minimum)} → ${formatValue(metric, maximum)}`}
          </strong>
          <small>{rankedEntries.length} observed teams</small>
        </article>
        {selectedEntry && selectedEntry.rank !== null && selectedEntry.percentile !== null && (
          <article className={`${refinementStyles.insightCard} ${refinementStyles.selectedInsight}`}>
            <span>Selected team</span>
            <strong>{selectedEntry.display_name}</strong>
            <small>
              {ordinal(selectedEntry.rank)} of {selectedEntry.out_of} · {Math.round(selectedEntry.percentile)}th percentile
            </small>
          </article>
        )}
      </section>

      <section className={styles.tablePanel}>
        <div className={styles.tableHeader}>
          <span>Rank</span>
          <span>Team</span>
          <span>Value</span>
          <span>League standing</span>
        </div>
        <div className={styles.rows}>
          {rankedEntries.map((entry) => {
            const selected = entry.persistent_team_code === selectedTeamCode;
            const podium = entry.rank !== null && entry.rank <= 3;
            return (
              <Link
                className={`${styles.row} ${podium ? refinementStyles.podiumRow : ""} ${selected ? refinementStyles.selectedRow : ""}`}
                key={entry.persistent_team_code}
                href={teamHref(rankings.season, entry, family)}
                aria-label={`Analyse ${entry.display_name}`}
              >
                <strong className={`${styles.rank} ${refinementStyles.rankBadge}`}>
                  {ordinal(entry.rank)}
                </strong>
                <div className={styles.team}>
                  <span className={styles.teamKit}>
                    <TeamKit teamName={entry.display_name} />
                  </span>
                  <div>
                    <strong>{entry.display_name}</strong>
                    <small>{selected ? "Selected team" : entry.persistent_team_code}</small>
                  </div>
                </div>
                <strong className={styles.value}>{formatValue(metric, entry.value)}</strong>
                <div className={refinementStyles.percentileText}>
                  <strong>
                    {entry.percentile === null ? "—" : `${Math.round(entry.percentile)}th percentile`}
                  </strong>
                  <span>
                    {entry.rank === null
                      ? "Rank unavailable"
                      : `Top ${topPercent(entry.rank, entry.out_of)}% of league`}
                  </span>
                </div>
              </Link>
            );
          })}
        </div>
      </section>
    </>
  );
}

export default async function TeamStatsRankingsPage({
  searchParams,
}: {
  searchParams: Promise<{ season?: string; family?: string; metric?: string; team?: string }>;
}) {
  const query = await searchParams;
  const seasonResponse = await getJson<SeasonResponse>("/api/v1/seasons");
  const seasons = seasonResponse?.seasons ?? [];
  const season =
    query.season && seasons.includes(query.season) ? query.season : seasons[0];

  const [teams, rankings] = season
    ? await Promise.all([
        getJson<TeamOption[]>(`/api/v1/teams/${encodeURIComponent(season)}`),
        getJson<LeagueRankingsResponse>(
          `/api/v1/team-stats/${encodeURIComponent(season)}/rankings`
        ),
      ])
    : [null, null];

  const governedTeams = (teams ?? []).filter(
    (team): team is TeamOption & { persistent_team_code: string } =>
      Boolean(team.persistent_team_code)
  );
  const selectedTeamCode =
    query.team && governedTeams.some((team) => team.persistent_team_code === query.team)
      ? query.team
      : undefined;

  const requestedFamily = families.find((family) => family.key === query.family)?.key;
  const activeFamily: FamilyKey = requestedFamily ?? "overview";
  const activeFamilyLabel =
    families.find((family) => family.key === activeFamily)?.label ?? "Overview";
  const activeFamilyMetrics = familyMetricKeys[activeFamily]
    .map((key) => rankings?.metrics.find((metric) => metric.key === key))
    .filter((metric): metric is RankingMetric => Boolean(metric))
    .filter(metricAvailableForSeason);
  const activeMetric = query.metric
    ? activeFamilyMetrics.find((metric) => metric.key === query.metric) ?? null
    : null;
  const teamViewCode = selectedTeamCode ?? governedTeams[0]?.persistent_team_code;

  return (
    <AppShell>
      <div className={teamStyles.page}>
        <header className={teamStyles.profileHeader}>
          <div className={teamStyles.identity}>
            <div className={teamStyles.kit}>
              <span className={teamStyles.placeholder}>LR</span>
            </div>
            <div>
              <p className={teamStyles.eyebrow}>Analysis · Team Stats</p>
              <h1>League Rankings</h1>
              <p className={teamStyles.context}>
                Premier League · {season ?? "Season unavailable"}
                {rankings ? ` · ${rankings.population_size} teams` : ""}
              </p>
            </div>
          </div>

          {season && (
            <TeamStatsControls
              seasons={seasons}
              teams={teams ?? []}
              currentSeason={season}
              currentTeam={teamViewCode}
              currentView="rankings"
              currentFamily={activeFamily}
            />
          )}
        </header>

        {rankings ? (
          <main className={styles.workspace}>
            <nav className={styles.familyNav} aria-label="League Rankings sections">
              {families.map((family) => (
                <Link
                  key={family.key}
                  href={rankingsHref(rankings.season, family.key, undefined, selectedTeamCode)}
                  className={
                    family.key === activeFamily ? styles.activeFamily : styles.familyLink
                  }
                >
                  {family.label}
                </Link>
              ))}
            </nav>

            {activeFamilyMetrics.length > 0 ? (
              activeMetric ? (
                <section className={styles.fullRanking}>
                  <header className={styles.fullRankingHeader}>
                    <div>
                      <p className={teamStyles.kicker}>Full ranking</p>
                      <h2>{activeMetric.label}</h2>
                      <p>
                        Ranked across the governed {rankings.season} Premier League population. Ties use competition ranking.
                      </p>
                    </div>
                    <Link
                      href={rankingsHref(
                        rankings.season,
                        activeFamily,
                        undefined,
                        selectedTeamCode
                      )}
                    >
                      Back to tiles
                    </Link>
                  </header>
                  <FullRanking
                    metric={activeMetric}
                    rankings={rankings}
                    family={activeFamily}
                    selectedTeamCode={selectedTeamCode}
                  />
                  <footer className={styles.detailMeta}>
                    <span>{representationLabel(activeMetric.representation)}</span>
                    <span>{rankings.ranking_policy}</span>
                  </footer>
                </section>
              ) : (
                <TeamRankingsLeaderboards
                  season={rankings.season}
                  family={activeFamily}
                  familyLabel={activeFamilyLabel}
                  metrics={activeFamilyMetrics}
                  selectedTeamCode={selectedTeamCode}
                  populationSize={rankings.population_size}
                />
              )
            ) : (
              <div className={styles.unavailableFamily}>
                <strong>No metric is available for this season.</strong>
                <span>
                  The family remains part of FRL, but variables with zero governed observations are not offered for {rankings.season}.
                </span>
              </div>
            )}

            <footer className={styles.methodNote}>
              <span>{rankings.analysis_version}</span>
              <span>
                The catalogue is season-aware: unavailable variables disappear from the selected season; partial coverage remains explicit.
              </span>
            </footer>
          </main>
        ) : (
          <section className={styles.emptyState}>
            <p className={teamStyles.kicker}>League Rankings</p>
            <h2>Ranking data is unavailable.</h2>
            <p>FRL could not resolve a governed league population for this season.</p>
          </section>
        )}
      </div>
    </AppShell>
  );
}
