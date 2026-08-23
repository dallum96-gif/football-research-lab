"""Profile variables that have relationship metadata but no verified attachment.

Evidence-only. Consumes the existing variable/entity coverage matrix and local
FRL variable dictionary when available. Does not infer joins or promote fields.
The goal is to isolate the next relationship-resolution frontier by source
surface, resource, grain and explicit relationship metadata.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
INPUT = DATA / "variable_entity_relationship_coverage.csv"
DICT = DATA / "frl_variable_dictionary.csv"
OUT = DATA / "relationship_metadata_review_frontier.csv"


def load(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def field_key(row: dict[str, str]) -> str:
    return (row.get("field_name") or "").strip()


def main() -> list[dict[str, str]]:
    coverage = [r for r in load(INPUT) if field_key(r)]
    dictionary = {field_key(r): r for r in load(DICT) if field_key(r)}

    frontier: list[dict[str, str]] = []
    for row in coverage:
        statuses = [row.get(f"{e}_link", "") for e in ("player", "fixture", "club")]
        if "RELATIONSHIP_METADATA_PRESENT" not in statuses and "RELATIONSHIP_REVIEW" not in statuses:
            continue

        meta = dictionary.get(field_key(row), {})
        frontier.append({
            "field_name": field_key(row),
            "source_surface": row.get("source_surface", ""),
            "resource": row.get("resource", ""),
            "grain": row.get("grain", ""),
            "player_link": row.get("player_link", ""),
            "fixture_link": row.get("fixture_link", ""),
            "club_link": row.get("club_link", ""),
            "canonical_attachment": row.get("canonical_attachment", "") or meta.get("canonical_attachment", ""),
            "relationship_kind": row.get("relationship_kind", "") or meta.get("relationship_kind", ""),
            "identity_contract": row.get("identity_contract", "") or meta.get("identity_contract", ""),
            "source_identity_required": row.get("source_identity_required", "") or meta.get("source_identity_required", ""),
            "relationship_note": row.get("relationship_note", "") or meta.get("relationship_note", ""),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols = list(frontier[0]) if frontier else ["field_name"]
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(frontier)

    return frontier


if __name__ == "__main__":
    rows = main()
    by_surface = Counter(r["source_surface"] or "UNKNOWN" for r in rows)
    by_grain = Counter(r["grain"] or "UNKNOWN" for r in rows)
    by_kind = Counter(r["relationship_kind"] or "UNSPECIFIED" for r in rows)
    by_contract = Counter(r["identity_contract"] or "UNSPECIFIED" for r in rows)

    print("FRL RELATIONSHIP METADATA REVIEW FRONTIER")
    print("=" * 100)
    print(f"Variables in review frontier: {len(rows)}")

    print("\nBY SOURCE SURFACE")
    for key, value in by_surface.most_common():
        print(f"  {value:5d}  {key}")

    print("\nBY GRAIN")
    for key, value in by_grain.most_common():
        print(f"  {value:5d}  {key}")

    print("\nBY RELATIONSHIP KIND")
    for key, value in by_kind.most_common():
        print(f"  {value:5d}  {key}")

    print("\nBY IDENTITY CONTRACT")
    for key, value in by_contract.most_common():
        print(f"  {value:5d}  {key}")

    print(f"\nOutput: {OUT}")
    print("Evidence-only relationship metadata profiling; no inferred joins and no canonical promotion.")
