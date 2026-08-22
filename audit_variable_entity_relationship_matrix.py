"""Summarise the 1,414-variable entity attachment matrix.

Evidence-only. Consumes data/variable_entity_relationship_coverage.csv generated
by audit_variable_entity_relationship_coverage.py and groups variables by the
three canonical attachment statuses. It does not infer joins or promote fields.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
INPUT = DATA / "variable_entity_relationship_coverage.csv"
OUTPUT = DATA / "variable_entity_relationship_matrix.csv"

ENTITIES = ("player", "fixture", "club")


def load_rows() -> list[dict[str, str]]:
    with INPUT.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def matrix_class(row: dict[str, str]) -> str:
    statuses = tuple(row[f"{e}_link"] for e in ENTITIES)
    if all(s == "VERIFIED_METADATA_SCOPE" for s in statuses):
        return "ALL_THREE_VERIFIED_METADATA_SCOPE"
    if statuses[0] == "VERIFIED_METADATA_SCOPE" and statuses[1] == "VERIFIED_METADATA_SCOPE":
        return "PLAYER_FIXTURE_VERIFIED"
    if statuses[0] == "VERIFIED_METADATA_SCOPE" and statuses[2] == "VERIFIED_METADATA_SCOPE":
        return "PLAYER_CLUB_VERIFIED"
    if statuses[1] == "VERIFIED_METADATA_SCOPE" and statuses[2] == "VERIFIED_METADATA_SCOPE":
        return "FIXTURE_CLUB_VERIFIED"
    verified = [e for e in ENTITIES if row[f"{e}_link"] == "VERIFIED_METADATA_SCOPE"]
    if len(verified) == 1:
        return f"ONLY_{verified[0].upper()}_VERIFIED"
    metadata = [e for e in ENTITIES if row[f"{e}_link"] == "RELATIONSHIP_METADATA_PRESENT"]
    if metadata:
        return "RELATIONSHIP_METADATA_PRESENT_REVIEW"
    reviews = [e for e in ENTITIES if row[f"{e}_link"] == "RELATIONSHIP_REVIEW"]
    if reviews:
        return "RELATIONSHIP_REVIEW"
    return "NO_DIRECT_ENTITY_SCOPE"


def main() -> list[dict[str, str]]:
    rows = load_rows()
    out: list[dict[str, str]] = []
    for row in rows:
        out.append({
            "field_name": row.get("field_name", ""),
            "source_surface": row.get("source_surface", ""),
            "resource": row.get("resource", ""),
            "grain": row.get("grain", ""),
            "player_link": row.get("player_link", ""),
            "fixture_link": row.get("fixture_link", ""),
            "club_link": row.get("club_link", ""),
            "matrix_class": matrix_class(row),
            "canonical_attachment": row.get("canonical_attachment", ""),
            "relationship_kind": row.get("relationship_kind", ""),
            "identity_contract": row.get("identity_contract", ""),
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        cols = list(out[0]) if out else ["field_name"]
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(out)
    return out


if __name__ == "__main__":
    rows = main()
    counts = Counter(r["matrix_class"] for r in rows)
    grain_counts = Counter(r["grain"] for r in rows)

    print("FRL VARIABLE -> ENTITY RELATIONSHIP MATRIX")
    print("=" * 100)
    print(f"Variables summarised: {len(rows)}")
    print("\nATTACHMENT MATRIX")
    for key, value in counts.most_common():
        print(f"  {value:5d}  {key}")
    print("\nGRAINS")
    for key, value in grain_counts.most_common():
        print(f"  {value:5d}  {key}")
    print(f"\nOutput: {OUTPUT}")
    print("Evidence-only matrix; no inferred joins and no canonical promotion.")
