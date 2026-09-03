import Link from "next/link";
import tileStyles from "./StatsListTiles.module.css";

export type TeamFamilyTileMetric = {
  key: string;
  label: string;
  unit: string;
  value: number | null;
  rank: number | null;
  outOf: number;
  percentile: number | null;
  observedMatches: number;
  eligibleMatches: number;
  href: string;
};

export type TeamFamilyTileKey = "attack" | "passing" | "defence" | "discipline";

type GroupSpec = {
  key: string;
  label: string;
  metricKeys: string[];
};

const TILE_TONES = ["coral", "green", "gold", "blue"] as const;

const GROUPS: Record<TeamFamilyTileKey, GroupSpec[]> = {
  attack: [
    {
      key: "output",
      label: "Output & finishing",
      metricKeys: [
        "goals_for_per_match",
        "Big chances scored_per_match",
        "shot_accuracy",
        "goals_per_shot",
        "failed_to_score_rate",
        "Hit woodwork_per_match",
      ],
    },
    {
      key: "shooting",
      label: "Shooting",
      metricKeys: [
        "Shots_per_match",
        "Shots on target_per_match",
        "Shots off target_per_match",
        "Blocked shots_per_match",
        "Shots inside box_per_match",
        "Shots outside box_per_match",
      ],
    },
    {
      key: "chance-creation",
      label: "Chance creation",
      metricKeys: [
        "Big chances created_per_match",
        "Big chances missed_per_match",
        "Open-play assists_per_match",
        "Set-piece assists_per_match",
      ],
    },
    {
      key: "territory",
      label: "Territory",
      metricKeys: [
        "Final third entries_per_match",
        "Penalty area entries_per_match",
        "Touches in opposition box_per_match",
        "Corners_per_match",
        "Offsides_per_match",
      ],
    },
  ],
  passing: [
    {
      key: "control",
      label: "Control",
      metricKeys: [
        "Possession_per_match",
        "Touches_per_match",
        "Possession lost_per_match",
        "Ball recoveries_per_match",
      ],
    },
    {
      key: "circulation",
      label: "Circulation",
      metricKeys: [
        "Passes_per_match",
        "Accurate passes_per_match",
        "pass_accuracy",
        "Forward passes_per_match",
      ],
    },
    {
      key: "progression",
      label: "Progression",
      metricKeys: [
        "Long balls_per_match",
        "Accurate long balls_per_match",
        "Final third passes_per_match",
        "Successful final third passes_per_match",
        "Through balls_per_match",
        "Accurate through balls_per_match",
      ],
    },
    {
      key: "territory-regains",
      label: "Territory & regains",
      metricKeys: [
        "Crosses_per_match",
        "Possession won attacking third_per_match",
        "Possession won middle third_per_match",
        "Possession won defensive third_per_match",
      ],
    },
  ],
  defence: [
    {
      key: "outcomes",
      label: "Outcomes & suppression",
      metricKeys: [
        "goals_against_per_match",
        "clean_sheet_rate",
        "Shots conceded inside box_per_match",
        "Shots conceded outside box_per_match",
        "Errors leading to shot_per_match",
        "Errors leading to goal_per_match",
      ],
    },
    {
      key: "duels",
      label: "Duels",
      metricKeys: [
        "Tackles_per_match",
        "Tackles won_per_match",
        "Duels won_per_match",
        "Duels lost_per_match",
        "Aerial duels won_per_match",
        "Aerial duels lost_per_match",
        "Contests won_per_match",
      ],
    },
    {
      key: "reading",
      label: "Reading & recovery",
      metricKeys: [
        "Interceptions_per_match",
        "Interceptions won_per_match",
        "Interceptions in box_per_match",
        "Clearances_per_match",
        "Effective clearances_per_match",
        "Blocks_per_match",
      ],
    },
    {
      key: "goalkeeping",
      label: "Goalkeeping",
      metricKeys: [
        "Saves_per_match",
        "Saves inside box_per_match",
        "Saves outside box_per_match",
        "High claims_per_match",
        "Keeper sweeper actions_per_match",
        "Accurate keeper sweeper actions_per_match",
      ],
    },
  ],
  discipline: [
    {
      key: "fouls",
      label: "Fouls",
      metricKeys: ["Fouls conceded_per_match", "Fouls won_per_match"],
    },
    {
      key: "cards",
      label: "Cards",
      metricKeys: ["Yellow cards_per_match", "Red cards_per_match"],
    },
  ],
};

function trim(value: number, decimals: number) {
  const fixed = value.toFixed(decimals);
  return fixed.includes(".")
    ? fixed.replace(/0+$/, "").replace(/\.$/, "")
    : fixed;
}

function formatMetric(metric: TeamFamilyTileMetric) {
  if (metric.value === null) return "—";
  if (metric.unit === "%") return `${trim(metric.value, 1)}%`;
  if (
    metric.key === "goals_for_per_match" ||
    metric.key === "goals_against_per_match" ||
    metric.key === "points_per_match"
  ) {
    return trim(metric.value, 1);
  }
  return trim(metric.value, Number.isInteger(metric.value) ? 0 : 2);
}

function ordinal(value: number) {
  const mod100 = value % 100;
  if (mod100 >= 11 && mod100 <= 13) return `${value}th`;
  const suffix =
    value % 10 === 1 ? "st" : value % 10 === 2 ? "nd" : value % 10 === 3 ? "rd" : "th";
  return `${value}${suffix}`;
}

export function TeamFamilyMetricTiles({
  family,
  teamName,
  metrics,
}: {
  family: TeamFamilyTileKey;
  teamName: string;
  metrics: TeamFamilyTileMetric[];
}) {
  const byKey = new Map(metrics.map((metric) => [metric.key, metric]));
  const groups = GROUPS[family]
    .map((group) => ({
      ...group,
      metrics: group.metricKeys
        .map((key) => byKey.get(key))
        .filter((metric): metric is TeamFamilyTileMetric => Boolean(metric)),
    }))
    .filter((group) => group.metrics.length > 0);

  if (!groups.length) {
    return (
      <div className={tileStyles.noTiles}>
        No governed metrics are available for this team and season.
      </div>
    );
  }

  return (
    <section className={tileStyles.leaderboardSection}>
      <header className={tileStyles.leaderboardHeading}>
        <div>
          <p className={tileStyles.familyKicker}>Team view</p>
          <h2>{teamName} · metric profile</h2>
        </div>
        <span>
          Read vertically through one team. Every row links to the matching league ranking.
        </span>
      </header>

      <div className={tileStyles.leaderboardGrid}>
        {groups.map((group, tileIndex) => (
          <article
            className={tileStyles.leaderboardCard}
            data-tone={TILE_TONES[tileIndex % TILE_TONES.length]}
            key={group.key}
          >
            <header className={tileStyles.cardHeader}>
              <div>
                <span>Team metrics</span>
                <h3>{group.label}</h3>
              </div>
              <strong>{group.metrics.length} stats</strong>
            </header>

            <ol className={tileStyles.leaderboardList}>
              {group.metrics.map((metric) => {
                const available = metric.value !== null && metric.rank !== null;
                return (
                  <li key={metric.key}>
                    <Link
                      href={metric.href}
                      className={tileStyles.teamMetricRow}
                      title={`Open ${metric.label} league ranking`}
                    >
                      <span className={tileStyles.metricIdentity}>
                        <strong>{metric.label}</strong>
                        <small>
                          {available && metric.rank !== null
                            ? `${ordinal(metric.rank)} of ${metric.outOf}`
                            : `${metric.observedMatches}/${metric.eligibleMatches} matches observed`}
                        </small>
                      </span>
                      <span className={tileStyles.teamMetricValue}>
                        {formatMetric(metric)}
                      </span>
                      <span className={tileStyles.teamMetricContext}>
                        {available && metric.percentile !== null
                          ? `P${Math.round(metric.percentile)}`
                          : "—"}
                      </span>
                    </Link>
                  </li>
                );
              })}
            </ol>

            <footer>
              <span>{group.label}</span>
              <span>{group.metrics.length}</span>
            </footer>
          </article>
        ))}
      </div>
    </section>
  );
}