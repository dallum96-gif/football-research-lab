"""Inspect analytical candidates from live player-season surfaces.

Evidence-only; no semantic/canonical promotion.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CLASS = ROOT / "data" / "player_season_live_universe_classification.csv"
UNIVERSE = ROOT / "data" / "player_season_live_universe.csv"
OUT = ROOT / "data" / "player_season_candidate_inspection.csv"


def run() -> list[dict[str, str]]:
    candidates: set[str] = set()
    with CLASS.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("category") == "ANALYTICAL_CANDIDATE" or row.get("status") == "ANALYTICAL_CANDIDATE":
                field = row.get("field_name", "").strip()
                if field:
                    candidates.add(field)

    out: list[dict[str, str]] = []
    with UNIVERSE.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            field = row.get("field_name", "").strip()
            if field in candidates:
                out.append(row)

    out.sort(key=lambda r: (r.get("field_name", ""), r.get("endpoint_name", ""), r.get("field_path", "")))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols = ["field_name", "endpoint_name", "field_path", "field_type", "sample_values", "status"]
    # tolerate universe files with slightly different schemas
    rows = [{c: r.get(c, "") for c in cols} for r in out]
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = run()
    print("FRL PLAYER-SEASON ANALYTICAL CANDIDATE INSPECTION")
    print("=" * 90)
    print(f"Evidence rows: {len(rows)}")
    print(f"Distinct candidates: {len({r['field_name'] for r in rows})}")
    for r in rows:
        print(f"  {r['field_name']:42s} [{r['endpoint_name']}] {r['field_path']} :: {r['field_type']} :: {r['sample_values']}")
    print(f"Output: {OUT}")
    print("Evidence-only inspection; no semantic/canonical promotion.")
