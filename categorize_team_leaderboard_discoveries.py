"""Group the discovered team_leaderboard metrics into research families.

Reads the existing cached candidate-value audit only. This is descriptive
triage and does not promote anything into the canonical model.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "team_leaderboard_candidate_values.csv"
OUTPUT = ROOT / "data" / "team_leaderboard_discovery_families.csv"

FAMILIES = {
    "Finishing & Goals": (
        "goals", "goalConversion", "cleanSheets", "penaltyGoals", "goalsConceded",
        "goalsConcededInsideBox", "goalsConcededOutsideBox", "expectedGoals",
        "expectedGoalsFreekick", "expectedGoalsOnTarget", "expectedGoalsOnTargetConceded",
        "pointsDroppedFromWinningPositions", "pointsGainedFromLosingPositions",
    ),
    "Shooting": (
        "shots", "blockedShots", "shotsOffTarget", "shotsOnTarget", "touchesInOppBox",
        "attemptsFromSetPieces", "penaltyGoalsConceded",
    ),
    "Passing & Territory": (
        "passes", "openPlayPasses", "successfulPasses", "unsuccessfulPasses",
        "successfulShortPasses", "unsuccessfulShortPasses", "successfulLongPasses",
        "unsuccessfulLongPasses", "successfulLaunches", "unsuccessfulLaunches",
        "successfulLayoffs", "unsuccessfulLayoffs", "OppositionHalf", "OwnHalf",
    ),
    "Crossing & Set Pieces": (
        "cross", "corner", "Corners", "SetPieces", "setPieces", "successfulCorners",
        "unsuccessfulCorners", "successfulCrosses", "unsuccessfulCrosses",
    ),
    "Dribbling": (
        "dribb", "successfulDribbles", "unsuccessfulDribbles",
    ),
    "Duels & Aerials": (
        "duel", "aerial",
    ),
    "Defending": (
        "tackle", "interceptions", "blocks", "clearances", "conceded", "penaltiesConceded",
    ),
    "Possession": (
        "possession", "touch",
    ),
    "Discipline & Offside": (
        "cards", "offsides", "fouls",
    ),
    "Corners": (
        "cornersTakenInclShortCorners", "cornersWon",
    ),
}


def family_for(field: str) -> str:
    matches: list[str] = []
    for family, tokens in FAMILIES.items():
        low = field.lower()
        if any(token.lower() in low for token in tokens):
            matches.append(family)
    if not matches:
        return "Review"
    # Keep the most specific set-piece bucket rather than the broader crossing bucket.
    if field in {"cornersTakenInclShortCorners", "cornersWon"}:
        return "Corners"
    return matches[0]


def run() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with INPUT.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            field = row.get("field_name", "").strip()
            rows.append({
                "field_name": field,
                "family": family_for(field),
                "field_type": row.get("field_type", ""),
                "sample_values": row.get("sample_values", ""),
            })
    rows.sort(key=lambda r: (r["family"], r["field_name"]))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["field_name", "family", "field_type", "sample_values"])
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = run()
    counts = Counter(r["family"] for r in rows)
    print("FRL TEAM LEADERBOARD DISCOVERY FAMILY MAP")
    print("=" * 90)
    print(f"Metrics grouped: {len(rows)}")
    for family, count in counts.most_common():
        print(f"  {count:3d}  {family}")
    print(f"Output: {OUTPUT}")
    print("Descriptive family mapping only; no semantic/canonical promotion.")
