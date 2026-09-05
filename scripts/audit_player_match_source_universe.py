from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import player_match_stats
from source_field_registry import fields_for_family

CORE_SEASONS = (
    "2016-17", "2017-18", "2018-19", "2019-20", "2020-21",
    "2021-22", "2022-23", "2023-24", "2024-25", "2025-26",
)


def build_audit() -> dict[str, object]:
    observed_by_season: dict[str, tuple[str, ...]] = {}
    union: set[str] = set()
    for season in CORE_SEASONS:
        fields = tuple(sorted(player_match_stats.source_fields(season)))
        observed_by_season[season] = fields
        union.update(fields)

    registry = {spec.source_field: spec.semantic_status for spec in fields_for_family("player_match")}
    rows = []
    for field in sorted(union):
        seasons = [season for season in CORE_SEASONS if field in observed_by_season[season]]
        rows.append({
            "source_field": field,
            "seasons": seasons,
            "season_count": len(seasons),
            "registry_status": registry.get(field, "UNCATALOGUED"),
        })

    uncatalogued = sorted(field for field in union if field not in registry)
    exposed_not_observed = sorted(
        field for field, status in registry.items() if status == "exposed" and field not in union
    )
    status_counts = Counter(row["registry_status"] for row in rows)
    return {
        "schema_version": "1.0.0",
        "seasons": list(CORE_SEASONS),
        "observed_source_field_union": len(union),
        "registry_status_counts_for_observed_fields": dict(sorted(status_counts.items())),
        "uncatalogued_observed_fields": uncatalogued,
        "exposed_registry_fields_not_observed_in_core_decade": exposed_not_observed,
        "all_observed_fields_accounted_for": not uncatalogued,
        "coverage_policy": (
            "Partial-period fields are legitimate capabilities. A source field is included when observed "
            "in any audited season; absence in other seasons remains unavailable rather than zero."
        ),
        "observed_by_season_counts": {
            season: len(fields) for season, fields in observed_by_season.items()
        },
        "rows": rows,
    }


def main() -> int:
    result = build_audit()
    print(json.dumps(result, indent=2))
    return 0 if result["all_observed_fields_accounted_for"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
