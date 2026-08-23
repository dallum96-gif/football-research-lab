"""Generate the verified FRL FPL-element -> source player identity registry.

Verified routes are deliberately explicit:

1. Existing canonical ``player_identity_audit`` exact 1:1 name + verified-team
   matches.
2. Historical source-family evidence where a season-local FPL ``element`` has
   an exact normalized name match in the committed seasonal PL player index
   and that source playerId is actually present in Player-Match for the same
   season.

Conflicting or ambiguous identities are never promoted.
"""

from __future__ import annotations

from collections import defaultdict
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


def _canonical_exact_rows() -> list[dict[str, str]]:
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
    return rows


def _historical_index_candidates() -> list[dict[str, str]]:
    """Return independently verified historical source-family identity candidates."""
    from audit_fpl_element_historical_pl_index import audit

    result = audit()
    rows: list[dict[str, str]] = []
    for item in result["rows"]:
        if item.get("status") != "VERIFIED_CANDIDATE":
            continue

        season = str(item.get("season") or "").strip()
        element = str(item.get("fpl_element") or "").strip()
        source_id = str(item.get("source_player_id") or "").strip()
        name = str(item.get("fpl_name") or "").strip()
        if not season or not element or not source_id or not name:
            continue

        rows.append(
            {
                "season": season,
                "fpl_element": element,
                "fpl_name_normalized": player_identity_audit.normalize_name(name),
                "team_code": "",
                "source_player_id": source_id,
                "match_method": "HISTORICAL_PL_INDEX_NAME_PLAYER_MATCH",
                "confidence": "VERIFIED",
                "identity_status": "VERIFIED",
                "evidence_basis": (
                    "exact season-local normalized FPL name match to committed historical PL "
                    "player index plus the same source playerId is present in Player-Match for "
                    "that season; no cross-season continuity or numeric-code equality used"
                ),
            }
        )
    return rows


def build_registry() -> list[dict[str, str]]:
    by_key: dict[tuple[str, str], dict[str, str]] = {}
    conflicts: set[tuple[str, str]] = set()

    for row in _canonical_exact_rows():
        key = (row["season"], row["fpl_element"])
        existing = by_key.get(key)
        if existing is not None and existing["source_player_id"] != row["source_player_id"]:
            conflicts.add(key)
            continue
        by_key[key] = row

    for row in _historical_index_candidates():
        key = (row["season"], row["fpl_element"])
        existing = by_key.get(key)
        if existing is None:
            by_key[key] = row
        elif existing["source_player_id"] != row["source_player_id"]:
            conflicts.add(key)

    for key in conflicts:
        by_key.pop(key, None)

    rows = list(by_key.values())
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
    counts = defaultdict(int)
    for row in rows:
        counts[row["match_method"]] += 1

    print("=" * 88)
    print("FRL VERIFIED PLAYER IDENTITY REGISTRY")
    print("=" * 88)
    print(f"Rows written: {len(rows):,}")
    for method, count in sorted(counts.items()):
        print(f"  {method}: {count:,}")
    print("Only evidence-backed, non-conflicting identity edges are included.")
    print("All unresolved or ambiguous identities remain outside the registry.")
    print("=" * 88)
