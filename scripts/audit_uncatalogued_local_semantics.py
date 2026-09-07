"""Read-only audit of uncatalogued local FRL semantic fields.

Focuses on FRL_LOCAL_CSV catalogue rows whose semantic_status is UNCATALOGUED
and whose capability inventory football meaning still fails closed.  The audit
looks for exact source-native field-name overlap with already governed source
field families.  It does not promote or rewrite any variable.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from canonical_variable_catalogue import canonical_variables
from source_field_registry import fields_for_family


def _registry_by_name() -> dict[str, list[dict[str, str]]]:
    rows: dict[str, list[dict[str, str]]] = {}
    for family in ("team_match", "player_match", "player_season", "squad"):
        for spec in fields_for_family(family):
            rows.setdefault(spec.source_field, []).append(
                {
                    "family": family,
                    "semantic_status": spec.semantic_status,
                    "frl_field": spec.frl_field or "",
                    "notes": spec.notes or "",
                }
            )
    return rows


def build_audit() -> dict[str, Any]:
    catalogue = canonical_variables()
    registry = _registry_by_name()

    targets = [
        row
        for row in catalogue
        if str(row.get("source_surface") or "") == "FRL_LOCAL_CSV"
        and str(row.get("semantic_status") or "").upper() == "UNCATALOGUED"
    ]

    audited: list[dict[str, Any]] = []
    for row in targets:
        field = str(row.get("field_name") or "")
        overlaps = registry.get(field, [])
        exposed_elsewhere = [
            item for item in overlaps
            if item["semantic_status"] in {"exposed", "derived"}
        ]
        retained_elsewhere = [
            item for item in overlaps
            if item["semantic_status"] == "retained"
        ]
        restricted_elsewhere = [
            item for item in overlaps
            if item["semantic_status"] == "restricted"
        ]
        if exposed_elsewhere:
            candidate = "EXACT_NAME_ALREADY_GOVERNED_ELSEWHERE"
        elif retained_elsewhere:
            candidate = "EXACT_NAME_RETAINED_ELSEWHERE"
        elif restricted_elsewhere:
            candidate = "EXACT_NAME_RESTRICTED_ELSEWHERE"
        else:
            candidate = "NO_EXACT_GOVERNED_NAME_MATCH"

        audited.append(
            {
                "resource": str(row.get("resource") or ""),
                "grain": str(row.get("grain") or ""),
                "field_name": field,
                "navigation_category": str(row.get("navigation_category") or ""),
                "navigation_subcategory": str(row.get("navigation_subcategory") or ""),
                "coverage": str(row.get("notes") or ""),
                "candidate_class": candidate,
                "registry_overlaps": overlaps,
            }
        )

    by_candidate = Counter(row["candidate_class"] for row in audited)
    by_resource = Counter(row["resource"] for row in audited)
    by_category = Counter(row["navigation_category"] for row in audited)

    exact_governed = [
        row for row in audited
        if row["candidate_class"] == "EXACT_NAME_ALREADY_GOVERNED_ELSEWHERE"
    ]
    unresolved = [
        row for row in audited
        if row["candidate_class"] == "NO_EXACT_GOVERNED_NAME_MATCH"
    ]

    return {
        "uncatalogued_local_count": len(audited),
        "by_candidate_class": dict(sorted(by_candidate.items())),
        "by_resource": dict(sorted(by_resource.items())),
        "by_navigation_category": dict(sorted(by_category.items())),
        "exact_name_already_governed_count": len(exact_governed),
        "exact_name_already_governed": exact_governed,
        "no_exact_governed_name_match_count": len(unresolved),
        "no_exact_governed_name_match": unresolved,
        "all_rows": audited,
        "interpretation": (
            "Exact-name overlap is semantic evidence, not automatic cross-grain promotion. "
            "A Player-Match field and Player-Season field can share a football meaning while "
            "still requiring separate aggregation, coverage and temporal governance."
        ),
    }


def main() -> int:
    audit = build_audit()
    print(f"Uncatalogued FRL_LOCAL_CSV fields: {audit['uncatalogued_local_count']}")
    print(f"Exact source-native name already governed elsewhere: {audit['exact_name_already_governed_count']}")
    print(f"No exact governed name match: {audit['no_exact_governed_name_match_count']}")

    print("\nCandidate classes:")
    for key, value in audit["by_candidate_class"].items():
        print(f"  {key}: {value}")

    print("\nResources:")
    for key, value in audit["by_resource"].items():
        print(f"  {key}: {value}")

    print("\nNavigation categories:")
    for key, value in audit["by_navigation_category"].items():
        print(f"  {key}: {value}")

    print("\nExact-name governed candidates:")
    for row in audit["exact_name_already_governed"]:
        overlaps = ", ".join(
            f"{item['family']}={item['semantic_status']}"
            for item in row["registry_overlaps"]
        )
        print(f"  {row['resource']} :: {row['field_name']} -> {overlaps}")

    print("\nNo exact governed-name match:")
    for row in audit["no_exact_governed_name_match"]:
        print(
            f"  {row['resource']} :: {row['field_name']} :: "
            f"{row['navigation_category']} / {row['navigation_subcategory']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
