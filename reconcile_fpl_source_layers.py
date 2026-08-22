"""Reconcile unresolved FPL variables across current raw and historical published layers.

Read-only audit helper. No semantic/canonical promotion.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QUEUE = ROOT / "data" / "unmapped_variable_review_queue.csv"
CURRENT = ROOT / "data" / "unmapped_variable_resolution_fpl_all_raw.csv"
HISTORICAL = ROOT / "data" / "upstream_historical_fpl_schema_audit.csv"
OUTPUT = ROOT / "data" / "fpl_source_layer_reconciliation.csv"


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def run() -> int:
    queue = load_csv(QUEUE)
    current = {row.get("field_name", ""): row for row in load_csv(CURRENT)}
    historical = {row.get("field_name", ""): row for row in load_csv(HISTORICAL)}

    rows: list[dict[str, str]] = []
    for row in queue:
        if row.get("source_surface") != "fpl":
            continue
        field = row.get("field_name", "")
        cur = current.get(field, {})
        hist = historical.get(field, {})
        current_found = cur.get("resolution_status") != "NOT_FOUND_IN_ALL_CAPTURED_RAW_FPL"
        historical_found = hist.get("historical_presence") == "FOUND"
        if current_found and historical_found:
            layer = "BOTH"
        elif current_found:
            layer = "CURRENT_RAW_ONLY"
        elif historical_found:
            layer = "HISTORICAL_PUBLISHED_ONLY"
        else:
            layer = "NEITHER"
        rows.append({
            "field_name": field,
            "resource": row.get("resource", ""),
            "original_grain": row.get("grain", ""),
            "field_type": row.get("field_type", ""),
            "current_raw_found": "YES" if current_found else "NO",
            "current_resolution_status": cur.get("resolution_status", ""),
            "current_resolved_grain": cur.get("resolved_grain", ""),
            "current_evidence_paths": cur.get("evidence_paths", ""),
            "historical_found": "YES" if historical_found else "NO",
            "historical_grains": hist.get("historical_grains", ""),
            "historical_season_files": hist.get("historical_season_files", ""),
            "source_layer_state": layer,
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0].keys()) if rows else []
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    states = Counter(row["source_layer_state"] for row in rows)
    resource_hist_misses = Counter(
        row["resource"] for row in rows if row["historical_found"] == "NO"
    )
    resource_neither = Counter(
        row["resource"] for row in rows if row["source_layer_state"] == "NEITHER"
    )

    print("FRL FPL SOURCE-LAYER RECONCILIATION")
    print("=" * 80)
    print(f"Unresolved FPL fields inspected: {len(rows)}")
    print("SOURCE LAYER STATE")
    for key in ("BOTH", "CURRENT_RAW_ONLY", "HISTORICAL_PUBLISHED_ONLY", "NEITHER"):
        print(f"  {key:28s} {states.get(key, 0)}")
    print("HISTORICAL MISSES BY RESOURCE")
    for resource, count in resource_hist_misses.most_common():
        print(f"  {resource:28s} {count}")
    print("NEITHER LAYER BY RESOURCE")
    for resource, count in resource_neither.most_common():
        print(f"  {resource:28s} {count}")
    print(f"Output: {OUTPUT}")
    print("Evidence reconciliation only; no semantic/canonical promotion.")
    return len(rows)


if __name__ == "__main__":
    run()
