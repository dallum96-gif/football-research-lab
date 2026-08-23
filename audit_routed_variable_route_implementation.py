"""Classify the explicit routed variable universe by route implementation state.

Read-only audit. It does not infer identity, perform joins, or promote canonical
relationships. It compares the explicit routed grain against the documented
source-family adapters and relationship contracts currently implemented in the
repository.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
ROUTED = DATA / "routed_variable_attachment_registry_v2.csv"
OUT = DATA / "routed_variable_route_implementation.csv"

FAMILIES = {
    "team_match": {
        "fixture": "IMPLEMENTED_SOURCE_MATCH_ROUTE",
        "team": "IMPLEMENTED_TEAM_SEASON_ROUTE",
        "player": "NOT_APPLICABLE",
    },
    "player_match": {
        "fixture": "IMPLEMENTED_SOURCE_MATCH_ROUTE",
        "player": "IMPLEMENTED_OBSERVATION_ROUTE_REQUIRES_VERIFIED_PLAYER",
        "team": "NOT_DIRECTLY_IMPLEMENTED",
    },
    "player_season": {
        "player": "IMPLEMENTED_SOURCE_PLAYER_SEASON_ROUTE_REQUIRES_IDENTITY_BRIDGE",
        "fixture": "NOT_APPLICABLE",
        "team": "NOT_APPLICABLE",
    },
    "squad": {
        "team": "CONTRACT_DECLARED_ADAPTER_NOT_PRESENT",
        "fixture": "NOT_APPLICABLE",
        "player": "NOT_APPLICABLE",
    },
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def n(value: object) -> str:
    return str(value or "").strip()


def main() -> None:
    rows = read_csv(ROUTED)
    out: list[dict[str, str]] = []

    for row in rows:
        grain = n(row.get("grain"))
        rules = FAMILIES.get(grain, {})
        item = dict(row)
        item["player_route_implementation"] = rules.get("player", "NO_GRAIN_ROUTE_RULE")
        item["fixture_route_implementation"] = rules.get("fixture", "NO_GRAIN_ROUTE_RULE")
        item["team_route_implementation"] = rules.get("team", "NO_GRAIN_ROUTE_RULE")
        out.append(item)

    print("FRL ROUTED VARIABLE ROUTE IMPLEMENTATION AUDIT")
    print("=" * 100)
    print(f"Routed variables reviewed: {len(rows)}")
    print("Repository implementation evidence only; no inferred joins and no canonical promotion.")

    for entity, key in (("PLAYER", "player_route_implementation"), ("FIXTURE", "fixture_route_implementation"), ("TEAM", "team_route_implementation")):
        print(f"\n{entity}")
        for status, count in Counter(n(r.get(key)) for r in out).most_common():
            print(f"{count:6}  {status}")

    print("\nBY GRAIN")
    for grain, count in Counter(n(r.get("grain")) for r in out).most_common():
        print(f"{count:6}  {grain or '<blank>'}")

    fields = list(dict.fromkeys(list(rows[0].keys()) if rows else []))
    fields.extend([
        "player_route_implementation",
        "fixture_route_implementation",
        "team_route_implementation",
    ])
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out)
    print(f"\nOutput: {OUT}")


if __name__ == "__main__":
    main()
