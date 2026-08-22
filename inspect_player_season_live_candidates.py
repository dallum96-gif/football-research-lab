"""Inspect analytical player-season candidates from cached live API evidence.

Evidence-only. Reads existing local CSV/JSON cache, reports endpoint/path/type/sample,
and performs no semantic or canonical promotion.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CLASS = ROOT / "data" / "player_season_live_universe_classification.csv"
UNIVERSE = ROOT / "data" / "player_season_live_universe.csv"
OUT = ROOT / "data" / "player_season_candidate_inspection.csv"
CACHE_DIR = ROOT / "data" / "live_pl_api_cache"


def load_candidates() -> set[str]:
    candidates: set[str] = set()
    with CLASS.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            category = row.get("category", row.get("candidate_family", row.get("status", "")))
            if category == "ANALYTICAL_CANDIDATE":
                candidates.add(row.get("field_name", "").strip())
    return {x for x in candidates if x}


def cached_payload(endpoint: str) -> Any | None:
    path = CACHE_DIR / f"{endpoint}.json"
    if not path.exists():
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        return obj.get("payload")
    except Exception:
        return None


def infer_sample_from_cache(endpoint: str, field_name: str) -> tuple[str, str, str] | None:
    payload = cached_payload(endpoint)
    if payload is None:
        return None

    def walk(value: Any, path: str = "") -> list[tuple[str, Any]]:
        out: list[tuple[str, Any]] = []
        if isinstance(value, dict):
            for k, v in value.items():
                p = f"{path}.{k}" if path else k
                if k == field_name and not isinstance(v, (dict, list)):
                    out.append((p, v))
                if isinstance(v, (dict, list)):
                    out.extend(walk(v, p if isinstance(v, dict) else f"{p}[]"))
        elif isinstance(value, list):
            for item in value[:5]:
                out.extend(walk(item, path))
        return out

    hits = walk(payload)
    if not hits:
        return None
    path, value = hits[0]
    return path, type(value).__name__, repr(value)[:120]


def run() -> list[dict[str, str]]:
    candidates = load_candidates()
    rows: list[dict[str, str]] = []

    with UNIVERSE.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            field = row.get("field_name", "").strip()
            if field not in candidates:
                continue
            endpoint = row.get("endpoint_name", "")
            path = row.get("field_path", "")
            field_type = row.get("field_type", "")
            sample = row.get("sample", row.get("sample_values", ""))
            cached = infer_sample_from_cache(endpoint, field)
            if cached:
                path, field_type, sample = cached
            rows.append({
                "field_name": field,
                "endpoint": endpoint,
                "path": path,
                "type": field_type,
                "sample": sample,
            })

    rows.sort(key=lambda r: (r["field_name"], r["endpoint"], r["path"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["field_name", "endpoint", "path", "type", "sample"])
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = run()
    print("FRL PLAYER-SEASON LIVE ANALYTICAL CANDIDATE INSPECTION")
    print("=" * 90)
    print(f"Evidence rows: {len(rows)}")
    print(f"Distinct candidates: {len({r['field_name'] for r in rows})}")
    for row in rows:
        print(f"  {row['field_name']:42s} [{row['endpoint']}] {row['path']} :: {row['type']} :: {row['sample']}")
    print(f"Output: {OUT}")
    print("Evidence review only; no semantic/canonical promotion.")
