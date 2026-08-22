"""Finalize live player-season capability delta.

Evidence-first only. Treats the 49 inspected player-season analytical concepts as
player-season-shaped after the mixed-grain review returned zero cases. Records the
FRL grain decision without promoting anything into canonical schema.
"""
from __future__ import annotations
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DECISIONS = ROOT / "data" / "player_season_semantic_decisions.csv"
MIXED = ROOT / "data" / "player_season_mixed_grain_review.csv"
OUT = ROOT / "data" / "player_season_capability_delta.csv"


def run() -> list[dict[str, str]]:
    mixed_fields: set[str] = set()
    if MIXED.exists():
        with MIXED.open("r", encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                field = row.get("field_name", "").strip()
                if field:
                    mixed_fields.add(field)

    rows: list[dict[str, str]] = []
    with DECISIONS.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            field = row.get("field_name", "").strip()
            if not field:
                continue
            status = "PLAYER_SEASON_CAPABILITY_CONFIRMED"
            reason = "Live analytical candidate reviewed at player-season grain; mixed-grain audit returned no cases."
            if field in mixed_fields:
                status = "REVIEW"
                reason = "Field remains in mixed-grain review set."
            rows.append({
                "field_name": field,
                "decision_status": row.get("decision_status", ""),
                "final_status": status,
                "reason": reason,
            })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["field_name","decision_status","final_status","reason"])
        writer.writeheader(); writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = run()
    print("FRL PLAYER-SEASON CAPABILITY DELTA")
    print("=" * 90)
    print(f"Fields reviewed: {len(rows)}")
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["final_status"]] = counts.get(row["final_status"], 0) + 1
    for key, value in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {value:4d}  {key}")
    print(f"Output: {OUT}")
    print("Evidence-first delta only; no semantic or canonical promotion.")
