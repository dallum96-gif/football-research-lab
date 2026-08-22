"""Crosswalk the stratified PL/PulseLive season schema against the FRL universe.

Exact grain + native field-name comparison only. No semantic promotion.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UPSTREAM = ROOT / "data" / "upstream_pl_stats_schema_by_season.csv"
FRL = ROOT / "data" / "master_variable_universe_decomposed.csv"
OUTPUT = ROOT / "data" / "pl_stats_season_universe_vs_frl.csv"


def load_pairs(path: Path, grain_col: str = "grain", field_col: str = "field_name") -> set[tuple[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return {
            (row.get(grain_col, ""), row.get(field_col, ""))
            for row in csv.DictReader(fh)
            if row.get(grain_col) and row.get(field_col)
        }


def compare(upstream: set[tuple[str, str]], frl: set[tuple[str, str]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for grain, field in sorted(upstream | frl):
        in_u = (grain, field) in upstream
        in_f = (grain, field) in frl
        state = "BOTH" if in_u and in_f else "UPSTREAM_ONLY" if in_u else "FRL_ONLY"
        out.append({"grain": grain, "field_name": field, "state": state})
    return out


def main() -> None:
    upstream = load_pairs(UPSTREAM)
    frl = load_pairs(FRL)
    rows = compare(upstream, frl)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["grain", "field_name", "state"])
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(row["state"] for row in rows)
    print("FRL VS STRATIFIED PL_STATS SEASON-UNIVERSE CROSSWALK")
    print("=" * 90)
    print(f"Upstream season-universe variables: {len(upstream)}")
    print(f"FRL local variables:                {len(frl)}")
    print(f"BOTH:                               {counts['BOTH']}")
    print(f"UPSTREAM_ONLY:                      {counts['UPSTREAM_ONLY']}")
    print(f"FRL_ONLY:                           {counts['FRL_ONLY']}")
    print("\nUPSTREAM_ONLY BY GRAIN")
    grain_counts = Counter(row["grain"] for row in rows if row["state"] == "UPSTREAM_ONLY")
    for grain, count in grain_counts.most_common():
        print(f"  {count:4d}  {grain}")
    print(f"\nOutput: {OUTPUT}")
    print("Exact grain + native field-name comparison; no semantic promotion.")


if __name__ == "__main__":
    main()
