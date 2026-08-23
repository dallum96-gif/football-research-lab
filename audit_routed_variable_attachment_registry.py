"""Build the explicit routed variable attachment registry.

Read-only over the current source-field universe. This does not infer identity
or promote source records; it records only relationship metadata already declared
in the repository's variable dictionary and source-family route definitions.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from variable_dictionary_relationships import relationship_for
from entity_route_inheritance import route_for_entity

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
MASTER = DATA / "master_variable_universe.csv"
OUT = DATA / "routed_variable_attachment_registry.csv"


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        r = csv.DictReader(fh)
        return list(r), r.fieldnames or []


def n(v):
    return str(v or "").strip()


def main() -> None:
    rows, _ = read_csv(MASTER)
    out = []
    routed = 0

    for row in rows:
        resource = n(row.get("resource"))
        grain = n(row.get("grain"))
        rel = relationship_for(resource, grain)

        entity_routes = {}
        explicit = bool(rel.identity_contract or rel.canonical_attachment != "UNMAPPED_REVIEW")
        for entity in ("player", "fixture", "team"):
            route = route_for_entity(grain, entity)
            entity_routes[entity] = route or ""
            explicit = explicit or bool(route)

        if not explicit:
            continue

        routed += 1
        item = dict(row)
        item.update({
            "canonical_attachment": rel.canonical_attachment,
            "relationship_kind": rel.relationship_kind,
            "identity_contract": rel.identity_contract,
            "source_identity_required": str(rel.source_identity_required),
            "relationship_note": rel.note,
            "player_route": entity_routes["player"],
            "fixture_route": entity_routes["fixture"],
            "team_route": entity_routes["team"],
            "route_status": "EXPLICIT_SOURCE_FAMILY_ROUTE",
            "attachment_verified": "NOT_YET_PROVEN",
        })
        out.append(item)

    print("FRL ROUTED VARIABLE ATTACHMENT REGISTRY")
    print("=" * 100)
    print(f"Master variables reviewed: {len(rows)}")
    print(f"Explicitly routed variables: {routed}")
    print("No identity inference and no canonical promotion.")

    print("\nBY GRAIN")
    for grain, count in Counter(n(r.get("grain")) for r in out).most_common():
        print(f"{count:6}  {grain or '<blank>'}")
    print("\nBY CONTRACT")
    for contract, count in Counter(n(r.get("identity_contract")) for r in out).most_common():
        print(f"{count:6}  {contract or '<none>'}")
    print("\nENTITY ROUTES")
    for key, label in (("player_route", "PLAYER"), ("fixture_route", "FIXTURE"), ("team_route", "TEAM")):
        print(f"\n{label}")
        for route, count in Counter(n(r.get(key)) for r in out if n(r.get(key))).most_common():
            print(f"{count:6}  {route}")

    fields = list(dict.fromkeys((rows[0].keys() if rows else []) + [
        "canonical_attachment", "relationship_kind", "identity_contract",
        "source_identity_required", "relationship_note", "player_route",
        "fixture_route", "team_route", "route_status", "attachment_verified"
    ]))
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(out)
    print(f"\nOutput: {OUT}")


if __name__ == "__main__":
    main()
