"""Summarise exact evidence for live-only analytical candidates.

Reads the locally generated evidence CSV and groups rows by candidate field.
No semantic or canonical promotion is performed.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "live_only_analytical_candidate_evidence.csv"
OUTPUT = ROOT / "data" / "live_only_analytical_evidence_summary.csv"


def run() -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    with INPUT.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            grouped[row.get("field_name", "")].append(row)

    out: list[dict[str, str]] = []
    for field in sorted(grouped):
        rows = grouped[field]
        paths = sorted({r.get("field_path", "") for r in rows if r.get("field_path")})
        endpoints = sorted({r.get("endpoint_name", "") for r in rows if r.get("endpoint_name")})
        types = sorted({r.get("field_type", "") for r in rows if r.get("field_type")})
        containers = [t for t in types if t in {"object", "array"}]
        scalar_types = [t for t in types if t not in {"object", "array", "CACHE_MISSING", "NOT_FOUND_IN_CACHE"}]
        if containers and not scalar_types:
            role = "CONTAINER_OR_NESTED_STRUCTURE"
        elif scalar_types:
            role = "SCALAR_EVIDENCE"
        else:
            role = "REVIEW"
        out.append({
            "field_name": field,
            "endpoint_count": str(len(endpoints)),
            "path_count": str(len(paths)),
            "endpoints": " | ".join(endpoints),
            "paths": " | ".join(paths),
            "field_types": " | ".join(types),
            "evidence_role": role,
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    columns = ["field_name", "endpoint_count", "path_count", "endpoints", "paths", "field_types", "evidence_role"]
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(out)
    return out


if __name__ == "__main__":
    rows = run()
    print("FRL LIVE-ONLY ANALYTICAL EVIDENCE SUMMARY")
    print("=" * 90)
    print(f"Distinct candidate fields: {len(rows)}")
    for row in rows:
        print(
            f"  {row['evidence_role']:30s} {row['field_name']:<55s} "
            f"paths={row['path_count']} endpoints={row['endpoint_count']}"
        )
    print(f"\nOutput: {OUTPUT}")
    print("Evidence structure only; no semantic/canonical promotion.")
