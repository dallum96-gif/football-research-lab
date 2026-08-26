"""Prioritised semantic-review queue for empirically discovered source fields.

No field is promoted by this module. It only orders evidence-backed source
fields for semantic review so the broad searchable universe can grow safely.
"""
from __future__ import annotations

from source_field_catalog import build_catalog

COVERAGE_PRIORITY = {
    "CORE_DECADE": 0,
    "LONG_RUN": 1,
    "INTERMITTENT": 2,
    "SINGLE_SEASON": 3,
}
STATUS_PRIORITY = {
    "UNCATALOGUED": 0,
    "retained": 1,
    "exposed": 2,
}


def build_review_queue() -> tuple[dict, ...]:
    rows = []
    for item in build_catalog():
        if item["registry_status"] != "UNCATALOGUED":
            continue
        priority = (
            COVERAGE_PRIORITY[item["coverage_class"]],
            -item["seasons_present"],
            item["family"],
            item["source_field"].casefold(),
        )
        rows.append({
            **item,
            "review_priority": priority,
            "review_reason": (
                "Empirically observed in approved source but not semantically assessed; "
                "promotion requires source meaning, unit/type, temporal coverage, and query-safety review."
            ),
        })
    return tuple(sorted(rows, key=lambda row: row["review_priority"]))


# Backwards-compatible public name used by the full-universe audit.
def build_queue() -> tuple[dict, ...]:
    return build_review_queue()


def summary() -> dict:
    queue = build_review_queue()
    return {
        "total_uncatalogued": len(queue),
        "core_decade": sum(r["coverage_class"] == "CORE_DECADE" for r in queue),
        "long_run": sum(r["coverage_class"] == "LONG_RUN" for r in queue),
        "intermittent": sum(r["coverage_class"] == "INTERMITTENT" for r in queue),
        "single_season": sum(r["coverage_class"] == "SINGLE_SEASON" for r in queue),
        "by_family": {
            family: sum(r["family"] == family for r in queue)
            for family in ("team_match", "player_match", "player_season", "squad")
        },
    }


if __name__ == "__main__":
    report = summary()
    print("=" * 96)
    print("FRL SOURCE-FIELD SEMANTIC REVIEW QUEUE")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    print(f"Uncatalogued fields: {report['total_uncatalogued']}")
    print(f"Core decade:         {report['core_decade']}")
    print(f"Long run:            {report['long_run']}")
    print(f"Intermittent:        {report['intermittent']}")
    print(f"Single season:       {report['single_season']}")
    print()
    print("BY FAMILY")
    for family, count in report["by_family"].items():
        print(f"  {family:14} {count}")
    print("=" * 96)
