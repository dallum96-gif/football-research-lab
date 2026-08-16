"""Generate the verified FRL FPL-element -> source player identity registry.

The registry is deliberately derived from the audited exact-name+verified-team
matches. It never promotes unresolved or ambiguous records.
"""

from __future__ import annotations

import csv
from pathlib import Path

import player_identity_crosswalk


OUTPUT = Path("player_identity_registry.csv")
FIELDS = (
    "season",
    "fpl_element",
    "fpl_name_normalized",
    "team_code",
    "source_player_id",
    "match_method",
    "confidence",
    "identity_status",
    "evidence_basis",
)


def build_registry() -> list[dict[str, str]]:
    report = player_identity_crosswalk.summarize()
    if report["review_rows"]:
        raise ValueError(
            f"Cannot promote crosswalk: {report['review_rows']} review rows remain."
        )

    rows = []
    seen = set()
    for item in report["confirmed"]:
        key = (item["season"], item["element"])
        if key in seen:
            raise ValueError(f"Duplicate FPL identity: {key}")
        seen.add(key)
        rows.append(
            {
                "season": item["season"],
                "fpl_element": item["element"],
                "fpl_name_normalized": item["name_norm"],
                "team_code": item["team_code"],
                "source_player_id": item["source_player_id"],
                "match_method": item["method"],
                "confidence": "VERIFIED",
                "identity_status": "VERIFIED",
                "evidence_basis": "exact normalized name + verified seasonal team identity",
            }
        )

    rows.sort(key=lambda r: (r["season"], int(r["fpl_element"])))
    return rows


def write_registry(output: Path = OUTPUT) -> list[dict[str, str]]:
    rows = build_registry()
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = write_registry()
    print("=" * 88)
    print("FRL VERIFIED PLAYER IDENTITY REGISTRY")
    print("=" * 88)
    print(f"Rows written: {len(rows):,}")
    print(f"Output: {OUTPUT}")
    print("Only deterministic EXACT_NAME_TEAM rows are included.")
    print("All unresolved identities remain outside the registry.")
    print("=" * 88)
