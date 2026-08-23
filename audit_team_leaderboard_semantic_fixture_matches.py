"""Audit Team Leaderboard concepts against existing FRL fixture-match evidence.

Evidence-first only. Reads local audit artefacts when run from frl-source-audit:
- data/team_leaderboard_candidate_inspection.csv
- data/team_leaderboard_capability_map.csv
- data/fixture_match_stats.csv

The audit uses conservative semantic mappings for concepts that can be clearly
related to the existing Team-Fixture evidence vocabulary. It does not claim
aggregation equivalence unless the underlying fixture-level representation is
present. No canonical promotion.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CAP = ROOT / "data" / "team_leaderboard_capability_map.csv"
FIXTURE = ROOT / "data" / "fixture_match_stats.csv"
OUT = ROOT / "data" / "team_leaderboard_fixture_semantic_audit.csv"

TARGETS = [
    "aerialDuels", "aerialDuelsLost", "aerialDuelsWon", "attemptsFromSetPieces",
    "blockedShots", "blocks", "cleanSheets", "clearancesOffTheLine",
    "cornersTakenInclShortCorners", "cornersWon", "duels", "duelsLost", "duelsWon",
    "gamesPlayed", "goals", "goalsConceded", "goalsConcededInsideBox",
    "goalsConcededOutsideBox", "interceptions", "offsides", "openPlayPasses",
    "penaltiesConceded", "penaltiesSaved", "penaltyGoals", "penaltyGoalsConceded",
    "shotsOffTargetIncWoodwork", "shotsOnTargetIncGoals", "successfulCornersIntoBox",
    "successfulCrossesAndCorners", "successfulCrossesOpenPlay", "successfulDribbles",
    "successfulLaunches", "successfulLayoffs", "successfulLongPasses",
    "successfulPassesOppositionHalf", "successfulPassesOwnHalf", "successfulShortPasses",
    "tacklesLost", "tacklesWon", "unsuccessfulCornersIntoBox",
    "unsuccessfulCrossesAndCorners", "unsuccessfulCrossesOpenPlay", "unsuccessfulDribbles",
    "unsuccessfulLaunches", "unsuccessfulLayoffs", "unsuccessfulLongPasses",
    "unsuccessfulPassesOwnHalf", "unsuccessfulShortPasses",
]

# Conservative concept-level matches to the canonical fixture-match vocabulary.
# These indicate an available underlying Team-Fixture concept, not automatic
# equivalence of the source definitions or automatic safe aggregation.
MATCHES = {
    "blockedShots": "*_core_blocked_shots",
    "interceptions": "*_core_interceptions",
    "offsides": "*_core_offsides",
    "tacklesWon": "*_core_tackles_won",
    "shotsOnTargetIncGoals": "*_core_shots_on_target",
    "shotsOffTargetIncWoodwork": "*_core_shots_off_target",
    "cornersWon": "*_core_corners",
    "openPlayPasses": "*_core_passes",
    "successfulShortPasses": "*_core_accurate_passes",
    "expectedGoals": "*_optional_expected_goals",
    "expectedAssists": "*_optional_expected_assists",
    "expectedGoalsOnTarget": "*_optional_expected_goals_on_target",
    "penaltiesSaved": "*_optional_saves",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> list[dict[str, str]]:
    capability = {r.get("field_name", ""): r for r in read_rows(CAP)}
    fixture_rows = read_rows(FIXTURE)
    fixture_columns = set(fixture_rows[0].keys()) if fixture_rows else set()

    out: list[dict[str, str]] = []
    for field in TARGETS:
        cap = capability.get(field, {})
        if field in MATCHES:
            pattern = MATCHES[field]
            status = "TEAM_FIXTURE_CONCEPT_MATCH"
            reason = (
                "Existing FRL Team-Fixture evidence exposes the corresponding concept "
                "under a different field name. This is not yet proof of semantic identity "
                "or safe Team-Season aggregation."
            )
        else:
            pattern = ""
            status = "NO_OBVIOUS_TEAM_FIXTURE_EQUIVALENT"
            reason = (
                "No conservative semantic counterpart is declared in the existing "
                "fixture-match evidence vocabulary; requires specialist/source review."
            )

        matched_columns = [
            c for c in sorted(fixture_columns)
            if pattern and c.startswith(pattern.replace("*", ""))
        ]
        if pattern and not matched_columns:
            status = "MAPPED_CONCEPT_NOT_PRESENT_IN_CURRENT_FILE"
            reason = (
                "A semantic counterpart is recognised conceptually, but the current "
                "fixture_match_stats.csv schema does not expose matching columns."
            )

        out.append({
            "field_name": field,
            "family": cap.get("family", ""),
            "live_status": cap.get("status", ""),
            "fixture_concept_status": status,
            "fixture_concept_pattern": pattern,
            "fixture_columns_found": " | ".join(matched_columns),
            "aggregation_status": "REVIEW_REQUIRED",
            "reason": reason,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols = [
        "field_name", "family", "live_status", "fixture_concept_status",
        "fixture_concept_pattern", "fixture_columns_found", "aggregation_status", "reason",
    ]
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(out)
    return out


if __name__ == "__main__":
    rows = main()
    counts: dict[str, int] = {}
    for row in rows:
        key = row["fixture_concept_status"]
        counts[key] = counts.get(key, 0) + 1

    print("FRL TEAM LEADERBOARD SEMANTIC FIXTURE-MATCH AUDIT")
    print("=" * 90)
    print(f"Team Leaderboard concepts reviewed: {len(rows)}")
    print("\nSTATUS")
    for key, value in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {value:4d}  {key}")
    print(f"\nOutput: {OUT}")
    print("Evidence-only semantic matching; aggregation remains explicitly open; no canonical promotion.")
