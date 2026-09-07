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


def _counter(rows: list[dict[str, str]], key: str, *, bucket: str | None = None) -> dict[str, int]:
    values = Counter(
        row[key] or "<blank>"
        for row in rows
        if bucket is None or row["bucket"] == bucket
    )
    return dict(sorted(values.items(), key=lambda item: (-item[1], item[0])))


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
        governance = row.get("governance", {})
        reconciled.append(
            {
                "record_id": record_id,
                "canonical_name": str(row["canonical_name"]),
                "capability_family": str(row["capability_family"]),
                "grain": str(row.get("grain", {}).get("name") or ""),
                "source_family": str(source["family"]),
                "source_surface": str(source["surface"]),
                "source_resource": str(source.get("resource") or ""),
                "semantic_status": semantic_status,
                "navigation_category": str(
                    (catalogue_row or {}).get("navigation_category")
                    or governance.get("navigation_category")
                    or ""
                ),
                "navigation_subcategory": str(
                    (catalogue_row or {}).get("navigation_subcategory")
                    or governance.get("navigation_subcategory")
                    or ""
                ),
                "canonical_attachment": str(
                    (catalogue_row or {}).get("canonical_attachment")
                    or governance.get("canonical_attachment")
                    or ""
                ),
                "bucket": _bucket(semantic_status, is_catalogue=catalogue_row is not None),
            }
        )

    bucket_counts = Counter(row["bucket"] for row in reconciled)
    promoted = bucket_counts["ALREADY_SEMANTICALLY_PROMOTED"]
    unclassified = [row for row in reconciled if row["bucket"] == "UNCLASSIFIED_SEMANTIC_STATUS"]

    promoted_examples = [
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

    unclassified_examples = [
        {
            "record_id": row["record_id"],
            "canonical_name": row["canonical_name"],
            "family": row["capability_family"],
            "grain": row["grain"],
            "surface": row["source_surface"],
            "resource": row["source_resource"],
            "semantic_status": row["semantic_status"],
            "navigation_category": row["navigation_category"],
            "navigation_subcategory": row["navigation_subcategory"],
            "canonical_attachment": row["canonical_attachment"],
        }
        for row in unclassified[:50]
    ]

    return {
        "inventory_version": inventory["inventory_version"],
        "current_review_required": len(review_rows),
        "already_semantically_promoted_but_still_counted_review": promoted,
        "review_required_after_bookkeeping_reconciliation": len(review_rows) - promoted,
        "bucket_counts": dict(sorted(bucket_counts.items())),
        "already_promoted_by_capability_family": _counter(
            reconciled, "capability_family", bucket="ALREADY_SEMANTICALLY_PROMOTED"
        ),
        "already_promoted_by_source_surface": _counter(
            reconciled, "source_surface", bucket="ALREADY_SEMANTICALLY_PROMOTED"
        ),
        "unclassified_by_semantic_status": _counter(unclassified, "semantic_status"),
        "unclassified_by_source_surface": _counter(unclassified, "source_surface"),
        "unclassified_by_source_resource": _counter(unclassified, "source_resource"),
        "unclassified_by_capability_family": _counter(unclassified, "capability_family"),
        "unclassified_by_grain": _counter(unclassified, "grain"),
        "unclassified_by_navigation_category": _counter(unclassified, "navigation_category"),
        "unclassified_by_navigation_subcategory": _counter(unclassified, "navigation_subcategory"),
        "unclassified_by_canonical_attachment": _counter(unclassified, "canonical_attachment"),
        "first_30_already_promoted_examples": promoted_examples,
        "first_50_unclassified_examples": unclassified_examples,
        "interpretation": (
            "ALREADY_SEMANTICALLY_PROMOTED means the authoritative source-field semantic "
            "registry/catalogue overlay says exposed or derived while the generated capability "
            "inventory still labels football meaning REVIEW_REQUIRED. UNCLASSIFIED_SEMANTIC_STATUS "
            "means the catalogue carries a semantic-status value outside the inventory audit's "
            "explicit exposed/derived/retained/restricted/unknown vocabulary. This audit does not "
            "change any governance state."
        ),
    }


def _print_section(title: str, values: dict[str, int]) -> None:
    print(f"\n{title}:")
    for key, value in values.items():
        print(f"  {key}: {value}")


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
    _print_section("Buckets", audit["bucket_counts"])
    _print_section(
        "Already-promoted records by capability family",
        audit["already_promoted_by_capability_family"],
    )
    _print_section(
        "Already-promoted records by source surface",
        audit["already_promoted_by_source_surface"],
    )
    _print_section("Unclassified records by semantic status", audit["unclassified_by_semantic_status"])
    _print_section("Unclassified records by source surface", audit["unclassified_by_source_surface"])
    _print_section("Unclassified records by source resource", audit["unclassified_by_source_resource"])
    _print_section("Unclassified records by capability family", audit["unclassified_by_capability_family"])
    _print_section("Unclassified records by grain", audit["unclassified_by_grain"])
    _print_section(
        "Unclassified records by navigation category",
        audit["unclassified_by_navigation_category"],
    )
    _print_section(
        "Unclassified records by navigation subcategory",
        audit["unclassified_by_navigation_subcategory"],
    )
    _print_section(
        "Unclassified records by canonical attachment",
        audit["unclassified_by_canonical_attachment"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
