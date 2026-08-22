"""Profile the variables whose grain could not be resolved by the current relationship audit.

Evidence-only. Reads the existing variable/entity coverage output and reports the
raw source/decomposed grain, source surface, resource, and decomposition basis for
unmapped variables. No grain inference, join inference, or canonical promotion.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
INPUT = DATA / "variable_entity_relationship_coverage.csv"
OUT = DATA / "unmapped_variable_grain_profile.csv"


def load(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> list[dict[str, str]]:
    rows = load(INPUT)
    unmapped = [r for r in rows if r.get("grain") == "unmapped_review"]

    grouped: dict[tuple[str, str, str, str], list[str]] = defaultdict(list)
    for r in unmapped:
        key = (
            r.get("grain", ""),
            r.get("source_surface", ""),
            r.get("resource", ""),
            r.get("decomposition_basis", ""),
        )
        grouped[key].append(r.get("field_name", ""))

    out: list[dict[str, str]] = []
    for (grain, surface, resource, basis), fields in sorted(grouped.items(), key=lambda x: (-len(x[1]), x[0])):
        out.append({
            "current_grain_status": grain,
            "source_surface": surface,
            "resource": resource,
            "decomposition_basis": basis,
            "variable_count": str(len(fields)),
            "sample_variables": " | ".join(fields[:12]),
        })

    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        cols = list(out[0]) if out else [
            "current_grain_status", "source_surface", "resource",
            "decomposition_basis", "variable_count", "sample_variables"
        ]
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(out)
    return out


if __name__ == "__main__":
    rows = main()
    print("FRL UNMAPPED VARIABLE GRAIN PROFILE")
    print("=" * 100)
    print(f"Unmapped variables: {sum(int(r['variable_count']) for r in rows)}")
    print(f"Distinct unmapped source/basis groups: {len(rows)}")
    print("\nTOP GROUPS")
    for r in rows[:30]:
        print(
            f"  {int(r['variable_count']):4d} | "
            f"surface={r['source_surface']} | resource={r['resource']} | "
            f"basis={r['decomposition_basis']} | samples={r['sample_variables']}"
        )
    print(f"\nOutput: {OUT}")
    print("Evidence-only profiling; no grain inference and no canonical promotion.")
