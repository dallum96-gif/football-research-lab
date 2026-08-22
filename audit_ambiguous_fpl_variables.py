"""Audit ambiguous FPL variables by captured source-path/resource evidence.

No semantic or canonical promotion. This report only groups ambiguous fields by
all observed raw resource/grain candidates so the remaining cases can be resolved
from context rather than guesswork.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "unmapped_variable_resolution_fpl_all_raw.csv"
OUTPUT = ROOT / "data" / "ambiguous_fpl_variable_audit.csv"


def load(path: Path = INPUT) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def run(input_path: Path = INPUT, output_path: Path = OUTPUT) -> list[dict[str, str]]:
    rows = [r for r in load(input_path) if r.get("resolution_status") == "AMBIGUOUS_RAW_FPL_GRAIN"]
    grouped: dict[str, dict[str, str]] = {}
    candidates: defaultdict[str, set[str]] = defaultdict(set)
    resources: defaultdict[str, set[str]] = defaultdict(set)
    surfaces: defaultdict[str, set[str]] = defaultdict(set)
    for row in rows:
        field = row.get("field_name", "")
        candidates[field].update(filter(None, (row.get("upstream_matches", "").split(";"))))
        resources[field].add(row.get("resource", ""))
        surfaces[field].add(row.get("source_surface", ""))
        grouped.setdefault(field, row)

    out: list[dict[str, str]] = []
    for field in sorted(grouped):
        base = grouped[field]
        out.append({
            "field_name": field,
            "candidate_grains": ";".join(sorted(candidates[field])),
            "resources": ";".join(sorted(x for x in resources[field] if x)),
            "source_surfaces": ";".join(sorted(x for x in surfaces[field] if x)),
            "field_type": base.get("field_type", ""),
            "review_status": "OPEN",
            "resolution": "",
            "evidence_required": "resource/path context, not field-name inference",
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(out[0].keys()) if out else [
        "field_name","candidate_grains","resources","source_surfaces",
        "field_type","review_status","resolution","evidence_required"
    ]
    with output_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(out)
    return out


def main() -> None:
    out = run()
    print("FRL AMBIGUOUS FPL VARIABLE AUDIT")
    print("=" * 80)
    print(f"Distinct ambiguous field names: {len(out)}")
    print(f"Output: {OUTPUT}")
    print("No semantic/canonical promotion; context-only review.")
    if out:
        counts = Counter(r["candidate_grains"] for r in out)
        print("\nCANDIDATE-GRAIN PATTERNS")
        for key, count in counts.most_common(15):
            print(f"  {count:4d}  {key}")


if __name__ == "__main__":
    main()
