"""Audit the complete cached team_leaderboard stats universe.

Evidence-only. Reads the existing cached live API payload and reports every
stats.* field observed, its type, sample values, and whether the native field
name appears in the local FRL catalogue headers. No semantic/canonical promotion.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "data" / "live_pl_api_cache" / "team_leaderboard.json"
OUT = ROOT / "data" / "team_leaderboard_universe_audit.csv"


def collect_local_fields() -> set[str]:
    fields: set[str] = set()
    for path in ROOT.rglob("*.csv"):
        if path.resolve() == OUT.resolve():
            continue
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as fh:
                reader = csv.reader(fh)
                header = next(reader, [])
                fields.update(x.strip() for x in header if x.strip())
        except Exception:
            continue
    return fields


def run() -> list[dict[str, str]]:
    payload = json.loads(CACHE.read_text(encoding="utf-8"))["payload"]
    data = payload.get("data", [])
    local = collect_local_fields()
    seen: dict[str, list[str]] = {}
    for row in data:
        stats = row.get("stats", {}) if isinstance(row, dict) else {}
        if not isinstance(stats, dict):
            continue
        for key, value in stats.items():
            seen.setdefault(key, []).append(repr(value)[:120])

    rows: list[dict[str, str]] = []
    for field in sorted(seen):
        samples = seen[field]
        status = "EXISTING_FIELD" if field in local else "LIVE_ONLY_CANDIDATE"
        rows.append({
            "field_name": field,
            "field_type": type(json.loads(samples[0])).__name__ if False else type(next((v for v in samples), None)).__name__,
            "sample_values": " | ".join(dict.fromkeys(samples[:5])),
            "status": status,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["field_name", "field_type", "sample_values", "status"])
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = run()
    print("FRL TEAM LEADERBOARD STATS UNIVERSE AUDIT")
    print("=" * 90)
    print(f"Observed team_leaderboard stats fields: {len(rows)}")
    print(f"Live-only candidates: {sum(r['status'] == 'LIVE_ONLY_CANDIDATE' for r in rows)}")
    print(f"Output: {OUT}")
    print("Cached payload only; no network access and no semantic/canonical promotion.")
