"""Inspect the small mixed-grain player-season review set."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DECISIONS = ROOT / "data" / "player_season_semantic_decisions.csv"
OVERLAP = ROOT / "data" / "player_season_semantic_overlap_audit.csv"
OUT = ROOT / "data" / "player_season_mixed_grain_review.csv"


def run() -> list[dict[str, str]]:
    fields = []
    with DECISIONS.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("semantic_status") == "MIXED_GRAIN_REVIEW":
                fields.append(row.get("field_name", ""))

    out = []
    with OVERLAP.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("field_name") in fields:
                out.append(row)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols = list(out[0]) if out else ["field_name"]
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(out)
    return out


if __name__ == "__main__":
    rows = run()
    print("FRL PLAYER-SEASON MIXED-GRAIN REVIEW")
    print("=" * 90)
    print(f"Fields requiring review: {len(rows)}")
    for row in rows:
        print(f"  {row.get('field_name','')} :: {row.get('frl_grains','')}")
    print(f"Output: {OUT}")
    print("Evidence-only review; no semantic/canonical promotion.")
