from __future__ import annotations

import csv
from pathlib import Path
from collections import Counter

from entity_route_inheritance import route_for_entity
from relationship_contracts import get_relationship_contract
from pulselive_season_namespace import season_map

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "routed_variable_attachment_registry_v2.csv"
OUTPUT = ROOT / "data" / "routed_variable_attachment_final.csv"


def n(value: object) -> str:
    return str(value or "").strip()


def main() -> None:
    with INPUT.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    out = []
    for row in rows:
        grain = n(row.get("grain")).lower()
        status = "ROUTE_IMPLEMENTED"
        evidence_gate = "NONE"
        player_gate = "NONE"
        fixture_gate = "NONE"
        team_gate = "NONE"

        if grain == "team_match":
            fixture_gate = "VERIFIED_SOURCE_MATCH_ROUTE"
            team_gate = "VERIFIED_TEAM_SEASON_ROUTE"
        elif grain == "player_match":
            fixture_gate = "VERIFIED_SOURCE_MATCH_ROUTE"
            player_gate = "VERIFIED_PLAYER_IDENTITY_REQUIRED"
        elif grain == "player_season":
            player_gate = "VERIFIED_SOURCE_PLAYER_IDENTITY_REQUIRED"
        elif grain == "squad":
            team_gate = "VERIFIED_TEAM_SEASON_ROUTE_WITH_AUDITED_PROVIDER_SEASON_MAP"
        else:
            status = "NOT_IN_ROUTED_FAMILY"
            evidence_gate = "UNMAPPED_GRAIN"

        contract = n(row.get("identity_contract"))
        if contract:
            try:
                get_relationship_contract(contract)
            except Exception:
                status = "CONTRACT_NOT_RESOLVED"
                evidence_gate = "RELATIONSHIP_CONTRACT_LOOKUP_FAILED"

        merged = dict(row)
        merged.update({
            "final_route_status": status,
            "player_evidence_gate": player_gate,
            "fixture_evidence_gate": fixture_gate,
            "team_evidence_gate": team_gate,
            "provider_season_namespace_entries": str(len(season_map())),
        })
        out.append(merged)

    fields = list(dict.fromkeys(list(out[0].keys()) if out else []))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out)

    print("FRL ROUTED VARIABLE ATTACHMENT FINAL AUDIT")
    print("=" * 80)
    print(f"Routed variables reviewed: {len(rows)}")
    print("Repository contracts/routes only; no inferred joins and no canonical promotion.")
    print()
    for entity, column in (("PLAYER", "player_evidence_gate"), ("FIXTURE", "fixture_evidence_gate"), ("TEAM", "team_evidence_gate")):
        counts = Counter(row[column] for row in out)
        print(entity)
        for key, value in counts.most_common():
            print(f"  {value:4d} {key}")
    print()
    print("FINAL ROUTE STATUS")
    counts = Counter(row["final_route_status"] for row in out)
    for key, value in counts.most_common():
        print(f"  {value:4d} {key}")
    print()
    print(f"Provider season namespace entries available: {len(season_map())}")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    main()
