"""Build a finite, evidence-first queue for unresolved variable grain review."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "master_variable_universe_decomposed.csv"
OUTPUT = ROOT / "data" / "unmapped_variable_review_queue.csv"

REQUIRED = (
    "source_surface",
    "resource",
    "grain",
    "field_name",
    "decomposed_grain",
    "decomposition_basis",
)


def build_queue(input_path: Path = INPUT, output_path: Path = OUTPUT) -> list[dict[str, str]]:
    with input_path.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))

    missing = [c for c in REQUIRED if c not in (rows[0].keys() if rows else [])]
    if missing:
        raise ValueError("Input missing required columns: " + ", ".join(missing))

    queue: list[dict[str, str]] = []
    for row in rows:
        if row.get("decomposed_grain") != "UNMAPPED_REVIEW":
            continue
        queue.append({
            "source_surface": row.get("source_surface", ""),
            "resource": row.get("resource", ""),
            "original_grain": row.get("grain", ""),
            "field_name": row.get("field_name", ""),
            "field_type": row.get("field_type", ""),
            "decomposed_grain": row.get("decomposed_grain", ""),
            "decomposition_basis": row.get("decomposition_basis", ""),
            "notes": row.get("notes", ""),
            "review_status": "OPEN",
            "resolution": "",
            "evidence_required": "raw path/context or source-schema evidence",
        })

    queue.sort(key=lambda r: (r["source_surface"], r["resource"], r["field_name"]))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(queue[0].keys()) if queue else [
        "source_surface", "resource", "original_grain", "field_name", "field_type",
        "decomposed_grain", "decomposition_basis", "notes", "review_status",
        "resolution", "evidence_required",
    ]
    with output_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(queue)
    return queue


def profile(queue: list[dict[str, str]]) -> dict[str, Counter[str] | int]:
    return {
        "count": len(queue),
        "source_surface": Counter(r["source_surface"] for r in queue),
        "resource": Counter(r["resource"] for r in queue),
        "field_type": Counter(r["field_type"] for r in queue),
    }


def main() -> None:
    queue = build_queue()
    p = profile(queue)
    print("FRL UNMAPPED VARIABLE STRUCTURAL REVIEW QUEUE")
    print("=" * 90)
    print(f"Open unresolved variables: {p['count']}")
    for label in ("source_surface", "resource", "field_type"):
        print(f"\n{label.upper()}")
        for key, count in p[label].most_common():
            print(f"  {count:4d}  {key}")
    print(f"\nOutput: {OUTPUT}")
    print("No canonical relationship is created; review remains fail-closed.")


if __name__ == "__main__":
    main()
