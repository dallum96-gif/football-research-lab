"""Generate the verified FRL FPL-element -> source player identity registry.

The registry is derived exclusively from the canonical player identity audit.
Only exact 1:1 rows already accepted by that audit are promoted. Unresolved
or ambiguous identities remain outside the registry.
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

    for season in player_identity_audit.SEASONS:
        report = player_identity_audit.audit_season(season)
        for item in report["exact"]:
            element = str(item.get("fpl_player_code") or "").strip()
            source_id = str(item.get("source_player_id") or "").strip()
            team_code = str(item.get("team_code") or "").strip()
            if not element or not source_id:
                continue

            name = str(item.get("fpl_name") or "").strip()
            rows.append(
                {
                    "season": season,
                    "fpl_element": element,
                    "fpl_name_normalized": player_identity_audit.normalize_name(name),
                    "team_code": team_code,
                    "source_player_id": source_id,
                    "match_method": "EXACT_NAME_TEAM",
                    "confidence": "VERIFIED",
                    "identity_status": "VERIFIED",
                    "evidence_basis": (
                        "canonical player_identity_audit exact 1:1 match using normalized name "
                        "and verified seasonal team identity"
                    ),
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
    print("Only canonical audit exact 1:1 rows are included.")
    print("All unresolved or ambiguous identities remain outside the registry.")
    print("=" * 88)
