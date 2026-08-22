"""Validate Team Leaderboard arithmetic relationships across all cached live observations.

Evidence-first only. Recursively scans the local live Team Leaderboard JSON cache and
looks for dictionaries containing the relevant source fields. Each relationship is
validated only when all required inputs are present and numeric in the same observation.
No canonical promotion.
"""
from __future__ import annotations

import json
import csv
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CACHE_CANDIDATES = [
    ROOT / "data" / "live_pl_api_cache" / "team_leaderboard.json",
    ROOT / "data" / "live_pl_api_cache" / "team_stats.json",
]
OUT = ROOT / "data" / "team_leaderboard_source_relationships_full.csv"

RULES = {
    "duels": (["duelsWon", "duelsLost"], lambda a, b: a + b),
    "goalsConceded": (["goalsConcededInsideBox", "goalsConcededOutsideBox"], lambda a, b: a + b),
    "aerialDuels": (["aerialDuelsWon", "aerialDuelsLost"], lambda a, b: a + b),
}


def numeric(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def walk(node: Any):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    observations: list[dict[str, Any]] = []

    for path in CACHE_CANDIDATES:
        if not path.exists():
            continue
        try:
            payload = load_json(path)
        except Exception:
            continue
        for obj in walk(payload):
            if any(field in obj for field in {k for k, _ in RULES.items()}):
                observations.append({"source_file": str(path), **obj})

    rows: list[dict[str, str]] = []
    for relationship, (inputs, formula) in RULES.items():
        tested = 0
        exact = 0
        violated = 0
        untestable = 0

        for obj in observations:
            observed = numeric(obj.get(relationship))
            vals = [numeric(obj.get(field)) for field in inputs]
            if observed is None or any(v is None for v in vals):
                untestable += 1
                continue
            derived = formula(*vals)
            diff = observed - derived
            tested += 1
            if abs(diff) < 1e-9:
                exact += 1
                status = "EXACT"
            else:
                violated += 1
                status = "VIOLATED"
            rows.append({
                "source_file": str(obj.get("source_file", "")),
                "relationship": relationship,
                "status": status,
                "observed": str(observed),
                "derived": str(derived),
                "difference": str(diff),
            })

        rows.append({
            "source_file": "SUMMARY",
            "relationship": relationship,
            "status": f"SUMMARY tested={tested} exact={exact} violated={violated} untestable={untestable}",
            "observed": "",
            "derived": "",
            "difference": "",
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        cols = ["source_file", "relationship", "status", "observed", "derived", "difference"]
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows)

    print("FRL TEAM LEADERBOARD FULL SOURCE RELATIONSHIP AUDIT")
    print("=" * 90)
    print(f"Candidate observations discovered: {len(observations)}")
    for relationship in RULES:
        summary = next(
            (r["status"] for r in rows if r["source_file"] == "SUMMARY" and r["relationship"] == relationship),
            "SUMMARY unavailable",
        )
        print(f"  {relationship:30s} {summary}")
    print(f"Output: {OUT}")
    print("Evidence-only cross-observation validation; no canonical promotion.")


if __name__ == "__main__":
    main()
