"""Audit actual types and value ranges for the 63 team-leaderboard candidates."""
from __future__ import annotations
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "data" / "live_pl_api_cache" / "team_leaderboard.json"
CLASS = ROOT / "data" / "team_leaderboard_universe_classification.csv"
OUT = ROOT / "data" / "team_leaderboard_candidate_values.csv"


def run() -> list[dict[str, str]]:
    candidates: set[str] = set()
    with CLASS.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("category") == "ANALYTICAL_CANDIDATE":
                candidates.add(row.get("field_name", ""))

    payload = json.loads(CACHE.read_text(encoding="utf-8"))["payload"]
    data = payload.get("data", [])
    observed: dict[str, list[object]] = {name: [] for name in candidates}

    for row in data:
        if not isinstance(row, dict):
            continue
        stats = row.get("stats", {})
        if not isinstance(stats, dict):
            continue
        for name in candidates:
            if name in stats:
                observed[name].append(stats[name])

    rows: list[dict[str, str]] = []
    for name in sorted(candidates):
        values = observed[name]
        type_names = sorted({type(v).__name__ for v in values})
        numeric = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
        samples = []
        for v in values:
            s = repr(v)
            if s not in samples:
                samples.append(s)
            if len(samples) >= 5:
                break
        rows.append({
            "field_name": name,
            "observed_types": " | ".join(type_names),
            "observed_count": str(len(values)),
            "numeric_min": str(min(numeric)) if numeric else "",
            "numeric_max": str(max(numeric)) if numeric else "",
            "sample_values": " | ".join(samples),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=[
            "field_name", "observed_types", "observed_count", "numeric_min", "numeric_max", "sample_values"
        ])
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = run()
    print("FRL TEAM LEADERBOARD CANDIDATE VALUE AUDIT")
    print("=" * 90)
    print(f"Candidates inspected: {len(rows)}")
    for row in rows:
        bounds = ""
        if row["numeric_min"]:
            bounds = f" min={row['numeric_min']} max={row['numeric_max']}"
        print(f"  {row['field_name']:46s} :: {row['observed_types']:10s} :: n={row['observed_count']}{bounds} :: {row['sample_values']}")
    print(f"Output: {OUT}")
    print("Cached payload only; no semantic/canonical promotion.")
