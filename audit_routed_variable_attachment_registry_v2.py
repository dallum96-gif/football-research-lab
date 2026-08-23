"""Build the explicitly routed variable attachment registry.

Read-only over the current master source-field universe. A variable enters this
registry only when entity_route_inheritance.py declares an explicit route for
its source grain. Relationship metadata alone is not treated as a route.
No identity inference and no canonical promotion.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from entity_route_inheritance import route_for_entity
from variable_dictionary_relationships import relationship_for

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
MASTER = DATA / "master_variable_universe.csv"
OUT = DATA / "routed_variable_attachment_registry_v2.csv"
ENTITIES = ("player", "fixture", "team")


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader), reader.fieldnames or []


def n(value: object) -> str:
    return str(value or "").strip()


def main() -> None:
    rows, matrix_fields = read_csv(MASTER)
    out: list[dict[str, str]] = []

    for row in rows:
        resource = n(row.get("resource"))
        grain = n(row.get("grain"))
        rel = relationship_for(resource, grain)

        routes = {
            entity: route_for_entity(grain, entity)
            for entity in ENTITIES
        }

        # Only an explicit entity route makes a variable part of this registry.
        # relationship_for(resource, grain) may provide useful metadata for a
        # source surface without proving that an entity route exists.
        if not any(routes.values()):
            continue

        item = dict(row)
        item.update({
            "canonical_attachment": rel.canonical_attachment,
            "relationship_kind": rel.relationship_kind,
            "identity_contract": rel.identity_contract,
            "source_identity_required": str(rel.source_identity_required),
            "relationship_note": rel.note,
            "player_route": routes["player"].route_family if routes["player"] else "",
            "player_contract": routes["player"].relationship_contract if routes["player"] else "",
            "fixture_route": routes["fixture"].route_family if routes["fixture"] else "",
            "fixture_contract": routes["fixture"].relationship_contract if routes["fixture"] else "",
            "team_route": routes["team"].route_family if routes["team"] else "",
            "team_contract": routes["team"].relationship_contract if routes["team"] else "",
            "route_status": "EXPLICIT_SOURCE_GRAIN_ROUTE",
            "attachment_verified": "NOT_YET_PROVEN",
        })
        out.append(item)

    print("FRL ROUTED VARIABLE ATTACHMENT REGISTRY V2")
    print("=" * 100)
    print(f"Master variables reviewed: {len(rows)}")
    print(f"Explicitly routed variables: {len(out)}")
    print("Only explicit source-grain routes are included; no inferred joins and no canonical promotion.")

    print("\nBY GRAIN")
    for grain, count in Counter(n(r.get("grain")) for r in out).most_common():
        print(f"{count:6}  {grain or '<blank>'}")

    for key, label in (
        ("player_route", "PLAYER"),
        ("fixture_route", "FIXTURE"),
        ("team_route", "TEAM"),
    ):
        print(f"\n{label}")
        for route, count in Counter(n(r.get(key)) for r in out if n(r.get(key))).most_common():
            print(f"{count:6}  {route}")

    fields = list(dict.fromkeys(
        list(matrix_fields)
        + [
            "canonical_attachment",
            "relationship_kind",
            "identity_contract",
            "source_identity_required",
            "relationship_note",
            "player_route",
            "player_contract",
            "fixture_route",
            "fixture_contract",
            "team_route",
            "team_contract",
            "route_status",
            "attachment_verified",
        ]
    ))
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out)

    print(f"\nOutput: {OUT}")


if __name__ == "__main__":
    main()
