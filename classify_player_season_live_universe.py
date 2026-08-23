"""Conservative classification of the cached live player-season field universe.

Evidence-first only. Reads data/player_season_live_universe.csv and classifies
native fields into analytical, identity/context, configuration, or review.
No semantic/canonical promotion.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "player_season_live_universe.csv"
OUTPUT = ROOT / "data" / "player_season_live_universe_classification.csv"

IDENTITY_TOKENS = {
    "id", "name", "shortname", "abbr", "code", "country", "seasonid",
    "teamid", "competitionid", "position", "positiongroup", "metadata",
    "player", "currentteam", "shirtno", "shirtnum", "firstName", "lastName"
}
CONFIG_TOKENS = {"index", "page", "limit", "offset"}

ANALYTICAL_PREFIXES = (
    "goals", "shots", "passes", "successful", "unsuccessful", "cross",
    "tackle", "duel", "aerial", "fouls", "cards", "offsides", "corners",
    "clean", "expected", "xg", "xa", "conversion", "possession", "touch",
    "dribb", "clear", "intercept", "block", "save", "penalt", "points",
    "wins", "loss", "draw", "games", "minutes", "accuracy", "attempt",
    "won", "lost", "conced", "scored", "inside", "outside", "openplay",
    "creativity", "bps", "bonus", "assists", "appearances", "starts",
    "starts", "fantasy", "involvement", "involvements", "discipline",
)


def classify(field: str) -> tuple[str, str]:
    f = field.strip()
    low = f.lower()
    if low in CONFIG_TOKENS or low.startswith("_"):
        return "CONFIGURATION", "pagination/config token"
    if low in {x.lower() for x in IDENTITY_TOKENS} or low.endswith("id") or low.endswith("metadata"):
        return "IDENTITY_CONTEXT", "identity/context token"
    if low.startswith(ANALYTICAL_PREFIXES):
        return "ANALYTICAL_CANDIDATE", "statistical/football metric naming pattern"
    return "REVIEW", "no safe structural classification rule"


def run() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with INPUT.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            field = row.get("field_name", "")
            category, basis = classify(field)
            rows.append({
                "field_name": field,
                "field_type": row.get("field_type", ""),
                "sample_values": row.get("sample_values", ""),
                "source_endpoints": row.get("source_endpoints", ""),
                "category": category,
                "classification_basis": basis,
            })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "field_name", "field_type", "sample_values", "source_endpoints",
                "category", "classification_basis"
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = run()
    totals: dict[str, int] = {}
    for row in rows:
        totals[row["category"]] = totals.get(row["category"], 0) + 1
    print("FRL PLAYER-SEASON LIVE UNIVERSE CLASSIFICATION")
    print("=" * 90)
    print(f"Distinct fields inspected: {len(rows)}")
    for key, value in sorted(totals.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {value:4d}  {key}")
    print(f"Output: {OUTPUT}")
    print("Candidate family only; no semantic/canonical promotion.")
