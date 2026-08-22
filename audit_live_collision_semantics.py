"""Audit live-only native-name collisions using exact endpoint/path/sample evidence.

Evidence-first only. Colliding native names are kept endpoint-specific; no semantic
merge or canonical promotion is performed.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "live_only_analytical_candidate_evidence.csv"
COLLISIONS = ROOT / "data" / "live_candidate_endpoint_semantics.csv"
OUTPUT = ROOT / "data" / "live_collision_semantic_review.csv"


def load_collisions() -> set[str]:
    with COLLISIONS.open("r", encoding="utf-8-sig", newline="") as fh:
        return {
            row.get("field_name", "")
            for row in csv.DictReader(fh)
            if row.get("semantic_merge_status") == "NATIVE_NAME_COLLISION"
        }


def run() -> list[dict[str, str]]:
    targets = load_collisions()
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    with INPUT.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            field = row.get("field_name", "")
            if field in targets:
                grouped[field].append(row)

    out: list[dict[str, str]] = []
    for field in sorted(grouped):
        observations = grouped[field]
        for row in sorted(observations, key=lambda r: (r.get("endpoint_name", ""), r.get("field_path", ""))):
            out.append({
                "field_name": field,
                "endpoint": row.get("endpoint_name", ""),
                "path": row.get("field_path", ""),
                "type": row.get("field_type", ""),
                "sample": row.get("sample", ""),
                "review_status": "OPEN",
            })
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    cols = ["field_name", "endpoint", "path", "type", "sample", "review_status"]
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(out)
    return out


if __name__ == "__main__":
    rows = run()
    by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_field[row["field_name"]].append(row)
    print("FRL LIVE NATIVE-NAME COLLISION SEMANTICS")
    print("=" * 90)
    print(f"Collision fields: {len(by_field)}")
    print(f"Evidence rows:    {len(rows)}")
    for field in sorted(by_field):
        print(f"\n{field}")
        for row in by_field[field]:
            print(f"  [{row['endpoint']}] {row['path']} :: {row['type']} :: {row['sample']}")
    print(f"\nOutput: {OUTPUT}")
    print("Evidence-only review; endpoint-specific semantics remain separate.")
