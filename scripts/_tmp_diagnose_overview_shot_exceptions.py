from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_source_routes import SEASONS, direct_index, num, player_index

SHOT_TOTAL = "totalScoringAtt"
COMPONENTS = ("ontargetScoringAtt", "shotOffTarget", "blockedScoringAtt")
CONTEXT_FIELDS = (
    SHOT_TOTAL,
    *COMPONENTS,
    "postScoringAtt",
    "hitWoodwork",
    "attPostHigh",
    "attPostLeft",
    "attPostRight",
    "attPenPost",
    "attFreekickPost",
    "ownGoals",
    "attIboxOwnGoal",
    "attOboxOwnGoal",
    "goalsFor",
    "expectedGoals",
)


def player_sum(rows, field):
    values = [num(row.get(field)) for row in rows if num(row.get("minutesPlayed")) not in (None, 0)]
    numeric = [value for value in values if value is not None]
    return sum(numeric) if numeric else None


def context(row):
    return {
        "team_id": str(row.get("team_id", "")),
        "team": row.get("team"),
        "venue": row.get("venue"),
        "kickoff": row.get("kickoff"),
        **{field: num(row.get(field)) for field in CONTEXT_FIELDS},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pl-root", type=Path, required=True)
    args = parser.parse_args()

    output = {"identity_mismatches": [], "blank_exceptions": [], "blank_totals": []}

    for season in SEASONS:
        direct, direct_pairs, _ = direct_index(args.pl_root, season)
        player, player_pairs, _ = player_index(args.pl_root, season)

        for pair, match_id in direct_pairs.items():
            player_match_id = player_pairs.get(pair)
            for side in ("home", "away"):
                row = direct[match_id].get(side)
                if row is None:
                    continue
                values = {field: num(row.get(field)) for field in (SHOT_TOTAL, *COMPONENTS)}
                if all(value is not None for value in values.values()):
                    component_sum = sum(values[field] for field in COMPONENTS)
                    if abs(values[SHOT_TOTAL] - component_sum) > 1e-9:
                        item = {
                            "season": season,
                            "match_id": match_id,
                            "component_sum": component_sum,
                            "difference_total_minus_components": values[SHOT_TOTAL] - component_sum,
                            **context(row),
                        }
                        if player_match_id:
                            team_id = str(row.get("team_id", "")).strip()
                            rows = player[player_match_id].get(team_id, [])
                            item["player_totalShots"] = player_sum(rows, "totalShots")
                            item["player_onTargetScoringAttempt"] = player_sum(rows, "onTargetScoringAttempt")
                            item["player_shotOffTarget"] = player_sum(rows, "shotOffTarget")
                            item["player_blockedScoringAttempt"] = player_sum(rows, "blockedScoringAttempt")
                        output["identity_mismatches"].append(item)

                for target in COMPONENTS:
                    if values[target] is not None:
                        continue
                    others = [field for field in COMPONENTS if field != target]
                    if values[SHOT_TOTAL] is None or any(values[field] is None for field in others):
                        continue
                    inferred = values[SHOT_TOTAL] - sum(values[field] for field in others)
                    if abs(inferred) > 1e-9:
                        item = {
                            "season": season,
                            "match_id": match_id,
                            "blank_target": target,
                            "inferred": inferred,
                            **context(row),
                        }
                        if player_match_id:
                            team_id = str(row.get("team_id", "")).strip()
                            rows = player[player_match_id].get(team_id, [])
                            field = {
                                "ontargetScoringAtt": "onTargetScoringAttempt",
                                "shotOffTarget": "shotOffTarget",
                                "blockedScoringAtt": "blockedScoringAttempt",
                            }[target]
                            item["player_target_sum"] = player_sum(rows, field)
                            item["player_totalShots"] = player_sum(rows, "totalShots")
                        output["blank_exceptions"].append(item)

                if values[SHOT_TOTAL] is None:
                    item = {"season": season, "match_id": match_id, **context(row)}
                    if player_match_id:
                        team_id = str(row.get("team_id", "")).strip()
                        rows = player[player_match_id].get(team_id, [])
                        item["player_totalShots"] = player_sum(rows, "totalShots")
                        item["player_onTargetScoringAttempt"] = player_sum(rows, "onTargetScoringAttempt")
                        item["player_shotOffTarget"] = player_sum(rows, "shotOffTarget")
                        item["player_blockedScoringAttempt"] = player_sum(rows, "blockedScoringAttempt")
                    output["blank_totals"].append(item)

    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
