from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from variable_capability_inventory import build_inventory

FPL_REGISTRY = ROOT / "data" / "fpl_canonical_variable_registry_v1.csv"


def _read_csv(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return tuple(csv.DictReader(fh))


def _fpl_index() -> dict[tuple[str, str, str, str], dict[str, str]]:
    return {
        (
            row.get("source_surface", ""),
            row.get("resource", ""),
            row.get("grain", ""),
            row.get("field_name", ""),
        ): row
        for row in _read_csv(FPL_REGISTRY)
    }


def _native(row: dict) -> str:
    fields = row.get("source", {}).get("native_fields", [])
    return str(fields[0]) if fields else ""


def main() -> int:
    inventory = build_inventory(ROOT)
    review = [r for r in inventory["variables"] if r["football_meaning"]["status"] == "REVIEW_REQUIRED"]
    print(f"TOTAL_REVIEW_REQUIRED: {len(review)}")

    by_surface = Counter(r["source"]["surface"] for r in review)
    print("\nBY_SURFACE")
    for k, v in by_surface.most_common():
        print(f"  {k}: {v}")

    # FRL local: expose the exact semantic-status composition.
    local = [r for r in review if r["source"]["surface"] == "FRL_LOCAL_CSV"]
    print("\nFRL_LOCAL_CSV_BY_SEMANTIC_STATUS")
    local_status = Counter(str(r["governance"].get("semantic_status") or "UNKNOWN") for r in local)
    for k, v in local_status.most_common():
        print(f"  {k}: {v}")
    print("FRL_LOCAL_CSV_BY_RESOURCE")
    for k, v in Counter(r["source"]["resource"] for r in local).most_common():
        print(f"  {k}: {v}")

    # FPL: use the authoritative registry subclass rather than guessing names.
    fpl_idx = _fpl_index()
    fpl = [r for r in review if r["source"]["surface"] == "fpl"]
    subclass_counts = Counter()
    resource_counts = Counter()
    subclass_fields: dict[str, list[str]] = {}
    for r in fpl:
        field = _native(r)
        key = ("fpl", r["source"]["resource"], "sample_payload", field)
        registry = fpl_idx.get(key)
        if registry is None:
            # Registry grain is sample_payload for discovery rows; fall back by resource/field.
            registry = next((x for x in fpl_idx.values() if x.get("resource") == r["source"]["resource"] and x.get("field_name") == field), None)
        subclass = (registry or {}).get("subclass") or "NO_REGISTRY_SUBCLASS"
        subclass_counts[subclass] += 1
        resource_counts[r["source"]["resource"]] += 1
        subclass_fields.setdefault(subclass, []).append(field)

    print("\nFPL_BY_SUBCLASS")
    for k, v in subclass_counts.most_common():
        print(f"  {k}: {v}")
    print("FPL_BY_RESOURCE")
    for k, v in resource_counts.most_common():
        print(f"  {k}: {v}")
    print("FPL_SUBCLASS_EXAMPLES")
    for subclass, _ in subclass_counts.most_common():
        examples = subclass_fields.get(subclass, [])[:12]
        print(f"  {subclass}: {', '.join(examples)}")

    # PulseLive: separate stat residue from events/lineups/commentary/fixture context.
    pulse = [r for r in review if r["source"]["surface"] == "pulselive"]
    groups = Counter()
    examples: dict[str, list[str]] = {}
    for r in pulse:
        field = _native(r)
        if field.startswith("resources.stats"):
            group = "TEAM_MATCH_STATS"
        elif field.startswith("resources.events"):
            group = "EVENTS"
        elif field.startswith("resources.lineups"):
            group = "LINEUPS"
        elif field.startswith("resources.commentary"):
            group = "COMMENTARY"
        elif any(token in field for token in (".headers", ".endpoint", ".params", ".status_code")) or field.endswith(".retrieved_at"):
            group = "INFRASTRUCTURE"
        else:
            group = "FIXTURE_CONTEXT"
        groups[group] += 1
        examples.setdefault(group, []).append(field)

    print("\nPULSELIVE_BY_GROUP")
    for k, v in groups.most_common():
        print(f"  {k}: {v}")
    print("PULSELIVE_GROUP_EXAMPLES")
    for group, _ in groups.most_common():
        print(f"  {group}: {', '.join(examples[group][:12])}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
