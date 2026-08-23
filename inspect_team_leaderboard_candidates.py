"""Inspect the 63 analytical candidates from the cached team_leaderboard.stats universe."""
from __future__ import annotations
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CLASS = ROOT / "data" / "team_leaderboard_universe_classification.csv"
UNIVERSE = ROOT / "data" / "team_leaderboard_universe_audit.csv"
OUT = ROOT / "data" / "team_leaderboard_candidate_inspection.csv"


def run() -> list[dict[str, str]]:
    candidates: set[str] = set()
    with CLASS.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("category") == "ANALYTICAL_CANDIDATE":
                candidates.add(row.get("field_name", ""))

    out: list[dict[str, str]] = []
    with UNIVERSE.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("field_name", "") in candidates:
                out.append(row)

    out.sort(key=lambda r: r.get("field_name", ""))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols = ["field_name", "field_type", "sample_values", "status"]
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(out)
    return out


if __name__ == "__main__":
    rows = run()
    print("FRL TEAM LEADERBOARD ANALYTICAL CANDIDATE INSPECTION")
    print("=" * 90)
    print(f"Analytical candidates: {len(rows)}")
    for r in rows:
        print(f"  {r['field_name']:46s} :: {r['field_type']} :: {r['sample_values']}")
    print(f"Output: {OUT}")
    print("Cached payload universe only; no semantic/canonical promotion.")
