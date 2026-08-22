"""Audit live-only analytical candidates against cached live API payloads.

Reads local live API cache + classification/inspection outputs. Evidence only:
records exact endpoint, field path, field type and a bounded sample representation.
No semantic or canonical promotion.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "data" / "live_pl_api_cache"
INPUT = ROOT / "data" / "live_only_football_field_inspection.csv"
OUTPUT = ROOT / "data" / "live_only_analytical_candidate_evidence.csv"


def flatten(value: Any, prefix: str = "") -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(child, (dict, list)):
                kind = "object" if isinstance(child, dict) else "array"
                sample = type(child).__name__
                out.append((path, kind, sample))
                if isinstance(child, dict):
                    out.extend(flatten(child, path))
                elif child and isinstance(child[0], dict):
                    out.extend(flatten(child[0], f"{path}[]"))
            else:
                out.append((path, type(child).__name__, repr(child)[:160]))
    return out


def terminal(path: str) -> str:
    return path.replace("[]", "").split(".")[-1]


def run() -> list[dict[str, str]]:
    candidates: dict[str, set[str]] = {}
    with INPUT.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("candidate_role") != "ANALYTICAL_CANDIDATE":
                continue
            for endpoint in [x.strip() for x in row.get("live_endpoints", "").split(" | ") if x.strip()]:
                candidates.setdefault(endpoint, set()).add(row["field_name"])

    rows: list[dict[str, str]] = []
    for endpoint, fields in sorted(candidates.items()):
        cache_path = CACHE / f"{endpoint}.json"
        if not cache_path.exists():
            for field in sorted(fields):
                rows.append({"endpoint_name": endpoint, "field_name": field, "field_path": "", "field_type": "CACHE_MISSING", "sample": ""})
            continue
        payload = json.loads(cache_path.read_text(encoding="utf-8"))["payload"]
        flattened = flatten(payload)
        for field in sorted(fields):
            matches = [item for item in flattened if terminal(item[0]) == field]
            if not matches:
                rows.append({"endpoint_name": endpoint, "field_name": field, "field_path": "", "field_type": "NOT_FOUND_IN_CACHE", "sample": ""})
                continue
            for path, kind, sample in matches:
                rows.append({"endpoint_name": endpoint, "field_name": field, "field_path": path, "field_type": kind, "sample": sample})

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    columns = ["endpoint_name", "field_name", "field_path", "field_type", "sample"]
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = run()
    print("FRL LIVE-ONLY ANALYTICAL CANDIDATE EVIDENCE")
    print("=" * 90)
    print(f"Candidate evidence rows: {len(rows)}")
    print(f"Output: {OUTPUT}")
    print("Exact cached payload paths only; no semantic/canonical promotion.")
