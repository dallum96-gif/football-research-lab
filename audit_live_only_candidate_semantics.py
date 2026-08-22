"""Inspect exact cached evidence for live-only analytical candidates.

Evidence-first only: reads the local audit outputs and cached live payloads,
prints full JSON paths, types and bounded samples for scalar candidates, and
keeps containers explicitly flagged. No semantic/canonical promotion.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "live_only_analytical_candidate_evidence.csv"
OUTPUT = ROOT / "data" / "live_only_candidate_semantic_audit.csv"

CONTAINER_TYPES = {"object", "array", "CACHE_MISSING", "NOT_FOUND_IN_CACHE"}


def flatten(value: Any, prefix: str = "") -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(child, dict):
                out.append((path, "object", "dict"))
                out.extend(flatten(child, path))
            elif isinstance(child, list):
                out.append((path, "array", "list"))
                if child and isinstance(child[0], dict):
                    out.extend(flatten(child[0], f"{path}[]"))
            else:
                out.append((path, type(child).__name__, repr(child)[:200]))
    return out


def terminal(path: str) -> str:
    return path.replace("[]", "").split(".")[-1]


def run() -> list[dict[str, str]]:
    candidates: defaultdict[str, set[str]] = defaultdict(set)
    with INPUT.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            field = row.get("field_name", "")
            endpoint = row.get("endpoint_name", "")
            if field and endpoint:
                candidates[endpoint].add(field)

    rows: list[dict[str, str]] = []
    for endpoint, fields in sorted(candidates.items()):
        cache_path = ROOT / "data" / "live_pl_api_cache" / f"{endpoint}.json"
        payload = None
        if cache_path.exists():
            try:
                payload = json.loads(cache_path.read_text(encoding="utf-8"))["payload"]
            except Exception:
                payload = None
        flat = flatten(payload) if payload is not None else []
        for field in sorted(fields):
            matches = [x for x in flat if terminal(x[0]) == field]
            if not matches:
                rows.append({
                    "endpoint_name": endpoint,
                    "field_name": field,
                    "field_path": "",
                    "field_type": "NOT_FOUND",
                    "sample": "",
                    "evidence_role": "REVIEW",
                })
                continue
            for path, kind, sample in matches:
                role = "CONTAINER" if kind in CONTAINER_TYPES else "SCALAR_OR_VALUE"
                rows.append({
                    "endpoint_name": endpoint,
                    "field_name": field,
                    "field_path": path,
                    "field_type": kind,
                    "sample": sample,
                    "evidence_role": role,
                })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    cols = ["endpoint_name", "field_name", "field_path", "field_type", "sample", "evidence_role"]
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = run()
    scalar = sum(r["evidence_role"] == "SCALAR_OR_VALUE" for r in rows)
    containers = sum(r["evidence_role"] == "CONTAINER" for r in rows)
    review = sum(r["evidence_role"] == "REVIEW" for r in rows)
    print("FRL LIVE-ONLY CANDIDATE SEMANTIC EVIDENCE AUDIT")
    print("=" * 90)
    print(f"Evidence rows: {len(rows)}")
    print(f"Scalar/value evidence: {scalar}")
    print(f"Container structures:  {containers}")
    print(f"Review/not found:      {review}")
    print(f"Output: {OUTPUT}")
    print("Evidence structure only; no semantic/canonical promotion.")
