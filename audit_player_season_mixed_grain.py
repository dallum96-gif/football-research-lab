"""Inspect the small mixed-grain player-season semantic review set.

Evidence-first only. Reads already-generated local CSV artefacts and makes no
semantic or canonical promotion.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DECISIONS = ROOT / "data" / "player_season_semantic_decisions.csv"
UNIVERSE = ROOT / "data" / "player_season_live_universe.csv"
OUT = ROOT / "data" / "player_season_mixed_grain_review.csv"


def run() -> list[dict[str, str]]:
    mixed: set[str] = set()
    with DECISIONS.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("semantic_status") == "MIXED_GRAIN_REVIEW":
                field = row.get("field_name", "").strip()
                if field:
                    mixed.add(field)

    rows: list[dict[str, str]] = []
    with UNIVERSE.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            field = row.get("field_name", "").strip()
            if field not in mixed:
                continue
            rows.append({
                "field_name": field,
                "endpoint": row.get("endpoint_name", ""),
                "field_path": row.get("field_path", ""),
                "field_type": row.get("field_type", ""),
                "grain": row.get("grain", ""),
                "sample": row.get("sample", ""),
                "review_status": "OPEN",
            })

    rows.sort(key=lambda r: (r["field_name"], r["endpoint"], r["field_path"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols = ["field_name", "endpoint", "field_path", "field_type", "grain", "sample", "review_status"]
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = run()
    distinct = sorted({r["field_name"] for r in rows})
    print("FRL PLAYER-SEASON MIXED-GRAIN REVIEW")
    print("=" * 90)
    print(f"Mixed-grain fields: {len(distinct)}")
    for field in distinct:
        print(f"\n{field}")
        for row in [r for r in rows if r["field_name"] == field]:
            print(
                f"  [{row['endpoint']}] {row['field_path']} :: "
                f"{row['field_type']} :: grain={row['grain']} :: {row['sample']}"
            )
    print(f"Output: {OUT}")
    print("Evidence-only mixed-grain inspection; no canonical promotion.")
