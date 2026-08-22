"""Conservative triage of the complete cached team_leaderboard.stats universe.

Evidence-only. Reads data/team_leaderboard_universe_audit.csv and classifies
LIVE_ONLY_CANDIDATE fields into analytical, identity/context, configuration,
or review buckets. No semantic or canonical promotion.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "team_leaderboard_universe_audit.csv"
OUTPUT = ROOT / "data" / "team_leaderboard_universe_classification.csv"

IDENTITY_TOKENS = {
    "id", "name", "shortname", "abbr", "code", "country", "seasonid",
    "teamid", "competitionid", "teammetadata", "metadata"
}
CONFIG_TOKENS = {"index", "page", "limit", "offset"}

ANALYTICAL_PREFIXES = (
    "goals", "shots", "passes", "successful", "unsuccessful", "cross",
    "tackle", "duel", "aerial", "fouls", "cards", "offsides", "corners",
    "clean", "expected", "xg", "xa", "conversion", "possession", "touch",
    "dribb", "clear", "intercept", "block", "save", "penalt", "points",
    "wins", "loss", "draw", "games", "minutes", "accuracy", "attempt",
    "won", "lost", "conced", "scored", "inside", "outside", "openplay",
)


def classify(field: str) -> tuple[str, str]:
    f = field.strip()
    low = f.lower()
    if low in IDENTITY_TOKENS or low.endswith("id") or low.endswith("metadata"):
        return "IDENTITY_CONTEXT", "identity/context token"
    if low in CONFIG_TOKENS or low.startswith("_"):
        return "CONFIGURATION", "pagination/config token"
    if low.startswith(ANALYTICAL_PREFIXES):
        return "ANALYTICAL_CANDIDATE", "statistical/football metric naming pattern"
    return "REVIEW", "no safe structural classification rule"


def run() -> list[dict[str, str]]:
    rows = []
    with INPUT.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("status") != "LIVE_ONLY_CANDIDATE":
                continue
            category, basis = classify(row.get("field_name", ""))
            rows.append({
                "field_name": row.get("field_name", ""),
                "field_type": row.get("field_type", ""),
                "sample_values": row.get("sample_values", ""),
                "category": category,
                "classification_basis": basis,
            })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=[
            "field_name", "field_type", "sample_values", "category", "classification_basis"
        ])
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = run()
    print("FRL TEAM LEADERBOARD UNIVERSE CLASSIFICATION")
    print("=" * 90)
    totals: dict[str, int] = {}
    for row in rows:
        totals[row["category"]] = totals.get(row["category"], 0) + 1
    print(f"LIVE-only fields inspected: {len(rows)}")
    for k, v in sorted(totals.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {v:4d}  {k}")
    print(f"Output: {OUTPUT}")
    print("Candidate family only; no semantic/canonical promotion.")
