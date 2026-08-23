"""Audit explicit entity-route inheritance for the master variable universe.

Read-only. This reports which entity routes are explicitly defined by source
grain and which variables remain outside the route registry. It does not
perform joins, verify identity rows, or promote relationships.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from entity_route_inheritance import routes_for_grain

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
MASTER = DATA / "master_variable_universe.csv"
OUT = DATA / "variable_entity_route_inheritance.csv"

ENTITIES = ("PLAYER", "FIXTURE", "TEAM")


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader), reader.fieldnames or []


def norm(value: object) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def main() -> None:
    rows, columns = read_csv(MASTER)
    out: list[dict[str, str]] = []
    summary = Counter()

    for row in rows:
        grain = norm(row.get("grain"))
        routes = routes_for_grain(grain)
        by_entity = {route.entity: route for route in routes}
        item = dict(row)
        for entity in ENTITIES:
            route = by_entity.get(entity)
            prefix = entity.lower()
            item[f"{prefix}_route_status"] = "EXPLICIT_ROUTE" if route else "NO_EXPLICIT_ROUTE"
            item[f"{prefix}_route_family"] = route.route_family if route else ""
            item[f"{prefix}_relationship_contract"] = route.relationship_contract if route else ""
            item[f"{prefix}_route_kind"] = route.route_kind if route else ""
            item[f"{prefix}_inherited_from"] = route.inherited_from if route else ""
            summary[(entity, item[f"{prefix}_route_status"])] += 1
        out.append(item)

    print("FRL VARIABLE -> ENTITY ROUTE INHERITANCE AUDIT")
    print("=" * 100)
    print(f"Variables reviewed: {len(rows)}")
    print("Explicit source-family routes only; no inferred joins and no canonical promotion.")
    for entity in ENTITIES:
        print(f"\n{entity}")
        for status in ("EXPLICIT_ROUTE", "NO_EXPLICIT_ROUTE"):
            print(f"  {summary[(entity, status)]:6}  {status}")

    route_grains = Counter(norm(r.get("grain")) for r in rows if routes_for_grain(norm(r.get("grain"))))
    print("\nGRAINS WITH EXPLICIT ROUTES")
    for grain, count in route_grains.most_common():
        print(f"  {count:6}  {grain}")

    fields = list(dict.fromkeys(columns + [
        "player_route_status", "player_route_family", "player_relationship_contract",
        "player_route_kind", "player_inherited_from",
        "fixture_route_status", "fixture_route_family", "fixture_relationship_contract",
        "fixture_route_kind", "fixture_inherited_from",
        "team_route_status", "team_route_family", "team_relationship_contract",
        "team_route_kind", "team_inherited_from",
    ]))
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out)

    print(f"\nOutput: {OUT}")


if __name__ == "__main__":
    main()
