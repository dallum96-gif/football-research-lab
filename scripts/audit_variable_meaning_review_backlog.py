"""Read-only audit of FRL Variable Capability Inventory meaning-review backlog.

This does not promote or rewrite any variable. It reconciles current
``football_meaning=REVIEW_REQUIRED`` records against semantic decisions already
present in the authoritative canonical catalogue/source-field registry overlay.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from canonical_variable_catalogue import canonical_variables
from variable_capability_inventory import build_inventory


def _catalogue_record_id(row: dict[str, str]) -> str:
    return "catalogue:" + ":".join(
        (
            str(row.get("source_surface") or ""),
            str(row.get("resource") or ""),
            str(row.get("grain") or ""),
            str(row.get("field_name") or ""),
        )
    )


def _bucket(semantic_status: str, *, is_catalogue: bool) -> str:
    status = semantic_status.strip().casefold()
    if not is_catalogue:
        return "NON_CATALOGUE_REVIEW"
    if status in {"exposed", "derived"}:
        return "ALREADY_SEMANTICALLY_PROMOTED"
    if status == "retained":
        return "RETAINED_SOURCE_NATIVE"
    if status == "restricted":
        return "RESTRICTED_FAIL_CLOSED"
    if status == "unknown":
        return "UNKNOWN_SEMANTICS"
    return "UNCLASSIFIED_SEMANTIC_STATUS"


def build_review_audit() -> dict[str, Any]:
    inventory = build_inventory()
    catalogue = {
        _catalogue_record_id(row): row
        for row in canonical_variables()
    }

    review_rows = [
        row
        for row in inventory["variables"]
        if row["football_meaning"]["status"] == "REVIEW_REQUIRED"
    ]

    reconciled: list[dict[str, str]] = []
    for row in review_rows:
        record_id = str(row["record_id"])
        catalogue_row = catalogue.get(record_id)
        semantic_status = (
            str(catalogue_row.get("semantic_status") or "UNKNOWN")
            if catalogue_row is not None
            else str(row.get("governance", {}).get("semantic_status") or "UNKNOWN")
        )
        source = row["source"]
        reconciled.append(
            {
                "record_id": record_id,
                "canonical_name": str(row["canonical_name"]),
                "capability_family": str(row["capability_family"]),
                "source_family": str(source["family"]),
                "source_surface": str(source["surface"]),
                "semantic_status": semantic_status,
                "bucket": _bucket(semantic_status, is_catalogue=catalogue_row is not None),
            }
        )

    bucket_counts = Counter(row["bucket"] for row in reconciled)
    promoted = bucket_counts["ALREADY_SEMANTICALLY_PROMOTED"]

    by_family = Counter(
        row["capability_family"]
        for row in reconciled
        if row["bucket"] == "ALREADY_SEMANTICALLY_PROMOTED"
    )
    by_surface = Counter(
        row["source_surface"]
        for row in reconciled
        if row["bucket"] == "ALREADY_SEMANTICALLY_PROMOTED"
    )

    examples = [
        {
            "record_id": row["record_id"],
            "canonical_name": row["canonical_name"],
            "family": row["capability_family"],
            "surface": row["source_surface"],
            "semantic_status": row["semantic_status"],
        }
        for row in reconciled
        if row["bucket"] == "ALREADY_SEMANTICALLY_PROMOTED"
    ][:30]

    return {
        "inventory_version": inventory["inventory_version"],
        "current_review_required": len(review_rows),
        "already_semantically_promoted_but_still_counted_review": promoted,
        "review_required_after_bookkeeping_reconciliation": len(review_rows) - promoted,
        "bucket_counts": dict(sorted(bucket_counts.items())),
        "already_promoted_by_capability_family": dict(sorted(by_family.items())),
        "already_promoted_by_source_surface": dict(sorted(by_surface.items())),
        "first_30_already_promoted_examples": examples,
        "interpretation": (
            "ALREADY_SEMANTICALLY_PROMOTED means the authoritative source-field semantic "
            "registry/catalogue overlay says exposed or derived while the generated capability "
            "inventory still labels football meaning REVIEW_REQUIRED. This audit does not change "
            "any governance state."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the complete audit object as JSON.",
    )
    args = parser.parse_args()

    audit = build_review_audit()
    if args.json:
        print(json.dumps(audit, indent=2, ensure_ascii=False))
        return 0

    print(f"Current REVIEW_REQUIRED meanings: {audit['current_review_required']}")
    print(
        "Already semantically promoted but still counted REVIEW_REQUIRED: "
        f"{audit['already_semantically_promoted_but_still_counted_review']}"
    )
    print(
        "Review backlog after bookkeeping reconciliation: "
        f"{audit['review_required_after_bookkeeping_reconciliation']}"
    )
    print("\nBuckets:")
    for key, value in audit["bucket_counts"].items():
        print(f"  {key}: {value}")
    print("\nAlready-promoted records by capability family:")
    for key, value in audit["already_promoted_by_capability_family"].items():
        print(f"  {key}: {value}")
    print("\nAlready-promoted records by source surface:")
    for key, value in audit["already_promoted_by_source_surface"].items():
        print(f"  {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
