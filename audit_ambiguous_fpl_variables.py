"""Audit ambiguous FPL structural resolutions by field/resource/grain evidence.

No semantic promotion and no identity resolution are performed. This tool only
summarises the evidence already captured by resolve_unmapped_fpl_from_all_raw.py.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "unmapped_variable_resolution_fpl_all_raw.csv"
OUTPUT = ROOT / "data" / "ambiguous_fpl_variable_audit.csv"


def load_rows(path: Path = INPUT) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _split_values(value: str) -> list[str]:
    return [v.strip() for v in value.split(";") if v.strip()]


def summarise(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    groups: dict[str, dict[str, set[str]]] = {}
    for row in rows:
        if row.get("resolution_status") != "AMBIGUOUS_RAW_FPL_GRAIN":
            continue
        field = row.get("field_name", "")
        bucket = groups.setdefault(field, {"grains": set(), "resources": set(), "paths": set()})
        bucket["grains"].update(_split_values(row.get("upstream_matches", "")))
        bucket["resources"].update(_split_values(row.get("matched_resources", "")))
        bucket["paths"].update(_split_values(row.get("matched_paths", "")))

    output: list[dict[str, str]] = []
    for field in sorted(groups):
        bucket = groups[field]
        output.append({
            "field_name": field,
            "candidate_grains": ";".join(sorted(bucket["grains"])),
            "candidate_resources": ";".join(sorted(bucket["resources"])),
            "evidence_paths": ";".join(sorted(bucket["paths"])),
            "review_status": "OPEN",
            "resolution": "",
            "evidence_required": "resource/path context sufficient to select one structural grain",
        })
    return output


def run(input_path: Path = INPUT, output_path: Path = OUTPUT) -> int:
    rows = summarise(load_rows(input_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    columns = ["field_name", "candidate_grains", "candidate_resources", "evidence_paths", "review_status", "resolution", "evidence_required"]
    with output_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    count = run()
    print("FRL AMBIGUOUS FPL VARIABLE AUDIT")
    print("=" * 80)
    print(f"Distinct ambiguous fields: {count}")
    print(f"Output: {OUTPUT}")
    print("Evidence summary only; no semantic/canonical promotion.")
