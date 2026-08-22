"""Inspect single-surface scalar live-only candidates.

Reads existing local evidence CSV only. No network access and no semantic/canonical promotion.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "live_candidate_endpoint_semantics.csv"
EVIDENCE = ROOT / "data" / "live_only_analytical_candidate_evidence.csv"
OUTPUT = ROOT / "data" / "live_single_surface_candidate_review.csv"


def run() -> list[dict[str, str]]:
    singles: set[str] = set()
    with INPUT.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("semantic_merge_status") == "SINGLE_SURFACE":
                singles.add(row.get("field_name", ""))

    rows: list[dict[str, str]] = []
    with EVIDENCE.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("field_name") in singles:
                rows.append({
                    "field_name": row.get("field_name", ""),
                    "endpoint": row.get("endpoint_name", ""),
                    "path": row.get("field_path", ""),
                    "type": row.get("field_type", ""),
                    "sample": row.get("sample", ""),
                    "review_status": "OPEN",
                })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["field_name","endpoint","path","type","sample","review_status"])
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = run()
    print("FRL LIVE SINGLE-SURFACE CANDIDATE REVIEW")
    print("=" * 90)
    print(f"Evidence rows: {len(rows)}")
    for row in rows:
        print(f"  {row['field_name']:42s} [{row['endpoint']}] {row['path']} :: {row['type']} :: {row['sample']}")
    print(f"Output: {OUTPUT}")
    print("Evidence review only; no semantic/canonical promotion.")
