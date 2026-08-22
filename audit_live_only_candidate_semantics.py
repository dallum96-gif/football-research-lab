"""Inspect the finite live-only analytical candidate evidence set.

Reads the already-captured evidence CSV and prints a compact, evidence-first
summary of each distinct candidate. No network access and no semantic/canonical
promotion.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "live_only_analytical_candidate_evidence.csv"
OUTPUT = ROOT / "data" / "live_only_candidate_semantics_audit.csv"


def run() -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    with INPUT.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            grouped[row.get("field_name", "")].append(row)

    rows: list[dict[str, str]] = []
    for field_name in sorted(k for k in grouped if k):
        evidence = grouped[field_name]
        paths = sorted({r.get("field_path", "") for r in evidence if r.get("field_path")})
        endpoints = sorted({r.get("endpoint_name", "") for r in evidence if r.get("endpoint_name")})
        types = sorted({r.get("field_type", "") for r in evidence if r.get("field_type")})
        samples = sorted({r.get("sample", "") for r in evidence if r.get("sample")})

        if any(t in {"object", "array"} for t in types):
            structure = "CONTAINER_OR_NESTED"
        elif types:
            structure = "SCALAR"
        else:
            structure = "NO_EVIDENCE"

        rows.append({
            "field_name": field_name,
            "structure": structure,
            "field_types": " | ".join(types),
            "endpoint_count": str(len(endpoints)),
            "endpoints": " | ".join(endpoints),
            "path_count": str(len(paths)),
            "exact_paths": " | ".join(paths),
            "samples": " | ".join(samples),
        })
    return rows


def main() -> None:
    rows = run()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "field_name", "structure", "field_types", "endpoint_count", "endpoints",
        "path_count", "exact_paths", "samples",
    ]
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    print("FRL LIVE-ONLY ANALYTICAL CANDIDATE SEMANTICS AUDIT")
    print("=" * 90)
    print(f"Distinct candidates: {len(rows)}")
    for row in rows:
        print(f"  {row['structure']:24s} {row['field_name']}")
        print(f"      endpoints: {row['endpoints']}")
        print(f"      paths:     {row['exact_paths']}")
        print(f"      types:     {row['field_types']}")
        if row["samples"]:
            print(f"      samples:   {row['samples']}")
    print(f"\nOutput: {OUTPUT}")
    print("Evidence-only inspection; no semantic/canonical promotion.")


if __name__ == "__main__":
    main()
