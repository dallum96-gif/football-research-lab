"""Crosswalk longitudinal upstream PL/PulseLive schema against FRL inventory."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UPSTREAM = ROOT / "data" / "upstream_pl_stats_schema_by_season.csv"
FRL_LOCAL = ROOT / "data" / "master_variable_universe.csv"
OUTPUT = ROOT / "data" / "pl_stats_season_universe_vs_frl.csv"


def load_pairs(path: Path) -> set[tuple[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        out: set[tuple[str, str]] = set()
        for row in csv.DictReader(fh):
            grain = row.get("grain") or row.get("resource")
            field = row.get("field_name", "")
            if grain and field:
                out.add((grain, field))
        return out


def compare(upstream: set[tuple[str, str]], frl: set[tuple[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for grain, field in sorted(upstream | frl):
        iu = (grain, field) in upstream
        iff = (grain, field) in frl
        rows.append({
            "grain": grain,
            "field_name": field,
            "state": "BOTH" if iu and iff else "UPSTREAM_ONLY" if iu else "FRL_ONLY",
        })
    return rows


def main() -> None:
    upstream = load_pairs(UPSTREAM)
    frl = load_pairs(FRL_LOCAL)
    rows = compare(upstream, frl)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["grain", "field_name", "state"])
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(r["state"] for r in rows)
    by_grain = Counter(r["grain"] for r in rows if r["state"] == "UPSTREAM_ONLY")
    print("FRL VS LONGITUDINAL UPSTREAM PL_STATS CROSSWALK")
    print("=" * 90)
    print(f"Upstream longitudinal variables: {len(upstream)}")
    print(f"FRL local variables:             {len(frl)}")
    print(f"BOTH:                            {counts['BOTH']}")
    print(f"UPSTREAM_ONLY:                   {counts['UPSTREAM_ONLY']}")
    print(f"FRL_ONLY:                        {counts['FRL_ONLY']}")
    print("\nUPSTREAM_ONLY BY GRAIN")
    for grain, count in by_grain.most_common():
        print(f"  {count:4d}  {grain}")
    print(f"\nOutput: {OUTPUT}")
    print("Exact grain + native field-name comparison; no semantic promotion.")


if __name__ == "__main__":
    main()
