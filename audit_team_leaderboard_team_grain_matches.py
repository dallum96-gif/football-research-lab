"""Inspect the seven live team-leaderboard discoveries that have FRL team-like grain evidence.

Evidence-first only. Reads the existing capability/overlap artifacts and prints exact
FRL grains plus source evidence paths where available. No semantic/canonical promotion.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "team_leaderboard_overlap_grain_semantics.csv"
OUTPUT = ROOT / "data" / "team_leaderboard_team_grain_matches.csv"

def run() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with INPUT.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("semantic_status") == "TEAM_GRAIN_MATCH_REVIEW":
                rows.append({
                    "field_name": row.get("field_name", ""),
                    "family": row.get("family", ""),
                    "frl_grains": row.get("frl_grains", ""),
                    "frl_dictionary_path": row.get("frl_dictionary_path", ""),
                    "review_status": "OPEN",
                })
    rows.sort(key=lambda r: r["field_name"])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["field_name"])
        writer.writeheader()
        writer.writerows(rows)
    return rows

if __name__ == "__main__":
    rows = run()
    print("FRL TEAM LEADERBOARD TEAM-GRAIN MATCH REVIEW")
    print("=" * 90)
    print(f"Fields requiring team-grain review: {len(rows)}")
    for r in rows:
        print(f"  {r['field_name']:46s} :: {r['family']:24s} :: grains={r['frl_grains']}")
    print(f"Output: {OUTPUT}")
    print("Evidence-only review; no semantic/canonical promotion.")
