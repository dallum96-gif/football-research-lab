"""Audit repeated live candidate names by endpoint/path.

Evidence-only: preserve endpoint-specific semantics and flag native-name collisions
that must not be merged into one canonical FRL variable.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "live_only_analytical_candidate_evidence.csv"
OUTPUT = ROOT / "data" / "live_candidate_endpoint_semantics.csv"


def run() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with INPUT.open("r", encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            rows.append(dict(r))

    by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row.get("field_type") in {"int", "float", "str", "bool", "NoneType"}:
            by_field[row.get("field_name", "")].append(row)

    out: list[dict[str, str]] = []
    for field, observations in sorted(by_field.items()):
        endpoints = sorted({o.get("endpoint_name", "") for o in observations if o.get("endpoint_name")})
        paths = sorted({o.get("field_path", "") for o in observations if o.get("field_path")})
        samples = sorted({o.get("sample", "") for o in observations if o.get("sample")})
        out.append({
            "field_name": field,
            "endpoint_count": str(len(endpoints)),
            "endpoints": " | ".join(endpoints),
            "path_count": str(len(paths)),
            "paths": " | ".join(paths),
            "samples": " | ".join(samples),
            "semantic_merge_status": "NATIVE_NAME_COLLISION" if len(endpoints) > 1 else "SINGLE_SURFACE",
            "review_status": "OPEN",
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    cols = [
        "field_name", "endpoint_count", "endpoints", "path_count", "paths",
        "samples", "semantic_merge_status", "review_status",
    ]
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(out)
    return out


if __name__ == "__main__":
    rows = run()
    print("FRL LIVE CANDIDATE ENDPOINT SEMANTICS")
    print("=" * 90)
    print(f"Distinct scalar candidates: {len(rows)}")
    print(f"Native-name collisions requiring separate semantic review: {sum(r['semantic_merge_status'] == 'NATIVE_NAME_COLLISION' for r in rows)}")
    print("\nMULTI-ENDPOINT COLLISIONS")
    for row in rows:
        if row["semantic_merge_status"] == "NATIVE_NAME_COLLISION":
            print(f"  {row['field_name']}: {row['endpoints']}")
    print(f"\nOutput: {OUTPUT}")
    print("Evidence only; no semantic merge or canonical promotion.")
