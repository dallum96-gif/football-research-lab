"""Audit the complete cached live player-season statistics universe.

Evidence-first. Reads cached player_season_stats and player_leaderboard payloads when
available, reports observed native fields and their source endpoint. No semantic or
canonical promotion.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "data" / "live_pl_api_cache"
OUT = ROOT / "data" / "player_season_live_universe.csv"
ENDPOINTS = ("player_season_stats", "player_leaderboard")


def flatten(value: Any, prefix: str = "") -> list[tuple[str, Any]]:
    out: list[tuple[str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            out.append((path, child))
            if isinstance(child, dict):
                out.extend(flatten(child, path))
            elif isinstance(child, list) and child and isinstance(child[0], dict):
                out.extend(flatten(child[0], f"{path}[]"))
    return out


def load_payload(name: str) -> Any:
    path = CACHE / f"{name}.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    return obj["payload"]


def candidate_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for endpoint in ENDPOINTS:
        path = CACHE / f"{endpoint}.json"
        if not path.exists():
            continue
        payload = load_payload(endpoint)
        seen: dict[str, list[Any]] = {}
        for field_path, value in flatten(payload):
            leaf = field_path.split(".")[-1]
            if leaf.endswith("[]"):
                continue
            seen.setdefault(field_path, []).append(value)
        for field_path, values in sorted(seen.items()):
            sample = values[0]
            rows.append({
                "endpoint": endpoint,
                "field_path": field_path,
                "field_name": field_path.split(".")[-1],
                "field_type": type(sample).__name__,
                "sample": repr(sample)[:200],
            })
    return rows


if __name__ == "__main__":
    rows = candidate_rows()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["endpoint","field_path","field_name","field_type","sample"])
        writer.writeheader()
        writer.writerows(rows)

    fields = sorted({r["field_name"] for r in rows})
    print("FRL PLAYER-SEASON LIVE UNIVERSE AUDIT")
    print("=" * 90)
    print(f"Evidence rows: {len(rows)}")
    print(f"Distinct native fields: {len(fields)}")
    for endpoint in ENDPOINTS:
        count = len([r for r in rows if r["endpoint"] == endpoint])
        print(f"  {endpoint:24s} {count}")
    print(f"Output: {OUT}")
    print("Cached payloads only; no semantic/canonical promotion.")
