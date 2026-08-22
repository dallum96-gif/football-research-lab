"""Read-only audit of the complete searchable source-field universe.

Counts empirical source-native fields across all approved seasons/families and
separates curated semantic fields from fields discovered in source but not yet
semantically reviewed.
"""
from __future__ import annotations

from collections import Counter, defaultdict

from source_field_catalog import FAMILIES, SEASONS, build_catalog


def run() -> dict:
    rows = build_catalog()
    by_family = Counter(row["family"] for row in rows)
    by_status = Counter(row["registry_status"] for row in rows)
    by_coverage = Counter(row["coverage_class"] for row in rows)

    uncatalogued = [
        row for row in rows
        if row["registry_status"] == "UNCATALOGUED"
    ]

    family_status = defaultdict(Counter)
    for row in rows:
        family_status[row["family"]][row["registry_status"]] += 1

    return {
        "seasons": len(SEASONS),
        "families": len(FAMILIES),
        "total_fields": len(rows),
        "by_family": dict(by_family),
        "by_status": dict(by_status),
        "by_coverage": dict(by_coverage),
        "family_status": {family: dict(values) for family, values in family_status.items()},
        "uncatalogued": uncatalogued,
    }


def print_report(report: dict) -> None:
    print("=" * 112)
    print("FRL SEARCHABLE SOURCE-FIELD UNIVERSE AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 112)
    print(f"Seasons:             {report['seasons']}")
    print(f"Source families:     {report['families']}")
    print(f"Distinct fields:     {report['total_fields']:,}")
    print()

    print("BY FAMILY")
    for family in FAMILIES:
        print(f"  {family:14} {report['by_family'].get(family, 0):4}")
    print()

    print("BY REGISTRY STATUS")
    for status, count in sorted(report["by_status"].items()):
        print(f"  {status:14} {count:4}")
    print()

    print("BY COVERAGE CLASS")
    for coverage, count in sorted(report["by_coverage"].items()):
        print(f"  {coverage:14} {count:4}")
    print()

    print("UNCATALOGUED FIELDS BY FAMILY")
    uncatalogued = report["uncatalogued"]
    for family in FAMILIES:
        fields = [row for row in uncatalogued if row["family"] == family]
        print(f"  {family}: {len(fields)}")
        for row in fields[:25]:
            print(
                f"    {row['source_field']} | "
                f"{row['first_seen_season']} -> {row['last_seen_season']} | "
                f"{row['coverage_class']} | seasons={row['seasons_present']}/{row['seasons_total']}"
            )
        if len(fields) > 25:
            print(f"    ... {len(fields) - 25} more")
    print()
    print("No files were written or modified.")
    print("=" * 112)


if __name__ == "__main__":
    print_report(run())
