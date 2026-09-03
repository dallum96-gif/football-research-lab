export type TeamStatsFamilyKey =
  | "overview"
  | "attack"
  | "passing"
  | "defence"
  | "discipline";

export type TeamStatsAnalyticalFamily = Exclude<TeamStatsFamilyKey, "overview">;

export type TeamStatsMetricGroup = {
  key: string;
  label: string;
  metricKeys: string[];
};

export const TEAM_STATS_FAMILIES: { key: TeamStatsFamilyKey; label: string }[] = [
  { key: "overview", label: "Overview" },
  { key: "attack", label: "Attack" },
  { key: "passing", label: "Passing" },
  { key: "defence", label: "Defence" },
  { key: "discipline", label: "Discipline" },
];

export const TEAM_STATS_OVERVIEW_METRIC_KEYS = [
  "goals_for_per_match",
  "Shots on target_per_match",
  "shot_accuracy",
  "pass_accuracy",
  "goals_against_per_match",
  "clean_sheet_rate",
];

export const TEAM_STATS_FAMILY_CONFIG: Record<
  TeamStatsAnalyticalFamily,
  { label: string; description: string; groups: TeamStatsMetricGroup[] }
> = {
  attack: {
    label: "Attack",
    description:
      "Goals, shooting, chance creation and attacking territory from the governed Team Stats analysis.",
    groups: [
      {
        key: "output",
        label: "Output",
        metricKeys: [
          "goals_for_per_match",
          "goals_per_shot",
          "failed_to_score_rate",
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
          "Hit woodwork_per_match",
          "shot_accuracy",
        ],
      },
      {
        key: "chance-creation",
        label: "Chance creation",
        metricKeys: [
          "Big chances created_per_match",
          "Big chances missed_per_match",
          "Big chances scored_per_match",
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
  },
  passing: {
    label: "Passing",
    description:
      "Possession, circulation, progression, distribution and regains. Possession lives here rather than as a separate analytical family.",
    groups: [
      {
        key: "control",
        label: "Control & regains",
        metricKeys: [
          "Possession_per_match",
          "Touches_per_match",
          "Possession lost_per_match",
          "Ball recoveries_per_match",
          "Possession won attacking third_per_match",
          "Possession won middle third_per_match",
          "Possession won defensive third_per_match",
        ],
      },
      {
        key: "circulation",
        label: "Circulation",
        metricKeys: [
          "Passes_per_match",
          "Accurate passes_per_match",
          "Forward passes_per_match",
          "pass_accuracy",
        ],
      },
      {
        key: "progression",
        label: "Progression",
        metricKeys: [
          "Final third passes_per_match",
          "Successful final third passes_per_match",
          "Through balls_per_match",
          "Accurate through balls_per_match",
        ],
      },
      {
        key: "distribution",
        label: "Distribution",
        metricKeys: [
          "Long balls_per_match",
          "Accurate long balls_per_match",
          "Crosses_per_match",
        ],
      },
    ],
  },
  defence: {
    label: "Defence",
    description:
      "Defensive outcomes, concession profile, duels, disruption and goalkeeper actions. High action counts are rankings, not automatic claims of better defending.",
    groups: [
      {
        key: "outcomes",
        label: "Outcomes & concession",
        metricKeys: [
          "goals_against_per_match",
          "clean_sheet_rate",
          "Shots conceded inside box_per_match",
          "Shots conceded outside box_per_match",
        ],
      },
      {
        key: "duels",
        label: "Tackling & duels",
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
        key: "disruption",
        label: "Disruption",
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
        key: "goalkeeper-errors",
        label: "Goalkeeper & errors",
        metricKeys: [
          "Saves_per_match",
          "Saves inside box_per_match",
          "Saves outside box_per_match",
          "High claims_per_match",
          "Keeper sweeper actions_per_match",
          "Accurate keeper sweeper actions_per_match",
          "Errors leading to shot_per_match",
          "Errors leading to goal_per_match",
        ],
      },
    ],
  },
  discipline: {
    label: "Discipline",
    description:
      "Foul and card measures, with ranking direction kept explicit rather than interpreted as a universal quality score.",
    groups: [
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
  },
};

export function teamStatsMetricKeys(family: TeamStatsFamilyKey): string[] {
  if (family === "overview") return TEAM_STATS_OVERVIEW_METRIC_KEYS;
  return TEAM_STATS_FAMILY_CONFIG[family].groups.flatMap((group) => group.metricKeys);
}
