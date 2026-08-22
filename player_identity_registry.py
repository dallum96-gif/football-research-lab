"""Generate the verified FRL FPL-element -> source player identity registry.

The registry is derived from the canonical player identity audit. It never
creates a new identity join path: only rows already classified as exact by the
existing audit seam are eligible for promotion. Unresolved and ambiguous rows
remain outside the registry.
"""

from __future__ import annotations

import csv
from pathlib import Path

import player_identity_audit

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
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    for season in player_identity_audit.SEASONS:
        report = player_identity_audit.audit_season(season)
        for item in report["exact"]:
            key = (str(season), str(item["fpl_player_code"]), str(item["source_player_id"]))
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                "season": str(season),
                "fpl_element": str(item["fpl_player_code"]),
                "fpl_name_normalized": player_identity_audit.normalize_name(item["fpl_name"]),
                "team_code": str(item["team_code"]),
                "source_player_id": str(item["source_player_id"]),
                "match_method": "EXACT_NAME_TEAM",
                "confidence": "VERIFIED",
                "identity_status": "VERIFIED",
                "evidence_basis": "canonical player_identity_audit exact normalized name + verified seasonal team identity + unique source playerId",
            })

    rows.sort(key=lambda row: (row["season"], int(row["fpl_element"])))
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
    print("Only canonical-audit exact rows are included.")
    print("All unresolved, ambiguous, unavailable, or contradictory identities remain outside the registry.")
    print("=" * 88)
