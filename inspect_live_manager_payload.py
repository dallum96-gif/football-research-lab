"""Inspect manager data already captured in the live match-lineups payload.

No network access. Evidence-only inspection of the local live API cache.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "data" / "live_pl_api_cache" / "match_lineups.json"
OUTPUT = ROOT / "data" / "live_manager_payload_evidence.csv"


def walk(value: Any, path: str = "") -> list[tuple[str, Any]]:
    out: list[tuple[str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            p = f"{path}.{key}" if path else str(key)
            out.append((p, child))
            out.extend(walk(child, p))
    elif isinstance(value, list):
        if value and isinstance(value[0], (dict, list)):
            out.extend(walk(value[0], f"{path}[]"))
    return out


def bounded(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))[:400]
    except TypeError:
        return repr(value)[:400]


def run() -> list[dict[str, str]]:
    if not CACHE.exists():
        raise FileNotFoundError(f"Missing cached payload: {CACHE}")
    payload = json.loads(CACHE.read_text(encoding="utf-8"))["payload"]
    rows: list[dict[str, str]] = []
    for path, value in walk(payload):
        leaf = path.replace("[]", "").split(".")[-1].lower()
        if "manager" in leaf or "manager" in path.lower():
            rows.append({
                "path": path,
                "field_type": type(value).__name__,
                "sample": bounded(value),
            })
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["path", "field_type", "sample"])
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = run()
    print("FRL LIVE MANAGER PAYLOAD EVIDENCE")
    print("=" * 90)
    print(f"Manager-related evidence rows: {len(rows)}")
    for row in rows:
        print(f"  {row['field_type']:12s} {row['path']}")
        print(f"      {row['sample']}")
    print(f"Output: {OUTPUT}")
    print("Evidence-only inspection; no identity or canonical promotion.")
