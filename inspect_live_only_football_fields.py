"""Inspect live-API-only fields that touch the football research family.

Evidence-first only: preserve endpoint/path provenance and distinguish likely
analytics candidates from identifier/context payload fields without semantic
or canonical promotion.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "live_api_only_field_classification.csv"
OUTPUT = ROOT / "data" / "live_only_football_field_inspection.csv"

FOOTBALL_MARKERS = {
    "goals", "goal", "assist", "shot", "scoring", "pass", "cross", "tackle",
    "interception", "clearance", "duel", "aerial", "dribble", "carry", "touch",
    "possession", "corner", "offside", "foul", "card", "save", "expected",
    "rating", "minutes", "lineup", "formation", "substitution", "result",
    "attendance", "score", "standings", "played", "wins", "draws", "losses", "points",
    "form", "leaderboard", "stat", "stats", "event", "commentary"
}
CONTEXT_MARKERS = {
    "id", "code", "name", "slug", "url", "image", "display", "type", "season",
    "competition", "team", "player", "venue", "ground", "official", "position",
    "date", "time", "kickoff", "status", "country", "nationality", "shirt"
}


def terminal(path: str) -> str:
    if not path:
        return ""
    token = path.replace("[]", "").split(".")[-1]
    return token.lower()


def candidate_role(field_name: str, candidate_family: str) -> str:
    t = terminal(field_name)
    if "FOOTBALL_RESEARCH" in candidate_family and t in CONTEXT_MARKERS:
        return "RESEARCH_CONTEXT"
    if any(marker in t for marker in FOOTBALL_MARKERS):
        return "ANALYTICAL_CANDIDATE"
    if t in CONTEXT_MARKERS or t.endswith("id") or t.endswith("code"):
        return "IDENTITY_CONTEXT"
    return "REVIEW"


def run() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with INPUT.open("r", encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            fam = r.get("candidate_family", "")
            if "FOOTBALL_RESEARCH" not in fam:
                continue
            row = dict(r)
            row["candidate_role"] = candidate_role(row.get("field_name", ""), fam)
            rows.append(row)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0].keys()) if rows else [
        "field_name", "state", "live_endpoints", "historical_grains",
        "candidate_family", "review_status", "candidate_role"
    ]
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = run()
    c = Counter(r["candidate_role"] for r in rows)
    print("FRL LIVE-ONLY FOOTBALL FIELD INSPECTION")
    print("=" * 90)
    print(f"Live-only fields touching football research family: {len(rows)}")
    for role, count in c.most_common():
        print(f"  {count:4d}  {role}")
    print("\nBY FIELD")
    for row in sorted(rows, key=lambda r: (r["candidate_role"], r["field_name"])):
        print(f"  {row['candidate_role']:20s}  {row['field_name']}  [{row.get('live_endpoints','')}]")
    print(f"\nOutput: {OUTPUT}")
    print("Candidate role only; semantic/canonical promotion remains fail-closed.")
